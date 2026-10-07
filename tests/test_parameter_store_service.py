from unittest.mock import patch

import pytest
from botocore.exceptions import ClientError

from app.services.parameter_store_service import get_parameter


@patch("app.services.parameter_store_service.ssm_client")
def test_get_parameter_string(mock_ssm_client):
    mock_ssm_client.get_parameter.return_value = {
        "Parameter": {
            "Value": "us-east-1"
        }
    }

    value = get_parameter(
        "/product-api/prod/aws-region"
    )

    assert value == "us-east-1"

    mock_ssm_client.get_parameter.assert_called_once_with(
        Name="/product-api/prod/aws-region",
        WithDecryption=False,
    )


@patch("app.services.parameter_store_service.ssm_client")
def test_get_secure_parameter(mock_ssm_client):
    mock_ssm_client.get_parameter.return_value = {
        "Parameter": {
            "Value": "fake-test-secret"
        }
    }

    value = get_parameter(
        "/product-api/prod/jwt-secret-key",
        with_decryption=True,
    )

    assert value == "fake-test-secret"

    mock_ssm_client.get_parameter.assert_called_once_with(
        Name="/product-api/prod/jwt-secret-key",
        WithDecryption=True,
    )


@patch("app.services.parameter_store_service.ssm_client")
def test_get_parameter_client_error(mock_ssm_client):
    mock_ssm_client.get_parameter.side_effect = ClientError(
        {
            "Error": {
                "Code": "ParameterNotFound",
                "Message": "Parameter not found",
            }
        },
        "GetParameter",
    )

    with pytest.raises(
        RuntimeError,
        match="Unable to retrieve parameter",
    ):
        get_parameter(
            "/product-api/prod/missing-parameter"
        )
