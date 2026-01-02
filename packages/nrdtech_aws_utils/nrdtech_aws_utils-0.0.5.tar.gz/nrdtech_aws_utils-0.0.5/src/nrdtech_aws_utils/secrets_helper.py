import json


class SecretsHelper:
    def __init__(self, secrets_client):
        self.secrets_client = secrets_client

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.secrets_client.close()

    def get_secret(self, secret_name):
        get_secret_value_response = self.secrets_client.get_secret_value(
            SecretId=secret_name
        )

        # Decrypts secret using the associated KMS key.
        secret = get_secret_value_response["SecretString"]
        if secret.startswith("{"):
            return json.loads(secret)
        return secret
