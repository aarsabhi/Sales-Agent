import pandas as pd

def get_kpi_dataframe(view):
    # Example data, replace with real analytics/DB queries
    data = [
        {"Customer": "Acme Corp", "Avg Response Length": 120, "Sentiment": "Positive", "Follow-Up Success": 0.8},
        {"Customer": "Beta Inc", "Avg Response Length": 90, "Sentiment": "Neutral", "Follow-Up Success": 0.6},
        {"Customer": "Gamma LLC", "Avg Response Length": 140, "Sentiment": "Negative", "Follow-Up Success": 0.3},
    ]
    df = pd.DataFrame(data)
    if view == "KPIs":
        return df[["Customer", "Avg Response Length", "Sentiment", "Follow-Up Success"]]
    else:
        return df
