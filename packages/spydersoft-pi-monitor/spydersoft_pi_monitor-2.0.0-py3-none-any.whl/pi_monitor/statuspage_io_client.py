import json
from types import SimpleNamespace
from typing import Dict, List
import logging
import requests

logger = logging.getLogger(__name__)


class StatusPageClient:
    """StatusPageClient Class

    The StatusPageClient class provides methods for interacting with the
    [Statuspage.io's APIs](https://developer.statuspage.io/)

    Attributes:
        component_status_list: A list of valid component status codes for StatusPage.io
        incident_status_list: A list of valid incident status codes for live incidents
                                in StatusPage.io
        scheduled_incident_status_list: A list of valid incident status codes for
                                        scheduledStatusPage.io
    """

    AUTH_HEADER = "Authorization"
    STATUS_PAGE_BASE_URL = "https://api.statuspage.io/v1/pages"
    CLIENT_ERROR_MESSAGE = "Request failed exception:"

    component_status_list: List[str] = [
        "operational",
        "under_maintenance",
        "degraded_performance",
        "partial_outage",
        "major_outage",
    ]
    incident_status_list: List[str] = [
        "investigating",
        "identified",
        "monitoring",
        "resolved",
    ]
    scheduled_incident_status_list: List[str] = [
        "scheduled",
        "in_progress",
        "verifying",
        "complete",
    ]

    def __init__(self, api_key: str, page_id: str):
        self.api_key = api_key
        self.page_id = page_id

    def _get_headers(self) -> Dict[str, str]:
        """Retrieve headers for all requests

        This function adds the necessary `Authorization` and `Content-Type` headers
        for the API to operate using JSON.

        Returns:
            A Dictionary that represents the headers for request to Statuspage.io

        """
        return {
            f"{self.AUTH_HEADER}": f"OAuth {self.api_key}",
            "Content-Type": "application/json",
        }

    def get_component(self, component_id: str) -> object:
        """Retrieve Component Information

        Retrieve the current component information using the provided component_id.

        Args:
            component_id: The id of the component to retrieve.

        Returns:
            A SimpleNamespace object created from the JSON return.  Object
                representation can be found in the
                [docs](https://developer.statuspage.io/#operation/getPagesPageIdComponentsComponentId).

        """
        component_url = (
            f"{self.STATUS_PAGE_BASE_URL}/{self.page_id}/components/{component_id}"
        )
        logger.debug("Retrieving component from StatusPage: %s", component_url)
        try:
            component = requests.get(component_url, headers=self._get_headers())
            logger.debug("Component Response: %s", component.text)

            if component.status_code == 404:
                logger.warning("Component %s not found", component_id)

            return component.json(object_hook=lambda d: SimpleNamespace(**d))
        except Exception as e:
            self._handle_exception(e)

    def update_component(self, component_id: str, payload: object) -> object:
        """Update Component Information

        Update the given component using the provided payload as the object body.  The
        payload object will be processed using `json.dumps()`.

        Args:
            component_id: The id of the component to update.
            payload: An object representing the JSON payload.  Valid object
                representation can be found in the
                [docs](https://developer.statuspage.io/#operation/putPagesPageIdComponentsComponentId).

        Returns:
            A SimpleNamespace object created from the JSON return.  Object
                representation can be found in the
                [docs](https://developer.statuspage.io/#operation/putPagesPageIdComponentsComponentId).

        """
        component_url = (
            f"{self.STATUS_PAGE_BASE_URL}/{self.page_id}/components/{component_id}"
        )
        logger.debug("Updating component %s: %s", component_id, payload)
        try:
            r = requests.put(
                component_url, headers=self._get_headers(), data=json.dumps(payload)
            )
            return r.json(object_hook=lambda d: SimpleNamespace(**d))
        except Exception as e:
            self._handle_exception(e)

    def get_unresolved_incidents(self) -> object:
        """Retrieve Unresolved Incidents

        Retrieve all the current unresolved incidents.

        Returns:
            A SimpleNamespace object created from the JSON return.  Object
                representation can be found in the
                [docs](https://developer.statuspage.io/#operation/getPagesPageIdIncidentsUnresolved).

        """
        logger.info("Retrieving unresolved incidents")
        unresolved_incidents_url = (
            f"{self.STATUS_PAGE_BASE_URL}/{self.page_id}/incidents/unresolved"
        )
        try:
            unresolved_incidents_response = requests.get(
                unresolved_incidents_url, headers=self._get_headers()
            )
            result = unresolved_incidents_response.json(
                object_hook=lambda d: SimpleNamespace(**d)
            )
            return result
        except Exception as e:
            self._handle_exception(e)

    def create_incident(self, payload: object) -> object:
        """Create Incident

        Create a new incident using the provided payload as the object body.  The
        payload object will be processed using `json.dumps()`.

        Args:
            payload: An object representing the JSON payload.  Valid object
                representation can be found in the
                [docs](https://developer.statuspage.io/#operation/postPagesPageIdIncidents).

        Returns:
            A SimpleNamespace object created from the JSON return.  Object
                representation can be found in the
                [docs](https://developer.statuspage.io/#operation/postPagesPageIdIncidents).

        """
        incident_url = f"{self.STATUS_PAGE_BASE_URL}/{self.page_id}/incidents"
        logger.info("Creating incident: %s", incident_url)
        try:
            r = requests.post(
                incident_url, headers=self._get_headers(), data=json.dumps(payload)
            )
            result_object = r.json(object_hook=lambda d: SimpleNamespace(**d))
            logger.debug("Create Incident Response: %s", result_object)
            return result_object
        except Exception as e:
            self._handle_exception(e)

    def update_incident(self, incident_id: str, payload: object) -> object:
        """Update Incident Information

        Update the given incident using the provided payload as the object body.  The
        payload object will be processed using `json.dumps()`.

        Args:
            incident_id: The id of the incident to update.
            payload: An object representing the JSON payload.  Valid object
                representation can be found in the
                [docs](https://developer.statuspage.io/#operation/patchPagesPageIdIncidentsIncidentId).

        Returns:
            A SimpleNamespace object created from the JSON return.  Object
                representation can be found in the
                [docs](https://developer.statuspage.io/#operation/patchPagesPageIdIncidentsIncidentId).

        """
        incident_url = (
            f"{self.STATUS_PAGE_BASE_URL}/{self.page_id}/incidents/{incident_id}"
        )
        logger.info("Updating incident %s: %s", incident_url, incident_id)
        try:
            r = requests.patch(
                incident_url, headers=self._get_headers(), data=json.dumps(payload)
            )
            result_object = r.json(object_hook=lambda d: SimpleNamespace(**d))
            logger.debug("Update Incident Response: %s", result_object)
            return result_object
        except Exception as e:
            self._handle_exception(e)

    def _handle_exception(self, e: Exception):
        logger.error("%s %s", self.CLIENT_ERROR_MESSAGE, e)
