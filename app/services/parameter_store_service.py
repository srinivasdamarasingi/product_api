import boto3
from botocore.exceptions import BotoCoreError, ClientError

ssm_client = boto3.client(
    "ssm",
    region_name="us-east-1",
)


def get_parameter(
    parameter_name: str,
    with_decryption: bool = False,
) -> str:
    try:
        response = ssm_client.get_parameter(
            Name=parameter_name,
            WithDecryption=with_decryption,
        )

        return response["Parameter"]["Value"]

    except (BotoCoreError, ClientError) as exc:
        raise RuntimeError(
            f"Unable to retrieve parameter: {parameter_name}"
        ) from exc
