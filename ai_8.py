import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import google.generativeai as genai

google_api_key = st.secrets["api_keys"]["google_api"]

st.set_page_config(page_title="AI-Powered Clothing Sales Analysis", layout="wide")
st.title("🧠 AI-Powered Clothing Sales Analysis")

uploaded_file = st.file_uploader("Upload your clothing sales CSV file", type="csv")

if uploaded_file:
    try:
        df = pd.read_csv(uploaded_file, parse_dates=['Date'])
        df['Revenue'] = df['Quantity'] * df['Price']
        df['Month'] = df['Date'].dt.to_period("M").astype(str)

        with st.expander("🔍 Preview Data"):
            st.dataframe(df.head())

        st.subheader("📈 Summary Metrics")
        col1, col2, col3 = st.columns(3)
        col1.metric("Total Revenue", f"₹{df['Revenue'].sum():,.0f}")
        col2.metric("Total Units Sold", f"{df['Quantity'].sum():,.0f}")
        col3.metric("Average Rating", f"{df['Review Rating (out of 5)'].mean():.2f} ⭐")

        st.subheader("🏆 Top 10 Products by Revenue")
        top_products = df.groupby('Product')['Revenue'].sum().sort_values(ascending=False).head(10)
        st.bar_chart(top_products)
        '''st.subheader("💳 Payment Method Distribution")
        payment_counts = df['Payment Method'].value_counts()
        st.bar_chart(payment_counts)
        st.subheader("👥 Revenue by Customer Segment")
        seg_rev = df.groupby('Customer Segment')['Revenue'].sum()
        st.bar_chart(seg_rev)
        st.subheader("🚻 Revenue by Gender")
        gender_rev = df.groupby('Gender')['Revenue'].sum()
        st.bar_chart(gender_rev)
        st.subheader("💸 Revenue with and without Discount")
        discount_rev = df.groupby('Discount Applied')['Revenue'].sum()
        st.bar_chart(discount_rev)
        st.subheader("📊 Revenue by Age Group")
        bins = [0, 18, 25, 35, 50, 65, 100]
        labels = ['<18', '18-25', '26-35', '36-50', '51-65', '65+']
        df['Age Group'] = pd.cut(df['Age'], bins=bins, labels=labels)
        age_rev = df.groupby('Age Group')['Revenue'].sum()
        st.bar_chart(age_rev)
        weekday_rev = df.groupby(df['Date'].dt.day_name())['Revenue'].sum().sort_values()'''

        st.subheader("🧠 AI Suggestions for Growth")

        summary_text = f"""
        You are a small business advisor helping a clothing store owner. Based on the following performance summary, do these 3 things:

        1. Check if there's any sign of issues — especially dip in performance (keep the tone honest but helpful).
        2. Give 3 constructive, specific tips to help improve. Avoid fluff. Focus on actions related to customer reviews, loyalty, and sales.
        3. Look at which weekdays had the lowest revenue and suggest 2-3 creative, actionable ideas to improve sales on those slow days.

        Be practical, supportive, and a little creative. Imagine you're advising a real clothing store owner who wants real results.

        Performance Summary:
        - Total Revenue: ₹{df['Revenue'].sum():,.0f}
        - Total Units Sold: {df['Quantity'].sum():,.0f}
        - Average Review Rating: {df['Review Rating (out of 5)'].mean():.2f}
        - Top 3 Products: {', '.join(top_products.index[:3])}
        - Most Used Payment Method: {payment_counts.idxmax()}
        - Most Profitable Segment: {seg_rev.idxmax()} with ₹{seg_rev.max():,.0f}
        - Gender with Highest Revenue: {gender_rev.idxmax()} with ₹{gender_rev.max():,.0f}
        - Revenue from Discounts: ₹{discount_rev.get(True, 0):,.0f}
        - Revenue without Discounts: ₹{discount_rev.get(False, 0):,.0f}
        - Best Performing Age Group: {age_rev.idxmax()} with ₹{age_rev.max():,.0f}
        - Avg Monthly Revenue: ₹{df.groupby('Month')['Revenue'].sum().mean():,.0f}

        Daily Revenue Breakdown:
        {weekday_rev.to_string()}
        """

        model = genai.GenerativeModel('gemini-2.0-flash-thinking-exp')
        with st.spinner("Getting AI-generated suggestions..."):
            response = model.generate_content(summary_text)
            st.success("Here's what the AI recommends:")
            st.markdown(response.text)
            st.download_button("💾 Download Suggestions", response.text, file_name="Clothing_AI_Insights.txt")

    except Exception as e:
        st.error(f"⚠ An error occurred while processing the file: {e}")

else:
    st.info("Please upload a CSV file with columns: Date, Product, Category, Quantity, Price, Review Rating, Payment Method, Age, Gender, Discount Applied, Customer Segment.")
