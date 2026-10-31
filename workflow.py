
from typing import TypedDict, Any
import pandas as pd

from langgraph.graph import StateGraph, START, END

from sales_agent import analyze_sales
from inventory_agent import analyze_inventory
from review_agent import analyze_review


class BusinessState(TypedDict, total=False):
    sales_data: Any
    inventory_data: Any
    review_text: str
    client: Any

    sales_report: str
    inventory_report: str
    review_report: str
    executive_report: str


# SALES AGENT NODE
def sales_node(state: BusinessState):

    result = analyze_sales(
        state["sales_data"],
        state["client"]
    )

    return {"sales_report": result}


# INVENTORY AGENT NODE
def inventory_node(state: BusinessState):

    result = analyze_inventory(
        state["inventory_data"],
        state["client"]
    )

    return {"inventory_report": result}


# CUSTOMER REVIEW AGENT NODE
def review_node(state: BusinessState):

    result = analyze_review(
        state["review_text"],
        state["client"]
    )

    return {"review_report": result}


# CHIEF BUSINESS OFFICER NODE
def cbo_node(state: BusinessState):

    prompt = f"""
    You are the Chief Business Officer of MerchantMind AI.

    Combine the reports from all three AI agents.

    SALES AGENT REPORT:
    {state["sales_report"]}

    INVENTORY AGENT REPORT:
    {state["inventory_report"]}

    CUSTOMER REVIEW AGENT REPORT:
    {state["review_report"]}

    Prepare an executive business report containing:

    1. Overall Business Health
    2. Sales Performance
    3. Inventory Situation
    4. Customer Satisfaction
    5. Top 5 Business Priorities
    6. Action Plan
    7. Final CEO-Level Advice

    Use practical recommendations.
    Do not invent business figures.
    """

    response = state["client"].models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt
    )

    return {
        "executive_report": response.text or
        "Executive report could not be generated."
    }


# BUILD LANGGRAPH WORKFLOW
builder = StateGraph(BusinessState)

builder.add_node("sales_agent", sales_node)
builder.add_node("inventory_agent", inventory_node)
builder.add_node("review_agent", review_node)
builder.add_node("chief_business_officer", cbo_node)

builder.add_edge(START, "sales_agent")
builder.add_edge(START, "inventory_agent")
builder.add_edge(START, "review_agent")

builder.add_edge("sales_agent", "chief_business_officer")
builder.add_edge("inventory_agent", "chief_business_officer")
builder.add_edge("review_agent", "chief_business_officer")

builder.add_edge("chief_business_officer", END)

business_workflow = builder.compile()


def run_business_workflow(
    sales_data,
    inventory_data,
    review_text,
    client
):

    result = business_workflow.invoke({
        "sales_data": sales_data,
        "inventory_data": inventory_data,
        "review_text": review_text,
        "client": client
    })

    return result["executive_report"]
