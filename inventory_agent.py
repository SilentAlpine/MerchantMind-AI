import pandas as pd
def analyze_inventory(df, client):

    if df.empty:
        return "Inventory data available nahi hai."

    df = df.copy()

    df["Stock"] = pd.to_numeric(df["Stock"], errors="coerce")
    df["Minimum Stock"] = pd.to_numeric(
        df["Minimum Stock"], errors="coerce"
    )

    df = df.dropna(
        subset=["Product", "Stock", "Minimum Stock"]
    )

    if df.empty:
        return "Valid inventory records nahi mile."

    low_stock = df[
        df["Stock"] < df["Minimum Stock"]
    ]

    prompt = f"""
    You are the Inventory Management Agent of MerchantMind AI.

    Analyze this inventory data.

    Complete Inventory:
    {df.to_string(index=False)}

    Products requiring restocking:
    {low_stock.to_string(index=False)}

    Provide:
    1. Current inventory health.
    2. Products that need restocking.
    3. How much additional stock is needed to reach minimum stock.
    4. Three practical inventory management suggestions.

    Use only the supplied figures. Do not invent data.
    """

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt
    )

    return response.text
