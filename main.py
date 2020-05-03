import click
from aiohttp import web
import logging

from app import create_app
from init_logging import init_logging
from world.level.creation.area import AREA_GENERATORS

init_logging('debug')

logger = logging.getLogger(__name__)


@click.group()
def cli():
    pass


@cli.command()
def run():
    app = create_app()
    web.run_app(app)


@cli.command()
@click.argument('generator_name')
def gen_map(generator_name):
    generator = AREA_GENERATORS[generator_name]()
    generator.generate()
    generator.draw()


cli()
