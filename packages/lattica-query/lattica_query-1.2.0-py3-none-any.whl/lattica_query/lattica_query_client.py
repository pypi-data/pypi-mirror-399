import time
import os
import tempfile

from lattica_query import worker_api
from lattica_query.performance_utils import log_timing_breakdown
from timeit_decorator import timeit

from typing import TYPE_CHECKING, Tuple

from lattica_common.app_api import LatticaAppAPI
from lattica_query.worker_api import LatticaWorkerAPI
import lattica_query.query_toolkit as toolkit_interface

from lattica_query.serialization.hom_op_pb2 import (
    QueryClientSequentialHomOp as ProtoQueryClientSequentialHomOp,
    ClientData as ProtoClientData,
)

if TYPE_CHECKING:
    from lattica_query.worker_api import ClientPtTensor


class QueryClient:
    """
    A simple client to demonstrate how to:
      - Retrieve context from worker
      - Generate keys (secret_key, evaluation_key)
      - Upload the evaluation key file to server
      - Preprocess the evaluation key on the server
      - Run multiple queries homomorphically (comparing with clear)
    """

    def __init__(self, query_token: str):
        """
        Initialize the QueryClient with a user (query) token.
        """
        self.query_token = query_token
        self.agent_app = LatticaAppAPI(self.query_token, module_name='lattica_query')
        self.worker_api = LatticaWorkerAPI(self.query_token)

    def get_init_data(self) -> Tuple[bytes, bytes]:
        print("Retrieving user init data from worker...")
        serialized_client_data = self.worker_api.get_user_init_data()
        client_data_proto = ProtoClientData()
        client_data_proto.ParseFromString(serialized_client_data)

        return (client_data_proto.serialized_context,
                client_data_proto.serialized_client_sequential_hom_op)

    def generate_key(self) -> Tuple[bytes, Tuple[bytes, bytes], bytes]:
        """
        - Retrieve context/hom-sequence from the worker.
        - Generate FHE key pair (secret_key, evaluation_key).
        - Upload evaluation key

        Returns:
            (serialized_context, serialized_secret_key, serialized_homseq)
        """
        serialized_context, serialized_homseq = self.get_init_data()

        print("Creating client FHE keys...")
        serialized_secret_key, serialized_evaluation_key = toolkit_interface.generate_key(
            serialized_homseq,
            serialized_context,
        )

        print(f'Registering FHE evaluation key...')

        # Use custom path from env var or create temp file
        evk_pathname = os.getenv('LATTICA_EVK_PATHNAME')
        if evk_pathname:
            temp_filename = evk_pathname
        else:
            temp_dir = tempfile.mkdtemp()
            temp_filename = os.path.join(temp_dir, 'my_pk.lpk')
        
        with open(temp_filename, 'wb') as handle:
            handle.write(serialized_evaluation_key)

        try:
            self.upload_evaluation_key_file(temp_filename)
        finally:
            # Clean up only if using temp directory
            if not evk_pathname:
                os.remove(temp_filename)
                os.rmdir(temp_dir)

        return (
            serialized_context,
            serialized_secret_key,
            serialized_homseq,
        )

    def apply_clear(self, data_pt: 'ClientPtTensor') -> 'ClientPtTensor':
        return self.worker_api.apply_clear(data_pt)

    def _upload_user_file(self, file_name: str, endpoint: str) -> None:
        file_key = self.agent_app.upload_file(file_name, endpoint=endpoint)
        response = self.agent_app.alert_upload_complete(file_key)
        print(f"{file_name} uploaded status is {response}.")

    def upload_evaluation_key_file(self, pk_filename: str) -> None:
        """
        Upload the user's evaluation key file to the Lattica server,
        alert the server that upload completed, and then have the worker
        preprocess the key.
        """
        self._upload_user_file(pk_filename, endpoint='api/token/get_pk_upload_url')

        # Instruct the worker to preprocess the newly uploaded evaluation key
        print(f'Calling to preprocess {pk_filename}')
        self.worker_api.preprocess_pk()
        print("Evaluation key preprocessing on worker is complete.")
        return

    def upload_custom_encrypted_data(self, file_name: str) -> None:
        """
        Upload the custom encrypted data ZIP file to the Lattica server,
        alert the server that upload completed, and then have the worker
        process data.
        """
        self._upload_user_file(file_name, endpoint='api/token/get_custom_data_upload_url')

        # Instruct the worker to process the newly uploaded custom encrypted data
        print(f'Calling to load custom encrypted data from {file_name}')
        self.worker_api.load_custom_encrypted_data()
        print("Custom encrypted data loading on worker is complete.")
        return

    @timeit(log_level=None)
    def run_query(self,
                    serialized_context: bytes,
                    serialized_sk: tuple[bytes, bytes],
                    pt: 'ClientPtTensor',
                    serialized_homseq: bytes,
                    timing_report: bool = False,
                    ) -> 'ClientPtTensor':
        be_timing_accumulator = []
        client_timing_accumulator = []

        start = time.perf_counter()
        serialized_pt = worker_api.dumps_proto_tensor(pt)
        homsec_proto = ProtoQueryClientSequentialHomOp()
        homsec_proto.ParseFromString(serialized_homseq)
        client_blocks_proto = homsec_proto.client_blocks
        client_timing_accumulator.append(("serialization", time.perf_counter() - start))

        for block_proto in client_blocks_proto:
            start = time.perf_counter()
            print(f'Applying client operators')
            serialized_block_proto = block_proto.SerializeToString()
            serialized_pt = toolkit_interface.apply_client_block(
                serialized_block_proto, serialized_context, serialized_pt)
            client_timing_accumulator.append(("client_block", time.perf_counter() - start))
            if block_proto.is_last:
                break

            start = time.perf_counter()
            pt_axis_external = block_proto.pt_axis_external if block_proto.HasField("pt_axis_external") else None
            serialized_ct = toolkit_interface.enc(
                serialized_context, serialized_sk, serialized_pt, pack_for_transmission=True, n_axis_external=pt_axis_external)
            client_timing_accumulator.append(("encryption", time.perf_counter() - start))
            serialized_ct_res = self.worker_api.apply_hom_pipeline(
                serialized_ct, block_index=block_proto.block_index+1)
            be_timing_accumulator.append(self.worker_api.get_last_timing())
            start = time.perf_counter()
            serialized_pt = toolkit_interface.dec(serialized_context, serialized_sk, serialized_ct_res, homsec_proto.as_complex)
            client_timing_accumulator.append(("decryption", time.perf_counter() - start))

        start = time.perf_counter()
        result = worker_api.load_proto_tensor(serialized_pt)
        client_timing_accumulator.append(("serialization", time.perf_counter() - start))
        if timing_report:
            log_timing_breakdown(be_timing_accumulator, client_timing_accumulator)
        return result
