import os.path
import asyncio
from itertools import zip_longest
from data import config
from blum.blum import Blum


def check_data_files():
    files_is_exists = True
    if not os.path.exists("data/proxy.txt"):
        f = open("data/proxy.txt", "w")
        f.close()
        files_is_exists = False

    if not os.path.isfile("data/access_key.txt"):
        f = open("data/access_key.txt", "w")
        f.close()
        files_is_exists = False

    if not os.path.isfile("data/user_agent.txt"):
        f = open("data/user_agent.txt", "w")
        f.close()
        files_is_exists = False

    return files_is_exists


async def main():
    if not check_data_files():
        print("There were not all data files. The script has been stopped")
        return

    action = int(input("To start the farm, press 1>"))

    if action == 1:
        print("Start farming")

        tasks = []

        with open("data/access_key.txt", "r") as access_key_file:
            access_key_arr = [line.strip() for line in access_key_file]

        with open("data/user_agent.txt", "r") as user_agent_file:
            user_agent_arr = [line.strip() for line in user_agent_file]

        with open("data/proxy.txt", "r") as proxy_file:
            proxy_arr = [line.strip() for line in proxy_file]

        i = 0
        for access_key, user_agent, proxy in zip_longest(access_key_arr, user_agent_arr, proxy_arr, fillvalue=""):
            i += 1

            if access_key == "":
                continue

            tasks.append(asyncio.create_task(Blum(i, jwt=access_key, proxy=proxy, user_agent=user_agent).start_game()))

        await asyncio.gather(*tasks)


if __name__ == '__main__':
    print(config.HELLO_MESSAGE)
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(main())
    loop.close()