import asyncio
import requests
import threading
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
import os

import riot_auth

def execute_requests(change_name_url, change_name_headers, change_name_body, event):
    max_requests = 25
    with ThreadPoolExecutor(max_workers=max_requests) as executor:
        futures = [executor.submit(sniper_request, change_name_url, change_name_headers, change_name_body, event) for _ in range(max_requests)]

        _ = [future.result() for future in futures]

    be = check_new_blue_essence(event['accountId'], change_name_headers['Authorization'])
    if be < 13900:
        print(f"Account is broke: {event['username']}:{event['password']}")
        send_insufficient_currency_webhook(event, be)

def check_summoner_name(account_id, auth_key, target_name):
    url = "https://na-red.lol.sgp.pvp.net/summoner-ledge/v1/regions/NA1/summoners/summoner-ids"
    headers = {
        "Accept": "application/json",
        "User-Agent": "LeagueOfLegendsClient/13.13.517.6152 (rcp-be-lol-summoner)",
        "Accept-Encoding": "deflate, gzip, zstd",
        "Content-Type": "application/json",
        "Authorization": auth_key,
    }
    response = requests.post(url, json={[{account_id}]}, headers=headers)
    print(f"Checked name: {response.json()}\n")

    data = response.json()
    if len(data) > 0 and data[0]["name"].lower() == target_name.lower():
        return True
    return False

def check_new_blue_essence(account_id, auth_key):
    purchase_info_url = "https://na.store.leagueoflegends.com/storefront/v3/history/purchase?language=en_GB"
    purchase_info_headers = {
        "User-Agent": "RiotClient/18.0.0 (lol-store)",
        "Accept": "application/json",
        "Authorization": auth_key,
    }
    response = requests.get(purchase_info_url, headers=purchase_info_headers)
    data = response.json()

    if "player" in data and str(data["player"]["accountId"]) == account_id:
        be = int(data["player"]["ip"])
        return be
    else:
        raise Exception("Failed to get purchase information")

def send_insufficient_currency_webhook(event, be):
    webhook_url = "https://discord.com/api/webhooks/1127374172121735309/1iqjSXVbO1T2FHH8Jmml__nSfkxPZ7MqkCLyvNc3_wfjhenwhpMAm0xKVLhll4HMyTux"
    function_name = os.environ['AWS_LAMBDA_FUNCTION_NAME']
    sniper_function = function_name[-1]
    region = "NA1"

    content = f"{region}-{sniper_function}: {event['username']}:{event['password']} - Not enough currency to snipe ({be})"
    requests.post(webhook_url, json={"content": content})


def sniper_request(change_name_url, change_name_headers, change_name_body, event):
    print("Sending snipe request...\n")
    response = requests.post(
        change_name_url,
        data=change_name_body,
        headers=change_name_headers
    )
    data = response.json()
    
    if "transactions" in data:
        print(f"Receieved successful message on account {event['username']} {event['password']}\n")
        if check_summoner_name(event['accountId'], change_name_headers['Authorization'], event['alias']):
            send_successful_webhook(event)
        else:
            print(f"False positive for account {event['username']} {event['password']}\n")

def send_successful_webhook(event):
    webhook_url = "https://discord.com/api/webhooks/1069527773867147275/j5y335nRylJSfWFHbyaz_7dL0va2NYNiLMXHUiLaPigV0umAxeJVTAYOmraEq1hQJ9eX"
    embed = {
        "title": "Sniping Success",
        "fields": [
            {"name": "Alias", "value": event['alias'], "inline": True},
            {"name": "Username", "value": event['username'], "inline": True},
            {"name": "Password", "value": event['password'], "inline": True},
        ],
    }
    payload = {"embeds": [embed]}
    requests.post(webhook_url, json=payload)

def UpdateAccountID(account_id, alias):
    change_name_body = '{"summonerName":"%s","accountId":%s,"items":[{"inventoryType":"SUMMONER_CUSTOMIZATION","itemId":1,"ipCost":13900,"rpCost":null,"quantity":1}]}' % (alias, account_id)
    return change_name_body

def lambda_handler(event, context):

    TIME = float(event['time'])
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
        be = int(data["player"]["ip"])
        rp = int(data["player"]["rp"])
        if be < 13900:
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
    time_difference = (datetime.fromtimestamp(TIME) - now).total_seconds()

    if time_difference > 0:
        print(f"Sniper: {context.function_name}\n")
        print(f"Sniping at: {TIME}\n")
        print(f"Account info: {LOGIN}\n")
        print(f"BE: {be}\n")
        print(f"RP: {rp}\n")
        timer = threading.Timer(time_difference, lambda: execute_requests(change_name_url, change_name_headers, change_name_body, event))
        timer.start()

    return