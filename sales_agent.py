
import pandas as pd
from google import genai


def analyze_sales(df, client):

    if df.empty:
        return "Sales data available nahi hai."

    df = df.copy()

    df["Revenue"] = pd.to_numeric(
        df["Revenue"], errors="coerce"
    )

    df["Orders"] = pd.to_numeric(
        df["Orders"], errors="coerce"
    )

    df = df.dropna(subset=["Revenue", "Orders"])

    if df.empty:
        return "Valid sales records nahi mile."

    total_revenue = df["Revenue"].sum()
    total_orders = df["Orders"].sum()

    best_day = df.loc[df["Revenue"].idxmax()]
    worst_day = df.loc[df["Revenue"].idxmin()]

    average_order_value = (
        total_revenue / total_orders
        if total_orders else 0
    )

    prompt = f"""
    You are the Sales Analytics Agent of MerchantMind AI.

    Analyze this business sales data.

    Total Revenue: {total_revenue}
    Total Orders: {total_orders}
    Average Order Value: {average_order_value:.2f}

    Best Sales Day: {best_day['Day']}
    Best Day Revenue: {best_day['Revenue']}

    Worst Sales Day: {worst_day['Day']}
    Worst Day Revenue: {worst_day['Revenue']}

    Full Sales Data:
    {df.to_string(index=False)}

    Provide:
    1. Sales performance summary.
    2. Best and worst day analysis.
    3. Revenue trends and possible problems.
    4. Three practical ways to improve sales.

    Use simple language and do not invent figures.
    """

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt
    )

    return response.text
