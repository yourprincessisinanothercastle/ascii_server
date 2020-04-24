import json
from collections import namedtuple

import click
import asyncio
from aiohttp import web

from init_logging import init_logging
from world.creatures.player import Player
from world.rooms.map_generators import generators
from world.world import World

init_logging('debug')


async def handle(request):
    return web.Response(body='nothing', content_type='text/html')


async def wshandler(request):
    app = request.app
    ws = web.WebSocketResponse()

    # auth here
    # print(request.headers)

    await ws.prepare(request)
    player = Player(ws)
    player.room = app['world'].start_room
    app['world'].add_player(player)
    app['players'].append(player)

    if app['state']['game_is_running'] == True:
        asyncio.ensure_future(game_loop(app))
    while 1:
        msg = await ws.receive()
        print(msg)
        if msg.type == web.WSMsgType.text:
            print("Got message %s" % msg.data)
            await ws.send_str("Pressed key code: {}".format(msg.data))
        elif msg.type == web.WSMsgType.close or \
                msg.type == web.WSMsgType.error:
            print("Closed connection")
            break
        else:
            print(msg)


    app["players"].remove(player)

    return ws


async def game_loop(app):
    TICK_TIME = .5
    
    while 1:
        app['world'].tick(TICK_TIME)
        for player in app["players"]:
            await player.websocket.send_str("game loop says: tick, %s" % player)
        if not app["players"]:
            break
        await asyncio.sleep(TICK_TIME)

    print('no clients left')
    app['state']['game_is_running'] = False


def create_app():
    app = web.Application()
    app['state'] = {}
    app['world'] = World()

    app['players'] = []
    app['state']['game_is_running'] = True

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
