# GenAI-powered Sales Assistant

This app helps sales teams craft personalized pitches, automate follow-ups, and surface actionable insights from calls and customer data. Powered by Azure OpenAI and Streamlit.

## Features
- Personalized pitch generation
- Omnichannel output (email, call scripts, LinkedIn, chatbots)
- Automated follow-up sequencing
- Call transcript summarization and sentiment analysis
- Analytics dashboard for KPIs
- CRM integration (Salesforce, HubSpot, etc.)
- Security and cost controls with Azure Key Vault

## Running Locally
1. Install dependencies: `pip install -r requirements.txt`
2. Add your Azure OpenAI credentials to `.streamlit/secrets.toml`
3. Run: `streamlit run app.py`

## Configuration
- Set Azure credentials and CRM API keys in the sidebar.
- Use the tabs to generate pitches, summarize calls, and view analytics.
