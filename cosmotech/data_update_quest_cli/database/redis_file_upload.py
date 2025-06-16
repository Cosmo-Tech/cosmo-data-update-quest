# Copyright (C) - 2025 - Cosmo Tech
# This document and all information contained herein is the exclusive property -
# including all intellectual property rights pertaining thereto - of Cosmo Tech.
# Any use, reproduction, translation, broadcasting, transmission, distribution,
# etc., to any person is prohibited unless it has been previously and
# specifically authorized by written means by Cosmo Tech.

from cosmotech.csm_data.utils.decorators import translate_help
from cosmotech.orchestrator.utils.translate import T

from cosmotech.data_update_quest.core.database.redis.client import file_upload
from cosmotech.data_update_quest_cli.utils.click import click
from cosmotech.data_update_quest_cli.utils.decorators import redis_connection_parameters


@click.option(
    "--file_path",
    "-f",
    type=click.Path(dir_okay=True, readable=True),
    help=T("data_update_quest.commands.redis_file_upload.parameters.file_path"),
    required=True,
)
@redis_connection_parameters
@translate_help("data_update_quest.commands.redis_file_upload.description")
@click.command("redis_file_upload")
def redis_file_upload_command(file_path: str, password: str, host: str, port: str):
    file_upload(file_path=file_path, host=host, port=port, password=password)
