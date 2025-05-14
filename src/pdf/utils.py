"""
Common utilities for PDF generation used across different entry points
"""

import os

from .generator import PDFGenerator
from .question_loader import QuestionLoader


def ensure_pdf_directory():
    """Create the PDF output directory if it doesn't exist"""
    pdf_dir = "pdf"
    if not os.path.exists(pdf_dir):
        os.makedirs(pdf_dir)
    return pdf_dir


def get_default_title(file_path):
    """Generate a default title from a file path"""
    return (
        os.path.splitext(os.path.basename(file_path))[0]
        .replace("_", " ")
        .title()
        .replace(" Questions", "")
    )


def get_output_filename(title, pdf_dir="pdf"):
    """Generate the output PDF filename"""
    return os.path.join(pdf_dir, f"{title.replace(' ', '_')}_Interview_Questions.pdf")


def create_pdf(questions, title, color_scheme, output_file=None):
    """
    Create a PDF from the given questions and settings

    Args:
        questions: List of question dictionaries
        title: Title for the PDF
        color_scheme: Color scheme to use
        output_file: Optional output file path. If not provided, one will be generated.

    Returns:
        tuple: (pdf_path, error_message)
        - pdf_path will be None if there was an error
        - error_message will be None if PDF was created successfully
    """
    try:
        # Ensure output directory exists
        pdf_dir = ensure_pdf_directory()

        # Generate output filename if not provided
        if not output_file:
            output_file = get_output_filename(title, pdf_dir)

        # Check write permissions
        if not os.access(os.path.dirname(output_file), os.W_OK):
            return (
                None,
                f"No write permission to directory: {os.path.dirname(output_file)}",
            )

        # Initialize and create the PDF
        pdf_generator = PDFGenerator(title, color_scheme)
        pdf_path, gen_error = pdf_generator.generate_pdf(questions, output_file)

        # If there was an error during generation, return it
        if gen_error:
            return None, gen_error

        # Verify the PDF was created successfully
        if not os.path.exists(pdf_path):
            return None, f"PDF file was not created at path: {pdf_path}"

        if os.path.getsize(pdf_path) == 0:
            return None, "PDF file was created but is empty"

        return pdf_path, None

    except Exception as e:
        return None, f"Error creating PDF: {str(e)}"
