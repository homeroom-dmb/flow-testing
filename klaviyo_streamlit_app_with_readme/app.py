import os
import requests
import streamlit as st
from typing import List, Dict

# Klaviyo API configuration
API_BASE = "https://a.klaviyo.com/api"
API_KEY = os.getenv("KLAVIYO_API_KEY")
HEADERS = {
    "Authorization": f"Klaviyo-API-Key {API_KEY}",
    "Revision": "2024-06-15"
}

# Cached functions to call Klaviyo endpoints
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

# Streamlit UI
st.set_page_config(page_title="Klaviyo Flow Extractor", layout="wide")
st.title("📊 Klaviyo Flow Extractor")

# Input for metric ID
task_id = st.text_input("Conversion Metric ID", help="Enter your "Placed Order" metric ID from Klaviyo.")

# Fetch and select Flow
flows = fetch_flows()
flow_map = {f['id']: f['attributes']['name'] for f in flows}
selected_flow = st.selectbox("Select a Flow", options=[None] + list(flow_map.keys()), format_func=lambda x: flow_map.get(x, ""))

if selected_flow:
    timeframe = st.selectbox("Timeframe", ["last_7_days", "last_30_days", "last_90_days"], index=1)
    if st.button("Extract Data"):
        # Metrics
        with st.spinner("Loading performance metrics..."):
            metrics = get_flow_metrics(selected_flow, task_id, timeframe)
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
        with st.spinner("Loading emails and HTML..."):
            emails = []
            actions = get_send_email_actions(selected_flow)
            for action in actions:
                msgs = get_flow_messages(action['id'])
                for msg in msgs:
                    html = get_message_template(msg['id'])
                    emails.append({"Subject": msg['attributes']['content']['subject'], "HTML": html})

        st.subheader("✉️ Emails Preview")
        for email in emails:
            st.markdown(f"**{email['Subject']}**")
            st.components.v1.html(email['HTML'], height=400, scrolling=True)
