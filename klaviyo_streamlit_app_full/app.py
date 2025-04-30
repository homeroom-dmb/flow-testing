import os
import requests
import streamlit as st
from typing import List, Dict

# Must be called first
st.set_page_config(page_title="Klaviyo Flow Extractor", layout="wide")

# Sidebar for API Key entry
st.sidebar.title("🔑 Klaviyo Config")
api_key = st.sidebar.text_input("Klaviyo API Key", type="password", help="Enter your private Klaviyo API Key")
if not api_key:
    st.sidebar.warning("Please enter your Klaviyo API Key to proceed.")
    st.stop()

# Conversion metric ID input
conversion_metric_id = st.text_input("Conversion Metric ID", help="Enter your 'Placed Order' metric ID from Klaviyo")
if not conversion_metric_id:
    st.warning("Please enter a Conversion Metric ID to fetch performance data.")
    st.stop()

# Klaviyo API base URL
API_BASE = "https://a.klaviyo.com/api"
HEADERS = {
    "Authorization": f"Klaviyo-API-Key {api_key}",
    "Revision": "2024-06-15"
}

# Cached Klaviyo calls
@st.cache_data(show_spinner=False)
def fetch_flows() -> List[Dict]:
    resp = requests.get(f"{API_BASE}/flows", headers=HEADERS)
    resp.raise_for_status()
    return resp.json().get("data", [])

@st.cache_data(show_spinner=False)
def get_send_email_actions(flow_id: str) -> List[Dict]:
    params = {"filter": 'equals(action_type,"SEND_EMAIL")'}
    resp = requests.get(f"{API_BASE}/flows/{flow_id}/flow-actions", headers=HEADERS, params=params)
    resp.raise_for_status()
    return resp.json().get("data", [])

@st.cache_data(show_spinner=False)
def get_flow_messages(action_id: str) -> List[Dict]:
    resp = requests.get(f"{API_BASE}/flow-actions/{action_id}/flow-messages", headers=HEADERS)
    resp.raise_for_status()
    return resp.json().get("data", [])

@st.cache_data(show_spinner=False)
def get_message_template(message_id: str) -> str:
    resp = requests.get(f"{API_BASE}/flow-messages/{message_id}/template/", headers=HEADERS)
    resp.raise_for_status()
    return resp.json().get("data", {}).get("attributes", {}).get("html", "")

@st.cache_data(show_spinner=False)
def get_flow_metrics(flow_id: str, conversion_metric_id: str, timeframe: str) -> List[Dict]:
    payload = {
        "data": {
            "type": "flow-values-report",
            "attributes": {
                "timeframe": {"key": timeframe},
                "conversion_metric_id": conversion_metric_id,
                "filter": f'equals(flow_id,"{flow_id}")',
                "statistics": [
                    "delivered","opens","open_rate",
                    "clicks","clicks_unique","conversion_rate"
                ]
            }
        }
    }
    resp = requests.post(f"{API_BASE}/flow-values-reports/", headers={**HEADERS, "Content-Type": "application/json"}, json=payload)
    resp.raise_for_status()
    return resp.json().get("data", {}).get("attributes", {}).get("results", [])

# Main UI Title
st.title("📊 Klaviyo Flow Extractor")

# Fetch and select flows
try:
    flows = fetch_flows()
except requests.HTTPError as e:
    st.error(f"Failed to fetch flows: {e}")
    st.stop()

flow_map = {f['id']: f['attributes']['name'] for f in flows}
selected_flow = st.selectbox("Select a Flow", options=[""] + list(flow_map.keys()), format_func=lambda x: flow_map.get(x, ""))

if selected_flow:
    timeframe = st.selectbox("Timeframe", ["last_7_days", "last_30_days", "last_90_days"], index=1)
    if st.button("Extract Data"):
        # Metrics
        try:
            with st.spinner("Loading performance metrics..."):
                metrics = get_flow_metrics(selected_flow, conversion_metric_id, timeframe)
        except requests.HTTPError as e:
            st.error(f"Error fetching metrics: {e}")
            metrics = []

        if metrics:
            st.subheader("🔍 Performance Metrics")
            table = []
            for m in metrics:
                stats = m['statistics']
                table.append({
                    "Message ID": m['groupings']['flow_message_id'],
                    "Delivered": stats['delivered'],
                    "Opens": stats['opens'],
                    "Open Rate": f"{stats['open_rate']*100:.1f}%",
                    "Clicks": stats['clicks'],
                    "Unique Clicks": stats['clicks_unique'],
                    "Conversion Rate": f"{stats['conversion_rate']*100:.1f}%"
                })
            st.table(table)
        else:
            st.warning("No metrics found for this flow.")

        # Emails
        try:
            with st.spinner("Loading emails and HTML..."):
                emails = []
                actions = get_send_email_actions(selected_flow)
                for action in actions:
                    msgs = get_flow_messages(action['id'])
                    for msg in msgs:
                        html = get_message_template(msg['id'])
                        emails.append({"Subject": msg['attributes']['content']['subject'], "HTML": html})
        except requests.HTTPError as e:
            st.error(f"Error fetching emails: {e}")
            emails = []

        if emails:
            st.subheader("✉️ Emails Preview")
            for email in emails:
                st.markdown(f"**{email['Subject']}**")
                st.components.v1.html(email['HTML'], height=400, scrolling=True)
        else:
            st.info("No emails to preview or an error occurred.")
