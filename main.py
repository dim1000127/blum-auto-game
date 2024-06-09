import requests as req
import json
import time
import random


def main(jwt, proxies, user_agent):
    session = req.Session()
    session.proxies = proxies

    head = {
        'Authorization': 'Bearer' + jwt,
        'Accept': 'application/json',
        'User-Agent': user_agent
    }
    resp = session.get('https://game-domain.blum.codes/api/v1/user/balance', headers=head, proxies=proxies)
    count = json.loads(resp.text)['playPasses']
    total_point = 0
    if count != 0:
        print("Начал играть...")
        for i in range(count):
            post_id = session.post('https://game-domain.blum.codes/api/v1/game/play', headers=head, proxies=proxies)
            id = json.loads(post_id.text)['gameId']
            time.sleep(random.randrange(30, 60, 5))
            points = random.randint(150, 220)
            endGame = session.post('https://game-domain.blum.codes/api/v1/game/claim', headers=head, json={
                "gameId": id, "points": points}, proxies=proxies)
            print(str(i + 1) + ' / ' + str(count) + " игр." + " Очки за игру - " + str(points))
            time.sleep(random.randint(1, 5))
            total_point += points
        print("Всего зафармленно поинтов:", total_point)
    else:
        print("Нету кристалов для игры :(")
        exit()

if __name__ == '__main__':
    print("Test")