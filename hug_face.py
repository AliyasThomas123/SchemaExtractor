import pdfplumber
import json
import torch
from transformers import pipeline
from pydantic import BaseModel, ValidationError
from typing import Dict, List, Optional
import re


# Pydantic models for schema validation
class Address(BaseModel):
    name: str
    address1: str
    address2: Optional[str] = ""
    address3: Optional[str] = ""
    city: str
    state: str
    country: Optional[str] = ""
    country_code: Optional[str] = ""
    zip: str


class Contact(BaseModel):
    name: str
    email: Optional[str] = ""
    contact_number: str


class Header(BaseModel):
    ship_to: Address
    bill_to: Address
    vendor: Optional[Address] = None
    buyer_contact: Contact
    shipping_contact: Optional[Contact] = None
    job_number: str
    purchase_order_number: Optional[str] = "N/A"
    project_number: Optional[str] = "N/A"
    date_ordered: str
    delivery_date: str
    shipping_instructions: Optional[str] = "N/A"
    notes: Optional[str] = "N/A"
    ship_via: Optional[str] = "N/A"
    payment_terms: Optional[str] = "N/A"


class LineItem(BaseModel):
    line_no: str
    quantity: int
    part_numbers: str
    product_description: str
    spell_corrected_product_description: str
    unit_price: Optional[str] = "N/A"
    currency: Optional[str] = "N/A"


class Extraction(BaseModel):
    header: Header
    line_items: List[LineItem]


# Hugging Face Extractor
class HuggingFaceExtractor:
    def __init__(self, model_name="deepset/roberta-base-squad2"):
        self.qa_pipeline = pipeline(
            "question-answering",
            model=model_name,
            tokenizer=model_name,
            device=0 if torch.cuda.is_available() else -1,
        )

    def extract_data(self, text: str, fields: Dict[str, str]) -> Dict:
        extracted_data = {}
        for field, description in fields.items():
            question = f"What is the {description}?"
            answer = self.ask_question(text, question)
            extracted_data[field] = answer if answer else "N/A"
        return extracted_data

    def ask_question(self, context: str, question: str) -> str:
        result = self.qa_pipeline(question=question, context=context)
        return result.get("answer", "N/A")


# PDF Extractor
class PDFExtractor:
    @staticmethod
    def extract_text_from_pdf(file_path: str) -> str:
        with pdfplumber.open(file_path) as pdf:
            return "\n".join([page.extract_text() for page in pdf.pages])

    @staticmethod
    def extract_sections(text: str) -> Dict:
        patterns = {
            "customer_info": r"(?<=CUSTOMER INFORMATION)(.*?)(?=MATERIAL|$)",
            "material_info": r"(?<=MATERIAL)(.*?)(?=TOTAL|$)",
        }
        return {key: re.search(pattern, text, re.DOTALL).group(1).strip() if re.search(pattern, text, re.DOTALL) else "" for key, pattern in patterns.items()}


# Helper functions to process extracted data
def process_header(customer_info: str) -> Header:
    # Parse Customer Information Section
    splitted = customer_info.split('\n')
   
   
    name = splitted[0] if splitted else "N/A"

    street_match = re.search(r"Street:\s*(.+)", customer_info)
    street = street_match.group(1).strip() if street_match else "N/A"

    city_match = re.search(r"City:\s*(\w+)", customer_info)
    city = city_match.group(1).strip() if city_match else "N/A"

    state_match = re.search(r"State:\s*(\w+)", customer_info)
    state = state_match.group(1).strip() if state_match else "N/A"

    zip_match = re.search(r"Zip:\s*(\d+)", customer_info)
    zip_code = zip_match.group(1).strip() if zip_match else "N/A"

    email_match = re.search(r"Email:\s*(.+)", customer_info)
    email = email_match.group(1).strip() if email_match else "N/A"

    cell_match = re.search(r"Cell:\s*(.+)", customer_info)
    contact_number = cell_match.group(1).strip() if cell_match else "N/A"

    # Construct Address objects for ship_to and bill_to
    address = Address(
        name=name,
        address1=f"{street}, {city}",
        city=city,
        state=state,
        zip=zip_code,
    )

    # Construct Buyer Contact
    buyer_contact = Contact(
        name=name,
        email=email,
        contact_number=contact_number,
    )

    return Header(
        ship_to=address,
        bill_to=address,
        buyer_contact=buyer_contact,
        job_number="N/A",  # Replace with extracted value
        date_ordered="N/A",  # Replace with extracted value
        delivery_date="N/A",  # Replace with extracted value
    )


def process_line_items(material_info: str) -> List[LineItem]:
    line_items = []
    # Example pattern to extract line items
    pattern = r"(?P<line_no>\d+)\s+(?P<quantity>\d+)\s+(?P<part_numbers>.*?)\s+(?P<description>.*?)\s*\n"
    matches = re.finditer(pattern, material_info, re.DOTALL)
    for match in matches:
        line_items.append(
            LineItem(
                line_no=match.group("line_no"),
                quantity=int(match.group("quantity")),
                part_numbers=match.group("part_numbers"),
                product_description=match.group("description"),
                spell_corrected_product_description=match.group("description"),  # Add spell-correction logic if needed
            )
        )
    return line_items


# Main function
def main():
    pdf_path = "./file1.pdf"  # Path to uploaded PDF

    pdf_extractor = PDFExtractor()
    text = pdf_extractor.extract_text_from_pdf(pdf_path)

    sections = pdf_extractor.extract_sections(text)
    customer_info = sections["customer_info"]
    material_info = sections["material_info"]

    # Process header and line items
    header = process_header(customer_info)
    line_items = process_line_items(material_info)

    # Construct the Extraction object
    try:
        extraction = Extraction(header=header, line_items=line_items)
        output_json = json.dumps(extraction.dict(), indent=4)
        print("Structured JSON Output:", output_json)
    except ValidationError as e:
        print("Validation Error:", e.json())


if __name__ == "__main__":
    main()
