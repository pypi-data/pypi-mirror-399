# -*- coding: utf-8 -*-
"""

Module for reading configuration.

This module provides a function for reading a JSON file into
 the provided Settings objects.

"""

import json
from typing import List
import logging
from pathlib import Path

logger = logging.getLogger(__name__)


class StatusPageComponentSettings:
    """Settings for StatusPage.io components.

    Attributes:
        component_id (str): The ID of the component in your statuspage.io page
    """

    component_id: str


class Generic:
    """Generic method for reading dictionary values."""

    @classmethod
    def from_dict(cls, dict):
        obj = cls()
        obj.__dict__.update(dict)
        return obj


class HealthCheckSettings:
    """Settings for a HealthCheck.

    A Healthcheck represents a simple request to the defined `url`.
     If a non-200 the request generates an exception or a non-200
     response, the site is determined to be down.

    If `status_page` is defined, statuspage.io will be updated
     according to the following rules.

    - If the site returns a 2xx response and statuspage.io lists
     the component as non-operational:
        - The component's status will be set to operational
        - Any open incidents associated with this component will
         be marked as resolved
    - If the site returns a non-2xx response or an exception and
     statuspage.io lists the component as operational:
        - The component's status will be set to operational
        - An incident will be opened using the `name` and
         associated with this component.


    Attributes:
        name (str): The name of the site being checked
        url (str): The url to be fetched as part of the check
        status_page (StatusPageComponentSettings): Any StatusPage-related
            component settings
    """

    name: str
    url: str
    status_page: StatusPageComponentSettings


class StatusPageSettings:
    """Settings for StatusPage.io.

    Attributes:
        api_key (str): The API Key to access statuspage.io
        page_id (str): Your PageId for statuspage.io
    """

    api_key: str
    page_id: str


class NotificationSettings:
    """Notification Settings

    This class represents settings for notifications.  If you are using Gmail to send,
    you need to set your account's `Allow Less Secure Apps` setting to `true`

    Attributes:
        smtp_url (str): The URL of the SMTP host
        smtp_port (int): The SMTP Port to use
        smtp_sender_id (str): The SMTP user
        smtp_sender_apikey (str): The SMTP user's password
        sms_email: The email to receive notifications

    """

    smtp_url: str
    smtp_port: int
    smtp_sender_id: str
    smtp_sender_apikey: str
    sms_email: str


class MonitorSettings:
    """MonitorSettings

    This class represents the entire structure of the configuration
    file (`monitor.config.json` by default).

    Attributes:
        status_checks: The collection of statusCheck settings
        notification: The settings object for notifications
        status_page: The settings object for StatusPage.io
    """

    status_checks: List[HealthCheckSettings]
    notification: NotificationSettings
    status_page: StatusPageSettings


def read_configuration(
    file: str, default_settings: MonitorSettings = {}
) -> MonitorSettings:
    """Read Configuration file and return settings

    Args:
        file: The file name to use for configuration.
                The default value is `monitor.config.json`
        default_settings: A default instance of the settings to use if the file
                            cannot be found.

    Returns:
        MonitorSettings: A MonitorSettings object populated from the given file,
                        or an empty Settings object.
    """
    config_path = Path(file)

    if not config_path.exists():
        logger.error("Configuration file not found: %s.  Using default", file)
        return default_settings

    config_data = config_path.read_text()
    return json.loads(config_data, object_hook=Generic.from_dict)
