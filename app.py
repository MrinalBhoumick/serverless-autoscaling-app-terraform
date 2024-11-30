import streamlit as st
import yfinance as yf
import matplotlib.pyplot as plt
import pandas as pd
from forex_python.converter import CurrencyRates

# Set the page configuration
st.set_page_config(page_title="Futuristic Advisor Application", layout="wide")

# Sidebar for user input
st.sidebar.header("Input Options")
ticker_symbol = st.sidebar.text_input("Enter Stock Ticker Symbol", "AAPL")
start_date = st.sidebar.date_input("Start Date", value=pd.to_datetime("2020-01-01"))
end_date = st.sidebar.date_input("End Date", value=pd.to_datetime("today"))
moving_avg_window = st.sidebar.slider("Moving Average Window (Days)", 5, 200, 50)
days_to_predict = st.sidebar.slider("Days to Predict", 1, 7, 7)  # Slider for number of prediction days

# Title
st.title("📈 Simple Stock Prediction App")

# Fetch data from Yahoo Finance
@st.cache_data
def fetch_data(ticker, start, end):
    stock_data = yf.download(ticker, start=start, end=end)
    return stock_data

# Function to predict closing prices for the next 'n' days
def predict_next_n_days_price(stock_data, moving_avg_window, days_to_predict):
    last_ma = stock_data[f"MA_{moving_avg_window}"].iloc[-1]
    predicted_prices = []

    # Calculate the trend (based on the last two moving average values)
    if stock_data[f"MA_{moving_avg_window}"].iloc[-1] > stock_data[f"MA_{moving_avg_window}"].iloc[-2]:
        trend = "upward"
    else:
        trend = "downward"

    # Predict the next 'days_to_predict' prices based on the moving average trend
    for i in range(days_to_predict):
        predicted_price = last_ma  # Start with the last moving average value
        if trend == "upward":
            predicted_price += (stock_data["Close"].iloc[-1] - stock_data["Close"].iloc[-moving_avg_window]).mean()
        else:
            predicted_price -= (stock_data["Close"].iloc[-1] - stock_data["Close"].iloc[-moving_avg_window]).mean()

        predicted_prices.append(predicted_price)
        last_ma = predicted_price  # Update the last moving average value for next prediction

    return predicted_prices, trend

# Function to check if the stock is Indian or foreign
def is_indian_stock(ticker_symbol):
    # List of common Indian stock tickers or exchanges (NSE, BSE)
    indian_stocks = ["RELIANCE.NS", "TCS.NS", "INFY.NS", "HDFC.NS", "BAJFINANCE.NS", "ICICIBANK.NS"]

    # If ticker symbol is in the list, return True (Indian stock)
    return ticker_symbol in indian_stocks

# Display stock data
try:
    stock_data = fetch_data(ticker_symbol, start_date, end_date)
    st.write(f"### {ticker_symbol} Stock Data from {start_date} to {end_date}")
    st.dataframe(stock_data.tail())

    # Plot stock closing prices
    st.write("### Closing Price Over Time")
    plt.figure(figsize=(10, 6))
    plt.plot(stock_data["Close"], label="Close Price", color="blue")
    plt.title(f"{ticker_symbol} Closing Price")
    plt.xlabel("Date")
    plt.ylabel("Price")
    plt.legend()
    st.pyplot(plt)

    # Add Moving Average
    stock_data[f"MA_{moving_avg_window}"] = stock_data["Close"].rolling(window=moving_avg_window).mean()
    st.write(f"### {moving_avg_window}-Day Moving Average")
    plt.figure(figsize=(10, 6))
    plt.plot(stock_data["Close"], label="Close Price", color="blue", alpha=0.6)
    plt.plot(stock_data[f"MA_{moving_avg_window}"], label=f"{moving_avg_window}-Day MA", color="orange")
    plt.title(f"{ticker_symbol} Price with {moving_avg_window}-Day Moving Average")
    plt.xlabel("Date")
    plt.ylabel("Price")
    plt.legend()
    st.pyplot(plt)

    # Prediction for next 'days_to_predict' days
    predicted_prices, trend = predict_next_n_days_price(stock_data, moving_avg_window, days_to_predict)

    # Display predicted closing prices
    st.write(f"🔮 **Predicted Closing Prices for Next {days_to_predict} Days**:")

    predicted_dates = pd.date_range(start=stock_data.index[-1] + pd.Timedelta(days=1), periods=days_to_predict)
    predicted_df = pd.DataFrame({
        'Date': predicted_dates,
        'Predicted Price': predicted_prices
    })

    # If the stock is Indian, convert the predicted price to INR using forex-python
    if is_indian_stock(ticker_symbol):
        # Convert USD to INR using forex-python
        cr = CurrencyRates()
        try:
            predicted_df['Predicted Price INR'] = predicted_df['Predicted Price'].apply(lambda x: cr.convert('USD', 'INR', x))
            st.write(predicted_df[['Date', 'Predicted Price INR']])
        except:
            st.error("Could not fetch conversion rates. Showing price in USD.")
            st.write(predicted_df[['Date', 'Predicted Price']])
    else:
        st.write(predicted_df[['Date', 'Predicted Price']])

    st.write(f"🔼 **Trend**: The stock is in an {trend} trend based on the moving average.")

except Exception as e:
    st.error(f"An error occurred: {e}")
