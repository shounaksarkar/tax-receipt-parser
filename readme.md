Here's a `README.md` file for your Streamlit app:

```markdown
# Tax Receipts Management System

This Streamlit app allows you to manage and analyze tax receipts. The app includes two main functionalities: **Adding Receipts** and **Analyzing Receipts**.

### Live Demo: https://taxreceipt.streamlit.app/


## Features

### 1. Add Receipt
- Upload a PDF of a tax receipt.
- Extract text from the PDF using `PyPDF2`.
- Parse the extracted text using an LLM (`langchain_groq`).
- Display parsed information including customer details, products, total amount, and purchase date.

### 2. Analysis
- View the latest receipt data from MongoDB.
- Analyze total purchases by year and by month.
- Visualize yearly and monthly purchase trends with interactive charts.

## Project Structure

```
my_streamlit_app/
│
├── streamlit_app.py        # Main entry point
├── pages/
│   ├── analysis.py         # Page for analysis
│   └── add_receipt.py      # Page for adding receipts
└── requirements.txt        # Python dependencies
```

### Live Demo: https://taxreceipt.streamlit.app/

### Usage

- **Add Receipt**: Navigate to the "Add Receipt" page, upload a PDF, and extract the receipt data.
- **Analysis**: Navigate to the "Analysis" page to view and analyze purchase data stored in MongoDB.


Made with ❤️ using Streamlit.
```
