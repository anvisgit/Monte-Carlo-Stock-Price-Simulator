import streamlit as st
import yfinance as yf
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime, timedelta

st.set_page_config(page_title="Monte Carlo Stock Price Simulator", page_icon="📈", layout="wide")
st.title("📈 Monte Carlo Stock Price Simulator")

st.sidebar.title("Set Parameteres")
ticker = st.text_input("Enter a stock ticker symbol:").upper()
hist_window = st.sidebar.number_input("Historical Window (days)", min_value=0, max_value=1000, value=252,)
auto = st.sidebar.checkbox("Auto-calculate μ and σ from historical data", value=True)
mu=st.sidebar.slider("Expected Daily Return:",min_value=-0.01, max_value=0.01,value=0.0005, step=0.0001, help="Only used if auto μ is OFF")
sigma=st.sidebar.slider("Daily Volatility:", min_value=0.0,max_value=0.2, value=0.02, step=0.001, help="Only used if auto σ is OFF")
start_price = st.sidebar.number_input("Starting Price (0 = auto fetch latest)", value=0.0,help="If 0, the latest market close will be fetched.")
num_simulations = st.sidebar.slider("Number of Simulations", 100, 5000, 1000, step=100)
future_days = st.sidebar.slider("Days to Simulate", 10, 1000, 252, step=10)


clicked=st.sidebar.button("Run Simulation▶️")
if clicked and ticker:
    try:
        if hist_window>0:
            st.write("Fetching Data")
            data = yf.download(ticker, period=f"{hist_window}d")
            closep=data["Close"]
            log_ret=np.log(closep/closep.shift(1)).dropna()
            auto_mu = log_ret.mean()
            auto_sigma = log_ret.std()

            if auto:
                mu=float(auto_mu)
                sigma=float(auto_sigma)
            st.success(f"μ = {mu:.5f}, σ = {sigma:.5f}")
            if start_price == 0.0:
                last_price = yf.Ticker(ticker).history(period="1d")["Close"].iloc[-1]
            else:
                last_price = start_price
            

            simulation =np.zeros((future_days, num_simulations))
            for i in range(num_simulations):
                price=[last_price]
                for _ in range(future_days):
                    drift = mu - 0.5 * sigma**2
                    shock = np.random.normal(0, sigma)
                    new_price = price[-1] * np.exp(drift + shock)
                    price.append(new_price)
                simulation[:, i] = price[1:]
                    
            st.subheader("Simulated Price Paths")
            fig, ax = plt.subplots(figsize=(10, 6))
            ax.plot(simulation)
            ax.set_title(f"Monte Carlo Simulation for {ticker}")
            ax.set_xlabel("Days")
            ax.set_ylabel("Price")
            st.pyplot(fig)

    except Exception as e:
        st.error(f"Error: {e}")
    




