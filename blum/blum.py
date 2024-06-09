import asyncio
import random
import json

import aiohttp
from aiohttp_socks import ProxyConnector
from fake_useragent import UserAgent
from data import config


class Blum:
    def __init__(self, number, jwt, proxy, user_agent):
        self.number = number
        self.proxy = proxy

        headers = {
            'Authorization': 'Bearer ' + jwt,
            'Accept': 'application/json',
            'User-Agent': user_agent if not user_agent == "" else UserAgent(os='android').random
        }
        connector = ProxyConnector.from_url(proxy)
        self.session = aiohttp.ClientSession(headers=headers, trust_env=True, connector=connector,
                                             timeout=aiohttp.ClientTimeout(120))

    async def start_game(self):
        await asyncio.sleep(random.randint(*config.ACC_DELAY))

        balance_response = await self.session.get(url='https://game-domain.blum.codes/api/v1/user/balance')
        balance_json = await balance_response.json()
        tickets_count = balance_json.get('playPasses')

        total_point = 0
        if tickets_count > config.MIN_TICKETS:
            print("Game started...")
            games_count = tickets_count - config.MIN_TICKETS
            for i in range(games_count):
                post_id_response = await self.session.post(url='https://game-domain.blum.codes/api/v1/game/play')
                post_id_json = await post_id_response.json()
                game_id = post_id_json.get('gameId')

                await asyncio.sleep(random.randint(*config.DURATION_GAME))

                points = random.randint(*config.POINTS)
                await self.session.post(url='https://game-domain.blum.codes/api/v1/game/claim', json={
                    "gameId": game_id, "points": points})

                print("Blum - " + str(self.number) + "\n" +
                      str(i + 1) + ' / ' + str(games_count) + " games." +
                      " Points per game - " + str(points) + "\n")

                await asyncio.sleep(random.randint(*config.SLEEP_GAME_TIME))

                total_point += points
            print("Total points earned:", total_point)
        else:
            print("Not enough tickets")
