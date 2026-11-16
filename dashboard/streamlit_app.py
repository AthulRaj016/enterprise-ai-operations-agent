"""Streamlit demonstration frontend for the deterministic intake MVP."""
import os

import requests
import streamlit as st

API_BASE_URL = os.getenv("OPERATIONS_API_URL", "http://localhost:8000")
st.set_page_config(page_title="Enterprise AI Operations Agent", page_icon="🧭", layout="wide")
st.title("Enterprise AI Operations Agent")
st.caption("Phase 1 — operational request intake and triage (rule-based MVP; no LLM yet)")

with st.form("new_request"):
    department = st.selectbox("Department", ["HR", "Finance", "IT", "Legal Operations", "Other"])
    description = st.text_area("Describe the operational request")
    submitted = st.form_submit_button("Submit for review")
    if submitted:
        try:
            response = requests.post(
                f"{API_BASE_URL}/requests",
                json={"department": department, "description": description},
                timeout=10,
            )
            response.raise_for_status()
            st.success("Request recorded for review")
            st.json(response.json())
        except requests.RequestException as error:
            st.error(f"API request failed: {error}")

st.subheader("Request tracker")
if st.button("Refresh requests"):
    st.rerun()
try:
    response = requests.get(f"{API_BASE_URL}/requests", timeout=10)
    response.raise_for_status()
    records = response.json()
    if records:
        st.dataframe(records, use_container_width=True, hide_index=True)
    else:
        st.info("No requests submitted yet.")
except requests.RequestException as error:
    st.warning(f"Unable to load requests: {error}")
