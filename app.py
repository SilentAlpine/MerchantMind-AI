
import streamlit as st
import pandas as pd
import plotly.express as px
import os
import json
from dotenv import load_dotenv
from google import genai
from database import init_db, save_data, load_data
from sales_agent import analyze_sales
from inventory_agent import analyze_inventory
from review_agent import analyze_review
from cbo_agent import generate_business_report

init_db()


# --------------------------------------------------
# 1. PAGE CONFIGURATION
# --------------------------------------------------

st.set_page_config(
    page_title="MerchantMind AI",
    page_icon="🧠",
    layout="wide"
)

load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY")

client = None

if API_KEY and API_KEY != "YOUR_ACTUAL_API_KEY":
    client = genai.Client(api_key=API_KEY)


# --------------------------------------------------
# 2. SESSION STATE
# --------------------------------------------------

if "uploaded_sales" not in st.session_state:
    st.session_state.uploaded_sales = None

if "uploaded_inventory" not in st.session_state:
    st.session_state.uploaded_inventory = None

if "messages" not in st.session_state:
    st.session_state.messages = []

if "ai_recommendations" not in st.session_state:
    st.session_state.ai_recommendations = None


# --------------------------------------------------
# 3. SAMPLE BUSINESS DATA
# --------------------------------------------------

sample_sales = pd.DataFrame({
    "Day": [
        "Monday", "Tuesday", "Wednesday",
        "Thursday", "Friday", "Saturday", "Sunday"
    ],
    "Revenue": [
        5000, 6500, 4000, 7200, 8500, 10500, 7800
    ],
    "Orders": [
        50, 65, 40, 72, 85, 105, 78
    ]
})

sample_inventory = pd.DataFrame({
    "Product": [
        "Coffee", "Burger", "Pizza",
        "Sandwich", "Cold Coffee"
    ],
    "Stock": [12, 45, 8, 30, 5],
    "Minimum Stock": [20, 15, 10, 15, 10]
})


sales_data = sample_sales.copy()
inventory_data = sample_inventory.copy()

if st.session_state.uploaded_sales is not None:
    sales_data = st.session_state.uploaded_sales.copy()

if st.session_state.uploaded_inventory is not None:
    inventory_data = st.session_state.uploaded_inventory.copy()


# --------------------------------------------------
# 4. DATA VALIDATION
# --------------------------------------------------

def validate_sales(df):

    required = ["Day", "Revenue", "Orders"]

    if not all(col in df.columns for col in required):
        raise ValueError(
            "Sales file must contain Day, Revenue and Orders columns."
        )

    df = df[required].copy()

    df["Revenue"] = pd.to_numeric(
        df["Revenue"], errors="coerce"
    )

    df["Orders"] = pd.to_numeric(
        df["Orders"], errors="coerce"
    )

    df = df.dropna(subset=["Day", "Revenue", "Orders"])

    return df


def validate_inventory(df):

    required = ["Product", "Stock", "Minimum Stock"]

    if not all(col in df.columns for col in required):
        raise ValueError(
            "Inventory file must contain Product, Stock and Minimum Stock columns."
        )

    df = df[required].copy()

    df["Stock"] = pd.to_numeric(
        df["Stock"], errors="coerce"
    )

    df["Minimum Stock"] = pd.to_numeric(
        df["Minimum Stock"], errors="coerce"
    )

    df = df.dropna(
        subset=["Product", "Stock", "Minimum Stock"]
    )

    return df


def read_business_file(file, sheet_name=0):

    if file.name.lower().endswith(".csv"):
        return pd.read_csv(file)

    return pd.read_excel(
        file,
        sheet_name=sheet_name
    )


# --------------------------------------------------
# 5. BUSINESS CALCULATIONS
# --------------------------------------------------

total_revenue = sales_data["Revenue"].sum()
total_orders = sales_data["Orders"].sum()

average_order_value = (
    total_revenue / total_orders
    if total_orders > 0 else 0
)

if not sales_data.empty:
    best_day_row = sales_data.loc[
        sales_data["Revenue"].idxmax()
    ]

    worst_day_row = sales_data.loc[
        sales_data["Revenue"].idxmin()
    ]

    best_day = best_day_row["Day"]
    best_day_revenue = best_day_row["Revenue"]

    worst_day = worst_day_row["Day"]
    worst_day_revenue = worst_day_row["Revenue"]

else:
    best_day = "N/A"
    worst_day = "N/A"
    best_day_revenue = 0
    worst_day_revenue = 0


low_stock = inventory_data[
    inventory_data["Stock"] < inventory_data["Minimum Stock"]
]


business_context = f"""
You are MerchantMind AI, an intelligent business management assistant.

Analyze the following business data.

SALES DATA:
{sales_data.to_string(index=False)}

INVENTORY DATA:
{inventory_data.to_string(index=False)}

BUSINESS METRICS:
Total Revenue: {total_revenue}
Total Orders: {total_orders}
Average Order Value: {average_order_value:.2f}
Best Sales Day: {best_day}
Best Day Revenue: {best_day_revenue}
Worst Sales Day: {worst_day}
Worst Day Revenue: {worst_day_revenue}

LOW STOCK PRODUCTS:
{low_stock.to_string(index=False)}

Give practical, accurate and easy-to-understand business advice.
Use only the supplied data for numerical claims.
"""


# --------------------------------------------------
# 6. SIDEBAR NAVIGATION
# --------------------------------------------------

st.sidebar.title("🧠 MerchantMind AI")

st.sidebar.caption(
    "Your AI-powered business manager"
)

page = st.sidebar.radio(
    "Navigation",
    [
        "Overview",
        "Sales Analytics",
        "Inventory",
        "Customer Reviews",
        "AI Business Manager",
        "AI Recommendations",
        "Chief Business Officer",
        "Reports",
        "Upload Business Data"
    ]
)

st.sidebar.divider()

st.sidebar.caption("MerchantMind AI")

if st.session_state.uploaded_sales is not None:
    st.sidebar.success("Sales data uploaded")

if st.session_state.uploaded_inventory is not None:
    st.sidebar.success("Inventory data uploaded")

saved_sales = load_data("sales")
saved_inventory = load_data("inventory")

if not saved_sales.empty:
    sales_data = saved_sales

if not saved_inventory.empty:
    inventory_data = saved_inventory

# --------------------------------------------------
# 7. OVERVIEW DASHBOARD
# --------------------------------------------------

if page == "Overview":

    st.title("📊 Business Overview")

    st.write(
        "Welcome to your MerchantMind AI dashboard."
    )

    col1, col2, col3, col4 = st.columns(4)

    col1.metric(
        "Total Revenue",
        f"${total_revenue:,.2f}"
    )

    col2.metric(
        "Total Orders",
        f"{total_orders:,.0f}"
    )

    col3.metric(
        "Average Order Value",
        f"${average_order_value:,.2f}"
    )

    col4.metric(
        "Low Stock Items",
        len(low_stock)
    )

    st.divider()

    st.subheader("Revenue Overview")

    fig = px.bar(
        sales_data,
        x="Day",
        y="Revenue",
        title="Daily Revenue",
        text_auto=True
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

    st.subheader("Inventory Status")

    st.dataframe(
        inventory_data,
        use_container_width=True,
        hide_index=True
    )

    if not low_stock.empty:

        st.warning(
            f"{len(low_stock)} products are below minimum stock."
        )

        st.dataframe(
            low_stock,
            use_container_width=True,
            hide_index=True
        )

    else:
        st.success("All products have sufficient stock.")


# --------------------------------------------------
# 8. SALES ANALYTICS
# --------------------------------------------------

elif page == "Sales Analytics":

    st.title("📈 Sales Analytics")

    col1, col2, col3 = st.columns(3)

    col1.metric(
        "Total Revenue",
        f"${total_revenue:,.2f}"
    )

    col2.metric(
        "Total Orders",
        f"{total_orders:,.0f}"
    )

    col3.metric(
        "Average Order Value",
        f"${average_order_value:,.2f}"
    )

    st.divider()

    st.subheader("Daily Revenue")

    revenue_chart = px.bar(
        sales_data,
        x="Day",
        y="Revenue",
        title="Revenue by Day",
        text_auto=True
    )

    st.plotly_chart(
        revenue_chart,
        use_container_width=True
    )

    st.subheader("Daily Orders")

    orders_chart = px.line(
        sales_data,
        x="Day",
        y="Orders",
        markers=True,
        title="Orders by Day"
    )

    st.plotly_chart(
        orders_chart,
        use_container_width=True
    )

    col1, col2 = st.columns(2)

    with col1:
        st.success(
            f"Best Sales Day: {best_day} "
            f"(${best_day_revenue:,.2f})"
        )

    with col2:
        st.error(
            f"Worst Sales Day: {worst_day} "
            f"(${worst_day_revenue:,.2f})"
        )

    st.subheader("Sales Data")
    st.divider()

    st.subheader("🤖 AI Sales Analytics Agent")

    if st.button("Analyze Sales with AI"):

        if client is None:
            st.error("Gemini API key configure nahi hai.")

        else:
            with st.spinner("AI analyzing sales..."):

                try:
                    result = analyze_sales(sales_data, client)
                    st.markdown(result)

                except Exception as e:
                    st.error(f"Sales Agent Error: {e}")

    st.dataframe(
        sales_data,
        use_container_width=True,
        hide_index=True
    )


# --------------------------------------------------
# 9. INVENTORY MANAGEMENT
# --------------------------------------------------

elif page == "Inventory":

    st.title("📦 Inventory Management")

    st.metric(
        "Total Products",
        len(inventory_data)
    )

    st.metric(
        "Products Requiring Restock",
        len(low_stock)
    )

    st.divider()

    st.subheader("Complete Inventory")

    st.dataframe(
        inventory_data,
        use_container_width=True,
        hide_index=True
    )

    st.subheader("Restock Alerts")

    st.divider()

    st.subheader("🤖 AI Inventory Management Agent")

    if st.button("Analyze Inventory with AI"):

        if client is None:
            st.error("Gemini API key configure nahi hai.")

        else:
            with st.spinner("AI analyzing inventory..."):

                try:
                    result = analyze_inventory(
                        inventory_data, client
                    )

                    st.markdown(result)

                except Exception as e:
                    st.error(f"Inventory Agent Error: {e}")
# --------------------------------------------------
# 10. CUSTOMER REVIEWS
# --------------------------------------------------


elif page == "Customer Reviews":

    st.title("⭐ Customer Review Agent")

    st.write(
        "Analyze customer feedback using Gemini AI."
    )

    review_text = st.text_area(
        "Paste Customer Review",
        placeholder="Example: Food was delicious but delivery was very late..."
    )

    if st.button("Analyze Customer Review", type="primary"):

        if not review_text.strip():

            st.warning("Please enter a customer review.")

        elif client is None:

            st.error("Gemini API key is not configured.")

        else:

            with st.spinner("Analyzing customer feedback..."):

                try:

                    result = analyze_review(
                        review_text,
                        client
                    )

                    st.subheader("AI Review Analysis")
                    st.markdown(result)

                except Exception as e:

                    st.error(f"Review Agent Error: {e}")


# --------------------------------------------------
# 11. AI BUSINESS MANAGER CHATBOT
# --------------------------------------------------

elif page == "AI Business Manager":

    st.title("🤖 AI Business Manager")

    st.write(
        "Ask questions about your sales, inventory and business."
    )

    for message in st.session_state.messages:

        with st.chat_message(message["role"]):

            st.markdown(message["content"])

    user_prompt = st.chat_input(
        "Ask your AI Business Manager..."
    )

    if user_prompt:

        st.session_state.messages.append({
            "role": "user",
            "content": user_prompt
        })

        with st.chat_message("user"):
            st.markdown(user_prompt)

        with st.chat_message("assistant"):

            if client is None:

                answer = (
                    "Gemini API key is not configured. "
                    "Please check your .env file."
                )

                st.error(answer)

            else:

                with st.spinner("Analyzing your business..."):

                    try:

                        conversation = ""

                        for msg in st.session_state.messages[-10:]:

                            conversation += (
                                f"{msg['role']}: "
                                f"{msg['content']}\n"
                            )

                        response = client.models.generate_content(
                            model="gemini-2.5-flash",
                            contents=f"""
                            {business_context}

                            Conversation:
                            {conversation}

                            Answer the user's latest question.
                            Be practical and specific.
                            """
                        )

                        answer = response.text or (
                            "AI could not generate a response."
                        )

                        st.markdown(answer)

                    except Exception as e:

                        answer = f"AI Error: {e}"

                        st.error(answer)

        st.session_state.messages.append({
            "role": "assistant",
            "content": answer
        })


# --------------------------------------------------
# 12. AI RECOMMENDATIONS
# --------------------------------------------------

elif page == "AI Recommendations":

    st.title("💡 AI Business Recommendations")

    st.write(
        "Get five practical recommendations based on your business data."
    )

    if st.button(
        "Generate AI Recommendations",
        type="primary"
    ):

        if client is None:

            st.error(
                "Gemini API key is not configured. "
                "Check your .env file."
            )

        else:

            with st.spinner(
                "AI is analyzing your business..."
            ):

                try:

                    response = client.models.generate_content(
                        model="gemini-2.5-flash",
                        contents=f"""
                        {business_context}

                        Generate exactly 5 practical business recommendations.

                        Return ONLY valid JSON.
                        Do not use markdown code fences.

                        Use this exact structure:

                        {{
                            "recommendations": [
                                {{
                                    "title": "Recommendation title",
                                    "priority": "HIGH",
                                    "problem": "Problem identified",
                                    "action": "Recommended action",
                                    "impact": "Expected business impact"
                                }}
                            ]
                        }}

                        Priority must be HIGH, MEDIUM or LOW.

                        Recommendations must be based on the supplied data.
                        Do not invent business figures.
                        """
                    )

                    recommendation_text = response.text

                    if not recommendation_text:

                        st.error(
                            "AI could not generate recommendations."
                        )

                    else:

                        clean_json = recommendation_text.strip()

                        if clean_json.startswith("```"):

                            clean_json = clean_json.split(
                                "\n", 1
                            )[1]

                            clean_json = clean_json.rsplit(
                                "```", 1
                            )[0].strip()

                        recommendations = json.loads(
                            clean_json
                        )

                        if not isinstance(
                            recommendations.get("recommendations"),
                            list
                        ):

                            raise ValueError(
                                "Invalid recommendations format"
                            )

                        st.session_state.ai_recommendations = (
                            recommendations
                        )

                except (
                    json.JSONDecodeError,
                    ValueError,
                    AttributeError
                ):

                    st.error(
                        "AI response format is incorrect. "
                        "Please generate again."
                    )

                except Exception as e:

                    st.error(
                        f"Recommendation Error: {e}"
                    )

    # Display saved recommendations

    saved_data = st.session_state.get(
        "ai_recommendations"
    )

    if saved_data:

        st.divider()

        st.subheader(
            "Your Business Recommendations"
        )

        recommendations_list = saved_data["recommendations"]

        for i, rec in enumerate(
            recommendations_list,
            start=1
        ):

            priority = str(
                rec.get("priority", "MEDIUM")
            ).upper()

            if priority == "HIGH":
                priority_icon = "🔴"

            elif priority == "MEDIUM":
                priority_icon = "🟡"

            else:
                priority_icon = "🟢"

            with st.container(border=True):

                st.markdown(
                    f"### {i}. {rec.get('title', 'Recommendation')}"
                )

                st.markdown(
                    f"**Priority:** {priority_icon} {priority}"
                )

                st.markdown(
                    f"**Problem:** "
                    f"{rec.get('problem', 'Not provided')}"
                )

                st.markdown(
                    f"**Recommended Action:** "
                    f"{rec.get('action', 'Not provided')}"
                )

                st.markdown(
                    f"**Expected Impact:** "
                    f"{rec.get('impact', 'Not provided')}"
                )


# --------------------------------------------------
# 13. REPORTS
# --------------------------------------------------

elif page == "Chief Business Officer":

    st.title("👔 Chief Business Officer")

    st.write(
        "Your central AI manager combines insights from all business agents."
    )

    review_text = st.text_area(
        "Enter a customer review for the combined report",
        placeholder="Food was excellent but delivery was late..."
    )

    if st.button("Generate Executive Business Report", type="primary"):

        if client is None:

            st.error("Gemini API key is not configured.")

        elif not review_text.strip():

            st.warning("Please enter a customer review.")

        else:

            with st.spinner(
                "Chief Business Officer is coordinating all agents..."
            ):

                try:

                    report = generate_business_report(
                        sales_data,
                        inventory_data,
                        review_text,
                        client
                    )

                    st.session_state["cbo_report"] = report

                except Exception as e:

                    st.error(f"CBO Error: {e}")

    if st.session_state.get("cbo_report"):

        st.divider()

        st.subheader("📊 Executive Business Report")

        st.markdown(
            st.session_state["cbo_report"]
        )

        st.download_button(
            "Download Executive Report",
            data=st.session_state["cbo_report"],
            file_name="MerchantMind_Executive_Report.txt",
            mime="text/plain"
        )


elif page == "Reports":

    st.title("📑 Business Reports")

    st.write(
        "View and download your current business data."
    )

    st.subheader("Business Summary")

    report_data = pd.DataFrame({
        "Metric": [
            "Total Revenue",
            "Total Orders",
            "Average Order Value",
            "Best Sales Day",
            "Worst Sales Day",
            "Low Stock Products"
        ],

        "Value": [
            total_revenue,
            total_orders,
            round(average_order_value, 2),
            best_day,
            worst_day,
            len(low_stock)
        ]
    })

    st.dataframe(
        report_data,
        use_container_width=True,
        hide_index=True
    )

    sales_csv = sales_data.to_csv(
        index=False
    ).encode("utf-8")

    st.download_button(
        "Download Sales Report",
        data=sales_csv,
        file_name="merchantmind_sales_report.csv",
        mime="text/csv"
    )

    inventory_csv = inventory_data.to_csv(
        index=False
    ).encode("utf-8")

    st.download_button(
        "Download Inventory Report",
        data=inventory_csv,
        file_name="merchantmind_inventory_report.csv",
        mime="text/csv"
    )

    report_csv = report_data.to_csv(
        index=False
    ).encode("utf-8")

    st.download_button(
        "Download Business Summary",
        data=report_csv,
        file_name="merchantmind_business_summary.csv",
        mime="text/csv"
    )


# --------------------------------------------------
# 14. UPLOAD BUSINESS DATA
# --------------------------------------------------

elif page == "Upload Business Data":

    st.title("📂 Upload Business Data")

    st.write(
        "Upload your Excel or CSV files to analyze your business."
    )

    st.info(
        "For Excel workbooks, upload the same workbook "
        "in both sections. Sales uses the Sales sheet "
        "and Inventory uses the Inventory sheet."
    )

    st.divider()

    st.subheader("Upload Sales Data")

    sales_file = st.file_uploader(
        "Choose Sales Excel or CSV file",
        type=["xlsx", "xls", "csv"],
        key="sales_upload"
    )

    if sales_file is not None:

        try:

            df = read_business_file(
                sales_file,
                sheet_name="Sales"
            )

            df = validate_sales(df)

            st.session_state.uploaded_sales = df
            save_data(df, "sales")

            st.success(
                "Sales data uploaded successfully!"
            )

            st.dataframe(
                df,
                use_container_width=True,
                hide_index=True
            )

        except Exception as e:

            st.error(
                f"Sales Upload Error: {e}"
            )

    st.divider()

    st.subheader("Upload Inventory Data")

    inventory_file = st.file_uploader(
        "Choose Inventory Excel or CSV file",
        type=["xlsx", "xls", "csv"],
        key="inventory_upload"
    )

    if inventory_file is not None:

        try:

            df = read_business_file(
                inventory_file,
                sheet_name="Inventory"
            )

            df = validate_inventory(df)

            st.session_state.uploaded_inventory = df
            save_data(df, "inventory")

            st.success(
                "Inventory data uploaded successfully!"
            )

            st.dataframe(
                df,
                use_container_width=True,
                hide_index=True
            )

        except Exception as e:

            st.error(
                f"Inventory Upload Error: {e}"
            )

    st.divider()

    if st.button("Reset Uploaded Data"):

        st.session_state.uploaded_sales = None

        st.session_state.uploaded_inventory = None

        st.session_state.ai_recommendations = None

        st.success(
            "Uploaded data reset. Refresh the application."
        )

        st.rerun()
