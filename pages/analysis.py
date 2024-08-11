import streamlit as st
import pandas as pd
import plotly.express as px
from pymongo import MongoClient
from bson import ObjectId

# MongoDB connection
username = st.secrets["mongodb"]["username"]
password = st.secrets["mongodb"]["password"]
hostname = st.secrets["mongodb"]["hostname"]
port = st.secrets["mongodb"]["port"]

connection_uri = f"mongodb+srv://{username}:{password}@{hostname}:{port}"
client = MongoClient(connection_uri)

db = client["receipt-data"]
collection = db["test1"]

# Helper functions
def get_total_purchases_breakdown():
    result = list(collection.find({}, {"_id": 1, "TOTAL AMOUNT": 1}))
    df = pd.DataFrame(result)
    df['_id'] = df['_id'].astype(str)
    df = df.rename(columns={"_id": "Document ID", "TOTAL AMOUNT": "Total Amount"})
    return df

def get_purchases_by_year():
    pipeline = [
        {"$group": {"_id": "$PURCHASE YEAR", "total": {"$sum": "$TOTAL AMOUNT"}}}
    ]
    result = list(collection.aggregate(pipeline))
    return pd.DataFrame(result).rename(columns={"_id": "Year", "total": "Total Amount"})

def get_purchases_by_month(year):
    pipeline = [
        {"$match": {"PURCHASE YEAR": year}},
        {"$group": {"_id": "$PURCHASE MONTH", "total": {"$sum": "$TOTAL AMOUNT"}}}
    ]
    result = list(collection.aggregate(pipeline))
    return pd.DataFrame(result).rename(columns={"_id": "Month", "total": "Total Amount"})

def get_latest_data(limit=10):
    latest_docs = list(collection.find().sort([("_id", -1)]).limit(limit))
    data = []
    for doc in latest_docs:
        data.append({
            "Document ID": str(doc["_id"]),
            "Customer": doc["CUSTOMER DETAILS"].split("\n")[0],
            "Total Amount": doc["TOTAL AMOUNT"],
            "Purchase Month": doc["PURCHASE MONTH"],
            "Purchase Year": doc["PURCHASE YEAR"],
        })
    return pd.DataFrame(data)

# Display functions
def show_latest_data():
    st.header("Latest Receipt Data")
    num_entries = 10
    latest_data = get_latest_data(num_entries)
    st.table(latest_data)

def show_total_purchase_analysis():
    st.header("Total Purchase Analysis")
    
    # Detailed breakdown
    st.subheader("Purchase Breakdown")
    purchases_breakdown = get_total_purchases_breakdown()
    st.dataframe(purchases_breakdown)
    
    # Total sum
    total_purchases = purchases_breakdown["Total Amount"].sum()
    st.metric("Total Purchases", f"₹{total_purchases:,.2f}")

    # Yearly bar chart
    purchases_by_year = get_purchases_by_year()
    fig = px.bar(purchases_by_year, x="Year", y="Total Amount", title="Total Purchases by Year")
    st.plotly_chart(fig)

def show_monthly_purchase_analysis():
    st.header("Monthly Purchase Analysis")
    years = sorted(collection.distinct("PURCHASE YEAR"))
    selected_year = st.selectbox("Select Year", years)

    purchases_by_month = get_purchases_by_month(selected_year)
    fig = px.bar(purchases_by_month, x="Month", y="Total Amount", title=f"Monthly Purchases in {selected_year}")
    st.plotly_chart(fig)

def show_yearly_purchase_analysis():
    st.header("Yearly Purchase Analysis")
    purchases_by_year = get_purchases_by_year()
    fig = px.line(purchases_by_year, x="Year", y="Total Amount", title="Yearly Purchase Trend")
    st.plotly_chart(fig)

# Main app
def main():
    st.title("Tax Receipts Analysis")

    # Sidebar with select box
    st.sidebar.title("Analysis Options")
    analysis_option = st.sidebar.selectbox(
        "Choose an analysis",
        ["Latest Data", "Total Purchase Analysis", "Monthly Purchase Analysis", "Yearly Purchase Analysis"]
    )

    # Display the selected analysis
    if analysis_option == "Latest Data":
        show_latest_data()
    elif analysis_option == "Total Purchase Analysis":
        show_total_purchase_analysis()
    elif analysis_option == "Monthly Purchase Analysis":
        show_monthly_purchase_analysis()
    elif analysis_option == "Yearly Purchase Analysis":
        show_yearly_purchase_analysis()

if __name__ == "__main__":
    main()

# Close the MongoDB connection
client.close()
