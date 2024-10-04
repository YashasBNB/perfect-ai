import time
from iqoptionapi.stable_api import IQ_Option

# Initialize your IQ Option credentials
email = "yashasnaidu3@gmail.com"  # Replace with your IQ Option email
password = "King@2005"  # Replace with your IQ Option password

# Create an IQ Option instance and log in
iq = IQ_Option(email, password)
iq.connect()

# Check if the connection was successful
if not iq.check_connect():
    print("Failed to connect to IQ Option")
    exit()

# Switch to demo balance
iq.change_balance('PRACTICE')  # Ensure the balance is set to demo mode
print("Successfully connected to IQ Option in demo mode.")

# Function to place a trade
def place_trade(asset, direction, amount, expiry_time):
    try:
        # Place a digital options trade
        check, trade_id = iq.buy_digital_spot(asset, amount, direction, expiry_time)
        if check:
            print(f"Trade placed successfully. Trade ID: {trade_id}")
            return True
        else:
            print("Failed to place trade.")
            return False
    except Exception as e:
        print(f"Error placing trade: {e}")
        return False

# Function to check the current balance
def get_balance():
    return iq.get_balance()

# Main function for trading based on balance comparison
def balance_based_trading(asset, direction, amount, expiry_time, num_trades):
    initial_balance = get_balance()
    print(f"Initial balance: {initial_balance}")

    for trade_num in range(1, num_trades + 1):
        print(f"Starting trade number {trade_num}")

        # Place a trade
        if place_trade(asset, direction, amount, expiry_time):
            print(f"Trade {trade_num} placed, waiting for trade to expire...")

            # Wait for 2 minutes (120 seconds) to check the balance after the trade
            time.sleep(120)

            # Check the new balance
            new_balance = get_balance()
            print(f"New balance after trade {trade_num}: {new_balance}")

            # Calculate profit or loss
            profit_or_loss = new_balance - initial_balance
            if profit_or_loss > 0:
                print(f"Trade {trade_num} was profitable. Profit: {profit_or_loss}")
            elif profit_or_loss < 0:
                print(f"Trade {trade_num} resulted in a loss. Loss: {abs(profit_or_loss)}")
            else:
                print(f"Trade {trade_num} broke even.")

            # Update the initial balance for the next trade
            initial_balance = new_balance

            # Wait 10 seconds before placing the next trade
            print("Waiting 10 seconds before the next trade...")
            time.sleep(10)
        else:
            print(f"Trade {trade_num} failed to place, skipping to next trade.")

# Example usage
asset = "EURUSD"  # Replace with your desired asset
direction = "call"  # Choose either "call" for buy or "put" for sell
amount = 1  # Adjust the amount as needed
expiry_time = 1  # Expiry time in minutes (validated by the system)
num_trades = 5  # Number of trades to perform

# Start trading based on balance comparison
balance_based_trading(asset, direction, amount, expiry_time, num_trades)
