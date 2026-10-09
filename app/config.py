import os

from app.services.parameter_store_service import get_parameter


ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


class Settings:
    def __init__(self):
        self.CONFIG_SOURCE = os.getenv(
            "CONFIG_SOURCE",
            "environment",
        )

        if self.CONFIG_SOURCE == "ssm":

            self.DATABASE_URL = get_parameter(
                "/product-api/prod/database-url",
               with_decryption=True,
        )

            self.S3_BUCKET_NAME = get_parameter(
                "/product-api/prod/s3-bucket"
            )

            self.AWS_REGION = get_parameter(
                "/product-api/prod/aws-region"
            )

            self.SECRET_KEY = get_parameter(
                "/product-api/prod/jwt-secret-key",
                with_decryption=True,
            )

            self.SMTP_HOST = get_parameter(
                "/product-api/prod/smtp-host"
            )

            self.SMTP_PORT = int(
                get_parameter(
                    "/product-api/prod/smtp-port"
                )
            )

            self.SMTP_USERNAME = get_parameter(
                "/product-api/prod/smtp-username",
                with_decryption=True,
            )

            self.SMTP_PASSWORD = get_parameter(
                "/product-api/prod/smtp-password",
                with_decryption=True,
            )

            self.MAIL_FROM = get_parameter(
                "/product-api/prod/mail-from"
            )

            self.MAIL_FROM_NAME = get_parameter(
                "/product-api/prod/mail-from-name"
            )
        else:

            self.DATABASE_URL = os.getenv("DATABASE_URL")

            self.S3_BUCKET_NAME = os.getenv(
                "S3_BUCKET_NAME"
            )

            self.AWS_REGION = os.getenv(
                "AWS_REGION",
                "us-east-1",
            )

            self.SECRET_KEY = os.getenv(
                "SECRET_KEY",
                "",
            )

            self.SMTP_HOST = os.getenv("SMTP_HOST")
            self.SMTP_PORT = int(os.getenv("SMTP_PORT", 587))
            self.SMTP_USERNAME = os.getenv("SMTP_USERNAME")
            self.SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")
            self.MAIL_FROM = os.getenv("MAIL_FROM")
            self.MAIL_FROM_NAME = os.getenv("MAIL_FROM_NAME")


settings = Settings()

SECRET_KEY = settings.SECRET_KEY
