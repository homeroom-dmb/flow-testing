
import requests
import streamlit as st
from datetime import datetime, timedelta

st.set_page_config(page_title="Klaviyo Flow Extractor", layout="wide")

st.sidebar.header("🔐 Klaviyo API Key")
api_key = st.sidebar.text_input("Enter your Klaviyo Private API Key", type="password")

def klaviyo_get(endpoint, params=None):
    headers = {"Authorization": f"Klaviyo-API-Key {api_key}"}
    url = f"https://a.klaviyo.com/api/{endpoint}"
    response = requests.get(url, headers=headers, params=params)
    response.raise_for_status()
    return response.json()

if api_key:
    try:
        st.header("📩 Available Flows")
        flow_data = klaviyo_get("flows/")
        flow_options = {f["attributes"]["name"]: f["id"] for f in flow_data["data"]}
        flow_name = st.selectbox("Select a Flow", list(flow_options.keys()))
        selected_flow_id = flow_options[flow_name]

        st.subheader(f"Emails in Flow: {flow_name}")
        actions = klaviyo_get("flow-actions/", params={"filter": f"flow_id=={selected_flow_id}"})
        emails = [a for a in actions["data"] if a["attributes"]["action_type"] == "EMAIL"]

        for email in emails:
            st.markdown("---")
            name = email["attributes"]["name"]
            email_id = email["id"]
            st.markdown(f"### ✉️ {name}")
            st.write(f"Email ID: {email_id}")
            st.write("📊 Performance (last 90 days):")
            st.write("Open Rate: (mocked)")
            st.write("Click Rate: (mocked)")
            st.write("Revenue: (mocked)")

    except Exception as e:
        st.error(f"Error: {e}")
else:
    st.info("Please enter your Klaviyo API key to begin.")
