import mimetypes
import os
import tempfile


class S3Helper:
    def __init__(self, s3_client):
        self.s3_client = s3_client

    def upload_file(self, input_filename: str, bucket_name: str, key: str):
        mime_type = self._guess_mime_type_from_filename(input_filename)
        self.s3_client.upload_file(
            input_filename, bucket_name, key, ExtraArgs={"ContentType": mime_type}
        )

    def upload_data(self, data: str, bucket_name: str, key: str):
        temp_file = tempfile.NamedTemporaryFile(delete=False)
        try:
            temp_file.write(data.encode("utf-8"))
            temp_file.close()
            mime_type = self._guess_mime_type_from_filename(key)
            self.s3_client.upload_file(
                temp_file.name, bucket_name, key, ExtraArgs={"ContentType": mime_type}
            )
        finally:
            try:
                os.remove(temp_file.name)
            except FileNotFoundError:
                pass

    def download_file(self, bucket_name: str, key: str) -> str:
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            self.s3_client.download_file(bucket_name, key, temp_file.name)
            temp_file.flush()
            temp_file.seek(0)  # Move the cursor to the beginning of the file

        with open(temp_file.name, "r") as file:
            content = file.read()

        os.remove(temp_file.name)  # Delete the temporary file
        return content

    def download_file_from_s3_path(self, s3_path: str) -> str:
        assert s3_path.startswith("s3://")
        parts = s3_path.split("/")
        bucket_name = parts[2]
        key = "/".join(parts[3:])
        return self.download_file(bucket_name, key)

    @staticmethod
    def _guess_mime_type_from_filename(filename: str):
        # Guess the MIME type
        mime_type, _ = mimetypes.guess_type(filename)
        if mime_type is None:
            mime_type = "application/octet-stream"  # Default MIME type
        return mime_type
