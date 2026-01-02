import json
import allure
from funfedi_connect.types import Attachments


def attach(attachment: Attachments, data: dict):
    allure.attach(
        json.dumps(data, indent=2),
        name=str(attachment),
        attachment_type="application/json",
        extension="json",
    )
