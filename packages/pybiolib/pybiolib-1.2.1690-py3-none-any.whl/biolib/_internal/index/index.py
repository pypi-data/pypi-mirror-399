from typing import Any, Dict

from biolib._index.types import IndexInfo
from biolib.api import client as api_client
from biolib.biolib_api_client.biolib_app_api import _get_app_uri_from_str


def get_index_from_uri(uri: str) -> IndexInfo:
    normalized_uri = _get_app_uri_from_str(uri)
    app_response: Dict[str, Any] = api_client.get(path='/app/', params={'uri': normalized_uri}).json()
    resource_uri = app_response['app_version']['app_uri']
    if app_response['app']['type'] != 'index':
        raise Exception(f'Resource "{resource_uri}" is not an Index')
    return IndexInfo(
        resource_uri=app_response['app_version']['app_uri'],
        resource_uuid=app_response['app']['public_id'],
        group_uuid=app_response['app']['group_uuid'],
    )
