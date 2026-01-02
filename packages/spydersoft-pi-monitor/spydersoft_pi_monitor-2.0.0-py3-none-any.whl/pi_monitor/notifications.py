from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
import logging
from .configuration import NotificationSettings

logger = logging.getLogger(__name__)


class Notifier:
    """Notifier Class

    The Notifier class encapsulates the functionality to send email notifications.

    Attributes:
        config: An instance of [NotificationSettings][pi_monitor.NotificationSettings]
    """

    config: NotificationSettings

    def __init__(self, notify_config: NotificationSettings) -> None:
        """Constructor

        Initialize the instance using the provided
        [NotificationSettings][pi_monitor.NotificationSettings].

        """
        self.config = notify_config

    def notify(self, subject: str, content: str) -> bool:
        """Send notification

        Build and send an email notificaiton using the provided parameters.

        Args:
            subject: The email subject.
            content: the email content.

        """

        if self.config is None:
            logger.info("No configuration provided.  Skipping...")
            return True

        if self.config.sms_email is not None and self.config.sms_email != "":
            logger.info("Sending Notification to %s", self.config.sms_email)

            message = Mail(
                from_email=self.config.smtp_sender_id,
                to_emails=self.config.sms_email,
                subject=subject,
                plain_text_content=content,
                html_content=content,
            )
            try:
                sg = SendGridAPIClient(self.config.smtp_sender_apikey)
                response = sg.send(message)
                return response.status_code == 202
            except Exception as e:
                logger.error("Error sending mail: %s", e)
                return False
        else:
            logger.info("No email address provided for notification.  Skipping...")
            return True
