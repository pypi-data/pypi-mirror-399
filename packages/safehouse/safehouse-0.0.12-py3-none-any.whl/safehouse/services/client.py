import json
import logging
import requests
from typing import List, Optional

import safehouse


logger = logging.Logger(__name__)


class ClientError(Exception):
    def __init__(self, detail):
        super().__init__(detail)


def get(
        *,
        acceptable_status_codes: Optional[List[int]] = [200],
        endpoint: str,
        headers: dict[str,str] | None=None,
) -> requests.Response:
        if headers is None:
            headers = _headers()
        response = requests.get(
            url=services_url() + endpoint,
            headers=headers,
        )
        validate_response(response, acceptable_status_codes=acceptable_status_codes)
        return response


def post(
        *,
        acceptable_status_codes: Optional[List[int]] = [200],
        data: Optional[str]='',
        endpoint: str,
        headers: dict[str,str] | None=None,
) -> requests.Response:
        if headers is None:
            headers = _headers()
        response = requests.post(
            url=services_url() + endpoint,
            headers=headers,
            data=data,
        )
        validate_response(response, acceptable_status_codes=acceptable_status_codes)
        return response


def services_url():
    if safehouse.active_project:
        return safehouse.active_project.services_url
    return safehouse.mode.services_url()


def validate_response(
        response: requests.Response,
        acceptable_status_codes: Optional[List[int]] = [200],
):
    if acceptable_status_codes and response.status_code not in acceptable_status_codes:
        error_string = str(response)
        error_detail = error_string
        try:
            error_string = response.json()
            if type(error_string) is list:
                error_detail = ', '.join(error_string)
            else:
                error_detail = error_string['detail']
        except json.JSONDecodeError:
            pass
        raise ClientError(error_detail)


def _headers():
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
    }
    if safehouse.active_project:
        if safehouse.user:
            headers['X-USER-ID'] = str(safehouse.user.id_for(safehouse.active_project.mode))
        headers['X-ORGANIZATION'] = safehouse.active_project.organization_name
        headers['X-PROJECT'] = safehouse.active_project.name
    return headers
