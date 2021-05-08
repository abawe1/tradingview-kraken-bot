# place main packages in requirements.txt
# e.g. in 'from pykrakenapi import KrakenAPI', add 'pykrakenapi'

import requests, json
from chalice import Chalice
from chalicelib import config
import krakenex
from pykrakenapi import KrakenAPI
import pandas as pd
import time

# 1. "pip install virtualenv"
# 2. "virtualenv bot-env"
# 3. "source ~/.bot-env/bin/activate"
# 4. "chalice new-project broker-bot-asset" to create a uniqute rest api url

# ----------------------------------------------------------------------------

# ----------------------------------------------------------------------------
# 6. copy/paste app.py, the chalicelib folder and requirements.txt
# 7. adjust volume for specific asset
# 8. deploy

# ----------------------------------------------------------------------------

# Check Postman & AWS Cloudwatch logs for server errors

app = Chalice(app_name='kraken-bot-ethusd')


kraken = krakenex.API()
k = KrakenAPI(kraken)


# public and private keys
# kraken.key file recognized in chalicelib for some reason...
kraken.load_key('chalicelib/kraken.key')


# POST request to export kraken reports
# send request and download from the history in the web browser (contains additional info, such as net)
# start time is entered manually as a UNIX timestamp
@app.route('/exportreport', methods=['POST'])
def exportreport():
    resp = kraken.query_private('AddExport',
                    {"nonce": str(int(1000*time.time())),
                    "description":"my_trades_1",
                    "format":"CSV",
                    "report":"trades",
                    "starttm":"1617402320"})
    return(resp.json())



@app.route('/main', methods=['POST'])
def main():
    # information about the tradingview request
    # incoming post request
    # convert data to json string 
    webhook_message = app.current_request.json_body

    if 'passphrase' not in webhook_message:
        return {
            "code": "error",
            "message": "Unauthorized, no passphrase"
        }

    if webhook_message['passphrase'] != config.passphrase:
        return {
            "code": "error",
            "message": "Invalid passphrase"
        }


    # set volume manually for the base asset
    # Base Asset: ETH
    # Leverage Quote Asset: USD
    # "type" refers to buy/sell
    # 0.007372048 * 5 = 0.03686024($100)

    # for leverage only
    kraken.query_private('OpenPositions',
                        {"consolidation": "market"})

    kraken.query_private('AddOrder',
                        {"pair": webhook_message["pair"],
                        "type": webhook_message["type"],
                        "ordertype": "market",
                        "volume": "0.03686024",
                        "leverage": "5"
                        })

    # for leverage only
    kraken.query_private('OpenPositions',
                        {"consolidation": "market"})


if __name__ == '__main__':
    order = main()
    print(order)

    
# ----------------------------------------------------------------------------

# sample tradingview alert message
# {
#     "pair": "{{ticker}}",
#     "type": "{{strategy.order.action}}",
#     "passphrase": "abc"
# }


# test payload
# {
#     "pair": "ETHUSD",
#     "type": "sell",
#     "passphrase": "abc"
# }


# tradingview testing
# curl -H 'Content-Type: application/json; charset=utf-8' -d '{"pair":"ETHUSDC","type":"buy","passphrase":"abc"}' -X POST localhost:8000/main
# curl -X POST localhost:8000/exportreport

# kraken trading minimums
# ETH  	0.005
# XBT  	0.0002
# 
# XDG  	50
# UNI  	1


# curl "https://api.kraken.com/0/public/AssetPairs?pair=XXBTZUSD,XETHXXBT"
