import streamlit as st
import PyPDF2
from langchain_groq import ChatGroq
import re
import json
import io

def pdf_to_text(pdf_file):
    pdf_reader = PyPDF2.PdfReader(pdf_file)
    text = ""
    for page_num in range(len(pdf_reader.pages)):
        page = pdf_reader.pages[page_num]
        text += page.extract_text()
    return text

def tax_receipt_extractor(llm, receipt_text):
    prompt = f"""
    ## Instruction ##
    You are an AI assistant tasked with extracting key information from tax receipts. Given a tax receipt text, extract and format the information for the following three fields:

    1. CUSTOMER DETAILS
       - Extract all available customer information including name, billing address, shipping address (if different), phone number, and email.
       - Include any customer identification numbers (e.g., GSTIN) if provided.

    2. PRODUCTS
       - List each product or service as a separate item.
       - For each product, include:
         * Name of the product or service
         * HSN/SAC code (if available)
         * Rate
         * Quantity and unit
         * Amount
         * Any applicable taxes (e.g., CGST, SGST, IGST)
         * Total amount for the product

    3. TOTAL AMOUNT
       - Provide the final payable amount, including all taxes and any roundoffs.

    Format your response exactly as shown in the examples below, using all caps for field names and quotation marks for the content. Use bullet points (-) for listing products. Ensure that the information is accurate and concise.
    If any information is missing, use "NA" for that field. Your answer must be based solely on the given receipt text.

    Example 1:

    INPUT: 
    TATA MOTORS LIMITED TATA MOTORS LIMITED Nigadi Bhosari Road, PIMPRI Pune, MAHARASHTRA- 411018 GSTIN: 27AAACT2727Q1ZWSeeds Lic. No: LASD67898369 Fertilizers Lic. No: LASD34564756 Insecticide Lic. No: LAID 26453734T A X I N V O I C E O R I G I N A L F O R R E C I P I E N T Customer Details: TEST Billing Address: Test Hyderabad, TELANGANA, 500089 Ph: 9108239284 test@gmail.com Shipping Address: Test Hyderabad, TELANGANA, 500089Invoice #: inv41Date: 18 Jul 2024 Place of Supply: 36-TELANGANA Enquire id: 06-06-2024 IMEI NOITEM / Calibration Charges For HSN/ SACRateQuantityAmountIGSTTotal Amount 1 WASTE AND SCRAP OF STAINLESS STEEL 7204219095.006,790 KGS6,45,050.001,16,109.00 (18%)7,61,159.00Total Items / Qty : 1 / 6790.000 Total amount (in words): INR Seven Lakh, Sixty-Eight Thousand, Seven Hundred And Seventy-One Rupees Only . Bank Details: BankAccount #: 1234567890 IFSC Code: IBKL0000432 Branch: GACHIBOWLI UPI ID: 7095285474@ybl BENEFICIARY NAME : ROMOLIKA SAHANI Taxable Amount ₹6,45,050.00 IGST 18.0%₹1,16,109.00 Round Off 0.41 Total₹7,68,771.00 TCS @ 1% 206C₹ 7611.58984375 Amount Payable ₹7,68,771.00 HSN/ SAC Taxable Value Integrated Tax Rate AmountTotal Tax Amount 72042190 645050.00 18% 116109.00 116109.00 TOTAL6,45,050.00 1,16,109.00 116109.00 Notes: Thankyou for shopping from us. See you again. Terms and Conditions: GOODS ONCE SOLD CANNOT BE RETURNED. ONLY GOODS THAT ARE DAMAGED CAN BE RETURNED UNDER SPECIFIC TERM S& CONDITIONS. Receiver's Signature For TATA MOTORS LIMITED Authorized Signatory Page 1 / 1 This is a digitally signed document.

    OUTPUT:

    CUSTOMER DETAILS:
    "TEST
    GSTIN: 27AAACT2727Q1ZW
    Billing Address: Test Hyderabad, TELANGANA, 500089
    Ph: 9108239284
    test@gmail.com
    Shipping Address: Test Hyderabad, TELANGANA, 500089"

    PRODUCTS:
    "- WASTE AND SCRAP OF STAINLESS STEEL
      HSN: 72042190
      Rate: 95.00
      Quantity: 6,790 KGS
      Amount: 6,45,050.00
      IGST: 1,16,109.00 (18%)
      Total Amount: 7,61,159.00"

    TOTAL AMOUNT:
    "₹7,68,771.00"

    Example 2:

    INPUT:
    RELIANCE INDUSTRIES LIMITED
    Maker Chambers IV, 222, Nariman Point, Mumbai, MAHARASHTRA- 400021
    GSTIN: 27AAACR5055K1ZS Petrochemicals Lic. No: LPCH78901234
    Telecommunications Lic. No: LTCM56789012 T A X I N V O I C E O R I G I N A L F O R R E C I P I E N T
    Customer Details: INDIAN OIL CORPORATION LIMITED Billing Address: IndianOil Bhavan,
    G-9, Ali Yavar Jung Marg, Bandra (East), Mumbai, MAHARASHTRA, 400051
    Ph: 022-26447616 feedback@indianoil.in Shipping Address: IOCL Refinery,
    Mathura, UTTAR PRADESH, 281006 Invoice #: RIL/2024/08/003 Date: 05 Aug 2024
    Place of Supply: 27-MAHARASHTRA Order id: IOCL/2024/07/28
    ITEM HSN/SAC Rate Quantity Amount CGST SGST Total Amount
    1 POLYPROPYLENE GRANULES 39021000 95.00 500000 KGS 4,75,00,000.00 42,75,000.00 42,75,000.00 5,60,50,000.00
    2 HIGH DENSITY POLYETHYLENE 39012000 105.00 300000 KGS 3,15,00,000.00 28,35,000.00 28,35,000.00 3,71,70,000.00
    Total Items / Qty : 2 / 800000.000 Total amount (in words): INR Nine Crore, Thirty-Two Lakh,
    Twenty Thousand Rupees Only . Bank Details: Bank: State Bank of India Account #: 30123456789
    IFSC Code: SBIN0009876 Branch: NARIMAN POINT BENEFICIARY NAME : RELIANCE INDUSTRIES LIMITED
    Taxable Amount ₹7,90,00,000.00 CGST 9.0% ₹71,10,000.00 SGST 9.0% ₹71,10,000.00
    Round Off 0.00 Total ₹9,32,20,000.00 Amount Payable ₹9,32,20,000.00

    OUTPUT:

    CUSTOMER DETAILS:
    "INDIAN OIL CORPORATION LIMITED
    Billing Address: IndianOil Bhavan, G-9, Ali Yavar Jung Marg, Bandra (East), Mumbai, MAHARASHTRA, 400051
    Ph: 022-26447616
    feedback@indianoil.in
    Shipping Address: IOCL Refinery, Mathura, UTTAR PRADESH, 281006"

    PRODUCTS:
    "- POLYPROPYLENE GRANULES
      HSN: 39021000
      Rate: 95.00
      Quantity: 500000 KGS
      Amount: 4,75,00,000.00
      CGST: 42,75,000.00
      SGST: 42,75,000.00
      Total Amount: 5,60,50,000.00

    - HIGH DENSITY POLYETHYLENE
      HSN: 39012000
      Rate: 105.00
      Quantity: 300000 KGS
      Amount: 3,15,00,000.00
      CGST: 28,35,000.00
      SGST: 28,35,000.00
      Total Amount: 3,71,70,000.00"

    TOTAL AMOUNT:
    "₹9,32,20,000.00"

    Example 3:

    INPUT:
    INFOSYS LIMITED
    Electronics City, Hosur Road, Bangalore, KARNATAKA- 560100
    GSTIN: 29AAACI4741E1ZX Software Development Lic. No: LSFT34567890
    IT Services Lic. No: LITS23456789 T A X I N V O I C E O R I G I N A L F O R R E C I P I E N T
    Customer Details: STATE BANK OF INDIA Billing Address: State Bank Bhavan,
    Madame Cama Road, Mumbai, MAHARASHTRA, 400021 Ph: 022-22740000 
    customer.care@sbi.co.in Shipping Address: IT Department, SBI Global IT Centre,
    CBD Belapur, Navi Mumbai, MAHARASHTRA, 400614 Invoice #: INF/2024/08/027 Date: 18 Aug 2024
    Place of Supply: 27-MAHARASHTRA Order id: SBI/2024/07/15
    ITEM SAC Rate Quantity Amount CGST SGST Total Amount
    1 CORE BANKING SOLUTION UPGRADE 998314 15,00,00,000 1 UNIT 15,00,00,000.00 1,35,00,000.00 1,35,00,000.00 17,70,00,000.00
    2 CYBERSECURITY SERVICES 998316 5,00,00,000 1 UNIT 5,00,00,000.00 45,00,000.00 45,00,000.00 5,90,00,000.00
    Total Items / Qty : 2 / 2.000 Total amount (in words): INR Twenty-Three Crore,
    Sixty Lakh Rupees Only . Bank Details: Bank: HDFC Bank Account #: 50012345678
    IFSC Code: HDFC0000042 Branch: ELECTRONIC CITY BENEFICIARY NAME : INFOSYS LIMITED
    Taxable Amount ₹20,00,00,000.00 CGST 9.0% ₹1,80,00,000.00 SGST 9.0% ₹1,80,00,000.00
    Round Off 0.00 Total ₹23,60,00,000.00 Amount Payable ₹23,60,00,000.00

    OUTPUT:

    CUSTOMER DETAILS:
    "STATE BANK OF INDIA
    Billing Address: State Bank Bhavan, Madame Cama Road, Mumbai, MAHARASHTRA, 400021
    Ph: 022-22740000
    customer.care@sbi.co.in
    Shipping Address: IT Department, SBI Global IT Centre, CBD Belapur, Navi Mumbai, MAHARASHTRA, 400614"

    PRODUCTS:
    "- CORE BANKING SOLUTION UPGRADE
      SAC: 998314
      Rate: 15,00,00,000
      Quantity: 1 UNIT
      Amount: 15,00,00,000.00
      CGST: 1,35,00,000.00
      SGST: 1,35,00,000.00
      Total Amount: 17,70,00,000.00

    - CYBERSECURITY SERVICES
      SAC: 998316
      Rate: 5,00,00,000
      Quantity: 1 UNIT
      Amount: 5,00,00,000.00
      CGST: 45,00,000.00
      SGST: 45,00,000.00
      Total Amount: 5,90,00,000.00"

    TOTAL AMOUNT:
    "₹23,60,00,000.00"

    Now, extract and format the information from the following tax receipt text:

    {receipt_text}
    """

    response = llm.invoke(prompt)
    return response.content
def parse_tax_receipt_output(output):
    parsed_data = {
        "CUSTOMER DETAILS": "",
        "PRODUCTS": [],
        "TOTAL AMOUNT": ""
    }
    lines = output.split('\n')
    current_field = None
    content_buffer = []
    
    def process_buffer():
        nonlocal content_buffer, current_field
        if content_buffer:
            full_content = '\n'.join(content_buffer).strip()
            if current_field == "PRODUCTS":
                parsed_data[current_field] = parse_products(full_content)
            else:
                parsed_data[current_field] = full_content.strip('"')
            content_buffer = []

    def parse_products(products_text):
        products = []
        current_product = {}
        for line in products_text.split('\n'):
            line = line.strip()
            if line.startswith("-"):  # New product
                if current_product:
                    products.append(current_product)
                current_product = {"name": line.lstrip("- ").strip()}
            elif ":" in line:
                key, value = line.split(":", 1)
                current_product[key.strip()] = value.strip()
        if current_product:
            products.append(current_product)
        return products

    for line in lines:
        line = line.strip()
        if line.startswith(("CUSTOMER DETAILS:", "PRODUCTS:", "TOTAL AMOUNT:")):
            process_buffer()
            current_field = line.split(":")[0]
        elif line.startswith('"') and line.endswith('"') and current_field != "PRODUCTS":
            process_buffer()
            parsed_data[current_field] = line.strip('"')
        elif current_field:
            content_buffer.append(line)

    process_buffer()  # Process any remaining content in the buffer
    return parsed_data


st.set_page_config(page_title="Tax Receipt Parser",page_icon="📝")

st.title("Tax Receipt Parser")

llm = ChatGroq(temperature=0.5, groq_api_key="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", model_name="llama3-70b-8192")


uploaded_file = st.file_uploader("Choose a Tax PDF file", type="pdf")

if uploaded_file is not None:
    pdf_file = io.BytesIO(uploaded_file.read())
    with st.spinner("Parsing your receipt..."):
        text = pdf_to_text(pdf_file)
        llm_response = tax_receipt_extractor(llm,text)
        output = parse_tax_receipt_output(llm_response)
        st.write(output)
    


