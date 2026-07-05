import streamlit as st
import pandas as pd

st.set_page_config(page_title="CSV Explorer", layout="wide")

st.title("📊 CSV Explorer")
st.write("Upload a CSV and get instant summary stats and charts.")

file = st.file_uploader("Upload a CSV file", type=["csv"])

if file is not None:
    df = pd.read_csv(file)

    st.subheader("Preview")
    st.dataframe(df.head(50))

    st.subheader("Summary")
    c1, c2, c3 = st.columns(3)
    c1.metric("Rows", df.shape[0])
    c2.metric("Columns", df.shape[1])
    c3.metric("Missing values", int(df.isna().sum().sum()))

    st.write(df.describe(include="all"))

    numeric_cols = df.select_dtypes(include="number").columns.tolist()

    if numeric_cols:
        st.subheader("Distribution")
        col = st.selectbox("Pick a numeric column", numeric_cols)
        st.bar_chart(df[col].value_counts().sort_index())

        if len(numeric_cols) >= 2:
            st.subheader("Scatter")
            x = st.selectbox("X axis", numeric_cols, index=0)
            y = st.selectbox("Y axis", numeric_cols, index=1)
            st.scatter_chart(df, x=x, y=y)
    else:
        st.info("No numeric columns found to chart.")
else:
    st.info("Waiting for a CSV — try any dataset (a Kaggle download, a spreadsheet export, anything).")
