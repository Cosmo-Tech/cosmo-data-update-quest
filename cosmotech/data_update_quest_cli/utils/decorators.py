# Copyright (C) - 2023 - 2025 - Cosmo Tech
# This document and all information contained herein is the exclusive property -
# including all intellectual property rights pertaining thereto - of Cosmo Tech.
# Any use, reproduction, translation, broadcasting, transmission, distribution,
# etc., to any person is prohibited unless it has been previously and
# specifically authorized by written means by Cosmo Tech.

from functools import wraps

from cosmotech.orchestrator.utils.translate import T
from cosmotech.data_update_quest_cli.utils.click import click


def redis_connection_parameters(func):
    @wraps(func)
    @click.option(
        "--host", type=str, default="localhost", envvar="REDIS_HOST", help=T("data_update_quest.commands.redis.host")
    )
    @click.option(
        "--port", type=int, default=6379, envvar="REDIS_PORT", help=T("data_update_quest.commands.redis.port")
    )
    @click.option(
        "--password",
        "-p",
        type=str,
        envvar="REDIS_SECRET",
        help=T("data_update_quest.commands.redis.password"),
        required=True,
    )
    def f(*args, **kwargs):
        return func(*args, **kwargs)

    return f
