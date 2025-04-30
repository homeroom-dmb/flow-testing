# Klaviyo Streamlit App

A Streamlit application to extract Klaviyo Flow performance metrics and rendered HTML.

## Features

- Securely input your Klaviyo API Key in-app (sidebar)
- List all Klaviyo Flows
- Fetch performance metrics (delivered, opens, clicks, conversion rate)
- Retrieve rendered HTML of each email in a Flow
- One-click data extract via a clean UI

## Prerequisites

- Python 3.8+
- Libraries: `streamlit`, `requests`

## Setup & Run

```bash
pip install streamlit requests
streamlit run app.py
```

- **API Key**: Enter your private Klaviyo API Key in the sidebar when the app launches.
- **Conversion Metric ID**: Enter your "Placed Order" metric ID to fetch performance data.

## Deployment

Follow the same Streamlit Cloud deployment steps, no environment variables required since the key is entered in-app.
