import os
import yaml
import logging.config
import logging
import logging.handlers
import coloredlogs
import argparse
from .enums import OpLevel
from .healthchecks import HealthCheckExecutor, HttpGetResult
from .configuration import (
    read_configuration,
    MonitorSettings,
    NotificationSettings,
    StatusPageSettings,
    HealthCheckSettings,
    StatusPageComponentSettings,
)
from .notifications import Notifier
from .statuspage_io import StatusPageOperator, Incident, StatusResult, IncidentResult
from .statuspage_io_client import StatusPageClient
from concurrent.futures import ThreadPoolExecutor


def get_parser():
    PARSER = argparse.ArgumentParser()
    PARSER.add_argument(
        "-c", "--configfile", help="Configuration File", default="monitor.config.json"
    )

    return PARSER


def setup_logging(
    default_path="logging.yaml", default_level=logging.INFO, env_key="LOG_CFG"
):
    """
    | **@author:** Prathyush SP
    | https://gist.github.com/kingspp/9451566a5555fb022215ca2b7b802f19
    | Logging Setup
    """
    path = default_path
    value = os.getenv(env_key, None)
    if value:
        path = value
    if os.path.exists(path):
        with open(path, "rt") as f:
            try:
                config = yaml.safe_load(f.read())
                logging.config.dictConfig(config)
                coloredlogs.install()
            except Exception as e:
                print(e)
                print("Error in Logging Configuration. Using default configuration.")
                logging.basicConfig(level=default_level)
                coloredlogs.install(level=default_level)
    else:
        logging.basicConfig(level=default_level)
        coloredlogs.install(level=default_level)
        print(f"File {default_path} not found. Using default logging configuration.")


def main():
    setup_logging()
    logger = logging.getLogger(__name__)

    parser = get_parser()
    args = parser.parse_args()

    logger.info("Reading Configuration File")
    config_data = read_configuration(args.configfile, MonitorSettings())

    notifier = Notifier(config_data.notification)
    status_page_operator = StatusPageOperator(config_data.status_page)
    healtch_check_executor = HealthCheckExecutor(status_page_operator, notifier)

    with ThreadPoolExecutor(max_workers=4) as executor:
        {
            executor.submit(
                healtch_check_executor.execute_health_check, statusCheck
            ): statusCheck
            for statusCheck in config_data.status_checks
        }
