import streamlit as st
import pandas as pd
import altair as alt

# Streamlit page config
st.set_page_config(layout="wide", page_title="Business Insights Dashboard")
st.title("📊 Dynamic Business Data Dashboard")

# File uploader
uploaded_file = st.file_uploader("Upload your CSV file", type="csv")

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file, encoding='cp1252')
    st.success("✅ File uploaded and parsed!")

    # --- Corrected Data Type Detection ---
    categorical_cols = df.select_dtypes(include=['object', 'category']).columns.tolist()
    numeric_cols = df.select_dtypes(include=['float64', 'int64']).columns.tolist()

    datetime_cols = []
    for col in df.columns:
        if df[col].dtype == 'object':
            try:
                parsed_col = pd.to_datetime(df[col], errors='raise', infer_datetime_format=True)
                if parsed_col.notna().mean() > 0.9:
                    df[col] = parsed_col
                    datetime_cols.append(col)
            except (ValueError, TypeError):
                continue

    # Data Preview
    st.subheader("📋 Uploaded Data: Data Preview")
    st.dataframe(df.head(), use_container_width=True)

    # --- Sidebar Controls ---
    st.sidebar.header("⚙️ Chart Controls")
    chart_type = st.sidebar.selectbox("Select Chart Type", ["Bar Chart", "Histogram", "Line Chart", "Box Plot"])

    selected_num_col = st.sidebar.selectbox("Select Numerical Column (for y-axis or analysis)", ["None"] + numeric_cols)
    selected_cat_col = st.sidebar.selectbox("Select Categorical Column (for x-axis, grouping)", ["None"] + categorical_cols)
    selected_date_col = st.sidebar.selectbox("Select Datetime Column (for time series)", ["None"] + datetime_cols)

    aggregation_func = st.sidebar.selectbox("Select Aggregation Method (if applicable)", ["sum", "mean", "count", "min", "max"])

    # --- Main Area Visualizations ---
    if chart_type == "Histogram" and selected_num_col != "None":
        st.subheader(f"📊 Histogram of {selected_num_col}")
        hist_chart = alt.Chart(df).mark_bar().encode(
            x=alt.X(selected_num_col, bin=True),
            y='count()',
            tooltip=[selected_num_col, 'count()']
        ).properties(width=800, height=400)
        st.altair_chart(hist_chart, use_container_width=True)

    elif chart_type == "Bar Chart" and selected_cat_col != "None" and selected_num_col != "None":
        st.subheader(f"📊 {aggregation_func.capitalize()} {selected_num_col} by {selected_cat_col}")
        bar_data = df.groupby(selected_cat_col)[selected_num_col].agg(aggregation_func).reset_index()
        bar_chart = alt.Chart(bar_data).mark_bar().encode(
            x=alt.X(selected_cat_col, sort='-y'),
            y=selected_num_col,
            tooltip=[selected_cat_col, selected_num_col]
        ).properties(width=800, height=400)
        st.altair_chart(bar_chart, use_container_width=True)

    elif chart_type == "Line Chart" and selected_date_col != "None" and selected_num_col != "None":
        st.subheader(f"🕒 {aggregation_func.capitalize()} {selected_num_col} over {selected_date_col}")
        time_data = df.groupby(selected_date_col)[selected_num_col].agg(aggregation_func).reset_index()
        line_chart = alt.Chart(time_data).mark_line().encode(
            x=selected_date_col,
            y=selected_num_col,
            tooltip=[selected_date_col, selected_num_col]
        ).properties(width=800, height=400)
        st.altair_chart(line_chart, use_container_width=True)

    elif chart_type == "Box Plot" and selected_cat_col != "None" and selected_num_col != "None":
        st.subheader(f"🎯 Distribution of {selected_num_col} across {selected_cat_col}")
        box_chart = alt.Chart(df).mark_boxplot().encode(
            x=alt.X(selected_cat_col),
            y=alt.Y(selected_num_col),
            tooltip=[selected_cat_col, selected_num_col]
        ).properties(width=800, height=400)
        st.altair_chart(box_chart, use_container_width=True)

    else:
        st.warning("⚠️ Please select appropriate columns based on your chart type.")

else:
    st.info("👆 Upload a CSV file to get started.")
