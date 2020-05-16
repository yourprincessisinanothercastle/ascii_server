import json

import click
import asyncio
import aiohttp_cors
from aiohttp import web
from pip._internal.utils import logging

from init_logging import init_logging
from world.creatures.player import Player
from world.world import World

init_logging('debug')

logger = logging.getLogger(__name__)


async def handle(request):
    return web.Response(body='nothing', content_type='text/html')


async def remove_player(app, player):
    logger.info('%s disconnected, closing socket' % player)
    await player.websocket.close()

    logger.info('removing player %s from world' % player)
    app['world'].remove_player(player)

    logger.info('removing player %s from app' % player)
    app['players'].remove(player)

    app['removed_players'].append(player)
    logger.info('players left: %s' % app['players'])


async def wshandler(request):
    app = request.app
    ws = web.WebSocketResponse()
    await ws.prepare(request)

    # auth here
    # print(request.headers)
    if app['state']['game_is_running'] == False:
        app['state']['game_is_running'] = True
        app['world'] = World()
        asyncio.ensure_future(game_loop(app))
    player = Player(ws)
    player.fov_needs_update = True

    app['world'].add_player(player)
    app['players'].append(player)


    await ws.send_str(json.dumps({
        'type': 'init',
        'data': player.get_client_init_data()}))

    try:
        async for msg in ws:
            if msg.type == web.WSMsgType.text:
                packet = json.loads(msg.data)
                logger.debug(json.dumps(packet, indent=2))
                if packet['type'] == 'actions':
                    player.update(packet['data'])
                print("Got message %s" % msg.data)
                # await ws.send_str("Pressed key code: {}".format(msg.data))
            elif msg.type == web.WSMsgType.close or \
                    msg.type == web.WSMsgType.error:
                print("Closed connection")
                break
            else:
                print(msg)

    except Exception as e:
        logger.error(e, exc_info=True)

    finally:
        await remove_player(app, player)

    return ws


async def game_loop(app):
    logger.info('starting game loop')
    TICK_TIME = 1 / 20

    while 1:
        app['world'].tick(TICK_TIME)

        for player in app["players"]:
            player: Player
            ex = player.websocket.exception()
            if ex:
                logger.error("exception: %s" % ex)
            try:
                if player.client_needs_init:
                    await player.websocket.send_str(json.dumps({
                        'type': 'init',
                        'data': player.get_client_init_data()}))
                    player.client_needs_init = False
                else:
                    update_data = player.get_client_update_data()
                    if update_data: 
                        await player.websocket.send_str(json.dumps({'type': 'update', 'data': update_data}))
            except Exception as e:
                logger.error(e)
                await remove_player(app, player)

        for player in app["players"]:
            player.update_sent = True

        if app['removed_players']:
            logger.info('sending remove_player for %s to %s players' % (app['removed_players'], len(app['players'])))

            for player in app['players']:
                try:
                    await player.websocket.send_str(
                        json.dumps(
                            {'type': 'remove_players',
                             'data': [str(left_player.uid) for left_player in app['removed_players']]}))
                except Exception as e:
                    logger.error(e)
                    await remove_player(app, player)

            app['removed_players'] = []
        if not app["players"]:
            break

        for room in app['world'].levels:
            room.map.set_tile_update_sent()

        await asyncio.sleep(TICK_TIME)

    logger.warning('no clients left')
    app['state']['game_is_running'] = False


async def create_app():
    app = web.Application()
    cors = aiohttp_cors.setup(app, defaults={
        "*": aiohttp_cors.ResourceOptions(
            expose_headers="*",
            allow_headers="*"),
    })

    app['state'] = {}
    app['world'] = None

    app['players'] = []

    # temp storage for players who left the game
    app['removed_players'] = []

    app['state']['game_is_running'] = False

    cors.add(app.router.add_route('GET', '/connect', wshandler))
    cors.add(app.router.add_route('GET', '/', handle))

    return app
