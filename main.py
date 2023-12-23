from flask import Flask, request, jsonify
from oandapyV20 import API
import oandapyV20.endpoints.orders as orders
import oandapyV20.endpoints.positions as positions

app = Flask(__name__)

import configparser

# Create a ConfigParser object
config = configparser.ConfigParser()

# Read the configuration file
config.read('config.ini')

# Access the API credentials
account_id = config.get('API', 'account_id')
access_token = config.get('API', 'access_token')

api = API(access_token=access_token)


@app.route('/webhook', methods=['POST'])
def trade():
    request_data = request.get_json()

    for item in request_data:
        symbol = item.get("symbol")
        units = item.get("units")
        side = item.get("side")
        exit_position = item.get("exit")

        if exit_position and exit_position == "true":
            # Fetch the open positions for the symbol
            open_positions = positions.PositionDetails(accountID=account_id, instrument=symbol)
            response = api.request(open_positions)

            # Check if there are any open positions
            if response['position']['long']['units'] != '0':
                # Close long position
                units_to_close = -int(response['position']['long']['units'])
                data = {
                    "order": {
                        "timeInForce": "FOK",
                        "instrument": symbol,
                        "units": str(units_to_close),
                        "type": "MARKET",
                        "positionFill": "REDUCE_ONLY"
                    }
                }
                order = orders.OrderCreate(accountID=account_id, data=data)
                api.request(order)

            if response['position']['short']['units'] != '0':
                # Close short position
                units_to_close = -int(response['position']['short']['units'])
                data = {
                    "order": {
                        "timeInForce": "FOK",
                        "instrument": symbol,
                        "units": str(units_to_close),
                        "type": "MARKET",
                        "positionFill": "REDUCE_ONLY"
                    }
                }
                order = orders.OrderCreate(accountID=account_id, data=data)
                api.request(order)

        else:
            # Place buy or sell order
            units = units if side == "buy" else f"-{units}"
            data = {
                "order": {
                    "timeInForce": "FOK",
                    "instrument": symbol,
                    "units": units,
                    "type": "MARKET",
                    "positionFill": "DEFAULT"
                }
            }
            order = orders.OrderCreate(accountID=account_id, data=data)
            api.request(order)

    return jsonify({"status": "success"})


if __name__ == '__main__':
    app.run(debug=True)
