import streamlit as st

# Set the page title and icon
st.set_page_config(page_title="Multipage Streamlit App", page_icon="📊", layout="wide")

# Add a title and sidebar for navigation
st.title("Tax Receipts Management System")
st.sidebar.title("Navigation")

# Create a navigation sidebar
page = st.sidebar.selectbox("Choose a page", ["Add Receipt", "Analysis"])

# Navigate to the selected page
if page == "Add Receipt":
    import pages.add_receipt as add_receipt
    add_receipt.main()
elif page == "Analysis Dashboard":
    import pages.analysis as analysis
    analysis.main()
