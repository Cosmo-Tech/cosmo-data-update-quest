# Copyright (C) - 2025 - Cosmo Tech
# This document and all information contained herein is the exclusive property -
# including all intellectual property rights pertaining thereto - of Cosmo Tech.
# Any use, reproduction, translation, broadcasting, transmission, distribution,
# etc., to any person is prohibited unless it has been previously and
# specifically authorized by written means by Cosmo Tech.

from cosmotech.data_update_quest.core.database.redis.client import get_redis_client
from cosmotech.data_update_quest.core.database.redis.client import get_redis_indexes
from cosmotech.data_update_quest_cli.utils.click import click
from cosmotech.data_update_quest_cli.utils.decorators import redis_connection_parameters


@click.command("redis_list_index")
@redis_connection_parameters
def redis_list_index_command(host, port, password):
    print(get_redis_indexes(get_redis_client(host=host, port=port, password=password), index_list=None))
