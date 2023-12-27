from flask import Flask, request, jsonify
from oandapyV20 import API
import oandapyV20.endpoints.orders as orders
import oandapyV20.endpoints.positions as positions
import logging
import configparser
from logging.handlers import RotatingFileHandler

app = Flask(__name__)
# Logging Configuration
log_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

log_file = 'server.log'

file_handler = RotatingFileHandler(log_file, maxBytes=1024 * 1024 * 100, backupCount=10)
file_handler.setFormatter(log_formatter)
file_handler.setLevel(logging.INFO)
app.logger.setLevel(logging.INFO)

app.logger.addHandler(file_handler)


config = configparser.ConfigParser()

# Read the configuration file
config.read('config.ini')

# Access the API credentials
account_id = config.get('API', 'account_id')
access_token = config.get('API', 'access_token')

api = API(access_token=access_token)


@app.route('/webhook', methods=['POST'])
def trade():
    app.logger.info("Webhook hit with a request")  # Log at the start of the function

    try:
        request_data = request.get_json()
        app.logger.info(f"Received request data: {request_data}")

        for item in request_data:
            symbol = item.get("symbol")
            units = item.get("units")
            side = item.get("side")
            exit_position = item.get("exit")

            if exit_position and exit_position == "true":
                # Fetch the open positions for the symbol
                open_positions = positions.PositionDetails(accountID=account_id, instrument=symbol)
                response = api.request(open_positions)
                app.logger.info(f"OpenPosition function executed successfully.{response}")

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
                    req = api.request(order)
                    app.logger.info(f"Trade function executed successfully.{req}")

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
                    req = api.request(order)
                    app.logger.info(f"Trade function executed successfully.{req}")


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
                req =api.request(order)
                app.logger.info(f"Trade function executed successfully.{req}")

        return jsonify({"status": "success"})
    except Exception as e:
        app.logger.error(f"An error occurred: {e}",exe_info=True)
        return jsonify({"status": "error", "message": str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True,host="0.0.0.0",port=80)
