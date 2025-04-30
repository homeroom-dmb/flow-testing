# Klaviyo Streamlit App

A simple Streamlit application to extract Klaviyo Flow performance metrics and rendered HTML for your email messages.

## Features

- List all Klaviyo Flows in your account
- Fetch performance metrics (delivered, opens, clicks, conversion rate)
- Retrieve rendered HTML of each email in a Flow
- One-click data extract via Streamlit interface

## Prerequisites

- Python 3.8 or higher
- A Klaviyo account with a valid API Key
- Streamlit installed (`pip install streamlit`)
- Requests library installed (`pip install requests`)

## Setup

1. **Clone** this repository (or unzip the provided archive):

   ```bash
   git clone <your-repo-url>
   cd <repo-directory>
   ```

2. **Install dependencies**:

   ```bash
   pip install streamlit requests
   ```

3. **Set your environment variable**:

   On macOS/Linux:
   ```bash
   export KLAVIYO_API_KEY="<your_api_key_here>"
   ```
   On Windows (PowerShell):
   ```powershell
   setx KLAVIYO_API_KEY "<your_api_key_here>"
   ```

## Running Locally

```bash
streamlit run app.py
```

The app will open in your default browser. Enter your **Conversion Metric ID**, select a Flow, and click **Extract Data**.

## Deployment

1. Push your code to a GitHub repository.
2. Log in to [Streamlit Cloud](https://streamlit.io/cloud).
3. Click **New app**, connect your GitHub repo, and deploy.
4. In the **Secrets** section of your app settings, add `KLAVIYO_API_KEY`.

## Troubleshooting

- **401 Unauthorized**: Verify your `KLAVIYO_API_KEY` is correct.
- **Network errors**: Ensure you have internet access and Klaviyo API is reachable.
