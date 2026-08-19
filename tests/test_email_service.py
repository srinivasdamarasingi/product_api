from app.services.email_service import render_template
import pytest
from unittest.mock import AsyncMock, patch

from app.services.email_service import send_email


def test_render_email_template():

    html = render_template(
        "welcome_email.html",
        username="Test User",
        email="test@example.com"
    )

    assert isinstance(html, str)
    assert len(html) > 0


@pytest.mark.anyio
async def test_send_email_success():

    with patch(
        "app.services.email_service.FastMail"
    ) as mock_fastmail:

        mock_instance = mock_fastmail.return_value

        mock_instance.send_message = AsyncMock()

        await send_email(
            to_email="test@example.com",
            subject="Test Email",
            template_name="welcome_email.html",
            username="Test User",
            email="test@example.com"
        )

        mock_instance.send_message.assert_awaited_once()

        sent_message = (
            mock_instance.send_message
            .await_args.args[0]
        )

        assert sent_message.subject == "Test Email"

        assert len(
            sent_message.recipients
        ) == 1

        assert str(
            sent_message.recipients[0].email
        ) == "test@example.com"

@pytest.mark.anyio
async def test_send_email_failure():

    with patch(
        "app.services.email_service.FastMail"
    ) as mock_fastmail:

        mock_instance = mock_fastmail.return_value

        mock_instance.send_message = AsyncMock(
            side_effect=Exception(
                "SMTP unavailable"
            )
        )

        with pytest.raises(
            Exception,
            match="SMTP unavailable"
        ):

            await send_email(
                to_email="test@example.com",
                subject="Test Email",
                template_name="welcome_email.html",
                username="Test User",
                email="test@example.com"
            )