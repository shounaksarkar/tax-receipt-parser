# Tax Receipt Parser

This project is an innovative tool for extracting and parsing key information from tax receipts using advanced large language models (LLMs). The application processes PDFs of tax receipts and returns structured data, which can be used for further analysis or record-keeping.

### Live demo: https://taxreceipt.streamlit.app/

## Features

- **PDF to Text Conversion**: Uses `PyPDF2` to extract raw text from PDF files, making it accessible for further processing.
- **Intelligent Information Extraction**: A custom prompt is used with a large language model (LLM) to extract key fields like customer details, products, and total amounts from the receipt text.
- **Structured JSON Output**: The extracted information is parsed and returned in a well-structured JSON format, making it easy to integrate with other systems or to store in databases.

## Techniques Used

1. **Prompt Engineering**:
   - The core of this project revolves around an intelligently crafted prompt that instructs the LLM to extract and format key information from a tax receipt.
   - The prompt is designed to handle a variety of receipt formats and ensures the output is consistent and accurate.
   - The use of example inputs and outputs within the prompt guides the LLM to understand the required format and precision.

2. **JSON Parsing**:
   - The raw output from the LLM is parsed into a structured JSON format.
   - The parsing logic ensures that the data is categorized correctly into `CUSTOMER DETAILS`, `PRODUCTS`, and `TOTAL AMOUNT`.
   - The product details are further broken down into fields like `Name`, `HSN/SAC`, `Rate`, `Quantity`, `Amount`, and applicable taxes.

3. **Streamlit Integration**:
   - The entire application is built using Streamlit, a popular framework for creating interactive web apps in Python.
   - The app provides a user-friendly interface for uploading PDFs and viewing the extracted information.

## How It Works

1. **PDF Upload**: 
   - Users upload a PDF file of a tax receipt through the Streamlit interface.

2. **Text Extraction**:
   - The uploaded PDF is converted to text using the `pdf_to_text` function.

3. **LLM Processing**:
   - The extracted text is passed to the `tax_receipt_extractor` function, which uses the `ChatGroq` model to process the text and extract relevant information.

4. **Output Parsing**:
   - The LLM's response is parsed using the `parse_tax_receipt_output` function, which organizes the data into a structured format.

5. **Display**:
   - The parsed data is displayed in the Streamlit app, providing a clear and concise view of the extracted information.

## Example Output

```json
{
  "CUSTOMER DETAILS": "STATE BANK OF INDIA\nBilling Address: State Bank Bhavan, Madame Cama Road, Mumbai, MAHARASHTRA, 400021\nPh: 022-22740000\ncustomer.care@sbi.co.in\nShipping Address: IT Department, SBI Global IT Centre, CBD Belapur, Navi Mumbai, MAHARASHTRA, 400614",
  "PRODUCTS": [
    {
      "name": "CORE BANKING SOLUTION UPGRADE",
      "HSN": "998314",
      "Rate": "15,00,00,000",
      "Quantity": "1 UNIT",
      "Amount": "15,00,00,000.00",
      "CGST": "1,35,00,000.00",
      "SGST": "1,35,00,000.00",
      "Total Amount": "17,70,00,000.00"
    },
    {
      "name": "CYBERSECURITY SERVICES",
      "HSN": "998316",
      "Rate": "5,00,00,000",
      "Quantity": "1 UNIT",
      "Amount": "5,00,00,000.00",
      "CGST": "45,00,000.00",
      "SGST": "45,00,000.00",
      "Total Amount": "5,90,00,000.00"
    }
  ],
  "TOTAL AMOUNT": "₹23,60,00,000.00"
}
