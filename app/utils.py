from decimal import Decimal

import pandas as pd

from app.models import VitexAccount


class Variables:
    start_trading = 1547647441
    year_ago = 1584705600
    end_date = 1621094485  # 1616355904  # 21 March 2021
    event_timestamp = 1615530744  # 12 March 2021
    trading_pair = "EPIC-001_BTC-000"
    eiou_multiplier = Decimal(0.5)


VARS = Variables.__dict__


def orders_processor(orders):
    # -----------------------------------------#
    # Define filters and process exchange data #
    # -----------------------------------------#
    df = pd.DataFrame(orders)

    bought = df.side == "Buy"
    sold = df.side == "Sell"
    total_buy = round(sum(df[bought].quantity), 2)
    total_sold = round(sum(df[sold].quantity), 2)

    buy_value = round(sum(df[bought].amount), 2)
    sold_value = round(sum(df[sold].amount), 2)

    buy_value_usd = round(sum(df[bought].usd_value), 2)
    sold_value_usd = round(sum(df[sold].usd_value), 2)

    balance = Decimal(total_buy - total_sold)
    balance_usd = Decimal(buy_value_usd - sold_value_usd)

    return {
        'total_buy': total_buy,
        'total_sold': total_sold,
        'buy_value': buy_value,
        'sold_value': sold_value,
        'buy_value_usd': buy_value_usd,
        'sold_value_usd': sold_value_usd,
        'balance': balance,
        'balance_usd': balance_usd,
        }

"""
# ---------------------------------------#
    # Define filters and process wallet data #
    # ---------------------------------------#
    epic_001, epic_002 = transactions
    wallet_df = pd.DataFrame(epic_001)
    sent = wallet_df.transactionType == "Sent"
    received = wallet_df.transactionType == "Recieved"
    time = wallet_df.datetime < VARS['event_timestamp']
    end_time = wallet_df.datetime < VARS['end_date']

    # Calculate balance before event date
    e_total_sent = round(sum(wallet_df[sent & time].decimalAmount), 2)
    e_total_received = round(sum(wallet_df[received & time].decimalAmount), 2)
    wallet_history_balance = int(e_total_received + e_total_sent)

    # Calculate balance for 21 March
    total_sent = round(sum(wallet_df[sent & end_time].decimalAmount), 2)
    total_received = round(sum(wallet_df[received & end_time].decimalAmount), 2)
    wallet_today_balance = int(total_received + total_sent)

    # EPIC-002 RECEIVED
    epic_002_received = int(epic_002['decimalAmount'])

    # Balance difference between event day and 21 March
    tokens_difference = abs(wallet_today_balance - epic_002_received)

"""