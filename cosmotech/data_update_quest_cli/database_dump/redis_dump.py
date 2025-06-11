# Copyright (C) - 2025 - Cosmo Tech
# This document and all information contained herein is the exclusive property -
# including all intellectual property rights pertaining thereto - of Cosmo Tech.
# Any use, reproduction, translation, broadcasting, transmission, distribution,
# etc., to any person is prohibited unless it has been previously and
# specifically authorized by written means by Cosmo Tech.

from cosmotech.csm_data.utils.decorators import translate_help
from cosmotech.orchestrator.utils.translate import T

from cosmotech.data_update_quest.core.redis.dump_data import dump_data
from cosmotech.data_update_quest_cli.utils.click import click
from cosmotech.data_update_quest_cli.utils.logger import LOGGER


@click.command("redis_dump")
@click.option(
    "--file_path",
    "-f",
    type=click.Path(dir_okay=True, readable=True),
    help=T("data_update_quest.commands.redis_dump.parameters.file_path"),
    required=True,
)
@click.option(
    "--password",
    "-p",
    type=str,
    envvar="REDIS_SECRET",
    help=T("data_update_quest.commands.redis_dump.parameters.password"),
    required=True,
)
@click.option("--host", type=str, default="localhost", help=T("data_update_quest.commands.redis_dump.parameters.host"))
@click.option("--port", type=str, default=6379, help=T("data_update_quest.commands.redis_dump.parameters.port"))
@translate_help("data_update_quest.commands.redis_dump.description")
def redis_dump(file_path: str, password: str, host: str, port: str):
    dump_data(file_path=file_path, host=host, port=port, password=password)
    LOGGER.info(T("data_update_quest.core.redis_dump.file_saved").format(file_path=file_path))
