import pandas as pd
import numpy as np
import os

# Specify the base directory where your data files are located
base_directory = r'C:\Users\yasha\OneDrive\Desktop\trading-ai'

# Load historical data
def load_historical_data(asset):
    historical_file = os.path.join(base_directory, 'historical_data', f'{asset}_historical_data_1m.csv')
    return pd.read_csv(historical_file)

# Calculate indicators
def calculate_indicators(data):
    data['MA20'] = data['Close'].rolling(window=20).mean()  # 20-period Moving Average
    data['MA50'] = data['Close'].rolling(window=50).mean()  # 50-period Moving Average
    data['RSI'] = compute_rsi(data['Close'], 14)  # 14-period RSI
    data['MACD'], data['Signal_Line'] = compute_macd(data['Close'])  # MACD Indicator
    data['ATR'] = compute_atr(data)  # Average True Range (volatility indicator)
    data['Upper_BB'], data['Lower_BB'] = compute_bollinger_bands(data['Close'], 20)  # Bollinger Bands
    data['Stochastic'], data['Stochastic_Signal'] = compute_stochastic(data)  # Stochastic Oscillator
    return data

# Compute RSI
def compute_rsi(series, period):
    delta = series.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    return rsi

# Compute MACD
def compute_macd(series, short_window=12, long_window=26, signal_window=9):
    short_ema = series.ewm(span=short_window, adjust=False).mean()
    long_ema = series.ewm(span=long_window, adjust=False).mean()
    macd = short_ema - long_ema
    signal_line = macd.ewm(span=signal_window, adjust=False).mean()
    return macd, signal_line

# Compute Average True Range (ATR)
def compute_atr(data, period=14):
    high_low = data['High'] - data['Low']
    high_close = np.abs(data['High'] - data['Close'].shift())
    low_close = np.abs(data['Low'] - data['Close'].shift())
    tr = high_low.combine(high_close, np.maximum).combine(low_close, np.maximum)
    atr = tr.rolling(window=period).mean()
    return atr

# Compute Bollinger Bands
def compute_bollinger_bands(series, window, num_std=2):
    rolling_mean = series.rolling(window=window).mean()
    rolling_std = series.rolling(window=window).std()
    upper_band = rolling_mean + (rolling_std * num_std)
    lower_band = rolling_mean - (rolling_std * num_std)
    return upper_band, lower_band

# Compute Stochastic Oscillator
def compute_stochastic(data, period=14):
    lowest_low = data['Low'].rolling(window=period).min()
    highest_high = data['High'].rolling(window=period).max()
    stochastic = (data['Close'] - lowest_low) / (highest_high - lowest_low) * 100
    stochastic_signal = stochastic.rolling(window=3).mean()  # 3-period moving average as the signal line
    return stochastic, stochastic_signal

# Recognize candlestick patterns (simplified example)
def recognize_candlestick_patterns(data):
    patterns = ["No Pattern"] * len(data)  # Initialize with a default value for all rows
    for i in range(1, len(data)):
        if data['Close'][i] > data['Open'][i] and data['Close'][i-1] < data['Open'][i-1] and \
           data['Close'][i] > data['Open'][i-1] and data['Open'][i] < data['Close'][i-1]:
            patterns[i] = "Bullish Engulfing"
        elif data['Close'][i] < data['Open'][i] and data['Close'][i-1] > data['Open'][i-1] and \
             data['Close'][i] < data['Open'][i-1] and data['Open'][i] > data['Close'][i-1]:
            patterns[i] = "Bearish Engulfing"
    return patterns

# Trade decision algorithm with confidence scoring
def make_trade_decision(data):
    latest_data = data.iloc[-1]
    confidence = 0  # Confidence level starts at 0

    # RSI condition
    if latest_data['RSI'] < 30:
        confidence += 1  # Increase confidence if RSI indicates oversold (buy signal)
    elif latest_data['RSI'] > 70:
        confidence -= 1  # Decrease confidence if RSI indicates overbought (sell signal)

    # Moving Average crossover condition
    if latest_data['MA20'] > latest_data['MA50']:
        confidence += 1  # Bullish signal (Call)
    elif latest_data['MA20'] < latest_data['MA50']:
        confidence -= 1  # Bearish signal (Put)

    # MACD crossover condition
    if latest_data['MACD'] > latest_data['Signal_Line']:
        confidence += 1  # Bullish signal (Call)
    elif latest_data['MACD'] < latest_data['Signal_Line']:
        confidence -= 1  # Bearish signal (Put)

    # Bollinger Bands condition
    if latest_data['Close'] < latest_data['Lower_BB']:
        confidence += 1  # Oversold, potential buy signal (Call)
    elif latest_data['Close'] > latest_data['Upper_BB']:
        confidence -= 1  # Overbought, potential sell signal (Put)

    # Stochastic Oscillator condition
    if latest_data['Stochastic'] < 20:
        confidence += 1  # Oversold, buy signal (Call)
    elif latest_data['Stochastic'] > 80:
        confidence -= 1  # Overbought, sell signal (Put)

    # Candlestick pattern condition
    if "Bullish Engulfing" in data['Pattern'].values[-1]:
        confidence += 1  # Bullish signal (Call)
    elif "Bearish Engulfing" in data['Pattern'].values[-1]:
        confidence -= 1  # Bearish signal (Put)

    # ATR consideration (to avoid high volatility trades)
    if latest_data['ATR'] > data['ATR'].mean():
        confidence -= 1  # Avoid trading in high volatility

    # Determine trade action based on confidence
    if confidence >= 3:  # Threshold for a confident Call
        return "Call", confidence
    elif confidence <= -3:  # Threshold for a confident Put
        return "Put", confidence
    
    return "No Action", confidence

# Main AI function
def ai_trade_decision(asset):
    # Load data
    data = load_historical_data(asset)
    # Calculate indicators
    data = calculate_indicators(data)
    # Recognize candlestick patterns
    patterns = recognize_candlestick_patterns(data)
    data['Pattern'] = patterns
    # Make trade decision
    decision, confidence = make_trade_decision(data)

    return asset, decision, confidence

# Main function to execute the AI
def main():
    available_assets_file = os.path.join(base_directory, 'available_assets.txt')
    with open(available_assets_file, 'r') as file:
        assets = [line.strip() for line in file.readlines()]

    best_decision = None
    highest_confidence = -float('inf')  # Initialize to negative infinity

    for asset in assets:
        print(f"\nAnalyzing asset: {asset}")
        asset, decision, confidence = ai_trade_decision(asset)

        # Track the best decision based on confidence
        if confidence > highest_confidence:
            highest_confidence = confidence
            best_decision = (asset, decision)

    if best_decision:
        print(f"\nBest trade decision based on analysis: Asset: {best_decision[0]}, Decision: {best_decision[1]} with confidence level: {highest_confidence}")
    else:
        print("No confident trade decisions were found.")

if __name__ == "__main__":
    main()
