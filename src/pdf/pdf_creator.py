"""
PDF Creator for Interview Questions
Creates beautiful PDF presentations from question sets
"""

import os
import traceback
import io
import re
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union
import random

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, letter, landscape
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch, cm, mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen.canvas import Canvas
from reportlab.platypus import (
    Flowable,
    Image,
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

from .color_schemes import COLOR_SCHEMES
from .motivational_quotes import get_random_quote
from .page_generators import (
    create_cover_page,
    create_final_page,
    create_milestone_page,
    create_qa_page,
    create_progress_slide,
    create_ending_page,
)
from .progress_messages import get_progress_message, PROGRESS_MESSAGES
from .text_renderer import TextRenderer
from src.utils.config import get_config

# Load configuration
DEFAULT_OUTPUT_DIR = get_config("DEFAULT_OUTPUT_DIR", "pdf")


def ensure_pdf_directory():
    """Create the PDF output directory if it doesn't exist"""
    pdf_dir = "pdf"
    if not os.path.exists(pdf_dir):
        os.makedirs(pdf_dir)
    return pdf_dir


def get_default_title(file_path):
    """Generate a default title from a file path"""
    # Extract basename without extension
    basename = os.path.basename(file_path)
    name = os.path.splitext(basename)[0]

    # Remove _questions suffix if present
    name = name.replace("_questions", "")

    # Replace underscores with spaces and title case
    return " ".join(word.capitalize() for word in name.split("_"))


def get_output_filename(title: str, output_dir: str = DEFAULT_OUTPUT_DIR) -> str:
    """
    Generate a filename for the PDF output.

    Args:
        title: Title of the PDF
        output_dir: Directory to save the PDF in

    Returns:
        Path to the output file
    """
    # Sanitize title for filename
    safe_title = re.sub(r'[\\/:*?"<>|]', "_", title).lower().replace(" ", "_")

    # Add timestamp to avoid overwriting
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)

    # Build filename
    filename = f"{safe_title}_{timestamp}.pdf"

    return os.path.join(output_dir, filename)


def find_matching_logo(title):
    """Find a logo file in the logos directory that matches the PDF title"""
    logos_dir = "logos"
    if not os.path.exists(logos_dir):
        return None

    # Normalize the title for comparison
    normalized_title = title.lower().replace(" ", "")

    # List all logo files
    logo_files = [
        f for f in os.listdir(logos_dir) if os.path.isfile(os.path.join(logos_dir, f))
    ]

    # First, try exact match
    for logo_file in logo_files:
        base_name = os.path.splitext(logo_file)[0].lower().replace(" ", "")
        if normalized_title == base_name:
            return os.path.join(logos_dir, logo_file)

    # If no exact match, try partial match
    for logo_file in logo_files:
        base_name = os.path.splitext(logo_file)[0].lower().replace(" ", "")
        if base_name in normalized_title or normalized_title in base_name:
            return os.path.join(logos_dir, logo_file)

    return None


def validate_questions(questions: List[Dict[str, str]]) -> bool:
    """
    Validate that the questions list is properly formatted.

    Args:
        questions: List of question dictionaries to validate

    Returns:
        True if questions are valid, False otherwise
    """
    if not questions:
        return False

    for question in questions:
        if "question" not in question:
            return False
        if "answer" not in question:
            return False

    return True


def register_fonts() -> None:
    """Register fonts for use in the PDF."""
    fonts_dir = os.path.join(os.path.dirname(__file__), "../../fonts")

    # Create fonts directory if it doesn't exist
    os.makedirs(fonts_dir, exist_ok=True)

    # Define font files and their names
    font_mapping = {
        "Roboto-Regular.ttf": "Roboto",
        "Roboto-Bold.ttf": "Roboto-Bold",
        "Roboto-Italic.ttf": "Roboto-Italic",
        "Roboto-BoldItalic.ttf": "Roboto-BoldItalic",
    }

    # Register each font
    for font_file, font_name in font_mapping.items():
        font_path = os.path.join(fonts_dir, font_file)

        # Skip if font file doesn't exist
        if not os.path.exists(font_path):
            continue

        try:
            pdfmetrics.registerFont(TTFont(font_name, font_path))
        except Exception:
            # If font registration fails, continue without the font
            pass


class QuestionNumbering(Flowable):
    """
    A custom flowable for numbering questions.
    This creates a circle with the question number inside.
    """

    def __init__(self, number: int, color: str, size: int = 24):
        Flowable.__init__(self)
        self.number = number
        self.size = size
        self.color = color

    def draw(self):
        """Draw the question number circle."""
        # Set circle color
        self.canv.setFillColor(self.color)

        # Draw circle
        radius = self.size / 2
        self.canv.circle(radius, radius, radius, fill=1)

        # Set text color and font
        self.canv.setFillColor(colors.white)
        self.canv.setFont("Helvetica-Bold", self.size * 0.6)

        # Draw number, centered in circle
        number_text = str(self.number)
        number_width = self.canv.stringWidth(
            number_text, "Helvetica-Bold", self.size * 0.6
        )
        self.canv.drawString(
            radius - number_width / 2, radius - self.size * 0.2, number_text
        )

    def wrap(self, availWidth, availHeight):
        """Return the size of the flowable."""
        return (self.size, self.size)


def create_cover_page(canvas, pdf_gen):
    """
    Create a cover page for the PDF.

    Args:
        canvas: ReportLab canvas to draw on
        pdf_gen: PDFGenerator object with parameters
    """
    # Extract parameters
    width, height = pdf_gen.page_size
    margin = pdf_gen.margin
    colors = pdf_gen.colors
    title = pdf_gen.title
    fonts = pdf_gen.fonts

    # Fill background
    canvas.setFillColorRGB(*colors["primary"])
    canvas.rect(0, 0, width, height, fill=True)

    # Add title
    title_y = height * 0.75
    canvas.setFont(fonts["title_font"], fonts["title_size"])
    canvas.setFillColorRGB(*colors["background"])
    title_width = canvas.stringWidth(title, fonts["title_font"], fonts["title_size"])
    canvas.drawString(width / 2 - title_width / 2, title_y, title)

    # Add subtitle
    subtitle = "Interview Questions"
    subtitle_y = title_y - 40
    canvas.setFont(fonts["content_font"], fonts["subtitle_size"])
    subtitle_width = canvas.stringWidth(
        subtitle, fonts["content_font"], fonts["subtitle_size"]
    )
    canvas.drawString(width / 2 - subtitle_width / 2, subtitle_y, subtitle)

    canvas.showPage()


def create_qa_page(canvas, pdf_gen, question_data):
    """
    Create a question and answer page.

    Args:
        canvas: The ReportLab canvas to draw on
        pdf_gen: PDF generator object with parameters
        question_data: Dictionary containing the question and answer
    """
    # Extract parameters
    width, height = pdf_gen.page_size
    margin = pdf_gen.margin
    colors = pdf_gen.colors
    fonts = pdf_gen.fonts
    text_renderer = pdf_gen.text_renderer

    # Available content area
    content_width = width - (2 * margin)
    content_height = height - (2 * margin)

    # Start positions
    start_x = margin
    start_y = height - margin - fonts["title_size"]

    # Draw background - use theme's background color
    background_color = colors.get(
        "background", (1, 1, 1)
    )  # Get background from colors or default to white
    canvas.setFillColorRGB(*background_color)
    canvas.rect(0, 0, width, height, fill=True)

    # Draw a thin header bar
    canvas.setFillColorRGB(*colors["primary"])
    canvas.rect(0, height - 40, width, 40, fill=True)

    # Add title to header
    canvas.setFillColorRGB(1, 1, 1)  # White text
    canvas.setFont(fonts["title_font"], fonts["title_size"] * 0.6)
    canvas.drawString(margin, height - 25, pdf_gen.title)

    # Question Label
    canvas.setFont(fonts["title_font"], fonts["title_size"] * 0.8)
    canvas.setFillColorRGB(*colors["title"])
    canvas.drawString(start_x, start_y - 40, "Question:")

    # Question content
    start_y -= fonts["title_size"] * 1.2 + 40
    text_renderer.draw_text_with_highlights(
        canvas,
        question_data["question"],
        start_x,
        start_y,
        content_width,
        fonts["content_font"],
        fonts["content_size"],
        colors["text"],
    )

    # Calculate where to start the answer based on question length
    question_lines = len(question_data["question"].split("\n"))
    code_blocks = question_data["question"].count("```")
    # If question has code blocks, allocate more space
    if code_blocks > 0:
        min_question_space = fonts["content_size"] * 1.2 * max(10, question_lines)
    else:
        min_question_space = fonts["content_size"] * 1.2 * max(5, question_lines)

    # Answer position - leave appropriate space based on question length
    answer_y = start_y - min_question_space

    # Answer Label
    canvas.setFont(fonts["title_font"], fonts["title_size"] * 0.8)
    canvas.setFillColorRGB(*colors["title"])
    canvas.drawString(start_x, answer_y, "Answer:")

    # Answer content
    answer_y -= fonts["title_size"] * 1.2

    # Draw the answer with special handling for code blocks
    final_y = text_renderer.draw_text_with_highlights(
        canvas,
        question_data["answer"],
        start_x,
        answer_y,
        content_width,
        fonts["content_font"],
        fonts["content_size"],
        colors["text"],
    )

    # Add page number at the bottom
    canvas.setFont(fonts["content_font"], 10)
    canvas.setFillColorRGB(*colors["text"])
    canvas.drawCentredString(
        width / 2, margin / 2, f"{pdf_gen.title} • Question & Answer"
    )

    return final_y


def create_milestone_page(c, pdf_gen, progress_percentage):
    """Create a milestone page showing progress"""
    # Extract parameters from pdf_gen - support both dict and object formats
    if hasattr(pdf_gen, "page_size") and hasattr(pdf_gen, "colors"):
        # Object format
        colors = pdf_gen.colors
        page_width, page_height = pdf_gen.page_size
    else:
        # Dictionary format
        colors = pdf_gen["colors"]
        page_width = pdf_gen["page_width"]
        page_height = pdf_gen["page_height"]

    # Get progress message - support both dict and object formats
    if hasattr(pdf_gen, "progress_slides"):
        progress_message = pdf_gen.progress_slides.get(
            progress_percentage, f"{progress_percentage}% Complete"
        )
    else:
        progress_message = pdf_gen["progress_slides"].get(
            progress_percentage, f"{progress_percentage}% Complete"
        )

    # Fill background
    c.setFillColor(colors["primary"])
    c.rect(0, 0, page_width, page_height, fill=True)

    # Add progress percentage
    c.setFillColor(colors["background"])
    c.setFont("Helvetica-Bold", 72)
    text = f"{progress_percentage}%"
    text_width = c.stringWidth(text, "Helvetica-Bold", 72)
    c.drawString(page_width / 2 - text_width / 2, page_height / 2 + 36, text)

    # Add progress message
    c.setFont("Helvetica", 24)
    message_width = c.stringWidth(progress_message, "Helvetica", 24)
    c.drawString(
        page_width / 2 - message_width / 2, page_height / 2 - 24, progress_message
    )

    # Draw progress bar
    bar_width = page_width * 0.6
    bar_height = 20
    bar_x = page_width * 0.2
    bar_y = page_height / 2 - 60

    # Draw background
    c.setFillColor(colors["secondary"])
    c.rect(bar_x, bar_y, bar_width, bar_height, fill=True)

    # Draw progress
    c.setFillColor(colors["text"])
    c.rect(bar_x, bar_y, bar_width * (progress_percentage / 100), bar_height, fill=True)

    c.showPage()


def create_final_page(c, pdf_gen):
    """Create a final page for the PDF"""
    # Extract parameters from pdf_gen - support both dict and object formats
    if hasattr(pdf_gen, "page_size") and hasattr(pdf_gen, "colors"):
        # Object format
        colors = pdf_gen.colors
        page_width, page_height = pdf_gen.page_size
        title = pdf_gen.title
    else:
        # Dictionary format
        colors = pdf_gen["colors"]
        page_width = pdf_gen["page_width"]
        page_height = pdf_gen["page_height"]
        title = pdf_gen["title"]

    # Fill background
    c.setFillColor(colors["primary"])
    c.rect(0, 0, page_width, page_height, fill=True)

    # Add completion message
    c.setFillColor(colors["background"])
    c.setFont("Helvetica-Bold", 36)
    completion_text = "Congratulations!"
    text_width = c.stringWidth(completion_text, "Helvetica-Bold", 36)
    c.drawString(page_width / 2 - text_width / 2, page_height / 2 + 50, completion_text)

    # Add subtitle
    c.setFont("Helvetica", 24)
    subtitle = f"You've completed all {title} questions"
    subtitle_width = c.stringWidth(subtitle, "Helvetica", 24)
    c.drawString(page_width / 2 - subtitle_width / 2, page_height / 2, subtitle)

    # Add footer message
    c.setFont("Helvetica", 14)
    footer = "Ready for your interview? Best of luck!"
    footer_width = c.stringWidth(footer, "Helvetica", 14)
    c.drawString(page_width / 2 - footer_width / 2, page_height / 2 - 50, footer)

    c.showPage()


def wrap_text(text, canvas, font_name, font_size, max_width):
    """
    Wrap text to fit within a specified width.

    Args:
        text: Text to wrap
        canvas: Canvas object for measuring text
        font_name: Font name
        font_size: Font size
        max_width: Maximum width

    Returns:
        List of text lines
    """
    canvas.setFont(font_name, font_size)
    words = text.split()
    lines = []
    current_line = []

    for word in words:
        # Test if adding this word exceeds the width
        test_line = " ".join(current_line + [word])
        if canvas.stringWidth(test_line) <= max_width:
            current_line.append(word)
        else:
            # If the current line is not empty, add it to lines
            if current_line:
                lines.append(" ".join(current_line))
                current_line = [word]
            else:
                # If the word itself is too long, split it
                lines.append(word)
                current_line = []

    # Add the last line if not empty
    if current_line:
        lines.append(" ".join(current_line))

    return lines


def create_pdf(questions, output_file, title=None, color_scheme="blue"):
    """
    Create a PDF from the given questions and answers.

    Args:
        questions: List of question dictionaries
        output_file: Path to save the PDF to
        title: Optional title for the PDF
        color_scheme: Name of the color scheme to use (default: "blue")

    Returns:
        Path to the created PDF
    """
    # Validate questions
    if not questions or not isinstance(questions, list):
        raise ValueError("Questions must be a non-empty list")

    # Set up default title if none provided
    if not title:
        title = get_default_title(output_file)

    # Validate and set color scheme
    if color_scheme not in COLOR_SCHEMES:
        print(f"Warning: Unknown color scheme '{color_scheme}'. Using 'blue' instead.")
        color_scheme = "blue"

    # Import the original create_qa_page to be used by both themes
    from .page_generators import create_qa_page as original_create_qa_page

    # Define an improved create_qa_page function for both themes
    def improved_create_qa_page(canvas, pdf_gen, question_data):
        """Enhanced create_qa_page function with better styling for both themes"""
        # Extract parameters
        width, height = pdf_gen.page_size
        margin = pdf_gen.margin
        colors = pdf_gen.colors
        fonts = pdf_gen.fonts
        text_renderer = pdf_gen.text_renderer

        # Check if we're using dark theme
        is_dark_theme = hasattr(pdf_gen, "is_dark_theme") and pdf_gen.is_dark_theme

        # Available content area
        content_width = width - (2 * margin)

        # Start positions
        start_x = margin
        start_y = height - margin - fonts["title_size"]

        # Set background color based on theme
        if is_dark_theme:
            # Use very dark background for dark theme
            background_color = (0.03, 0.03, 0.03)
        else:
            # Use standard background color for light theme
            background_color = colors.get("background", (1, 1, 1))

        canvas.setFillColorRGB(*background_color)
        canvas.rect(0, 0, width, height, fill=True, stroke=False)

        # Get the primary color for header
        primary_color = colors.get("primary", (0, 0, 0.8))

        # Draw a thin header bar with the primary color
        canvas.setFillColorRGB(*primary_color)
        canvas.rect(0, height - 40, width, 40, fill=True, stroke=False)

        # Add title to header - white text
        canvas.setFillColorRGB(1, 1, 1)
        canvas.setFont(fonts["title_font"], fonts["title_size"] * 0.6)
        canvas.drawString(margin, height - 25, pdf_gen.title)

        # Set text color based on theme
        if is_dark_theme:
            # Medium gray text for dark theme
            text_color = (0.75, 0.75, 0.75)
        else:
            # Standard text color for light theme
            text_color = colors.get("text", (0, 0, 0))

        # Question Label
        canvas.setFont(fonts["title_font"], fonts["title_size"] * 0.8)
        canvas.setFillColorRGB(*primary_color if not is_dark_theme else text_color)
        canvas.drawString(start_x, start_y - 40, "Question:")

        # Question content
        start_y -= fonts["title_size"] * 1.2 + 40

        # Draw the question
        canvas.saveState()
        text_renderer.draw_text_with_highlights(
            canvas,
            question_data["question"],
            start_x,
            start_y,
            content_width,
            fonts["content_font"],
            fonts["content_size"],
            text_color,
        )
        canvas.restoreState()

        # Calculate answer position
        question_lines = len(question_data["question"].split("\n"))
        code_blocks = question_data["question"].count("```")
        inline_code = question_data["question"].count("`") - (code_blocks * 2)

        if code_blocks > 0:
            min_question_space = fonts["content_size"] * 1.2 * (question_lines + 2)
        else:
            min_question_space = (
                fonts["content_size"]
                * 1.2
                * max(5, question_lines + (inline_code // 4))
            )

        answer_y = start_y - min_question_space

        # Answer Label
        canvas.setFont(fonts["title_font"], fonts["title_size"] * 0.8)
        canvas.setFillColorRGB(*primary_color if not is_dark_theme else text_color)
        canvas.drawString(start_x, answer_y, "Answer:")

        # Answer content
        answer_y -= fonts["title_size"] * 1.2

        # Draw the answer
        canvas.saveState()
        final_y = text_renderer.draw_text_with_highlights(
            canvas,
            question_data["answer"],
            start_x,
            answer_y,
            content_width,
            fonts["content_font"],
            fonts["content_size"],
            text_color,
        )
        canvas.restoreState()

        # Add page number
        canvas.setFont(fonts["content_font"], 10)
        canvas.setFillColorRGB(*primary_color if not is_dark_theme else text_color)
        canvas.drawCentredString(
            width / 2, margin / 2, f"{pdf_gen.title} • Question & Answer"
        )

        return final_y

    # Replace the original function with our improved version for all themes
    from . import page_generators

    page_generators.create_qa_page = improved_create_qa_page

    # Get color dictionary for selected scheme
    color_dict = COLOR_SCHEMES.get(color_scheme)

    # Convert color hex values to RGB tuples for canvas drawing
    colors = {}
    for key, hex_color in color_dict.items():
        # Check if we already have an RGB tuple
        if isinstance(hex_color, tuple):
            colors[key] = hex_color
        else:
            # Convert hex to RGB tuple
            if isinstance(hex_color, str) and hex_color.startswith("#"):
                # Remove the # if present
                hex_color = hex_color[1:]

            if isinstance(hex_color, str):
                r = int(hex_color[0:2], 16) / 255.0
                g = int(hex_color[2:4], 16) / 255.0
                b = int(hex_color[4:6], 16) / 255.0
                colors[key] = (r, g, b)
            else:
                # If it's already a reportlab color, use its RGB components
                try:
                    # ReportLab colors already have attributes in the 0-1 range
                    r = hex_color.red
                    g = hex_color.green
                    b = hex_color.blue
                    colors[key] = (r, g, b)
                except (AttributeError, TypeError) as e:
                    # Fallback to a default color if conversion fails
                    if key == "primary":
                        colors[key] = (0, 0, 0.8)  # Default blue
                    elif key == "secondary":
                        colors[key] = (0, 0, 0.6)  # Dark blue
                    elif key == "accent":
                        colors[key] = (0.2, 0.6, 0.8)  # Light blue
                    elif key == "background":
                        # For dark theme use dark background, for light themes use white
                        if color_scheme == "dark":
                            colors[key] = (
                                0.03,
                                0.03,
                                0.03,
                            )  # #080808 very dark background
                        else:
                            colors[key] = (1.0, 1.0, 1.0)  # White for light themes
                    elif key == "text":
                        # For dark theme use light text, for light themes use dark text
                        if color_scheme == "dark":
                            colors[key] = (
                                0.9,
                                0.9,
                                0.9,
                            )  # Light gray for dark theme (changed from pure white)
                        else:
                            colors[key] = (0.1, 0.1, 0.1)  # Dark gray for light themes
                    else:
                        colors[key] = (0, 0, 0)  # Black for other cases

    # Ensure all required color keys are available
    required_colors = ["primary", "secondary", "accent", "text", "background", "title"]
    for color_key in required_colors:
        if color_key not in colors:
            # Map missing colors to appropriate existing ones
            if color_key == "title" and "text" in colors:
                colors["title"] = colors["text"]
            elif color_key == "primary" and "accent" in colors:
                colors["primary"] = colors["accent"]
            elif color_key == "secondary" and "background" in colors:
                colors["secondary"] = colors["background"]
            elif color_key == "accent" and "primary" in colors:
                colors["accent"] = colors["primary"]
            elif color_key == "text" and "primary" in colors:
                # For dark theme use light text, for light themes use dark text
                if color_scheme == "dark":
                    colors["text"] = (0.75, 0.75, 0.75)  # Medium gray for dark theme
                else:
                    colors["text"] = (0.1, 0.1, 0.1)  # Dark gray for light themes
            elif color_key == "background":
                # For dark theme use dark background, for light themes use white
                if color_scheme == "dark":
                    colors["background"] = (
                        0.03,
                        0.03,
                        0.03,
                    )  # #080808 very dark background
                else:
                    colors["background"] = (1.0, 1.0, 1.0)  # White for light themes

    # Final background and text color check for dark theme
    if color_scheme == "dark":
        # Force background to be very dark
        colors["background"] = (0.03, 0.03, 0.03)  # #080808 very dark background
        # Force text to be gray, not white
        colors["text"] = (0.75, 0.75, 0.75)  # Medium gray for better contrast

    # Set up page parameters
    page_size = letter  # Use letter size (8.5 x 11 inches)
    margin = 0.75 * inch

    # Set up fonts
    fonts = {
        "title_font": "Helvetica-Bold",
        "content_font": "Helvetica",
        "title_size": 24,
        "subtitle_size": 18,
        "content_size": 12,
    }

    # Prepare progress messages for milestone pages
    from .motivational_quotes import get_random_quote
    from .progress_messages import PROGRESS_MESSAGES

    # Get quotes for each milestone
    progress_quotes = {
        25: get_random_quote(),
        50: get_random_quote(),
        75: get_random_quote(),
    }

    # Create progress_slides dictionary with messages and quotes
    progress_slides = {}
    for percentage, messages in PROGRESS_MESSAGES.items():
        progress_slides[percentage] = {
            "messages": messages,
            "quote": progress_quotes[percentage],
        }

    # Initialize PDF parameters
    pdf_gen = PDFGenerator(
        page_size=page_size,
        margin=margin,
        colors=colors,
        fonts=fonts,
        title=title,
        progress_slides=progress_slides,
        color_scheme=color_scheme,
    )

    try:
        # Create PDF
        canvas = Canvas(output_file, pagesize=page_size)

        # Create cover page
        create_cover_page(canvas, pdf_gen)

        # Calculate the milestone positions
        total_questions = len(questions)
        milestones = {
            25: max(1, round(total_questions * 0.25)),
            50: max(1, round(total_questions * 0.5)),
            75: max(1, round(total_questions * 0.75)),
        }

        # Create a page for each question with milestone pages at appropriate positions
        for i, question in enumerate(questions, 1):
            # Check if we've reached a milestone
            for percentage, position in milestones.items():
                if i == position:
                    # Create milestone page with progress information
                    canvas.setPageSize(page_size)

                    # Use progress_slides dictionary for messages and quotes
                    milestone_data = progress_slides[percentage]
                    milestone_message = random.choice(milestone_data["messages"])
                    milestone_quote = milestone_data["quote"]

                    # Add a progress milestone page
                    create_progress_slide(canvas, pdf_gen, i, total_questions)

                    # Uncomment this if you also want to add a milestone quote page
                    # canvas.showPage()
                    # create_quote_page(canvas, milestone_quote[0], milestone_quote[1], colors)

            # Create a new page for this question
            canvas.setPageSize(page_size)
            create_qa_page(canvas, pdf_gen, question)
            canvas.showPage()

        # Create a final page
        canvas.setPageSize(page_size)
        create_ending_page(
            canvas, pdf_gen, f"You've completed all {len(questions)} questions!"
        )

        # Save PDF
        canvas.save()

        return output_file
    except Exception as e:
        print(f"Error creating PDF: {str(e)}")
        import traceback

        print(traceback.format_exc())
        raise e


class PDFGenerator:
    """
    Class to hold PDF generation parameters.

    This class encapsulates all the settings and objects needed for PDF generation.
    """

    def __init__(
        self,
        page_size,
        margin,
        colors,
        fonts,
        title,
        progress_slides,
        color_scheme=None,
    ):
        """
        Initialize the PDF generator.

        Args:
            page_size: The page size for the PDF (tuple of width, height)
            margin: The margin for the PDF
            colors: Dictionary of colors to use
            fonts: Dictionary of fonts to use
            title: Title for the PDF
            progress_slides: Dictionary of progress slides
            color_scheme: The name of the color scheme
        """
        self.page_size = page_size
        self.margin = margin
        self.colors = colors
        self.fonts = fonts
        self.title = title
        self.progress_slides = progress_slides
        self.color_scheme = color_scheme

        # Determine if we're using a dark theme
        self.is_dark_theme = False
        if color_scheme == "dark":
            self.is_dark_theme = True

        # Double check background color
        if "background" in colors:
            bg_color = colors["background"]
            if isinstance(bg_color, tuple) and len(bg_color) >= 3:
                # If the average RGB value is less than 0.5, it should be a dark theme
                avg_rgb = sum(bg_color[:3]) / 3
                if avg_rgb < 0.2:
                    self.is_dark_theme = True

        # Initialize the text renderer
        from .text_renderer import TextRenderer

        self.text_renderer = TextRenderer(colors)
        self.text_renderer.is_dark_theme = self.is_dark_theme
