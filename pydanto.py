import json
from pydantic import BaseModel, Field, validator
from typing import List, Optional
import pdfplumber , json

class Address(BaseModel):
    name: Optional[str] = None
    address1: str
    address2: Optional[str] = None
    address3: Optional[str] = None
    city: Optional[str] = None
    state: str
    country: Optional[str] = None
    country_code: Optional[str] = None
    zip: str


class Contact(BaseModel):
    name: str
    email: Optional[str] = None  
    contact_number: str



class Header(BaseModel):
    ship_to: Address
    bill_to: Address
    buyer_contact: Contact
    shipping_contact: Contact
    job_number: str
    date_ordered: str
    delivery_date: str
    shipping_instructions: Optional[str] = None 
    notes: Optional[str] = None



class LineItem(BaseModel):
    line_no: str
    quantity: int
    part_numbers: str
    product_description: str
    spell_corrected_product_description: str


class Extraction(BaseModel):
    header: Header
    line_items: List[LineItem]


class RootSchema(BaseModel):
    extraction: List[Extraction]



def extract_text_from_pdf(file_path: str) -> str:
    with pdfplumber.open(file_path) as pdf:
        text = ""
        for page in pdf.pages:
            text += page.extract_text() + "\n"
    return text


def process_data(raw_text: str) -> RootSchema:
    header = Header(
        ship_to=Address(
            name="John Doe",
            address1="123 Main St",
            state="CA",
            zip="90210",
        ),
        bill_to=Address(
            name="Jane Smith",
            address1="456 Elm St",
            city="Springfield",
            state="IL",
            zip="62704",
        ),
        buyer_contact=Contact(
            name="John Buyer",
            contact_number="555-1234"
        ),
        shipping_contact=Contact(
            name="Jane Shipper",
            contact_number="555-5678"
        ),
        job_number="12345",
        date_ordered="2024-08-08",
        delivery_date="2024-08-15",
    )
    line_items = [
        LineItem(
            line_no="1",
            quantity=10,
            part_numbers="ABC123",
            product_description="Sample Product",
            spell_corrected_product_description="Sample Product"
        )
    ]
    return RootSchema(extraction=[Extraction(header=header, line_items=line_items)])






pdf_path = "./file2.pdf"
raw_text = extract_text_from_pdf(pdf_path)
print("raw>>",raw_text)
structured_data = process_data(raw_text)


output_json = json.dumps(structured_data.model_dump(), indent=4) 
output_file = "parsed_data2.json"
with open(output_file, "w") as f:
    f.write(output_json)

print(f"Data successfully parsed and saved to {output_file}")