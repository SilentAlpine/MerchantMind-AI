
def analyze_review(review_text, client):

    if not review_text.strip():
        return "Please enter a customer review."

    prompt = f"""
    You are the Customer Review Agent of MerchantMind AI.

    Analyze this customer review:

    {review_text}

    Give your analysis in this format:

    1. Sentiment: Positive, Negative or Neutral
    2. Customer's Main Concern:
    3. What Customer Likes:
    4. Suggested Business Action:
    5. Priority: HIGH, MEDIUM or LOW
    6. Short Business Improvement Suggestion:

    Be practical and do not invent information.
    """

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt
    )

    return response.text
