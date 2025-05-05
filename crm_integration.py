import pandas as pd
import os

CRM_PATH = os.path.join(os.path.dirname(__file__), 'dummy_crm.csv')
INTERACTIONS_PATH = os.path.join(os.path.dirname(__file__), 'crm_interactions.csv')

# Load CRM data into a DataFrame (cached)
def load_crm():
    return pd.read_csv(CRM_PATH)

def load_interactions():
    return pd.read_csv(INTERACTIONS_PATH)

def fetch_customer_profile(crm_id):
    df = load_crm()
    row = df[df['customer_id'] == crm_id]
    if row.empty:
        return "No profile found for this CRM ID."
    r = row.iloc[0]
    profile = f"Name: {r['name']}\nCompany: {r['company']}\nIndustry: {r['industry']}\nRole: {r['role']}\nNeeds: {r['needs']}\nEngagement: {r['engagement']}\nEmail: {r['contact_email']}\nPhone: {r['phone']}"
    return profile

def fetch_last_interaction(crm_id):
    df = load_interactions()
    cust = df[df['customer_id'] == crm_id]
    if cust.empty:
        return None
    last = cust.sort_values('date', ascending=False).iloc[0]
    return {
        'date': last['date'],
        'summary': last['summary'],
        'interaction_type': last['interaction_type'],
        'status': last['status']
    }

def fetch_all_interactions(crm_id):
    df = load_interactions()
    cust = df[df['customer_id'] == crm_id]
    if cust.empty:
        return []
    return cust.sort_values('date', ascending=False).to_dict(orient='records')

def list_customers():
    df = load_crm()
    return df[['customer_id', 'name', 'company', 'needs']].to_dict(orient='records')

def add_interaction(crm_id, summary, interaction_type, status, date=None):
    import datetime
    df = load_interactions()
    if date is None:
        date = datetime.datetime.now().strftime('%Y-%m-%d')
    new_id = f"INT{str(len(df)+1).zfill(3)}"
    new_row = {
        'customer_id': crm_id,
        'interaction_id': new_id,
        'date': date,
        'summary': summary,
        'interaction_type': interaction_type,
        'status': status
    }
    df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
    df.to_csv(INTERACTIONS_PATH, index=False)
    return new_row
