from cosmotech.orchestrator.utils.translate import T
from cosmotech.orchestrator.utils.logger import get_logger
from cosmotech.csm_data.utils.click import click
import click_log
from cosmotech.csm_data.utils.decorators import translate_help
from cosmotech.data_update_quest import __version__

LOGGER = get_logger("csm.duq")


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


if __name__ == "__main__":
    main()
