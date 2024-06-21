import asyncio
import random

import aiohttp
from pyrogram import Client
from pyrogram.raw.functions.messages import RequestWebView
from urllib.parse import unquote, quote
from aiohttp_socks import ProxyConnector
from fake_useragent import UserAgent
from loguru import logger
from data import config
from utils.accounts import lang_code_by_phone


class Blum:
    def __init__(self, number: int, session_name: str, phone_number: str, user_agent: str, proxy: [str, None]):
        self.session_name = session_name
        self.number = number
        self.phone_number = phone_number
        self.proxy = f"socks5://{proxy}" if proxy is not None else None

        if proxy:
            client_proxy = {
                "scheme": "socks5",
                "hostname": proxy.split(":")[1].split("@")[1],
                "port": int(proxy.split(":")[2]),
                "username": proxy.split(":")[0],
                "password": proxy.split(":")[1].split("@")[0]
            }
        else:
            client_proxy = None

        self.client = Client(
            name=session_name,
            api_id=config.API_ID,
            api_hash=config.API_HASH,
            workdir=config.WORKDIR,
            proxy=client_proxy,
            lang_code=lang_code_by_phone(phone_number)
        )

        headers = {
            'Accept': 'application/json',
            'User-Agent': user_agent if not user_agent == "" else UserAgent(os='android').random
        }
        connector = ProxyConnector.from_url(self.proxy) if self.proxy else aiohttp.TCPConnector(verify_ssl=False)
        self.session = aiohttp.ClientSession(headers=headers, trust_env=True, connector=connector,
                                             timeout=aiohttp.ClientTimeout(120))

    async def close_session(self):
        await self.session.close()

    async def start_game(self):
        try:
            balance_response = await self.session.get(url='https://game-domain.blum.codes/api/v1/user/balance')
            balance_json = await balance_response.json()
            tickets_count = balance_json.get('playPasses')
            logger.success(F"Blum - {str(self.session_name)}. Ticket balance - {tickets_count}")
            await asyncio.sleep(random.randint(1, 3))

            total_point = 0
            min_tickets = random.randint(*config.MIN_TICKETS)
            if tickets_count > min_tickets:
                games_count = tickets_count - min_tickets
                for i in range(games_count):
                    post_id_response = await self.session.post(url='https://game-domain.blum.codes/api/v1/game/play')
                    post_id_json = await post_id_response.json()
                    game_id = post_id_json.get('gameId')
                    logger.success(F"Blum - {str(self.session_name)}. Play started")

                    await asyncio.sleep(random.randint(*config.DURATION_GAME))

                    points = random.randint(*config.POINTS)
                    await self.session.post(url='https://game-domain.blum.codes/api/v1/game/claim', json={
                        "gameId": game_id, "points": points})

                    logger.success(
                        F"Blum - {str(self.session_name)}. {str(i + 1)} / {str(games_count)} games. Points per "
                        F"game - {str(points)}\n")

                    await asyncio.sleep(random.randint(*config.SLEEP_GAME_TIME))

                    total_point += points
                logger.info(F"Blum - {str(self.session_name)} Total points earned: {total_point}")
            else:
                logger.info("Not enough tickets")
        except Exception as e:
            logger.exception(e)

    async def login(self):
        self.session.headers.pop('Authorization', None)
        query = await self.get_tg_web_data()

        if query is None:
            logger.error(f"Thread {self.number} | {self.session_name} | Session {self.session_name} invalid")
            await self.close_session()
            return None

        json_data = {"query": query}
        token_response = await self.session.post(
            "https://gateway.blum.codes/v1/auth/provider/PROVIDER_TELEGRAM_MINI_APP", json=json_data)
        token_response_json = await token_response.json()

        self.session.headers['Authorization'] = f"Bearer {token_response_json.get("token").get("access")}"
        return True

    async def get_tg_web_data(self):
        try:
            await self.client.connect()

            web_view = await self.client.invoke(RequestWebView(
                peer=await self.client.resolve_peer('BlumCryptoBot'),
                bot=await self.client.resolve_peer('BlumCryptoBot'),
                platform='android',
                from_bot_menu=False,
                url='https://telegram.blum.codes/'
            ))
            await self.client.disconnect()

            auth_url = web_view.url

            query = unquote(string=unquote(string=auth_url.split('tgWebAppData=')[1].split('&tgWebAppVersion')[0]))
            query_id = query.split('query_id=')[1].split('&user=')[0]
            user = quote(query.split("&user=")[1].split('&auth_date=')[0])
            auth_date = query.split('&auth_date=')[1].split('&hash=')[0]
            hash_ = query.split('&hash=')[1]

            return f"query_id={query_id}&user={user}&auth_date={auth_date}&hash={hash_}"
        except Exception as e:
            logger.exception(e)
