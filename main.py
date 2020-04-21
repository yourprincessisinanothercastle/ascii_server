import json
from collections import namedtuple

import click
import asyncio
from aiohttp import web

from world.rooms.map_generators import generators
from world.world import World

async def handle(request):
    return web.Response(body='nothing', content_type='text/html')


async def wshandler(request):
    app = request.app
    ws = web.WebSocketResponse()

    # auth here
    # print(request.headers)

    await ws.prepare(request)

    app['players'].append({ws: app['world'].add_player()})

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
            break

    app["sockets"].remove(ws)
    print("Closed connection")

    return ws


async def game_loop(app):
    while 1:
        app['world'].tick()

        for ws, player in app["players"].items():
            await ws.send_str("game loop says: tick")
        if len(app["sockets"]) == 0:
            break
        await asyncio.sleep(.5)
    print('no clients left')
    app['state']['game_is_running'] = False


def create_app():
    app = web.Application()
    app['state'] = {}
    app['world'] = World()

    app['players'] = {}
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
