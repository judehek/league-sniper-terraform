import asyncio
import requests
import time
from datetime import datetime

import riot_auth

def lambda_handler(event, context):

    TIME = event['time']
    LOGIN = event['username'], event['password']

    auth = riot_auth.RiotAuth()
    auth.RIOT_CLIENT_USER_AGENT = "RiotClient/62.0.1.4852117.4789131 %s (Windows;10;;Professional, x64)" # might have to update, doesn't seem to be issue atm

    asyncio.run(auth.authorize(*LOGIN))

    # purchase info
    response = requests.get(purchase_info_url, headers=purchase_info_headers)
    data = response.json()

    if "player" in data:
        account_id = str(data["player"]["accountId"])
        if int(data["player"]["ip"]) < 13900:
            # not enough BE
            raise Exception("Not enough essence")
    else:
        raise Exception("Failed to get purchase information")

    # change name
    while True:
        difference = TIME - datetime.now()
        if difference.total_seconds() - 1 == 0: # need to account for travel time
            for i in 25:
                response = requests.post(
                    change_name_url,
                    data=UpdateAccountID(account_id, event['alias']),
                    headers=change_name_headers
                )
                data = response.json()
                if "transactions" in data:
                    print("Receieved successful message")
                time.sleep(0.05)
        break

    purchase_info_headers = {
    "User-Agent": "RiotClient/18.0.0 (lol-store)",
    "Accept": "application/json",
    "Authorization": "Bearer " + {auth.access_token},
    }

    change_name_headers = {
        "User-Agent": "RiotClient/18.0.0 (lol-store)",
        "Accept": "application/json",
        "Content-type": "application/json",
        "Authorization": "Bearer " + {auth.access_token},
        "Referer": change_name_referer,
    }
    #stop lambda
    return

purchase_info_url = "https://na.store.leagueoflegends.com/storefront/v3/history/purchase?language=en_GB"
change_name_url = "https://na.store.leagueoflegends.com/storefront/v3/summonerNameChange/purchase?language=en_GB"
change_name_referer = "https://na.store.leagueoflegends.com/storefront/ui/v1/app.html?language=en_GB&port=52684&clientRegion=na2&selectedItems=&page=featured&recipientSummonerId="

def UpdateAccountID(account_id, alias):
    change_name_body = '{"summonerName":"'
    change_name_body += alias
    change_name_body += '","accountId":'
    change_name_body += account_id
    change_name_body += ',"items":[{"inventoryType":"SUMMONER_CUSTOMIZATION","itemId":1,"ipCost":13900,"rpCost":null,"quantity":1}]}'
    return change_name_body
