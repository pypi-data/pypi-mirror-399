import requests
import logging
from .configuration import HealthCheckSettings
from .enums import OpLevel
from .statuspage_io import StatusPageOperator, StatusResult, Incident
from .notifications import Notifier

logger = logging.getLogger(__name__)


class HttpGetResult:
    """HttpGetResult

    Attributes:
        success: Whether or not the request was successful
        message: The error message from an unsuccessful request
        raw_response: The string value of the response body
        response: An object representing the response body converted as JSON

    """

    success: bool = True
    message: str = ""
    raw_response: str
    response: any = {}

    def __init__(self, success: bool, msg: str = ""):
        self.success = success
        self.message = msg


class HealthCheckExecutor:
    """HealthCheckExecutor

    The HealthCheckExecutor encapsulates the functionality to perform a health check on
    a site and properly notify users or update statuspage.io accordingly.

    A Healthcheck represents a simple request to the defined `url`. If a non-200 the
    request generates an exception or a non-200 response, the site is determined to
    be down.

    If `statuspage_operator` is present and the HealthCheckSettings have a component_id
    set, statuspage.io will be updated according to the following rules.

    - If the site returns a 2xx response and statuspage.io lists the component as
        non-operational:
        - The component's status will be set to operational
        - Any open incidents associated with this component will be marked as resolved
    - If the site returns a non-2xx response or an exception and statuspage.io lists
        the component as operational:
        - The component's status will be set to operational
        - An incident will be opened using the `name` and associated with
          this component.


    Attributes:
        statuspage_operator: The name of the site being checked
        notifier: The url to be fetched as part of the check
    """

    statuspage_operator: StatusPageOperator
    notifier: Notifier

    def __init__(
        self,
        status_operator: StatusPageOperator,
        notifier: Notifier,
    ):
        """Constructor

        Constructs an instance of the HealthCheckExecutor with the given
        [StatusPageOperator][pi_monitor.StatusPageOperator] and
        [Notifier][pi_monitor.Notifier].

        Attributes:
            statuspage_operator: The name of the site being checked
            notifier: The url to be fetched as part of the check
        """
        self.statuspage_operator = status_operator
        self.notifier = notifier

    def execute_health_check(self, check_settings: HealthCheckSettings):
        """Execute a health check

        Executes a health check using the provided HealthCheckSettings.

        Args:
            check_settings: An instance of
                [HealthCheckSettings][pi_monitor.HealthCheckSettings]
        """
        logger.info("Checking %s...", check_settings.name)

        send_notification = False

        http_result = self._get_http(check_settings.url)

        if http_result.success:
            # Good Check
            logger.info("Status OK")
            op_level = OpLevel.Operational
        else:
            # Bad check
            op_level = OpLevel.Full_Outage
            logger.warning(http_result.message)
            send_notification = True

        notification_text = http_result.message
        if check_settings.status_page and check_settings.status_page.component_id != "":
            status_result = self._update_status_page(check_settings, op_level)
            send_notification = (
                status_result.incident_result.incident_created
                or status_result.incident_result.incident_resolved
            )
            notification_text = status_result.incident_result.incident.description

        if (
            send_notification
            and notification_text is not None
            and notification_text != ""
        ):
            logger.info("Sending notification: %s", notification_text)
            self.notifier.notify(check_settings.name, notification_text)

    def _get_http(self, url: str) -> HttpGetResult:
        """Retrieve data from the URL

        Attempt to get data from the provided URL

        Args:
            url: The url to be retrieved

        Returns:
            An [HttpGetResult][pi_monitor.HttpGetResult]
        """
        if not url or url == "":
            result = HttpGetResult(False, "no url defined")
            return result

        try:
            logger.debug("Requesting %s", url)
            r = requests.get(url)
            result = self._process_response(r)
        except Exception as e:
            logger.error("Request failed exception %s", e)
            result = HttpGetResult(False, "Unknown status failure")

        return result

    def _process_response(self, response: requests.Response) -> HttpGetResult:
        """Process the HTTP Requests response

        Convert the provided Response object from the requests module into an
        [HttpGetResult][healthchecks.HttpGetResult].

        Args:
            response: The [requests.Response] object from the HTTP operation

        Returns:
            An [HttpGetResult][healthchecks.HttpGetResult]
        """
        result = HttpGetResult(response.status_code == 200)
        if not result.success:
            logger.info(
                "Request failed with Response Code %d: %s",
                response.status_code,
                response.text,
            )
            result.message = f"{response.status_code} {response.text}"
            return result

        result.raw_response = response.text
        return result

    def _update_status_page(
        self, check_settings: HealthCheckSettings, op_level: OpLevel
    ) -> StatusResult:
        incident = Incident()
        incident.name = check_settings.name

        description_dict = {
            OpLevel.Operational: "Operating Normally",
            OpLevel.Degraded: "Service Degraded",
            OpLevel.Partial_Outage: "Partial Service Outage",
            OpLevel.Full_Outage: "Major Service Outage",
        }
        incident.description = description_dict[op_level]
        return self.statuspage_operator.update_component_status(
            check_settings.status_page.component_id, op_level, incident
        )
