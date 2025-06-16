# Copyright (C) - 2025 - Cosmo Tech
# This document and all information contained herein is the exclusive property -
# including all intellectual property rights pertaining thereto - of Cosmo Tech.
# Any use, reproduction, translation, broadcasting, transmission, distribution,
# etc., to any person is prohibited unless it has been previously and
# specifically authorized by written means by Cosmo Tech.

import redis
import json
from pathlib import Path
from typing import Optional

from cosmotech.orchestrator.utils.translate import T

from cosmotech.data_update_quest_cli.utils.logger import LOGGER


def get_redis_client(host, port, password):
    LOGGER.info(T("data_update_quest.core.redis_dump.redis_connection"))
    return redis.Redis(host=host, port=port, password=password, decode_responses=True)


def get_redis_indexes(r, index_list: Optional[list[str]]):
    if not index_list:
        index_list = r.execute_command("FT._LIST")

    LOGGER.info(T("data_update_quest.core.redis_dump.redis_index"))
    indexes = {}

    for index in index_list:
        index_name = index.split(".")[2]
        indexes.setdefault(index_name, index)
        LOGGER.info(f"  -   {index}")

    return indexes


def redis_dump(file_path, host, port, password, index_list):
    r = get_redis_client(host=host, port=port, password=password)
    indexes = get_redis_indexes(r, index_list)

    for index in indexes:
        result = r.ft(indexes[index]).search("*")
        path = Path(file_path) / index
        path.mkdir(parents=True, exist_ok=True)

        for doc in result.docs:
            json_id = json.loads(doc.json)["id"]

            with open(file=path / json_id, mode="w") as f:
                f.write(doc.json)
                LOGGER.info(f'{T("data_update_quest.core.redis_dump.dump").format(index=index):<20} :    {json_id}')


def file_upload(file_path, host, port, password):
    r = get_redis_client(host=host, port=port, password=password)

    p = Path(file_path)
    if not p.is_dir():
        raise Exception()

    indexes = {}
    for x in p.iterdir():
        indexes.setdefault(x, f"com.cosmotech.{x.name}.domain.{x.name.capitalize()}Idx")

    for index in indexes:
        p = Path(index)
        for file in p.iterdir():
            with open(file=Path(file), mode=r) as f:
                r.json().set(f"{indexes[index]}:", Path(file), file)
