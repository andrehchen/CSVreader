import streamlit as st
import pandas as pd
import numpy as np
import anthropic

st.set_page_config(page_title="CSV Explorer", layout="wide")
st.title("CSV Explorer")
st.write("Upload a CSV and get instant summary stats and charts.")

file = st.file_uploader("Upload a CSV file", type=["csv"])


@st.cache_data(show_spinner=False)
def get_ai_summary(insights_text: str, row_count: int, col_count: int) -> str:
    client = anthropic.Anthropic(api_key=st.secrets["ANTHROPIC_API_KEY"])
    prompt = (
        f"A dataset has {row_count} rows and {col_count} columns. "
        f"Here are its automated findings:\n{insights_text}\n\n"
        "In exactly two sentences, describe what this dataset likely contains "
        "and summarize its most important data-quality issues."
    )
    msg = client.messages.create(
        model="claude-opus-4-8",
        max_tokens=150,
        messages=[{"role": "user", "content": prompt}],
    )
    return msg.content[0].text


if file is not None:
    df = pd.read_csv(file, sep=None, engine='python')

    # Compute all analysis first so the AI summary can appear at the top
    profile = pd.DataFrame({
        "dtype": df.dtypes.astype(str),
        "missing %": (df.isna().mean() * 100).round(1),
        "unique": df.nunique(),
    })

    insights = []
    high_missing = profile[profile["missing %"] > 20].index.tolist()
    if high_missing:
        insights.append(f"High missingness (>20%): {', '.join(high_missing)}")
    constant_cols = profile[profile["unique"] <= 1].index.tolist()
    if constant_cols:
        insights.append(f"Constant columns (no information): {', '.join(constant_cols)}")
    likely_ids = profile[(profile["unique"] == df.shape[0]) & (df.dtypes != float)].index.tolist()
    if likely_ids:
        insights.append(f"Likely ID columns: {', '.join(likely_ids)}")
    numeric_cols = df.select_dtypes(include="number").columns.tolist()
    for col in numeric_cols:
        skew = df[col].skew()
        if abs(skew) > 1:
            insights.append(f"'{col}' is skewed (skew={skew:.1f}) — consider log transform")
    for col in numeric_cols:
        mean, std = df[col].mean(), df[col].std()
        outliers = ((df[col] - mean).abs() > 3 * std).sum()
        if outliers > 0:
            insights.append(f"'{col}' has {outliers} outlier(s) beyond 3 standard deviations")
    if len(numeric_cols) >= 2:
        corr = df[numeric_cols].corr()
        for i in range(len(numeric_cols)):
            for j in range(i + 1, len(numeric_cols)):
                r = corr.iloc[i, j]
                if abs(r) > 0.7:
                    insights.append(f"'{numeric_cols[i]}' and '{numeric_cols[j]}' are strongly correlated (r={r:.2f})")

    # --- AI Summary (displayed first) ---
    try:
        insights_text = "\n".join(insights) if insights else "No major data quality issues detected."
        with st.spinner("Generating AI summary…"):
            summary = get_ai_summary(insights_text, df.shape[0], df.shape[1])
        st.info(f"**AI Summary:** {summary}")
    except Exception:
        pass  # silently skip if key not configured

    # --- Overview ---
    st.subheader("Overview")
    c1, c2, c3 = st.columns(3)
    c1.metric("Rows", df.shape[0])
    c2.metric("Columns", df.shape[1])
    c3.metric("Missing values", int(df.isna().sum().sum()))

    st.subheader("Preview")
    st.dataframe(df.head(50))

    st.subheader("Column Profile")
    st.dataframe(profile)

    st.subheader("Insights")
    if insights:
        for insight in insights:
            st.write(f"- {insight}")
    else:
        st.write("No major issues detected.")

    if numeric_cols:
        st.subheader("Distribution")
        col = st.selectbox("Pick a numeric column", numeric_cols)
        counts, edges = np.histogram(df[col].dropna(), bins=20)
        hist_df = pd.DataFrame({"count": counts}, index=edges[:-1].round(2))
        st.bar_chart(hist_df)

    if len(numeric_cols) >= 2:
        st.subheader("Correlation Matrix")
        st.dataframe(df[numeric_cols].corr().round(2))

        st.subheader("Scatter")
        x = st.selectbox("X axis", numeric_cols, index=0)
        y = st.selectbox("Y axis", numeric_cols, index=1)
        st.scatter_chart(df, x=x, y=y)

else:
    st.info("Waiting for a CSV — try any dataset (a Kaggle download, a spreadsheet export, anything).")
