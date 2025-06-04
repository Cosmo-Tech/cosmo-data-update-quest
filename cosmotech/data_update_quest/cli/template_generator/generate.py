# Copyright (C) - 2025 - Cosmo Tech
# This document and all information contained herein is the exclusive property -
# including all intellectual property rights pertaining thereto - of Cosmo Tech.
# Any use, reproduction, translation, broadcasting, transmission, distribution,
# etc., to any person is prohibited unless it has been previously and
# specifically authorized by written means by Cosmo Tech.

from cosmotech.data_update_quest.cli.utils.click import click
from cosmotech.data_update_quest.core.migration.template_generator import MigrationTemplateGenerator
from cosmotech.orchestrator.utils.translate import T
from cosmotech.data_update_quest.cli.utils.logger import LOGGER
from cosmotech.csm_data.utils.decorators import translate_help


@click.command("generate-templates")
@click.argument("source_path", type=click.Path(exists=True, dir_okay=False, readable=True))
@click.argument("target_path", type=click.Path(exists=True, dir_okay=False, readable=True))
@click.argument("source_model", type=str)
@click.argument("target_model", type=str)
@click.option(
    "--output-dir",
    type=click.Path(file_okay=False, writable=True, readable=True),
    default=".",
    help=T("data_update_quest.commands.generate_templates.parameters.output_dir"),
)
@translate_help("data_update_quest.commands.generate_templates.description")
def generate_templates(source_path: str, target_path: str, source_model: str, target_model: str, output_dir: str):
    generator = MigrationTemplateGenerator.from_openapi_files(source_path, target_path, source_model, target_model)

    # Save all templates to the specified output directory
    generator.save_all_templates(output_dir)

    LOGGER.info(T("data_update_quest.commands.generate_templates.save_file_target").format(output_dir=output_dir))


if __name__ == "__main__":
    generate_templates()
