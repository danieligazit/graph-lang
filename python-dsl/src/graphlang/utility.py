from typing import Tuple

import shortuuid


def unique_name():
    return f'u{shortuuid.uuid()[:12]}'


def collection_and_key_to_id(collection: str, key: str) -> str:
    return f'{collection}/{key}'


def id_to_collection_and_key(id_: str) -> Tuple[str, str]:
    parts = id_.split('/')
    return parts[0], parts[1]


def id_to_key(id_: str) -> str:
    return id_to_collection_and_key(id_)[1]
