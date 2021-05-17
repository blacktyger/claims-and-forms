from decimal import Decimal

import Coinpaprika
from datetime import datetime, timezone
import pandas as pd
import ciso8601
import requests
import random
import time

from app.utils import VARS

client = Coinpaprika.Client()


# -----------------------------------------------------#
# Code here is responsible for connection to ViteX API #
# It's mix of my code and code from here:              #
# https://github.com/theMoe/vite/tree/main/004_vitetxs #
# -----------------------------------------------------#


def get_exchange_orders(viteAddress, limit, filterTime, side, symbol, status):
    """ Connect to ViteX API and save to CSV exchange orders """
    # https://vite.wiki/dex/api/dex-apis.html#get-orders
    url = 'https://api.vitex.net/api/v2/orders'
    status_parser = {
        0: 'Unknown', 1: 'Pending', 2: 'Received',
        3: 'Open', 4: 'Filled', 5: 'Partially Filled',
        6: 'Pending Cancel', 7: 'Cancelled', 8: 'Partially',
        9: 'Failed', 10: 'Expired'}

    side_parser = {0: 'Buy', 1: 'Sell'}

    # Prepare all query parameters to get API response
    params = {
        'address': viteAddress,
        'limit': limit,
        'startTime': filterTime[0],
        'endTime': filterTime[1],
        'side': side, 'symbol': symbol,
        'quoteTokenSymbol': symbol.split('_')[1].strip('_'),
        'tradeTokenSymbol': symbol.split('_')[0].strip('_'),
        'status': status
        }

    # Empty list, we will add all matching orders here
    orders = []
    for_balance = []

    # Send our prepared query to ViteX API
    response = requests.get(url=url, params=params)
    if response.status_code == 200:
        # Check for any errors in API response
        resp = response.json()
        if resp['code'] != 0:
            return {'errorMsg': resp['msg']}
        elif 'data' not in resp:
            return {'errorMsg': 'No data received from exchange'}
        elif 'order' not in resp['data']:
            return {'errorMsg': 'No orders received from exchange'}
        else:

            # Download historical Bitcoin price in USD to calculate orders value,
            # data provided by Coinpaprika API <3
            btc_prices = client.tickers.historical_ticker_for_coin(
                coin_id="btc-bitcoin",
                start=datetime.fromtimestamp(VARS['event_timestamp']),
                end=datetime.fromtimestamp(filterTime[1]),
                interval="1h",
                limit=1000
                )

            # Change date string to UNIX timestamp in bitcoin_prices data
            for item in btc_prices:
                item['timestamp'] = time.mktime(ciso8601.parse_datetime(str(item['timestamp'])).timetuple())
            btc_prices = {x['timestamp']: x['price'] for x in btc_prices}
            print('btc_prices downloaded')

            # Iterate through API response orders, create order dictionary,
            # change status and time to human readable form and add to our list
            for order in resp['data']['order']:
                if order['status'] in [4, 5]:
                    order_dict = {key: value for key, value in order.items()}
                    order_dict['status'] = status_parser[order_dict['status']]
                    order_dict['timestamp'] = order_dict['createTime']
                    order_dict['createTime'] = datetime. \
                        fromtimestamp(int(order_dict['createTime'])).strftime('%d/%m/%Y %H:%M')
                    order_dict['side'] = side_parser[order_dict['side']]
                    order_dict['quantity'] = float(order_dict['executedQuantity'])
                    order_dict['amount'] = round(float(order_dict['executedAmount']), 6)

                    # Find timestamp closest to time of event in our bitcoin_prices list and calculate
                    # order value in USD
                    closest_timestamp = min(
                        list(btc_prices.keys()), key=lambda x: abs(x - int(order_dict['timestamp'])))
                    btc_price = btc_prices[closest_timestamp]
                    order_dict['usd_value'] = round(float(btc_price * order_dict['amount']), 1)
                    orders.append(order_dict)
    else:
        return {'errorMsg': response.status_code}

    return orders


def get_rollback_transaction(viteAddress):
    """ Search for first EPIC-002 transaction - this is 'rollback tx' """

    backupIP = ['170.106.33.134', '150.109.116.1', '150.109.51.8']

    def getHeader():
        header = {
            'Cache-Control': 'no-cache',
            'Content-Type': 'application/json'
            }
        return header

    def getBody(viteAddr, pg, transPerRequest):
        body = {
            'jsonrpc': '2.0',
            'id': 2,
            'method': 'ledger_getAccountBlocksByAddress',
            'params': [viteAddr, pg, transPerRequest]
            }
        return body

    def tryIP(ip):
        url = getURL(ip)
        header = getHeader()
        body = {
            'jsonrpc': '2.0',
            'id': 2,
            'method': 'ledger_getSnapshotChainHeight',
            'params': None
            }
        try:
            response = requests.post(url=url, json=body, headers=header, timeout=2)
            if response.status_code == 200:
                return True
            else:
                return False
        except:
            return False

    def getNodeIP():
        localIP = backupIP.copy()
        random.shuffle(localIP)
        for ip in localIP:
            if tryIP(ip):
                print('Connecting to VITEX node IP: ' + ip)
                return ip
            else:
                print('bad backIP ' + ip)

        urlReward = 'https://rewardapi.vite.net/reward/full/real?cycle='
        cycle_incomplete = int((datetime.timestamp(datetime.now()) - 1558411200) / 24 / 3600)
        url = urlReward + str(cycle_incomplete)
        response = requests.get(url=url)

        if response.status_code == 200:
            resp = response.json()
            if resp['msg'] == 'success':
                for result in resp['data']:
                    if result['onlineRatio'] == 1.0:
                        if tryIP(result['ip']):
                            print('good ip ' + result['ip'])
                            return result['ip']
                        else:
                            print('bad ip ' + result['ip'])
        return False

    def getURL(ip):
        return 'http://' + ip + ':48132'

    nodeIP = getNodeIP()

    if not nodeIP:
        print('Connection ERROR...')
        return {'errorMsg': 'Connection error...'}

    url = getURL(nodeIP)
    header = getHeader()
    body = getBody(viteAddress, None, 8000)
    EPIC_002 = 'tti_f370fadb275bc2a1a839c753'
    txs = []

    try:
        response = requests.post(url=url, json=body, headers=header)
        print('Downloading data...')
        if response.status_code == 200:
            resp = response.json()
            if resp['result'] is None:
                print('Last requested page has no transaction results.')

            for result in resp['result']:
                if result['tokenInfo'] is not None \
                    and result['tokenInfo']['tokenId'] == EPIC_002:

                    amount = int(result['amount'])
                    decimals = int(result['tokenInfo']['decimals'])
                    decimal_amount = (amount / 10 ** decimals)
                    txs.append(Decimal(decimal_amount))
                    # print(decimal_amount)
            try:
                return txs[-1]

            except IndexError:
                return False
        else:
            print(response.status_code)

    except Exception as e:
        print(e)
        return {'errorMsg': 'Exception during request.'}
