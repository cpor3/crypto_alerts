import os
from ccxt.ftx import ftx

def ftx_init(sub_account: str = None):
    ftx_exchange = ftx({
        'apiKey': os.environ.get('API_KEY'),
        'secret': os.environ.get('SECRET_KEY'),
        'enableRateLimit': True
    })

    if sub_account is not None:
        ftx_exchange.headers = {
            "FTX-SUBACCOUNT": sub_account
        }

    return ftx_exchange

def get_ftx_balance(ftx_exchange):
    balance = ftx_exchange.fetch_balance()

    return balance['USD']
