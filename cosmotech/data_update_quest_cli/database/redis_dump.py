# Copyright (C) - 2025 - Cosmo Tech
# This document and all information contained herein is the exclusive property -
# including all intellectual property rights pertaining thereto - of Cosmo Tech.
# Any use, reproduction, translation, broadcasting, transmission, distribution,
# etc., to any person is prohibited unless it has been previously and
# specifically authorized by written means by Cosmo Tech.

from typing import Optional

from cosmotech.csm_data.utils.decorators import translate_help
from cosmotech.orchestrator.utils.translate import T

from cosmotech.data_update_quest_cli.utils.click import click
from cosmotech.data_update_quest_cli.utils.decorators import redis_connection_parameters
from cosmotech.data_update_quest_cli.utils.logger import LOGGER


@click.command("redis_dump")
@click.option(
    "--file_path",
    "-f",
    type=click.Path(dir_okay=True, readable=True),
    envvar="REDIS_FILE_PATH",
    help=T("data_update_quest.commands.redis_dump.parameters.file_path"),
    required=True,
)
@click.option(
    "--index_list",
    "-i",
    type=str,
    default=None,
    multiple=True,
    help=T("data_update_quest.commands.redis_dump.parameters.index_list"),
)
@redis_connection_parameters
@translate_help("data_update_quest.commands.redis_dump.description")
def redis_dump_command(file_path, password, host, port, index_list: Optional[tuple]):
    from cosmotech.data_update_quest.core.database.redis.client import redis_dump

    redis_dump(file_path=file_path, host=host, port=port, password=password, index_list=index_list)
    LOGGER.info(T("data_update_quest.core.redis_dump.file_saved").format(file_path=file_path))
