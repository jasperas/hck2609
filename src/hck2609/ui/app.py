"""Streamlit front end. Run with: uv run streamlit run src/hck2609/ui/app.py"""

import streamlit as st

from hck2609.pipeline import run_pipeline

st.title("hck2609")

data, insights = run_pipeline()
st.dataframe(data)
for insight in insights:
    st.subheader(insight["title"])
    st.write(insight["summary"])
