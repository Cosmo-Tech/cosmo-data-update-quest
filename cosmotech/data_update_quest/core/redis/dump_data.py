# Copyright (C) - 2025 - Cosmo Tech
# This document and all information contained herein is the exclusive property -
# including all intellectual property rights pertaining thereto - of Cosmo Tech.
# Any use, reproduction, translation, broadcasting, transmission, distribution,
# etc., to any person is prohibited unless it has been previously and
# specifically authorized by written means by Cosmo Tech.

import redis
import json
from pathlib import Path

from cosmotech.orchestrator.utils.translate import T

from cosmotech.data_update_quest_cli.utils.logger import LOGGER


def configuration(host, port, password):
    LOGGER.info(T("data_update_quest.core.redis_dump.redis_connection"))
    r = redis.Redis(host=host, port=port, password=password, decode_responses=True)

    domains = {}
    domain_list = r.execute_command("FT._LIST")
    LOGGER.info(T("data_update_quest.core.redis_dump.redis_index"))
    for domain in domain_list:
        domain_name = domain.split(".")[2]
        domains.setdefault(domain_name, domain)
        LOGGER.info(f"  -   {domain}")
    return r, domains


def dump_data(file_path: str, host="localhost", port=6379, password=""):
    r, domains = configuration(host, port, password)
    for domain in domains:
        result = r.ft(domains[domain]).search("*")
        path = Path(file_path + domain)
        path.mkdir(parents=True, exist_ok=True)
        for doc in result.docs:
            object_id = json.loads(doc.json)["id"]
            with open(file=file_path + domain + "/" + object_id, mode="w") as f:
                f.write(doc.json)
                LOGGER.info(f'{T("data_update_quest.core.redis_dump.dump").format(domain=domain):<20} :    {object_id}')
