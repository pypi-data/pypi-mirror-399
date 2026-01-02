import logging
from .statuspage_io_client import StatusPageClient
from .configuration import StatusPageSettings
from .enums import OpLevel

logger = logging.getLogger(__name__)


class Incident:
    """Incident Class

    This class represents the details about a Statuspage.io incident

    Attributes:
        name: The incident name.
        description: The incident description.

    """

    name: str = "Incident Name"
    description: str = "Incident Description"


class IncidentResult:
    """IncidentResult Class

    This class represents information about incidents created or resolved as part of
    a status change

    Attributes:
        incident_created: True if an incident was created, false otherwise.
        incident_resolved: True if an incident was created, false otherwise.

    """

    incident_created: bool = False
    incident_resolved: bool = False
    incident: Incident

    def __init__(self):
        self.incident_created = False
        self.incident_resolved = False
        self.incident = Incident()


class StatusResult:
    """StatusResult Class

    This class represents information about actions taken during a check and update.

    Attributes:
        status_changed: True if the status has changed from the previous check,
                        false otherwise.
        incident_result: An instance of
                        [IncidentResult][pi_monitor.statuspage_io.IncidentResult].

    """

    status_changed: bool = False
    incident_result: IncidentResult = IncidentResult()

    def __init__(self):
        self.incident_result = IncidentResult()


class StatusPageOperator:
    """StatusResult Class

    This class represents information about actions taken during a check and update.

    Attributes:
        config: An instance of [StatusPageSettings][pi_monitor.StatusPageSettings]
                which contains settings for Statuspage.io communication
        client: An instance of
                [StatusPageClient][pi_monitor.statuspage_io_client.StatusPageClient],
                built from the configuration values provided.

    """

    config: StatusPageSettings = StatusPageSettings()
    client: StatusPageClient

    def __init__(self, status_page_config: StatusPageSettings):
        """Constructor

        Initialize the instance using the provided
        [StatusPageSettings][pi_monitor.StatusPageSettings].

        """
        if status_page_config is None:
            raise ValueError("No configuration provided")

        self.config = status_page_config
        self.client = StatusPageClient(self.config.api_key, self.config.page_id)

    def is_configured(self) -> bool:
        """Validate configuration data

        Returns:
            True if the operator has a valid configuration, False otherwise.
        """
        return self.config.api_key != ""

    def update_component_status(
        self, component_id: str, op_level: OpLevel, incident_details: Incident = {}
    ) -> StatusResult:
        """Update Component Status

        Using the provided OpLevel, determine the component's statuspage.io status.

        If the incoming `op_level` is [Operational][pi_monitor.enums.OpLevel] and the
        statuspage.io status is not, the component's status will be changed to
        `operational`, and any open incidents for that component will be resolved.

        If the incoming `op_level` is any other value and the statuspage.io status is
        operational, the component's status will be changed to `major_outage` and an
        incident will be created using the provided `incident_details`


        Args:
            component_id: The component ID to check
            op_level: The current OpLevel for the provided component
            incident_details: An instance of
                              [Incident][pi_monitor.statuspage_io.Incident]
                              which has the details of the incident to be created,
                                if necessary.

        Returns:
            An instance of [StatusResult][pi_monitor.statuspage_io.StatusResult]
        """

        if op_level == OpLevel.Operational:
            component_status = "operational"
        else:
            component_status = "major_outage"

        result = StatusResult()
        component = self.client.get_component(component_id)
        if component is None:
            logger.warning("Failed to retrieve component %s", component_id)
            return result

        if (
            component.status != component_status
            and component.status != "under_maintenance"
        ):
            result.status_changed = True
            logger.info(
                "Changing status from %s to %s", component.status, component_status
            )
            self._update_component_status(component_id, component_status)
            result.incident_result = self._process_incident_on_status_change(
                component_id, component_status, incident_details
            )

        return result

    def _update_component_status(self, component_id, new_component_status):
        logger.debug(
            "Setting component status to %s: %s", new_component_status, component_id
        )
        payload = {"component": {"status": new_component_status}}
        component = self.client.update_component(component_id, payload)
        if component is None:
            logger.warning("Failed to update component %s", component_id)

    def _filter_set(self, incidents, component_id):
        def iterator_func(incident):
            for comp in incident.components:
                if comp.id == component_id:
                    return True
            return False

        return filter(iterator_func, incidents)

    def _get_associated_incident(self, component_id):
        result = self.client.get_unresolved_incidents()
        if result is None:
            return []
        return list(self._filter_set(result, component_id))

    def _process_incident_on_status_change(
        self, component_id: str, new_component_status: str, incident_details: Incident
    ) -> IncidentResult:
        """Create or Close incidents based on the incoming component status

        For now, if it's operational, close open incidents, and if it's not operational
        , create a new ticket if one isn't already open for this component.
        Future state will involve more detail around outage and maintenance
        """
        incident_result = IncidentResult()
        incident_result.incident = incident_details

        associated_incidents = self._get_associated_incident(component_id)
        asscociated_incident_count = len(associated_incidents)
        logger.info(
            "Associated Incidents for %s: %d", component_id, asscociated_incident_count
        )

        if new_component_status == "operational" and asscociated_incident_count > 0:
            for incident in associated_incidents:
                self._close_incident(incident.id)
                incident_result.incident_resolved = True

        elif new_component_status == "major_outage" and asscociated_incident_count == 0:
            self._create_incident(component_id, new_component_status, incident_details)
            incident_result.incident_created = True

        return incident_result

    def _close_incident(self, incident_id):
        logger.info("Closing incident %s", incident_id)
        payload = {"incident": {"status": "resolved"}}
        self.client.update_incident(incident_id, payload)

    def _create_incident(
        self, component_id, new_component_status: str, incident_details: Incident
    ):
        logger.info(
            "Creating incident: Component %s - New Component Status %s",
            component_id,
            new_component_status,
        )
        payload = {
            "incident": {
                "name": incident_details.name,
                "status": "investigating",
                "body": incident_details.description,
                "component_ids": [component_id],
                "components": {component_id: new_component_status},
            }
        }
        self.client.create_incident(payload)
