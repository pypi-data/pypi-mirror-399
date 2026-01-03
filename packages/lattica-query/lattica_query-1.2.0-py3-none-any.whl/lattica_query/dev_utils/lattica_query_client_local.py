from lattica_query.lattica_query_client import QueryClient
from lattica_common.dev_utils.dev_mod_utils import RunMode, RUN_MODE, mock_upload_pk, mock_upload_custom_data


class LocalQueryClient(QueryClient):

    def upload_evaluation_key_file(self, pk_filename: str) -> None:
        print(f"Uploading evaluation key file '{pk_filename}' to server...")
        s3_key = self.agent_app.http_client.send_http_request('api/token/get_pk_upload_url')['s3Key']

        mock_upload_pk(pk_filename, s3_key)

        alert_upload_complete = self.agent_app.alert_upload_complete(s3_key)
        print(f"pk {pk_filename} uploaded status is {alert_upload_complete}.")

        print(f"Calling to preprocess {pk_filename}")
        self.worker_api.preprocess_pk()
        print("Evaluation key preprocessing on worker is complete.")

        return

    def upload_custom_encrypted_data(self, file_name: str) -> None:
        print(f"Uploading custom data file '{file_name}' to server...")
        s3_key = self.agent_app.http_client.send_http_request('api/token/get_custom_data_upload_url')['s3Key']

        mock_upload_custom_data(file_name, s3_key)

        alert_upload_complete = self.agent_app.alert_upload_complete(s3_key)
        print(f"{file_name} uploaded status is {alert_upload_complete}.")

        print(f'Calling to load custom encrypted data from {file_name}')
        self.worker_api.load_custom_encrypted_data()
        print("Custom encrypted data loading on worker is complete.")
        return

    def execute_query_flow(self, pipeline, pt=None):
        context, sk, client_pipeline = self.generate_key()

        pipeline.set_preprocessing_data(client_pipeline)

        if pt is None:
            pt = pipeline.get_example_pt()
        pt_expected = self.apply_clear(pt)
        pt_dec = self.run_query(context, sk, pt, client_pipeline, timing_report=True)

        pipeline.display_results(pt_dec, pt_expected)
        pipeline.verify_results(pt_dec, pt_expected)
