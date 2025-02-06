import os
import sys

import requests
from dotenv import load_dotenv
from loguru import logger

load_dotenv()
logger.remove()
logger.add(sys.stdout, level=os.environ['LOGLEVEL'].upper())


class AlarmHandler:

    def __init__(self, token: str) -> None:
        self.headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
        self.url = "https://house-alarm.memomate.me/app/v1/"

    def send_alarm_state(self, data: dict) -> None:
        """
        Send the current alarm state to the alarm API.

        Args:
            data: Dictionary holding the create_alarm_state (see docs)
        """
        try:
            response = requests.post(self.url + "create_alarm_state", json=data, headers=self.headers, timeout=10)
            response.raise_for_status()
            logger.debug("Response Status Code:", response.status_code)

            try:
                response_json = response.json()  # Try parsing JSON response
                logger.error("Response JSON:", response_json)
            except ValueError:
                logger.error("Response is not in JSON format:", response.text)

        except requests.exceptions.Timeout:
            logger.error("Request timed out. The server may be unreachable.")
        except requests.exceptions.ConnectionError:
            logger.error("Failed to connect to the server. Check if the server is running.")
        except requests.exceptions.HTTPError as err:
            logger.error(f"HTTP error occurred: {err}")
        except requests.exceptions.RequestException as err:
            logger.error(f"An error occurred: {err}")
