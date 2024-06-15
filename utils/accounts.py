import os
import asyncio
from pyrogram import Client
from data import config
from utils.file_system import save_to_json, load_from_json
from loguru import logger
import phonenumbers
from langcodes import Language


def lang_code_by_phone(phone_number: str):
    try:
        country_code = phonenumbers.region_code_for_number(phonenumbers.parse(phone_number))
        if country_code:
            return Language.get(country_code).language
        else:
            return "en"
    except:
        return "en"


async def create_session():
    while True:
        session_mame = input("\nInput session name (press Enter to exit)")
        if not session_mame:
            return

        proxy = input("Input the proxy in the format login:password@ip:port (press Enter to use without proxy): ")
        if proxy:
            client_proxy = {
                "scheme": "socks5",
                "hostname": proxy.split(":")[1].split("@")[1],
                "port": int(proxy.split(":")[2]),
                "username": proxy.split(":")[0],
                "password": proxy.split(":")[1].split("@")[0]
            }
        else:
            client_proxy, proxy = None, None

        phone_number = (input("Input the phone number of the account: ")).replace(' ', '')

        user_agent = input("Input useragent: ")

        client = Client(
            api_id=config.API_ID,
            api_hash=config.API_HASH,
            name=session_mame,
            workdir=config.WORKDIR,
            phone_number=phone_number,
            proxy=client_proxy
        )

        async with client:
            me = await client.get_me()

        save_to_json('sessions/accounts.json', dict_={
            "session_name": session_mame,
            "phone_number": phone_number,
            "proxy": proxy,
            "user_agent": user_agent
        })
        logger.success(f'Added a account {me.username} ({me.first_name}) | {me.phone_number}')


def get_available_accounts(sessions: list):
    accounts_from_json = load_from_json('sessions/accounts.json')

    if not accounts_from_json:
        raise ValueError("Have not account's in sessions/accounts.json")

    available_accounts = []
    for session in sessions:
        for saved_account in accounts_from_json:
            if saved_account['session_name'] == session:
                available_accounts.append(saved_account)
                break

    return available_accounts


def pars_sessions():
    sessions = []
    for file in os.listdir(config.WORKDIR):
        if file.endswith(".session"):
            sessions.append(file.replace(".session", ""))

    logger.info(f"Searched sessions: {len(sessions)}.")
    return sessions


async def get_accounts():
    sessions = pars_sessions()
    available_accounts = get_available_accounts(sessions)

    if not available_accounts:
        raise ValueError("Have not available accounts!")
    else:
        logger.success(f"Search available accounts: {len(available_accounts)}.")

    valid_accounts = await check_valid_accounts(available_accounts)

    if not valid_accounts:
        raise ValueError("Have not valid sessions")
    else:
        return valid_accounts


async def check_valid_account(account: dict):
    session_name, phone_number, proxy, user_agent = account.values()

    try:
        proxy_dict = {
            "scheme": "socks5",
            "hostname": proxy.split(":")[1].split("@")[1],
            "port": int(proxy.split(":")[2]),
            "username": proxy.split(":")[0],
            "password": proxy.split(":")[1].split("@")[0]
        } if proxy else None

        client = Client(name=session_name, api_id=config.API_ID, api_hash=config.API_HASH, workdir=config.WORKDIR,
                        proxy=proxy_dict)

        connect = await asyncio.wait_for(client.connect(), timeout=config.TIMEOUT)
        if connect:
            await client.get_me()
            await client.disconnect()
            return account
        else:
            await client.disconnect()
    except:
        pass


async def check_valid_accounts(accounts: list):
    logger.info(f"Checking accounts for valid...")

    tasks = []
    for account in accounts:
        tasks.append(asyncio.create_task(check_valid_account(account)))

    v_accounts = await asyncio.gather(*tasks)
    valid_accounts = [valid_accounts for valid_accounts in v_accounts if valid_accounts is not None]

    logger.success(f"Valid accounts: {len(valid_accounts)}; Invalid: {len(accounts) - len(valid_accounts)}")
    return valid_accounts
