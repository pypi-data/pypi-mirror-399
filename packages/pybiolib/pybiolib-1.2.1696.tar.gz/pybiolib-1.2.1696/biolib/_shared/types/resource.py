from .typing import Optional, TypedDict


class SemanticVersionDict(TypedDict):
    major: int
    minor: int
    patch: int


class ResourceUriDict(TypedDict):
    account_handle_normalized: str
    account_handle: str
    resource_name_normalized: Optional[str]
    resource_name: Optional[str]
    resource_prefix: Optional[str]
    version: Optional[SemanticVersionDict]
    tag: Optional[str]
