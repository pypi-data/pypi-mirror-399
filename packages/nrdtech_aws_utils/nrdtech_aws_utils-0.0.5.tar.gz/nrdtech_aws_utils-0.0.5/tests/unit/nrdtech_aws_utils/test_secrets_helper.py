from unittest.mock import MagicMock

from nrdtech_aws_utils.secrets_helper import SecretsHelper


def test_secrets_success():
    secrets_client = MagicMock()
    secrets_client.get_secret_value = MagicMock(
        return_value={"SecretString": "some secret"}
    )
    with SecretsHelper(secrets_client) as secrets_helper:
        result = secrets_helper.get_secret("a_secret")
        assert result == "some secret"


def test_secrets_object_success():
    secrets_client = MagicMock()
    secrets_client.get_secret_value = MagicMock(
        return_value={
            "SecretString": '{"some": "json", "data": "structure", "count": 3}'
        }
    )
    with SecretsHelper(secrets_client) as secrets_helper:
        result = secrets_helper.get_secret("a_secret")
        assert result == {"some": "json", "data": "structure", "count": 3}
