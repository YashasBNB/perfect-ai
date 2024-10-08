# Import libraries
import os

# File path (adjust if you saved the file in a different location)
assets_file = "available_assets.txt"

# Check if the file exists
if not os.path.exists(assets_file):
    print(f"File '{assets_file}' not found. Make sure the main script creates it.")
    exit()

# Open the file for reading
with open(assets_file, "r") as file:
    # Read lines and print available assets
    print("Available assets for trading:")
    for line in file:
        asset = line.strip()  # Remove trailing newline character
        print(f"- {asset}")