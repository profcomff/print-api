import logging

import click as click
import uvicorn

from print_service.settings import Settings, get_settings


logger = logging.getLogger(__name__)


@click.group()
@click.pass_context
def main(ctx):
    """Основная группа."""
    ctx.obj['settings'] = get_settings()


@click.command()
@click.pass_context
def start(ctx):
    """Инициализирует и запускает прокси и UI."""
    logger.info('Starting environment')
    settings: Settings = ctx.obj['settings']
    uvicorn.run('print_service.fastapi:app', host="0.0.0.0", port=8000)


main.add_command(start)
