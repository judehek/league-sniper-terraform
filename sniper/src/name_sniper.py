import asyncio
import requests
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from aiohttp import ClientSession
import os

import riot_auth
#todo:set icon, check last played match, test cases, webserver for managing accounts + deletion
async def execute_requests(change_name_url, change_name_headers, change_name_body, event, account_id):
    max_requests = 25
    print(f"Executing requests...\n")

    tasks = [sniper_request(i, change_name_url, change_name_headers, change_name_body, event, account_id) for i in range(max_requests)]
    await asyncio.gather(*tasks)

async def check_summoner_name(auth_key, target_name):
    print("Checking name...\n")
    url = "https://auth.riotgames.com/userinfo"
    headers = {
        "Authorization": auth_key,
    }

    async with ClientSession() as session:
        async with session.get(url, headers=headers) as response:
            data = await response.json()

    print(f"Checked name: {data}\n")

    if data["lol_account"]["summoner_name"].lower() == target_name.lower():
        return True
    return False

async def check_new_blue_essence(account_id, auth_key):
    purchase_info_url = "https://na.store.leagueoflegends.com/storefront/v3/history/purchase?language=en_GB"
    purchase_info_headers = {
        "User-Agent": "RiotClient/18.0.0 (lol-store)",
        "Accept": "application/json",
        "Authorization": auth_key,
    }
    async with ClientSession() as session:
        async with session.get(purchase_info_url, headers=purchase_info_headers) as response:
            data = await response.json()

    if "player" in data and str(data["player"]["accountId"]) == account_id:
        be = int(data["player"]["ip"])
        return be
    else:
        raise Exception("Failed to get purchase information")

async def send_insufficient_currency_webhook(event, be):
    webhook_url = "https://discord.com/api/webhooks/1127374172121735309/1iqjSXVbO1T2FHH8Jmml__nSfkxPZ7MqkCLyvNc3_wfjhenwhpMAm0xKVLhll4HMyTux"
    function_name = os.environ['AWS_LAMBDA_FUNCTION_NAME']
    sniper_function = function_name.rpartition('-')[-1]
    region = "NA1"

    content = f"{region}-{sniper_function}: {event['username']}:{event['password']} - Not enough currency to snipe ({be})"
    requests.post(webhook_url, json={"content": content})


async def sniper_request(request_id, change_name_url, change_name_headers, change_name_body, event, account_id):
    print(f"[{request_id}] Sending snipe request {request_id}: {datetime.now()}\n")
    async with ClientSession() as session:
        async with session.post(
            change_name_url,
            data=change_name_body,
            headers=change_name_headers
        ) as response:
            data = await response.json()

    if "transactions" in data:
        print(f"Received successful message on request: {request_id} for account: {event['username']}:{event['password']}\n")
        if await check_summoner_name(change_name_headers['Authorization'], event['alias']):
            print(f"Successful message was not a false positive on request: {request_id} and account: {event['username']}:{event['password']}\n")
            await send_successful_webhook(event)
        else:
            print(f"False positive for request {request_id} and account: {event['username']}:{event['password']}\n")
        be = await check_new_blue_essence(account_id, change_name_headers['Authorization'])
        if be < 13900:
            print(f"Account blue essence is too low for request: {request_id} and account: {event['username']}:{event['password']}\n")
            await send_insufficient_currency_webhook(event, be)
    

async def send_successful_webhook(event):
    webhook_url = "https://discord.com/api/webhooks/1069527773867147275/j5y335nRylJSfWFHbyaz_7dL0va2NYNiLMXHUiLaPigV0umAxeJVTAYOmraEq1hQJ9eX"
    embed = {
        "title": "Sniping Success",
        "fields": [
            {"name": "Name", "value": event['alias'], "inline": False},
            {"name": "Username", "value": event['username'], "inline": True},
            {"name": "Password", "value": event['password'], "inline": True},
        ],
        "footer": {
        "text": os.environ['AWS_LAMBDA_FUNCTION_NAME']
      }
    }
    payload = {"embeds": [embed]}
    requests.post(webhook_url, json=payload)

def update_account_id(account_id, alias):
    change_name_body = '{"summonerName":"%s","accountId":%s,"items":[{"inventoryType":"SUMMONER_CUSTOMIZATION","itemId":1,"ipCost":13900,"rpCost":null,"quantity":1}]}' % (alias, account_id)
    return change_name_body

async def main(event, context):

    TIME = float(event['time'])
    LOGIN = event['username'], event['password']

    auth = riot_auth.RiotAuth()
    auth.RIOT_CLIENT_USER_AGENT = "RiotClient/62.0.1.4852117.4789131 %s (Windows;10;;Professional, x64)"

    await auth.authorize(*LOGIN)
    
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
            await send_insufficient_currency_webhook(event, be)
            raise Exception("Not enough BE")
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

    change_name_body = update_account_id(account_id, event['alias'])

    now = datetime.now()
    time_difference = (datetime.fromtimestamp(TIME) - now).total_seconds()

    if time_difference > 870:
        print(f"Wrong name, time difference is: {time_difference} seconds")
        return
    if time_difference > 0:
        print(f"Sniper: {context.function_name}")
        print(f"Sniping at: {TIME}\n")
        print(f"Account info: {LOGIN[0]}:{LOGIN[1]}\n")
        print(f"BE: {be}\n")
        print(f"RP: {rp}\n")
        print(f"SNIPING: {event['alias']}\n")
        print(f"Starting timer for: {time_difference} seconds.\n")
        await asyncio.sleep(time_difference)
        await execute_requests(change_name_url, change_name_headers, change_name_body, event, account_id)
    return

def lambda_handler(event, context):
    asyncio.run(main(event, context))
    return