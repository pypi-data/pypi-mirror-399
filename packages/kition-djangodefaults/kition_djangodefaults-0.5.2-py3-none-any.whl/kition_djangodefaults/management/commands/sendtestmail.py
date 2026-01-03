import logging
from importlib.util import find_spec
from typing import Type

from django.conf import settings
from django.core.mail import send_mail
from django.core.management import BaseCommand

logger = logging.getLogger(__name__)


def _send_mail(recipient) -> bool | Exception:
    try:
        send_mail(
            recipient_list=[recipient],
            from_email=settings.DEFAULT_FROM_EMAIL,
            subject="Email Delivery works 🎉",
            message="This is a test email sent to verify the SMTP configuration.",
        )
        logger.info(f"Email sent to {recipient}")
        return True
    except Exception as err:
        logger.exception(f"Failed to send email to {recipient}")
        return err


class SendTestMailCommand(BaseCommand):
    email_recipient_arg_name = "recipient"
    help = "Sends a test email to verify the email configuration"

    def add_arguments(self, parser):
        parser.add_argument(
            self.email_recipient_arg_name,
            type=str,
            help="Recipient address of the test email.",
        )

    def handle(self, *args, **options):
        recipient = options[self.email_recipient_arg_name]
        _send_mail(recipient)


class BackgroundSendTestMailCommand(SendTestMailCommand):
    completion_wait_duration_seconds = 15

    def add_arguments(self, parser):
        super().add_arguments(parser)
        parser.add_argument(
            "--background",
            default=False,
            action="store_true",
            help="Send the test email via the background worker instead of sending it through this process.",
        )

    def handle(self, *args, **options):
        recipient = options[self.email_recipient_arg_name]
        is_background_send = options["background"]

        if is_background_send:
            self._send_background(recipient)
        else:
            _send_mail(recipient)

    def _send_background(self, recipient):
        from django_q.tasks import async_task, result

        logger.info("Adding email delivery task to background worker queue...")
        task_id = async_task(_send_mail, recipient)
        logger.info(
            f"Waiting up to {self.completion_wait_duration_seconds} seconds for background task completion..."
        )

        task_result = result(task_id, wait=self.completion_wait_duration_seconds * 1000)

        if type(task_result) is bool:
            print(
                "Background task successfully executed. Check the worker log for additional information."
            )
        else:
            print(
                f"Background task failed. Check the worker log for additional information. Error: {task_result}"
            )


Command: Type[SendTestMailCommand]
if find_spec("django_q") is None:
    Command = SendTestMailCommand
else:
    Command = BackgroundSendTestMailCommand
