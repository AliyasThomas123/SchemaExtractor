from hug_face import PDFExtractor ,process_header ,process_line_items ,Extraction
from pydanto import extract_text_from_pdf , process_data

import streamlit as st
import json

def main():
    st.title("PDF Data Extraction Tool")

   
    method = st.selectbox("Choose the method for extraction:", ["Pydantic"])

 
    uploaded_file = st.file_uploader("Upload a PDF file", type=["pdf"])

   
    st.subheader("JSON Schema")
    schema = {
        "header": {
            "ship_to": {
                "name": "string",
                "address1": "string",
                "address2": "string",
                "address3": "string",
                "city": "string",
                "state": "string",
                "zip": "string",
            },
            "bill_to": {
                "name": "string",
                "address1": "string",
                "address2": "string",
                "address3": "string",
                "city": "string",
                "state": "string",
                "zip": "string",
            },
            "buyer_contact": {
                "name": "string",
                "email": "string",
                "contact_number": "string",
            },
            "job_number": "string",
            "date_ordered": "string",
            "delivery_date": "string",
        },
        "line_items": [
            {
                "line_no": "string",
                "quantity": "integer",
                "part_numbers": "string",
                "product_description": "string",
                "spell_corrected_product_description": "string",
            }
        ],
    }
    st.json(schema)

    if uploaded_file is not None:
        if method == "Pydantic":
            text = PDFExtractor.extract_text_from_pdf(uploaded_file)
            sections = PDFExtractor.extract_sections(text)
            customer_info = sections["customer_info"]
            material_info = sections["material_info"]

            header = process_header(customer_info)
            line_items = process_line_items(material_info)

            try:
                extraction = Extraction(header=header, line_items=line_items)
                output_json = json.dumps(extraction.dict(), indent=4)
               
               
            except Exception as e:
                st.error(f"Validation Error: {e.json()}")

        elif method == "Pydantic":
           raw_data = extract_text_from_pdf(uploaded_file)
           structured_data = process_data(raw_data)
           output_json = json.dumps(structured_data.model_dump(), indent=4) 
        st.subheader("Extraction Result")
        st.code(output_json, language="json")   
        st.download_button(
                    label="Download JSON Result",
                    data=output_json,
                    file_name="extracted_data.json",
                    mime="application/json",
                )


if __name__ == "__main__":
    main()
