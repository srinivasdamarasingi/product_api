from unittest.mock import MagicMock, patch

import pytest
from botocore.exceptions import ClientError

from app.services.s3_service import (
    upload_file_to_s3,
    delete_file_from_s3,
    generate_presigned_url,
)


def test_upload_file_to_s3_success():
    file_obj = MagicMock()

    with patch(
        "app.services.s3_service.s3_client.upload_fileobj"
    ) as mock_upload:

        result = upload_file_to_s3(
            file_obj,
            "products/test.png",
            "image/png"
        )

    assert result == "products/test.png"

    mock_upload.assert_called_once()


def test_upload_file_to_s3_failure():
    file_obj = MagicMock()

    error = ClientError(
        {
            "Error": {
                "Code": "AccessDenied",
                "Message": "Access denied"
            }
        },
        "PutObject"
    )

    with patch(
        "app.services.s3_service.s3_client.upload_fileobj",
        side_effect=error
    ):
        with pytest.raises(
            RuntimeError,
            match="Failed to upload file to S3"
        ):
            upload_file_to_s3(
                file_obj,
                "products/test.png",
                "image/png"
            )


def test_delete_file_from_s3_success():
    with patch(
        "app.services.s3_service.s3_client.delete_object"
    ) as mock_delete:

        delete_file_from_s3(
            "products/test.png"
        )

    mock_delete.assert_called_once()


def test_delete_file_from_s3_failure():
    error = ClientError(
        {
            "Error": {
                "Code": "AccessDenied",
                "Message": "Access denied"
            }
        },
        "DeleteObject"
    )

    with patch(
        "app.services.s3_service.s3_client.delete_object",
        side_effect=error
    ):
        with pytest.raises(
            RuntimeError,
            match="Failed to delete file from S3"
        ):
            delete_file_from_s3(
                "products/test.png"
            )


def test_generate_presigned_url_success():
    with patch(
        "app.services.s3_service.s3_client.generate_presigned_url",
        return_value="https://example.com/signed"
    ) as mock_presigned:

        result = generate_presigned_url(
            "products/test.png",
            expires_in=300
        )

    assert result == "https://example.com/signed"

    mock_presigned.assert_called_once()


def test_generate_presigned_url_failure():
    error = ClientError(
        {
            "Error": {
                "Code": "AccessDenied",
                "Message": "Access denied"
            }
        },
        "GetObject"
    )

    with patch(
        "app.services.s3_service.s3_client.generate_presigned_url",
        side_effect=error
    ):
        with pytest.raises(
            RuntimeError,
            match="Failed to generate presigned URL"
        ):
            generate_presigned_url(
                "products/test.png",
                expires_in=300
            )
