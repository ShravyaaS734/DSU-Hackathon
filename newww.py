import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import google.generativeai as genai

google_api_key = st.secrets["api_keys"]["google_api"]
st.set_page_config(page_title="AI-Powered Personalized Gift Analysis", layout="wide")
st.title("🎁 AI-Powered Personalized Gift Analysis")

uploaded_file = st.file_uploader("Upload your sales CSV file", type="csv")

business_type = st.selectbox("Select your business type", ["Personalized Gifts"])

required_columns = [
    "Order ID", "Order Date", "Quantity Sold", "Product Name", "Price", "Customer ID", 
    "Customer Age", "Customer Gender", "Customer Segment", "Payment Method", 
    "Discount Applied", "Product Category", "Review Rating", "Shipping Cost", 
    "Shipping Time", "Return Rate", "CAC", "CLTV", "Repeat Purchase Rate"
]

ai_prompt = """
You are a business advisor helping a personalized gift shop owner. Based on the following performance summary, do these 3 things:
1. Check if there's any sign of issues, especially a dip in performance.
2. Give 3 specific tips to help improve. Focus on reviews, loyalty, and sales.
3. Suggest 2-3 creative, actionable ideas to improve sales on slow days. Also, analyze uncertainties and give practical suggestions.
"""

if uploaded_file:
    try:
        df = pd.read_csv(uploaded_file, parse_dates=['Order Date'])
        
        missing_columns = [col for col in required_columns if col not in df.columns]
        
        if missing_columns:
            st.error(f"⚠️ Missing columns: {', '.join(missing_columns)}. Please upload a CSV file with the required columns.")
        else:
            df['Revenue'] = df['Quantity Sold'] * df['Price']
            df['Month'] = df['Order Date'].dt.to_period("M").astype(str)

            with st.expander("🔍 Preview Data"):
                st.dataframe(df.head())

            st.subheader("📈 Summary Metrics")
            col1, col2, col3 = st.columns(3)
            col1.metric("Total Revenue", f"₹{df['Revenue'].sum():,.0f}")
            col2.metric("Total Units Sold", f"{df['Quantity Sold'].sum():,.0f}")
            col3.metric("Average Rating", f"{df['Review Rating'].mean():.2f} ⭐")

            st.subheader("🏆 Top 10 Products by Revenue")
            top_products = df.groupby('Product Name')['Revenue'].sum().sort_values(ascending=False).head(10)
            st.bar_chart(top_products)

            st.subheader("💳 Payment Method Distribution")
            payment_counts = df['Payment Method'].value_counts()
            st.bar_chart(payment_counts)

            st.subheader("👥 Revenue by Customer Segment")
            seg_rev = df.groupby('Customer Segment')['Revenue'].sum()
            st.bar_chart(seg_rev)

            st.subheader("🚻 Revenue by Gender")
            gender_rev = df.groupby('Customer Gender')['Revenue'].sum()
            st.bar_chart(gender_rev)

            st.subheader("💸 Revenue with and without Discount")
            discount_rev = df.groupby('Discount Applied')['Revenue'].sum()
            st.bar_chart(discount_rev)

            st.subheader("📊 Revenue by Age Group")
            bins = [0, 18, 25, 35, 50, 65, 100]
            labels = ['<18', '18-25', '26-35', '36-50', '51-65', '65+']
            df['Age Group'] = pd.cut(df['Customer Age'], bins=bins, labels=labels)
            age_rev = df.groupby('Age Group')['Revenue'].sum()
            st.bar_chart(age_rev)

            st.subheader("📦 Shipping Time vs. Revenue")
            shipping_time_rev = df.groupby('Shipping Time')['Revenue'].sum()
            st.bar_chart(shipping_time_rev)

            st.subheader("📉 Return Rate vs. Revenue")
            return_rate_rev = df.groupby('Return Rate')['Revenue'].sum()
            st.bar_chart(return_rate_rev)

            st.subheader("💡 CAC vs. CLTV")
            cac_cltv = df.groupby('Customer Segment')[['CAC', 'CLTV']].mean()
            st.bar_chart(cac_cltv)

            st.subheader("🧠 AI Suggestions for Growth")

            summary_text = f"""
            You are a business advisor helping a personalized gift shop owner. Based on the following performance summary, do these 3 things:
            1. Check if there's any sign of issues, especially a dip in performance.
            2. Give 3 specific tips to help improve. Focus on reviews, loyalty, and sales.
            3. Suggest 2-3 creative, actionable ideas to improve sales on slow days. Also, analyze uncertainties and give practical suggestions.

            Performance Summary:
            - Total Revenue: ₹{df['Revenue'].sum():,.0f}
            - Total Units Sold: {df['Quantity Sold'].sum():,.0f}
            - Average Review Rating: {df['Review Rating'].mean():.2f}
            - Top 3 Products: {', '.join(top_products.index[:3])}
            - Most Used Payment Method: {payment_counts.idxmax()}
            - Most Profitable Segment: {seg_rev.idxmax()} with ₹{seg_rev.max():,.0f}
            - Gender with Highest Revenue: {gender_rev.idxmax()} with ₹{gender_rev.max():,.0f}
            - Revenue from Discounts: ₹{discount_rev.get(True, 0):,.0f}
            - Revenue without Discounts: ₹{discount_rev.get(False, 0):,.0f}
            - Best Performing Age Group: {age_rev.idxmax()} with ₹{age_rev.max():,.0f}
            - Avg Monthly Revenue: ₹{df.groupby('Month')['Revenue'].sum().mean():,.0f}
            - Shipping Time vs Revenue: {shipping_time_rev.to_string()}
            - Return Rate vs Revenue: {return_rate_rev.to_string()}
            - CAC vs CLTV: {cac_cltv.to_string()}

            Daily Revenue Breakdown:
            {df.groupby(df['Order Date'].dt.day_name())['Revenue'].sum().sort_values().to_string()}
            """

            # 🔍 Generate AI Suggestions
            model = genai.GenerativeModel('gemini-2.0-flash-thinking-exp')
            with st.spinner("Getting AI-generated suggestions..."):
                response = model.generate_content(summary_text)
                st.success("Here's what the AI recommends:")
                st.markdown(response.text)
                st.download_button("💾 Download Suggestions", response.text, file_name="Business_AI_Insights.txt")

    except Exception as e:
        st.error(f"⚠️ An error occurred while processing the file: {e}")

else:
    st.info("Please upload a CSV file with the relevant columns for your business.")
