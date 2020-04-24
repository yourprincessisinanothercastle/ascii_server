import json
from collections import namedtuple

import click
import asyncio
from aiohttp import web
from pip._internal.utils import logging

from init_logging import init_logging
from world.creatures.player import Player
from world.rooms.map_generators import generators
from world.world import World

init_logging('debug')

logger = logging.getLogger(__name__)


async def handle(request):
    return web.Response(body='nothing', content_type='text/html')


async def wshandler(request):
    app = request.app
    ws = web.WebSocketResponse()

    # auth here
    # print(request.headers)

    player = Player(ws)
    player.fov_needs_update = True
    app['world'].add_player(player)
    app['players'].append(player)

    if app['state']['game_is_running'] == False:
        app['state']['game_is_running'] = True
        asyncio.ensure_future(game_loop(app))

    # init map for new player
    player.update_field_of_view()

    await ws.prepare(request)
    await ws.send_str(json.dumps({'init': player.get_client_init_data()}))

    try:
        async for msg in ws:
            if msg.type == web.WSMsgType.text:
                print("Got message %s" % msg.data)
                await ws.send_str("Pressed key code: {}".format(msg.data))
            elif msg.type == web.WSMsgType.close or \
                    msg.type == web.WSMsgType.error:
                print("Closed connection")
                break
            else:
                print(msg)

    except Exception as e:
        logger.error(e)

    finally:
        app['world'].remove_player(player)
        await player.websocket.close()
        app['players'].remove(player)

        print('%s disconnected' % player)

    app["players"].remove(player)

    return ws


async def game_loop(app):
    TICK_TIME = .5

    while 1:
        app['world'].tick(TICK_TIME)
        for player in app["players"]:
            player: Player
            ex = player.websocket.exception()
            if ex:
                logger.error("exception: %s" % ex)
            await player.websocket.send_str(json.dumps({'update': player.get_client_update_data()}))

        if not app["players"]:
            break

        for room in app['world'].rooms:
            room.map.set_tile_update_sent()

        await asyncio.sleep(TICK_TIME)

    print('no clients left')
    app['state']['game_is_running'] = False


def create_app():
    app = web.Application()
    app['state'] = {}
    app['world'] = World()

    app['players'] = []
    app['state']['game_is_running'] = False

    app.router.add_route('GET', '/connect', wshandler)
    app.router.add_route('GET', '/', handle)
    return app


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
    generator = generators[generator_name]
    generator().draw()


cli()
