import time
import csv
import os
from datetime import datetime, timedelta
from iqoptionapi.stable_api import IQ_Option
import MetaTrader5 as mt5

# Initialize IQ Option and MetaTrader credentials
email = "yashasnaidu3@gmail.com"
password = "King@2005"
MT5_ACCOUNT = "86342017"
MT5_PASSWORD = "3@BdTaVs"
MT5_SERVER = "MetaQuotes-Demo"

# Create an IQ Option instance and log in
iq = IQ_Option(email, password)
iq.connect()

# Check if the connection was successful
if not iq.check_connect():
    print("Failed to connect to IQ Option")
    exit()
iq.change_balance('PRACTICE')
print("Connected to IQ Option in demo mode.")

# Initialize MetaTrader
if not mt5.initialize():
    print("Failed to initialize MetaTrader5")
    exit()
if not mt5.login(int(MT5_ACCOUNT), MT5_PASSWORD, MT5_SERVER):
    print("Failed to login to MetaTrader5")
    exit()

# Function to fetch available binary options (excluding OTC)
def fetch_available_binary_options():
    all_assets = iq.get_all_open_time()
    binary_options = {"turbo": [], "binary": []}
    for asset_type, assets in all_assets.items():
        if asset_type in ["binary", "turbo"]:
            for asset, details in assets.items():
                if details['open'] and "OTC" not in asset:
                    binary_options[asset_type].append(asset)
    return binary_options

# Fetch and print available binary options excluding OTC
binary_options = fetch_available_binary_options()
print("Available binary options (excluding OTC):", binary_options)

# Fetch historical data
def fetch_historical_data(asset, timeframe, num_bars):
    return mt5.copy_rates_from_pos(asset, timeframe, 0, num_bars)

# Save data to CSV
def save_to_csv(asset, data, timeframe):
    os.makedirs('historical_data', exist_ok=True)
    filename = f'historical_data/{asset}_historical_data_{timeframe}.csv'
    with open(filename, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['Asset', 'Time', 'Open', 'High', 'Low', 'Close', 'Tick_volume', 'Spread', 'Real_volume'])
        for row in data:
            writer.writerow([asset] + list(row))

# Update historical data, removing data older than 1 month
def update_historical_data(asset, timeframe, num_bars):
    filename = f'historical_data/{asset}_historical_data_{timeframe}.csv'
    data = fetch_historical_data(asset, timeframe, num_bars)
    if data is None or len(data) == 0:
        print(f"Failed to fetch historical data for {asset}")
        return False

    current_time = datetime.now()
    one_month_ago = current_time - timedelta(days=30)
    updated_data = [row for row in data if datetime.fromtimestamp(row[0]) > one_month_ago]
    
    save_to_csv(asset, updated_data, timeframe)
    return True

# Fetch live data
def fetch_live_data(asset, timeframe):
    data = fetch_historical_data(asset, timeframe, 1)
    if data is None or len(data) == 0:
        print(f"Failed to fetch live data for {asset}")
        return False
    print(f"Fetched live data for {asset}: {data[-1]}")
    return True

# Save available assets to a file for the other script to read
def save_available_assets(assets_available_to_trade):
    with open('available_assets.txt', 'w') as file:
        for asset in assets_available_to_trade:
            file.write(f"{asset}\n")

# Main loop
num_bars_1m = 43200
num_bars_1h = 720

while True:
    assets_failed_to_download = []
    assets_available_to_trade = []

    for asset in set(binary_options['turbo'] + binary_options['binary']):
        print(f"\nProcessing {asset}...")

        # Flags for tracking
        historical_success = True
        live_success = True

        # Update 1-minute historical data
        if update_historical_data(asset, mt5.TIMEFRAME_M1, num_bars_1m):
            print(f"1-minute historical data for {asset} updated successfully.")
        else:
            print(f"Skipping {asset} for 1-minute historical data due to fetch failure.")
            historical_success = False

        # Update 1-hour historical data
        if update_historical_data(asset, mt5.TIMEFRAME_H1, num_bars_1h):
            print(f"1-hour historical data for {asset} updated successfully.")
        else:
            print(f"Skipping {asset} for 1-hour historical data due to fetch failure.")
            historical_success = False

        # Fetch live data every 2 minutes
        if fetch_live_data(asset, mt5.TIMEFRAME_M1):
            print(f"Live data for {asset} fetched successfully.")
        else:
            print(f"Skipping {asset} for live data due to fetch failure.")
            live_success = False

        # Track assets based on success
        if historical_success and live_success:
            assets_available_to_trade.append(asset)
        else:
            assets_failed_to_download.append(asset)

    # Save assets that are available for trading to a file
    save_available_assets(assets_available_to_trade)

    # Summary of trading availability
    print("\nSummary of asset availability:")
    if assets_available_to_trade:
        print("Assets available for trading:")
        for asset in assets_available_to_trade:
            print(f" - {asset}")
    if assets_failed_to_download:
        print("\nAssets unavailable due to missing data:")
        for asset in assets_failed_to_download:
            print(f" - {asset}")

    # Sleep to respect update intervals
    print("Sleeping for 1 minute...")
    time.sleep(25)

# Shutdown MetaTrader
mt5.shutdown()
