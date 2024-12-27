from PyPDF2 import PdfMerger, PdfReader, PdfWriter
from io import BytesIO
import zipfile
from pdf2image import convert_from_bytes
import pytesseract
import tempfile
import pdfplumber
import pytesseract
from PIL import Image
import io

def merge_pdfs(pdf_files):
    """
    Merge multiple PDF files into a single PDF.

    Args:
        pdf_files: List of file objects (PDFs) to merge.

    Returns:
        BytesIO object containing the merged PDF.

    Raises:
        ValueError: If any file is not a valid or readable PDF.
    """
    merger = PdfMerger()
    for idx, pdf in enumerate(pdf_files, 1):
        try:
            reader = PdfReader(pdf)
            if reader.is_encrypted:
                raise ValueError(f"PDF file {idx} is encrypted and cannot be merged.")
            pdf.seek(0)
            merger.append(pdf)
        except Exception as e:
            raise ValueError(f"Invalid or corrupted PDF file {idx}: {str(e)}")

    output = BytesIO()
    merger.write(output)
    merger.close()
    output.seek(0)
    return output


def split_pdf(pdf_file, page_ranges):
    """
    Split a PDF into specified page ranges.

    Args:
        pdf_file: File object (PDF) to split.
        page_ranges: String of page ranges (e.g., '1-3,5').

    Returns:
        BytesIO object containing the split PDF.

    Raises:
        ValueError: If the PDF is invalid, encrypted, or page ranges are invalid.
    """
    try:
        reader = PdfReader(pdf_file)
        if reader.is_encrypted:
            raise ValueError("PDF file is encrypted and cannot be split.")
        total_pages = len(reader.pages)

        writer = PdfWriter()
        ranges = page_ranges.split(',')
        for range_str in ranges:
            try:
                if '-' in range_str:
                    start, end = map(int, range_str.split('-'))
                    if start < 1 or end > total_pages or start > end:
                        raise ValueError
                    for page in range(start - 1, end):
                        writer.add_page(reader.pages[page])
                else:
                    page = int(range_str) - 1
                    if page < 0 or page >= total_pages:
                        raise ValueError
                    writer.add_page(reader.pages[page])
            except ValueError:
                raise ValueError(f"Invalid page range '{range_str}'. Pages must be between 1 and {total_pages}.")

        output = BytesIO()
        writer.write(output)
        writer.close()
        output.seek(0)
        return output
    except Exception as e:
        raise ValueError(f"Invalid or corrupted PDF file: {str(e)}")


def split_pdf_by_page(pdf_file):
    """
    Split a PDF into one PDF per page and return as a ZIP file.

    Args:
        pdf_file: File object (PDF) to split.

    Returns:
        BytesIO object containing a ZIP file with one PDF per page.

    Raises:
        ValueError: If the PDF is invalid or encrypted.
    """
    try:
        reader = PdfReader(pdf_file)
        if reader.is_encrypted:
            raise ValueError("PDF file is encrypted and cannot be split.")
        total_pages = len(reader.pages)

        if total_pages == 0:
            raise ValueError("PDF file is empty.")

        # Create a BytesIO for the ZIP file
        zip_buffer = BytesIO()
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            for page_num in range(total_pages):
                writer = PdfWriter()
                writer.add_page(reader.pages[page_num])

                # Write the single-page PDF to a BytesIO
                pdf_buffer = BytesIO()
                writer.write(pdf_buffer)
                writer.close()

                # Add the PDF to the ZIP
                pdf_buffer.seek(0)
                zip_file.writestr(f'page_{page_num + 1}.pdf', pdf_buffer.getvalue())

        zip_buffer.seek(0)
        return zip_buffer
    except Exception as e:
        raise ValueError(f"Invalid or corrupted PDF file: {str(e)}")


def encrypt_pdf(pdf_file, password):
    """
    Encrypt a PDF file with a password.

    Args:
        pdf_file: File object (PDF) to encrypt.
        password: String password to lock the PDF.

    Returns:
        BytesIO object containing the encrypted PDF.

    Raises:
        ValueError: If the PDF is invalid or already encrypted.
    """
    try:
        reader = PdfReader(pdf_file)
        if reader.is_encrypted:
            raise ValueError("PDF file is already encrypted.")

        writer = PdfWriter()
        for page in reader.pages:
            writer.add_page(page)

        # Encrypt the PDF with the password
        writer.encrypt(password)

        output = BytesIO()
        writer.write(output)
        writer.close()
        output.seek(0)
        return output
    except Exception as e:
        raise ValueError(f"Invalid or corrupted PDF file: {str(e)}")

#
# def ocr_pdf(pdf_file):
#     """
#     Perform OCR on a PDF file to extract text.
#
#     Args:
#         pdf_file: File object (PDF) to process.
#
#     Returns:
#         String containing the extracted text from all pages.
#
#     Raises:
#         ValueError: If the PDF is invalid, encrypted, or empty.
#     """
#     try:
#         reader = PdfReader(pdf_file)
#         if reader.is_encrypted:
#             raise ValueError("PDF file is encrypted and cannot be processed for OCR.")
#         if len(reader.pages) == 0:
#             raise ValueError("PDF file is empty.")
#
#         # Save PDF content to a temporary file
#         with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as temp_pdf:
#             temp_pdf.write(pdf_file.read())
#             temp_pdf_path = temp_pdf.name
#
#         # Convert PDF to images
#         images = convert_from_bytes(open(temp_pdf_path, 'rb').read())
#
#         # Perform OCR on each page
#         text_content = []
#         for page_num, image in enumerate(images, 1):
#             try:
#                 text = pytesseract.image_to_string(image)
#                 text_content.append(f"Page {page_num}:\n{text}\n")
#             except Exception as e:
#                 text_content.append(f"Page {page_num}:\nError extracting text: {str(e)}\n")
#
#         # Clean up temporary file
#         import os
#         os.unlink(temp_pdf_path)
#
#         return ''.join(text_content)
#     except Exception as e:
#         raise ValueError(f"Invalid or corrupted PDF file: {str(e)}")

def ocr_pdf(pdf_file):
    """
    Perform OCR on a PDF file to extract text.

    Args:
        pdf_file: File object (PDF) to process.

    Returns:
        String containing the extracted text from all pages.

    Raises:
        ValueError: If the PDF is invalid, encrypted, or empty.
    """
    try:
        reader = PdfReader(pdf_file)
        if reader.is_encrypted:
            raise ValueError("PDF file is encrypted and cannot be processed for OCR.")
        if len(reader.pages) == 0:
            raise ValueError("PDF file is empty.")

        # Reset file pointer to start
        pdf_file.seek(0)

        # Use pdfplumber to process the PDF
        with pdfplumber.open(pdf_file) as pdf:
            text_content = []
            for page_num, page in enumerate(pdf.pages, 1):
                try:
                    # Try direct text extraction first
                    direct_text = page.extract_text()
                    if direct_text and direct_text.strip():
                        text_content.append(f"Page {page_num}:\n{direct_text}\n")
                        continue

                    # Fall back to OCR by rendering the page as an image
                    page_image = page.to_image(resolution=300)
                    pil_image = page_image.original

                    # Perform OCR
                    text = pytesseract.image_to_string(pil_image)
                    if text.strip():
                        text_content.append(f"Page {page_num}:\n{text}\n")
                    else:
                        text_content.append(f"Page {page_num}:\nNo text extracted\n")
                except Exception as e:
                    text_content.append(f"Page {page_num}:\nError extracting text: {str(e)}\n")

        return ''.join(text_content)
    except Exception as e:
        raise ValueError(f"Invalid or corrupted PDF file: {str(e)}")