import os.path
import asyncio
import random
from asyncio import sleep

from data import config
from blum.blum import Blum
from utils.accounts import create_session, get_accounts


async def main():
    if not os.path.exists('data/secret_key.py'):
        print("Getting started: fill secret_key.py")
        secret_key_file = open("secret_key.py", "w+")
        secret_key_file.write("API_ID = 12345\nAPI_HASH = 12345")
        secret_key_file.close()
        return

    action = int(input("Select action:\n1. Start farm\n2. Create sessions\n\n"))

    if not os.path.exists('sessions'):
        os.mkdir('sessions')

    if not os.path.exists('sessions/accounts.json'):
        with open("sessions/accounts.json", 'w') as f:
            f.write("[]")

    if action == 2:
        await create_session()

    if action == 1:
        print("Start farming")

        accounts = await get_accounts()

        start_tasks = []
        for number, account in enumerate(accounts):
            start_tasks.append(start(number, account))

        await asyncio.gather(*start_tasks)


async def start(number, account):
    session_name, phone_number, proxy, user_agent = account.values()
    blum_client = Blum(number=number, session_name=session_name, phone_number=phone_number,
                       proxy=proxy, user_agent=user_agent)

    await asyncio.sleep(random.randint(*config.ACC_DELAY))
    await blum_client.login()

    await sleep(random.uniform(10, 20))
    await blum_client.start_game()

    await blum_client.close_session()


if __name__ == '__main__':
    print(config.HELLO_MESSAGE)
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(main())
    loop.close()
