import pdfplumber
import json
from datetime import datetime
import re

pdf_path = r'raw\WhatsApp Chat with 300lvl  CS Info Group D\Undergradute (Regular) Calendar for 2025-2026 Academic Session - Final - Published Friday-August 8 - 2025.pdf'

with pdfplumber.open(pdf_path) as pdf:
    text = ''
    for page in pdf.pages:
        text += page.extract_text() + '\n'

# Print first 3000 characters to understand structure
print("=== PDF Content Preview ===")
print(text[:3000])
print("\n=== Total length ===")
print(len(text))
