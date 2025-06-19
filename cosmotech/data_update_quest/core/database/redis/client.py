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

    LOGGER.info(T("data_update_quest.core.redis_dump.redis_index"))

    indexes = {}
    if index_list:
        full_index_list = list(
            f"com.cosmotech.{index_name.lower()}.domain.{index_name.capitalize()}Idx" for index_name in index_list)
    else:
        full_index_list = r.execute_command("FT._LIST")

    for index in full_index_list:
        index_name = index.split(".")[2]
        indexes[index_name] = index
        LOGGER.info(f"  -   {index}")

    return indexes


def redis_dump(file_path, host, port, password, index_list):
    redis_client = get_redis_client(host=host, port=port, password=password)
    indexes = get_redis_indexes(redis_client, index_list)

    for index in indexes:
        result = redis_client.ft(indexes[index]).search("*")
        path = Path(file_path) / index
        path.mkdir(parents=True, exist_ok=True)

        for doc in result.docs:
            json_id = json.loads(doc.json)["id"]

            with open(file=path / (json_id + ".json"), mode="w") as file:
                file.write(doc.json)
                LOGGER.info(f'{T("data_update_quest.core.redis_dump.dump").format(index=index):<20} :    {json_id}')


def file_upload(file_path, host, port, password):
    redis_client = get_redis_client(host=host, port=port, password=password)

    path = Path(file_path)
    if not path.is_dir():
        raise ValueError(
            f"The provided file path '{file_path}' is not a directory. Please provide a valid directory path."
        )

    indexes = {}
    for index in path.iterdir():
        indexes.setdefault(index, f"com.cosmotech.{index.name}.domain.{index.name.capitalize()}Idx")

    for index in indexes:
        index_p = path / index
        for json_file in index_p.glob("*.json"):
            json_name = json_file.name.split(".")[0]
            with json_file.open() as file:
                redis_client.json().set(f"{indexes[index]}:{json_name}", ".", json.load(file))
            LOGGER.info(
                f'{T("data_update_quest.core.redis_file_upload.upload").format(index=index):<20} :    {json_name}'
            )
