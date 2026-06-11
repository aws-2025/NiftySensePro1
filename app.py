import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
import time

# Page Layout Configuration - मोबाईलसाठी अनुकूल केले आहे
st.set_page_config(page_title="NiftySense Pro - Mobile", layout="centered")

# Custom UI Styling (Mobile-Friendly Responsive Sizes)
st.markdown("""
    <style>
    .big-title { font-size:32px !important; font-weight: bold; text-align: center; margin-bottom: 15px; }
    .signal-box { padding: 30px 15px; border-radius: 15px; text-align: center; box-shadow: 0px 4px 15px rgba(0,0,0,0.1); margin-bottom: 25px; }
    .buy-box { background-color: #28a745; border: 4px solid #1e7e34; color: #ffffff; }
    .sell-box { background-color: #dc3545; border: 4px solid #bd2130; color: #ffffff; }
    .hold-box { background-color: #fff3cd; border: 3px solid #ffc107; color: #856404; }
    .text-title { font-size: 38px !important; font-weight: 900 !important; letter-spacing: 1px; line-height: 1.2; }
    .text-details { font-size: 22px !important; font-weight: bold; margin-top: 15px; line-height: 1.5; }
    .text-instruction { font-size: 18px !important; font-weight: bold; margin-top: 15px; background: rgba(0,0,0,0.15); padding: 12px; border-radius: 8px; }
    .hold-instruction { font-size: 18px !important; font-weight: bold; margin-top: 15px; background: rgba(255,255,255,0.6); padding: 12px; border-radius: 8px; }
    </style>
""", unsafe_allow_html=True)

st.markdown('<div class="big-title">📲 NiftySense Pro Live</div>', unsafe_allow_html=True)

try:
    # 1. Fetch Fresh 5-Minute Data
    data = yf.download("^NSEI", period="1d", interval="5m", multi_level_index=False)
    data = data.dropna()
    close = data["Close"]

    # 2. Indicators Calculation (Fast 9 EMA and 21 EMA)
    data["EMA9"] = close.ewm(span=9, min_periods=1).mean()
    data["EMA21"] = close.ewm(span=21, min_periods=1).mean()

    # RSI Calculation
    delta = close.diff()
    gain = delta.clip(lower=0).rolling(14).mean()
    loss = (-delta.clip(upper=0)).rolling(14).mean()
    rs = gain / loss
    data["RSI"] = 100 - (100 / (1 + rs))

    # 3. Extract Live and Previous Data Points
    live_price = float(close.iloc[-1])
    previous_close = float(close.iloc[-2])
    live_ema9 = float(data["EMA9"].iloc[-1])
    live_ema21 = float(data["EMA21"].iloc[-1])
    live_rsi = float(data["RSI"].iloc[-1])

    target_points = 15.0
    sl_points = 10.0

    # 4. Mobile Layout: Top Big Signal -> Bottom Candle Chart
    # Condition For BUY: Green Candle AND EMA Bullish AND RSI Strong
    if (live_price > previous_close) and (live_ema9 > live_ema21) and (live_rsi > 45):
        st.markdown(f"""
            <div class="signal-box buy-box">
                <div class="text-title">🟢 BUY SIGNAL 🟢</div>
                <div class="text-details">
                    PRICE: {live_price:.2f} (Up)<br>
                    🎯 TARGET: {live_price + target_points:.2f}<br>
                    🛑 STOP LOSS: {live_price - sl_points:.2f}
                </div>
                <div class="text-instruction">
                    🚨 ACTION: Open broker app & place a BUY MARKET ORDER right now!
                </div>
            </div>
        """, unsafe_allow_html=True)

    # Condition For SELL: Red Candle AND EMA Bearish AND RSI Weak
    elif (live_price < previous_close) and (live_ema9 < live_ema21) and (live_rsi < 55):
        st.markdown(f"""
            <div class="signal-box sell-box">
                <div class="text-title">🔴 SELL SIGNAL 🔴</div>
                <div class="text-details">
                    PRICE: {live_price:.2f} (Down)<br>
                    🎯 TARGET: {live_price - target_points:.2f}<br>
                    🛑 STOP LOSS: {live_price + sl_points:.2f}
                </div>
                <div class="text-instruction">
                    🚨 ACTION: Open broker app & place a SELL MARKET ORDER right now!
                </div>
            </div>
        """, unsafe_allow_html=True)

    # Neutral Conditions -> HOLD
    else:
        st.markdown(f"""
            <div class="signal-box hold-box">
                <div class="text-title">🟡 HOLD ZONE 🟡</div>
                <div class="text-details">
                    PRICE: {live_price:.2f} (Sideways)<br>
                    📊 RSI Strength: {live_rsi:.1f}
                </div>
                <div class="text-instruction hold-instruction">
                    🚫 TRADING RULE: Sideways market. DO NOT TAKE ANY TRADE!
                </div>
            </div>
        """, unsafe_allow_html=True)

    # मोबाईलवर सिग्नलच्या खाली कॅन्डल चार्ट दिसेल
    st.markdown("---")
    st.subheader("🕯️ Live 5m Candles")
    chart_data = data.tail(12) # मोबाईल स्क्रीनसाठी फक्त १२ कॅन्डल्स पुरेशा आहेत
    
    fig = go.Figure(data=[go.Candlestick(
        x=chart_data.index.strftime('%H:%M'), # मोबाईलवर फक्त वेळ दिसेल (तास:मिनिट)
        open=chart_data['Open'],
        high=chart_data['High'],
        low=chart_data['Low'],
        close=chart_data['Close'],
        increasing_line_color='#28a745',   # Pure Green Candle
        decreasing_line_color='#dc3545'    # Pure Red Candle
    )])
    
    fig.update_layout(
        xaxis_rangeslider_visible=False,
        margin=dict(l=5, r=5, t=5, b=5),
        height=280,
        template="plotly_white"
    )
    st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

except Exception as e:
    st.error("Live market data loading error. Please refresh.")

# Auto-Refresh every 2 seconds for active tick updates
time.sleep(2)
st.rerun()
