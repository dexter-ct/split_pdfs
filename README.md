
# PDF Splitter

A simple Python script to split multi-page PDFs into individual pages. This is used for invoices that come in that are all in the same .pdf, or to seperate scanned images  
Uses a `.env` file to keep folder paths private and configurable.

---

## Features
- Splits PDFs into separate pages
- Custom input folder and output subdirectory via `.env`
- Keeps sensitive paths out of the code

---

## Requirements
- Python 3.x
- [PyPDF2](https://pypi.org/project/PyPDF2/)
- [python-dotenv](https://pypi.org/project/python-dotenv/)

---

## Setup

1. **Clone the repository**
     ```bash
   git clone <your-repo-url>
