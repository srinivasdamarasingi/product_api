from datetime import timedelta

import os

from dotenv import load_dotenv

SECRET_KEY = "@858BHYU12@#"

ALGORITHM = "HS256"

ACCESS_TOKEN_EXPIRE_MINUTES = 30

load_dotenv()

class Settings:
    SMTP_HOST = os.getenv("SMTP_HOST")
    SMTP_PORT = int(os.getenv("SMTP_PORT", 587))

    SMTP_USERNAME = os.getenv("SMTP_USERNAME")
    SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")

    MAIL_FROM = os.getenv("MAIL_FROM")
    MAIL_FROM_NAME = os.getenv("MAIL_FROM_NAME")

    S3_BUCKET_NAME = os.getenv("S3_BUCKET_NAME")
    AWS_REGION = os.getenv("AWS_REGION", "us-east-1")


settings = Settings()
