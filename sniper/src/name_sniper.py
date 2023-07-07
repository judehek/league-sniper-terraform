import asyncio
import requests
import threading
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime

import riot_auth

def execute_requests(change_name_url, change_name_headers, change_name_body):
    max_requests = 25
    with ThreadPoolExecutor(max_workers=max_requests) as executor:
        futures = [executor.submit(sniper_request, change_name_url, change_name_headers, change_name_body) for _ in range(max_requests)]
        _ = [future.result() for future in futures]

def sniper_request(change_name_url, change_name_headers, change_name_body):
    print("Sending snipe request...")
    response = requests.post(
        change_name_url,
        data=change_name_body,
        headers=change_name_headers
    )
    data = response.json()
    if "transactions" in data:
        print(f"Receieved successful message.")

def UpdateAccountID(account_id, alias):
    change_name_body = '{"summonerName":"'
    change_name_body += alias
    change_name_body += '","accountId":'
    change_name_body += account_id
    change_name_body += ',"items":[{"inventoryType":"SUMMONER_CUSTOMIZATION","itemId":1,"ipCost":13900,"rpCost":null,"quantity":1}]}'
    return change_name_body

def lambda_handler(event, context):

    TIME = event['time']
    LOGIN = event['username'], event['password']

    auth = riot_auth.RiotAuth()
    auth.RIOT_CLIENT_USER_AGENT = "RiotClient/62.0.1.4852117.4789131 %s (Windows;10;;Professional, x64)"

    asyncio.run(auth.authorize(*LOGIN))

    print(f"Access Token: {auth.access_token}\n")

    purchase_info_url = "https://na.store.leagueoflegends.com/storefront/v3/history/purchase?language=en_GB"

    purchase_info_headers = {
        "User-Agent": "RiotClient/18.0.0 (lol-store)",
        "Accept": "application/json",
        "Authorization": f"Bearer {auth.access_token}",
    }

    response = requests.get(purchase_info_url, headers=purchase_info_headers)
    data = response.json()

    if "player" in data:
        account_id = str(data["player"]["accountId"])
        if int(data["player"]["ip"]) < 13900:
            raise Exception("Not enough essence")
    else:
        raise Exception("Failed to get purchase information")

    change_name_url = "https://na.store.leagueoflegends.com/storefront/v3/summonerNameChange/purchase?language=en_GB"
    change_name_referer = "https://na.store.leagueoflegends.com/storefront/ui/v1/app.html?language=en_GB&port=52684&clientRegion=na2&selectedItems=&page=featured&recipientSummonerId="

    change_name_headers = {
        "User-Agent": "RiotClient/18.0.0 (lol-store)",
        "Accept": "application/json",
        "Content-type": "application/json",
        "Authorization": f"Bearer {auth.access_token}",
        "Referer": change_name_referer,
    }

    change_name_body = UpdateAccountID(account_id, event['alias'])

    now = datetime.now()
    time_difference = (TIME - now).total_seconds()

    if time_difference > 0:
        print(f"Sniping at: {TIME}")
        timer = threading.Timer(time_difference, lambda: execute_requests(change_name_url, change_name_headers, change_name_body))
        timer.start()

    return

lambda_handler('', '')