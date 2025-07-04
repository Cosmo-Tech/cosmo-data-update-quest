# Copyright (C) - 2025 - Cosmo Tech
# This document and all information contained herein is the exclusive property -
# including all intellectual property rights pertaining thereto - of Cosmo Tech.
# Any use, reproduction, translation, broadcasting, transmission, distribution,
# etc., to any person is prohibited unless it has been previously and
# specifically authorized by written means by Cosmo Tech.

from cosmotech.orchestrator.utils.translate import T
from cosmotech.data_update_quest_cli.utils.click import click
import click_log
from cosmotech.csm_data.utils.decorators import translate_help
from cosmotech.data_update_quest import __version__
from cosmotech.data_update_quest_cli.utils.logger import LOGGER

from cosmotech.data_update_quest_cli.template_generator.generate import generate_templates
from cosmotech.data_update_quest_cli.database.redis_dump import redis_dump_command
from cosmotech.data_update_quest_cli.database.redis_list_index import redis_list_index_command
from cosmotech.data_update_quest_cli.database.redis_file_upload import redis_file_upload_command


def print_version(ctx, param, value):
    if not value or ctx.resilient_parsing:
        return
    click.echo(T("data_update_quest.core.logs.version").format(version=__version__))
    ctx.exit()


@click.group("csm-data", invoke_without_command=True)
@click.pass_context
@click_log.simple_verbosity_option(LOGGER, "--log-level", envvar="LOG_LEVEL", show_envvar=True)
@click.option(
    "--version",
    is_flag=True,
    callback=print_version,
    expose_value=False,
    is_eager=True,
    help=T("data_update_quest.commands.main.parameters.version"),
)
@translate_help("data_update_quest.commands.main.description")
def main(ctx):
    if ctx.invoked_subcommand is None:
        click.echo(T("data_update_quest.commands.main.content").format(version=__version__))


main.add_command(generate_templates, name="generate-templates")
main.add_command(redis_dump_command, name="redis-dump")
main.add_command(redis_list_index_command, name="redis-list-index")
main.add_command(redis_file_upload_command, name="redis-file-upload")

if __name__ == "__main__":
    main()
