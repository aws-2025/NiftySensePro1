import streamlit as st
import yfinance as yf

st.set_page_config(page_title="NiftySense Pro", layout="wide")

st.title("📊 NiftySense Pro - Trading Dashboard")
st.markdown("---")

# Data
data = yf.download("^NSEI", period="1d", interval="5m")
data = data.dropna()

close = data["Close"]

# RSI
delta = close.diff()
gain = delta.clip(lower=0).rolling(14).mean()
loss = (-delta.clip(upper=0)).rolling(14).mean()

rs = gain / loss
data["RSI"] = 100 - (100 / (1 + rs))

# EMA
data["EMA20"] = close.ewm(span=20, min_periods=1).mean()
data["EMA50"] = close.ewm(span=50, min_periods=1).mean()

ema20 = float(data["EMA20"].dropna().iloc[-1])
ema50 = float(data["EMA50"].dropna().iloc[-1])

# Layout
col1, col2, col3 = st.columns(3)

with col1:
    st.subheader("📈 Price Chart")
    st.line_chart(close)

with col2:
    st.subheader("📊 RSI")
    st.line_chart(data["RSI"])

    st.subheader("📉 EMA Trend")

    if ema20 > ema50:
        st.success("Bullish 📈")
    else:
        st.error("Bearish 📉")

with col3:
    st.subheader("⚡ Signal")

    rsi = float(data["RSI"].dropna().iloc[-1])

    if rsi < 30:
        st.success("BUY 📈")
    elif rsi > 70:
        st.error("SELL 📉")
    else:
        st.info("HOLD ⚠️")

# Volume
st.markdown("---")
st.subheader("📊 Volume Analysis")

volume = data["Volume"].dropna()

avg_volume = volume.rolling(10).mean()

latest_volume = float(volume.iloc[-1])
avg_vol = float(avg_volume.dropna().iloc[-1])

if latest_volume > avg_vol:
    st.success("High Activity 📈")
else:
    st.info("Normal Volume ⚠️")

# Trade Plan
st.markdown("---")
st.subheader("💰 Trade Plan")

entry = float(close.iloc[-1])
rsi = float(data["RSI"].dropna().iloc[-1])

if rsi < 30:
    st.success(f"BUY SETUP 📈 Entry: {entry:.2f} | Target: {entry*1.01:.2f} | SL: {entry*0.995:.2f}")

elif rsi > 70:
    st.error(f"SELL SETUP 📉 Entry: {entry:.2f} | Target: {entry*0.99:.2f} | SL: {entry*1.005:.2f}")

else:
    st.info("NO TRADE ⚠️")