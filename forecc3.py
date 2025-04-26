import pandas as pd
from prophet import Prophet
import streamlit as st
import matplotlib.pyplot as plt


st.set_page_config(page_title="Personalised Gifts Forecast", layout="wide")
st.title("🎁 Personalised Gifts Forecasting Dashboard")

uploaded = st.file_uploader("Upload CSV for Personalised Gifts", type="csv")
if not uploaded:
    st.info("Please upload a CSV with fields: Order Date, Product Category, Quantity Sold, Price, etc.")
    st.stop()

df = pd.read_csv(uploaded, parse_dates=["Order Date"])

required_cols = ["Order Date", "Product Category", "Quantity Sold", "Price"]
missing = [col for col in required_cols if col not in df.columns]
if missing:
    st.error(f"Missing required columns: {', '.join(missing)}")
    st.stop()

df["Total Revenue"] = df["Quantity Sold"] * df["Price"]


st.header("📈 Overall Sales Forecast (Total Revenue)")

daily_rev = df.groupby("Order Date").agg({"Total Revenue": "sum"}).reset_index()
df_prophet = daily_rev.rename(columns={"Order Date": "ds", "Total Revenue": "y"})

model = Prophet(daily_seasonality=True)
model.fit(df_prophet)

future = model.make_future_dataframe(periods=180)
forecast = model.predict(future)

fig1 = model.plot(forecast)
st.pyplot(fig1)

next_30 = forecast[forecast['ds'] > pd.Timestamp.today()].head(30)['yhat'].sum()
next_180 = forecast[forecast['ds'] > pd.Timestamp.today()].head(180)['yhat'].sum()

st.subheader("📊 Forecast Summary")
st.write(f"Projected Revenue (Next 30 Days): ₹{next_30:,.0f}")
st.write(f"Projected Revenue (Next 6 Months): ₹{next_180:,.0f}")

st.header("📦 Forecast: Quantity Sold by Category (Next 3 Months)")

cat_forecasts = []

for cat, group in df.groupby("Product Category"):
    daily_qty = group.groupby("Order Date")["Quantity Sold"].sum().reset_index()
    if len(daily_qty) < 30:
        continue
    prophet_df = daily_qty.rename(columns={"Order Date": "ds", "Quantity Sold": "y"})
    model_cat = Prophet(daily_seasonality=True)
    model_cat.fit(prophet_df)
    future_cat = model_cat.make_future_dataframe(periods=90)
    forecast_cat = model_cat.predict(future_cat)
    total_qty = forecast_cat.tail(90)['yhat'].sum()
    cat_forecasts.append({"Product Category": cat, "Forecasted Quantity": int(total_qty)})

cat_df = pd.DataFrame(cat_forecasts)

if not cat_df.empty:
    st.dataframe(cat_df.set_index("Product Category"))

    fig2, ax2 = plt.subplots()
    ax2.pie(cat_df["Forecasted Quantity"], labels=cat_df["Product Category"], autopct="%1.1f%%", startangle=90)
    ax2.axis("equal")
    st.pyplot(fig2)
else:
    st.warning("Insufficient data for category-wise forecasting.")


st.header("📉 Optional Insights")

if "Return Rate" in df.columns:
    st.write(f"Average Return Rate: {df['Return Rate'].mean():.2%}")

if "Repeat Purchase Rate" in df.columns:
    st.write(f"Average Repeat Purchase Rate: {df['Repeat Purchase Rate'].mean():.2%}")

if "Review Rating" in df.columns:
    st.write(f"Average Customer Rating: {df['Review Rating'].mean():.1f} ⭐")

if "Shipping Time" in df.columns:
    st.write(f"Average Shipping Time: {df['Shipping Time'].mean():.1f} days")

st.header("💡 Recommendations")
st.write("- Prioritize categories with rising demand for inventory planning.")
st.write("- Use repeat purchase and return rates to optimize retention strategies.")
st.write("- Offer promotions on high CLTV segments for better profitability.")
