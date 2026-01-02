from unittest import mock

import pytest
from unittest.mock import MagicMock, Mock, patch, mock_open

from nrdtech_aws_utils.s3_helper import S3Helper


@pytest.fixture
def s3_client_mock():
    return Mock()


@pytest.fixture
def s3_helper(s3_client_mock):
    return S3Helper(s3_client_mock)


def test_upload_file_success(s3_helper, s3_client_mock):
    # Setup
    filename = "test.txt"
    bucket_name = "mybucket"
    key = "test/test.txt"

    # Act
    s3_helper.upload_file(filename, bucket_name, key)

    # Assert
    s3_client_mock.upload_file.assert_called_once_with(
        filename, bucket_name, key, ExtraArgs={"ContentType": "text/plain"}
    )


def test_upload_data_success(s3_helper, s3_client_mock):
    # Setup
    data = "Hello, World!"
    bucket_name = "mybucket"
    key = "test/data.txt"

    # Act
    s3_helper.upload_data(data, bucket_name, key)

    # Assert
    # You should check that a file was created, data written to it, and uploaded
    # Asserts will depend on how you mock tempfile.NamedTemporaryFile


def test_download_file_success(s3_helper, s3_client_mock):
    # Setup
    bucket_name = "mybucket"
    key = "test/test.txt"
    expected_content = "File content"

    # Act
    with patch("builtins.open", mock_open(read_data=expected_content)) as mock_file:
        content = s3_helper.download_file(bucket_name, key)

    # Assert
    s3_client_mock.download_file.assert_called_once_with(bucket_name, key, mock.ANY)
    assert content == expected_content


def test_download_file_from_s3_path_success(s3_helper, s3_client_mock):
    # Setup
    s3_path = "s3://mybucket/test/test.txt"
    expected_content = "File content"

    # Act
    with patch("builtins.open", mock_open(read_data=expected_content)) as mock_file:
        content = s3_helper.download_file_from_s3_path(s3_path)

    # Assert
    assert content == expected_content


def test_guess_mime_type_from_filename():
    # Test with known file extensions
    assert S3Helper._guess_mime_type_from_filename("file.txt") == "text/plain"
    assert S3Helper._guess_mime_type_from_filename("image.jpg") == "image/jpeg"
    assert S3Helper._guess_mime_type_from_filename("document.pdf") == "application/pdf"
    assert S3Helper._guess_mime_type_from_filename("archive.zip") == "application/zip"


def test_guess_mime_type_from_filename_unknown():
    # Test with unknown file extension - should default to application/octet-stream
    assert (
        S3Helper._guess_mime_type_from_filename("file.unknown")
        == "application/octet-stream"
    )
    assert (
        S3Helper._guess_mime_type_from_filename("file_without_extension")
        == "application/octet-stream"
    )


def test_upload_data_file_not_found_error(s3_helper, s3_client_mock):
    # Setup
    data = "Hello, World!"
    bucket_name = "mybucket"
    key = "test/data.txt"

    # Act
    with patch("tempfile.NamedTemporaryFile") as mock_tempfile:
        mock_file = MagicMock()
        mock_file.write = MagicMock()
        mock_file.close = MagicMock()
        mock_file.name = "/tmp/test_file"
        mock_tempfile.return_value = mock_file
        with patch("os.remove", side_effect=FileNotFoundError):
            # Should not raise an exception even if file is already removed
            s3_helper.upload_data(data, bucket_name, key)
        # Verify upload_file was called
        assert s3_client_mock.upload_file.called
