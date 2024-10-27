from pybit.unified_trading import HTTP
from time import sleep

# Define API credentials directly in the main file
api = "5woBX33GF7OxgI7ACf"
secret = "R3UDsEfwFhhUQwJOIThvitHy5z6Xut08Ebb4"

# Initialize session
session = HTTP(
    api_key=api,
    api_secret=secret
)

accountType = "UNIFIED"

# Your trading logic here
# Example: Make a simple request to verify the connection
try:
    response = session.get_account_info()
    print(response)
except Exception as e:
    print(f"An error occurred: {e}")
# Config
mode = 0  # 1 - Isolated, 0 - Cross


# Cancel remaining orders
def cancel_remaining_orders(symbol):
    try:
        open_orders = session.get_open_orders(category='linear', symbol=symbol)['result']['list']
        if not open_orders:
            print(f"No open orders to cancel for {symbol}.")
            return

        for order in open_orders:
            session.cancel_order(orderId=order['orderId'], category='linear', symbol=symbol)
            print(f"Canceled order {order['orderId']} for {symbol}.")
        print(f"Canceled remaining orders for {symbol}.")
    except Exception as err:
        print(f"Error canceling orders for {symbol}: {err}")


# Get current price for the symbol
def get_current_price(symbol):
    try:
        ticker = session.get_tickers(category='linear')['result']['list']
        for item in ticker:
            if item['symbol'] == symbol:
                return float(item['lastPrice'])
    except Exception as err:
        print(f"Error fetching current price for {symbol}: {err}")
    return None


# Monitoring positions
def monitor_positions():
    monitored_symbols = set()  # To keep track of symbols being monitored

    while True:
        try:
            # Get current positions
            positions = session.get_positions(category='linear', settleCoin='USDT')['result']['list']

            for pos in positions:
                symbol = pos['symbol']
                size = float(pos['size'])  # Convert size to float for comparison
                if size > 0 and symbol not in monitored_symbols:  # Only monitor if position size is greater than 0
                    monitored_symbols.add(symbol)
                    print(f"Monitoring position for {symbol}")

            # Check if any monitored position is closed
            for symbol in list(monitored_symbols):  # Create a list to avoid modifying the set while iterating
                open_positions = [pos for pos in positions if pos['symbol'] == symbol and float(pos['size']) > 0]
                if not open_positions:  # No open positions means the position is closed
                    print(f"Position closed for {symbol}. Canceling remaining orders.")
                    cancel_remaining_orders(symbol)
                    monitored_symbols.remove(symbol)  # Remove the symbol from monitored symbols
                else:
                    # Fetch and display current price, TP price, average entry price, and SL price
                    current_price = get_current_price(symbol)
                    tp_price = float(open_positions[0]['takeProfit']) if 'takeProfit' in open_positions[0] and \
                                                                         open_positions[0]['takeProfit'] not in [None,
                                                                                                                 ''] else None

                    # Debugging: Print the entire open position for inspection
                    #print(f"Open position data for {symbol}: {open_positions[0]}")

                    # Correctly get the average entry price
                    avg_entry_price = (
                        float(open_positions[0].get('avgPrice', 0))
                        if 'avgPrice' in open_positions[0] and open_positions[0]['avgPrice'] not in [None, '']
                        else None
                    )
                    sl_price = float(open_positions[0].get('stopLoss', 0)) if 'stopLoss' in open_positions[0] and \
                                                                              open_positions[0]['stopLoss'] not in [
                                                                                  None, ''] else None

                    # Display information
                    print("---------------------------------------------\n"
                          f"Current price for {symbol}: {current_price}, "
                          f"TP price: {tp_price}, "
                          f"Average Entry Price: {avg_entry_price if avg_entry_price is not None else 'Not set'}, "
                          f"SL price: {sl_price if sl_price is not None else 'Not set'}")

            # Log current monitored positions for debugging
            #print(f"Current monitored positions: {monitored_symbols}. Checking again...")
            #print("______________________________________________________________________")
            sleep(5)  # Wait before checking again

        except Exception as err:
            print(f"Error monitoring positions: {err}")


def main():
    monitor_positions()


if __name__ == "__main__":
    main()
