import logging
import asyncio
import requests
import re
import time
from datetime import datetime

import riot_auth

logging.basicConfig(level = logging.INFO)
LOGGER = logging.getLogger()

purchase_info_url = "https://na.store.leagueoflegends.com/storefront/v3/history/purchase?language=en_GB"
change_name_url = "https://na.store.leagueoflegends.com/storefront/v3/summonerNameChange/purchase?language=en_GB"
change_name_referer = "https://na.store.leagueoflegends.com/storefront/ui/v1/app.html?language=en_GB&port=52684&clientRegion=na2&selectedItems=&page=featured&recipientSummonerId="

def get_drop_time(alias):
    url = "https://www.nameslol.com/lol-name-checker?region=na&name=" + alias
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.103 Safari/537.36"
    }
    response = requests.get(url, headers=headers)
    reg_exp = re.search("(?<=availabilityDate\":)[0-9]{13}", response.text)
    return int(reg_exp.group(0))

def update_account_id(account_id, alias):
    change_name_body = '{"summonerName":"'
    change_name_body += alias
    change_name_body += '","accountId":'
    change_name_body += account_id
    change_name_body += ',"items":[{"inventoryType":"SUMMONER_CUSTOMIZATION","itemId":1,"ipCost":13900,"rpCost":null,"quantity":1}]}'
    return change_name_body

def lambda_handler(event, context):

    TIME = get_drop_time(event['alias'])
    LOGIN = event['username'], event['password']

    LOGGER.info("[PLAN] Snipe name: %s at %s", event['alias'], datetime.fromtimestamp(TIME / 1000))

    auth = riot_auth.RiotAuth()
    auth.RIOT_CLIENT_USER_AGENT = "RiotClient/62.0.1.4852117.4789131 %s (Windows;10;;Professional, x64)" # might have to update, doesn't seem to be issue atm

    asyncio.run(auth.authorize(*LOGIN))
    LOGGER.info("Successfully logged in to account: %s:%s", event['username'], event['password'])

    purchase_info_headers = {
        "User-Agent": "RiotClient/18.0.0 (lol-store)",
        "Accept": "application/json",
        "Authorization": "Bearer " + auth.access_token,
    }

    change_name_headers = {
        "User-Agent": "RiotClient/18.0.0 (lol-store)",
        "Accept": "application/json",
        "Content-type": "application/json",
        "Authorization": "Bearer " + auth.access_token,
        "Referer": change_name_referer,
    }

    # purchase info
    response = requests.get(purchase_info_url, headers=purchase_info_headers)
    data = response.json()

    if "player" in data:
        account_id = str(data["player"]["accountId"])
        be = int(data["player"]["ip"])
        rp = int(data["player"]["rp"])
        if be < 13900:
            # not enough BE
            LOGGER.fatal("Not enough BE for name change!")
            return
    else:
        LOGGER.fatal("Failed to get purchase information!")
        return
    
    LOGGER.info("Account: %s:%s BE: %s RP: %s", event['username'], event['password'], be, rp)
    # change name
    while True:
        difference = TIME - (int(time.time()) * 1000)
        if ((difference / 1000) - 1) == 0: # need to account for travel time
            for i in range(25):
                response = requests.post(
                    change_name_url,
                    data=update_account_id(account_id, event['alias']),
                    headers=change_name_headers
                )
                data = response.json()
                if "transactions" in data:
                    LOGGER.info("Received successful message on request: %s on account: %s:%s", i, event['username'], event['password'])
                else:
                    LOGGER.info("Failed on request: %s", i)
                time.sleep(0.05)
            break
        time.sleep(0.10)

    #stop lambda
    return

lambda_handler({
  "username": "Zialuton",
  "password": "g0nBj4sLU6oTz4jAJ0dAc7eAF4l",
  "alias": "deserve"
}, "")
