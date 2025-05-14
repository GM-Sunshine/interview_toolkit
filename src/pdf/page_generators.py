"""
Page generators for PDF creation.

This module provides functions for generating different types of pages in PDF documents.
"""

import os
import random
import tempfile
from datetime import datetime
from pathlib import Path
import io

# Check if qrcode is available
qrcode_available = False
try:
    import qrcode  # type: ignore
    import qrcode.constants  # type: ignore
    from io import BytesIO

    qrcode_available = True
except ImportError:
    # Create mock constants for compatibility
    class Constants:
        ERROR_CORRECT_L = 1
        ERROR_CORRECT_M = 0
        ERROR_CORRECT_Q = 3
        ERROR_CORRECT_H = 2

    # If qrcode module is not available, create a mock module
    class QrcodeModule:
        def __init__(self):
            self.constants = Constants()

    # Create a mock qrcode module with constants
    qrcode = QrcodeModule()
    pass

from reportlab.lib.pagesizes import letter, landscape
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import cm, inch
from reportlab.pdfbase.pdfmetrics import stringWidth
from reportlab.platypus import Frame, Image, Paragraph

from .pdf_utils import add_subtle_pattern, draw_smooth_gradient, hex_to_rgb


def create_cover_page(c, pdf_gen):
    """
    Create a cover page for the PDF.

    Args:
        c: ReportLab canvas to draw on
        pdf_gen: PDFGenerator object with parameters
    """
    # Extract parameters
    width, height = pdf_gen.page_size
    colors = pdf_gen.colors
    title = pdf_gen.title
    text_renderer = pdf_gen.text_renderer
    fonts = pdf_gen.fonts

    # Fill background with a gradient
    draw_smooth_gradient(
        c,
        0,
        0,
        width,
        height,
        colors.get("primary", (0, 0, 0.8)),
        colors.get("secondary", (0, 0, 0.6)),
        "vertical",
    )

    # Add decorative elements - a subtle pattern overlay
    add_subtle_pattern(
        c, 0, 0, width, height, colors.get("primary", (0, 0, 0.8)), opacity=0.1
    )

    # Try to load and display a technology-specific logo first, then fall back to default
    logo_found = False

    # Check for technology-specific logo
    normalized_title = title.lower().replace(" ", "").replace("-", "").replace("_", "")

    # Common technology names and their variations
    tech_variations = {
        "python": ["python", "py", "django", "flask"],
        "javascript": ["javascript", "js", "typescript", "ts", "node", "nodejs"],
        "php": ["php", "laravel", "symfony", "wordpress"],
        "java": ["java", "springboot", "spring"],
        "kubernetes": ["kubernetes", "k8s", "kube"],
        "mysql": ["mysql", "sql", "database"],
        "bash": ["bash", "shell", "linux", "unix"],
        "vuejs": ["vue", "vuejs"],
        "next": ["next", "nextjs"],
    }

    # Try to find a matching logo
    for logo_file in os.listdir("logos"):
        # Skip non-image files
        if not logo_file.lower().endswith((".png", ".jpg", ".jpeg", ".gif", ".webp")):
            continue

        # Check if filename (without extension) matches the title
        logo_name = (
            os.path.splitext(logo_file)[0]
            .lower()
            .replace(" ", "")
            .replace("-", "")
            .replace("_", "")
        )

        # Direct match with title
        if logo_name in normalized_title or normalized_title in logo_name:
            try:
                c.saveState()
                # Calculate the logo size and position
                logo_width = width * 0.3  # 30% of page width
                logo_height = logo_width * 0.75  # Maintain aspect ratio
                logo_x = (width - logo_width) / 2
                logo_y = height * 0.8

                # Draw logo
                c.drawImage(
                    f"logos/{logo_file}",
                    logo_x,
                    logo_y,
                    width=logo_width,
                    height=logo_height,
                    mask="auto",
                )
                c.restoreState()
                logo_found = True
                break
            except Exception:
                # Silently handle logo errors, not critical for PDF generation
                pass

        # Check for technology variations
        for tech, variations in tech_variations.items():
            if any(var in normalized_title for var in variations) and tech in logo_name:
                try:
                    c.saveState()
                    # Calculate the logo size and position
                    logo_width = width * 0.3  # 30% of page width
                    logo_height = logo_width * 0.75  # Maintain aspect ratio
                    logo_x = (width - logo_width) / 2
                    logo_y = height * 0.8

                    # Draw logo
                    c.drawImage(
                        f"logos/{logo_file}",
                        logo_x,
                        logo_y,
                        width=logo_width,
                        height=logo_height,
                        mask="auto",
                    )
                    c.restoreState()
                    logo_found = True
                    break
                except Exception:
                    # Silently handle logo errors, not critical for PDF generation
                    pass

            if logo_found:
                break

    # If no technology-specific logo found, use the default gm-sunshine logo
    if not logo_found:
        try:
            gm_logo_path = "logos/gm-sunshine.webp"
            if os.path.exists(gm_logo_path):
                c.saveState()
                # Calculate the logo size and position
                logo_width = width * 0.2  # 20% of page width
                # Use correct aspect ratio for GM Sunshine logo (556:200 or 2.78:1)
                logo_height = logo_width / 2.78  # Original aspect ratio is 556:200
                logo_x = width - logo_width - 30
                logo_y = height - logo_height - 30

                # Draw logo
                c.drawImage(
                    gm_logo_path,
                    logo_x,
                    logo_y,
                    width=logo_width,
                    height=logo_height,
                    mask="auto",
                )
                c.restoreState()
        except Exception:
            # Silently handle logo errors, not critical for PDF generation
            pass

    # Add title
    title_y = height * 0.65
    c.setFont(fonts["title_font"], fonts["title_size"] * 1.5)
    c.setFillColorRGB(*colors.get("background", (1, 1, 1)))
    title_width = c.stringWidth(title, fonts["title_font"], fonts["title_size"] * 1.5)
    c.drawString(width / 2 - title_width / 2, title_y, title)

    # Add subtitle
    subtitle = "Interview Questions"
    subtitle_y = title_y - 60
    c.setFont(fonts["content_font"], fonts["subtitle_size"] * 1.2)
    subtitle_width = c.stringWidth(
        subtitle, fonts["content_font"], fonts["subtitle_size"] * 1.2
    )
    c.drawString(width / 2 - subtitle_width / 2, subtitle_y, subtitle)

    # Add decorative line
    c.setStrokeColorRGB(*colors.get("background", (1, 1, 1)))
    c.setLineWidth(2)
    c.line(width / 4, subtitle_y - 30, width * 3 / 4, subtitle_y - 30)

    # Add inspirational quote if available
    try:
        from .motivational_quotes import get_random_quote

        quote, author = get_random_quote()

        # Draw quote
        quote_y = height * 0.4
        c.setFont(fonts["content_font"], fonts["content_size"])
        c.setFillColorRGB(*colors.get("background", (1, 1, 1)))

        # Wrap quote text to fit
        max_quote_width = width * 0.7
        quote_lines = []
        current_line = ""
        for word in quote.split():
            test_line = current_line + " " + word if current_line else word
            if (
                c.stringWidth(test_line, fonts["content_font"], fonts["content_size"])
                < max_quote_width
            ):
                current_line = test_line
            else:
                quote_lines.append(current_line)
                current_line = word
        if current_line:
            quote_lines.append(current_line)

        # Draw each line of the quote
        for i, line in enumerate(quote_lines):
            line_width = c.stringWidth(
                line, fonts["content_font"], fonts["content_size"]
            )
            c.drawString(width / 2 - line_width / 2, quote_y - i * 20, line)

        # Draw author
        author_y = quote_y - len(quote_lines) * 20 - 20
        c.setFont(fonts["content_font"], fonts["content_size"])
        author_text = f"— {author}"
        author_width = c.stringWidth(
            author_text, fonts["content_font"], fonts["content_size"]
        )
        c.drawString(width / 2 - author_width / 2, author_y, author_text)
    except Exception:
        # Silently handle quote errors, not critical for PDF generation
        pass

    c.showPage()


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

    # Check if we're using a dark theme from pdf_gen object
    is_dark_theme = hasattr(pdf_gen, "is_dark_theme") and pdf_gen.is_dark_theme

    # Available content area
    content_width = width - (2 * margin)
    content_height = height - (2 * margin)

    # Start positions
    start_x = margin
    start_y = height - margin - fonts["title_size"]

    # Draw background - use the theme's background color
    if is_dark_theme:
        # Force dark background for dark theme
        background_color = (0.03, 0.03, 0.03)  # Very dark background
    else:
        background_color = colors.get(
            "background", (1, 1, 1)
        )  # Default to white if not found

    canvas.setFillColorRGB(*background_color)
    canvas.rect(0, 0, width, height, fill=True, stroke=False)

    # Ensure we have valid RGB colors for the primary color
    primary_color = colors.get("primary", (0, 0, 0.8))  # Default to blue if not found
    if not isinstance(primary_color, tuple) or len(primary_color) != 3:
        # Convert from hex if needed
        if isinstance(primary_color, str) and primary_color.startswith("#"):
            # Convert hex to RGB
            r = int(primary_color[1:3], 16) / 255.0
            g = int(primary_color[3:5], 16) / 255.0
            b = int(primary_color[5:7], 16) / 255.0
            primary_color = (r, g, b)
        else:
            # Fallback to default blue
            primary_color = (0, 0, 0.8)

    # Draw a thin header bar with the primary color
    canvas.setFillColorRGB(*primary_color)
    canvas.rect(0, height - 40, width, 40, fill=True, stroke=False)

    # Add title to header - always use white for contrast against primary color header
    canvas.setFillColorRGB(1, 1, 1)  # White text for header
    canvas.setFont(fonts["title_font"], fonts["title_size"] * 0.6)
    canvas.drawString(margin, height - 25, pdf_gen.title)

    # Define text color for dark theme
    if is_dark_theme:
        # Force gray text for dark theme
        text_color = (0.75, 0.75, 0.75)  # Medium gray
    else:
        text_color = colors.get("text", (0, 0, 0))  # Default to black
        if not isinstance(text_color, tuple) or len(text_color) != 3:
            text_color = (0, 0, 0)  # Fallback to black

    # Question Label - use primary color if not dark theme, otherwise use text color
    canvas.setFont(fonts["title_font"], fonts["title_size"] * 0.8)
    if is_dark_theme:
        canvas.setFillColorRGB(*text_color)
    else:
        canvas.setFillColorRGB(*primary_color)
    canvas.drawString(start_x, start_y - 40, "Question:")

    # Question content
    start_y -= fonts["title_size"] * 1.2 + 40

    # Check if the question contains code blocks and adjust spacing
    question_has_code = (
        "```" in question_data["question"] or "`" in question_data["question"]
    )

    # Make sure canvas is in the right state for the text renderer
    canvas.saveState()

    # Draw the question with special handling for code blocks
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

    # Restore canvas state
    canvas.restoreState()

    # Calculate where to start the answer based on question length and complexity
    question_lines = len(question_data["question"].split("\n"))
    code_blocks = question_data["question"].count("```")
    inline_code = question_data["question"].count("`") - (
        code_blocks * 2
    )  # Each code block has 2 sets of ```

    # If question has code blocks, allocate more space
    if code_blocks > 0:
        min_question_space = fonts["content_size"] * 1.2 * (question_lines + 2)
    else:
        min_question_space = (
            fonts["content_size"] * 1.2 * max(5, question_lines + (inline_code // 4))
        )

    # Answer position - leave appropriate space based on question length
    answer_y = start_y - min_question_space

    # Answer Label - use primary color if not dark theme, otherwise use text color
    canvas.setFont(fonts["title_font"], fonts["title_size"] * 0.8)
    if is_dark_theme:
        canvas.setFillColorRGB(*text_color)
    else:
        canvas.setFillColorRGB(*primary_color)
    canvas.drawString(start_x, answer_y, "Answer:")

    # Answer content
    answer_y -= fonts["title_size"] * 1.2

    # Check if the answer contains code blocks
    answer_has_code = "```" in question_data["answer"] or "`" in question_data["answer"]

    # Save canvas state again for answer rendering
    canvas.saveState()

    # Draw the answer with special handling for code blocks
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

    # Restore canvas state
    canvas.restoreState()

    # Add page number at the bottom
    canvas.setFont(fonts["content_font"], 10)
    if is_dark_theme:
        canvas.setFillColorRGB(*text_color)  # Use text color for footer in dark mode
    else:
        canvas.setFillColorRGB(
            *primary_color
        )  # Use primary color for footer in light mode
    canvas.drawCentredString(
        width / 2, margin / 2, f"{pdf_gen.title} • Question & Answer"
    )

    return final_y


def create_milestone_page(c, pdf_gen, progress_percentage):
    """
    Create a milestone page showing progress.

    Args:
        c: ReportLab canvas to draw on
        pdf_gen: Dictionary of PDF generation parameters
        progress_percentage: Current progress percentage
    """
    # Extract parameters from pdf_gen
    colors = pdf_gen["colors"]
    page_width = pdf_gen["page_width"]
    page_height = pdf_gen["page_height"]

    # Get progress message
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
    """
    Create a final page for the PDF.

    Args:
        c: ReportLab canvas to draw on
        pdf_gen: Dictionary of PDF generation parameters
    """
    # Extract parameters from pdf_gen
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


def create_summary_page(c, pdf_gen, questions_data):
    """Create a summary page listing all questions"""
    try:
        # Draw background
        bg_color = hex_to_rgb(pdf_gen["colors"]["background"])
        r, g, b = bg_color
        c.setFillColorRGB(r, g, b)
        c.rect(
            0, 0, pdf_gen["page_width"], pdf_gen["page_height"], fill=True, stroke=False
        )

        # Add header
        header_text_color = pdf_gen["colors"]["text"]
        r, g, b = hex_to_rgb(header_text_color)
        c.setFillColorRGB(r, g, b)
        c.setFont(pdf_gen["fonts"]["bold"], 18)
        c.drawString(1 * cm, pdf_gen["page_height"] - 1.5 * cm, "Summary of Questions")
        c.drawRightString(
            pdf_gen["page_width"] - 1 * cm,
            pdf_gen["page_height"] - 1.5 * cm,
            pdf_gen["title"],
        )

        # Add divider
        divider_y = pdf_gen["page_height"] - 2 * cm
        gradient_height = 0.3 * cm
        gradient_y = divider_y - gradient_height / 2

        # Get colors for gradient
        primary_color = hex_to_rgb(pdf_gen["colors"]["primary"])
        accent_color = hex_to_rgb(pdf_gen["colors"]["accent"])

        # Draw gradient bar
        draw_smooth_gradient(
            c,
            1 * cm,
            gradient_y,
            pdf_gen["page_width"] - 2 * cm,
            gradient_height,
            primary_color,
            accent_color,
            "horizontal",
        )

        # List all questions
        text_color = hex_to_rgb(pdf_gen["colors"]["text"])
        r, g, b = text_color
        c.setFillColorRGB(r, g, b)
        c.setFont(pdf_gen["fonts"]["regular"], 12)

        y_position = pdf_gen["page_height"] - 3 * cm
        for idx, qa in enumerate(questions_data):
            question = qa.get("question", "No question provided")
            # Truncate long questions
            if len(question) > 80:
                question = question[:77] + "..."

            c.drawString(2 * cm, y_position, f"{idx + 1}. {question}")
            y_position -= 0.8 * cm

            # Add a new page if we've run out of space
            if y_position < 2 * cm:
                # Add footer
                footer_color = hex_to_rgb(pdf_gen["colors"]["text"])
                r, g, b = footer_color
                c.setFillColorRGB(r, g, b)
                c.setFont(pdf_gen["fonts"]["regular"], 10)
                c.drawCentredString(
                    pdf_gen["page_width"] / 2,
                    1 * cm,
                    f"{pdf_gen['title']} Interview Questions • Summary",
                )

                # Start a new page
                c.showPage()

                # Draw background on new page
                c.setFillColorRGB(*bg_color)
                c.rect(
                    0,
                    0,
                    pdf_gen["page_width"],
                    pdf_gen["page_height"],
                    fill=True,
                    stroke=False,
                )

                # Reset position
                y_position = pdf_gen["page_height"] - 1.5 * cm

                # Add continuation header
                c.setFillColorRGB(*text_color)
                c.setFont(pdf_gen["fonts"]["bold"], 18)
                c.drawString(1 * cm, y_position, "Summary of Questions (continued)")

                # Add divider
                divider_y = y_position - 0.5 * cm
                gradient_y = divider_y - gradient_height / 2

                # Draw gradient bar
                draw_smooth_gradient(
                    c,
                    1 * cm,
                    gradient_y,
                    pdf_gen["page_width"] - 2 * cm,
                    gradient_height,
                    primary_color,
                    accent_color,
                    "horizontal",
                )

                # Reset for continuing the list
                y_position = divider_y - 1 * cm
                c.setFont(pdf_gen["fonts"]["regular"], 12)

        # Add footer on the last page
        footer_color = hex_to_rgb(pdf_gen["colors"]["text"])
        r, g, b = footer_color
        c.setFillColorRGB(r, g, b)
        c.setFont(pdf_gen["fonts"]["regular"], 10)
        c.drawCentredString(
            pdf_gen["page_width"] / 2,
            1 * cm,
            f"{pdf_gen['title']} Interview Questions • Summary",
        )

        c.showPage()
    except Exception as e:
        raise e


def create_progress_slide(c, pdf_gen, current_milestone, total_questions):
    """Create a progress slide showing how far along the user is"""
    # Get percentage completed (rounded to nearest 5%)
    percentage = round((current_milestone / total_questions) * 20) * 5

    # Get a progress message
    if hasattr(pdf_gen, "progress_slides") and pdf_gen.progress_slides:
        # Get milestone data if available in new format
        milestone_data = pdf_gen.progress_slides.get(percentage, {})
        if isinstance(milestone_data, dict) and "messages" in milestone_data:
            messages = milestone_data["messages"]
            milestone_message = random.choice(messages)
        else:
            # Fallback for string values in old format
            milestone_message = (
                str(milestone_data)
                if milestone_data
                else f"You've completed {percentage}% of the questions!"
            )
    else:
        # Default message if no progress_slides dictionary
        milestone_message = f"You've completed {percentage}% of the questions!"

    # Extract parameters
    width, height = (
        pdf_gen.page_size if hasattr(pdf_gen, "page_size") else (letter[0], letter[1])
    )
    margin = pdf_gen.margin if hasattr(pdf_gen, "margin") else 0.75 * inch
    colors = (
        pdf_gen.colors
        if hasattr(pdf_gen, "colors")
        else {"primary": (0, 0, 0.8), "secondary": (0, 0, 0.6)}
    )
    fonts = (
        pdf_gen.fonts
        if hasattr(pdf_gen, "fonts")
        else {"title_font": "Helvetica-Bold", "content_font": "Helvetica"}
    )

    # Draw background - gradient
    draw_smooth_gradient(
        c,
        0,
        0,
        width,
        height,
        colors.get("primary", (0, 0, 0.8)),
        colors.get("secondary", (0, 0, 0.6)),
        "vertical",
    )

    # Add gm-sunshine logo
    try:
        gm_logo_path = "logos/gm-sunshine.webp"
        if os.path.exists(gm_logo_path):
            c.saveState()
            # Calculate the logo size and position
            logo_width = width * 0.15  # 15% of page width
            # Use correct aspect ratio for GM Sunshine logo (556:200 or 2.78:1)
            logo_height = logo_width / 2.78  # Original aspect ratio is 556:200
            logo_x = width - logo_width - 30
            logo_y = height - logo_height - 30

            # Draw logo
            c.drawImage(
                gm_logo_path,
                logo_x,
                logo_y,
                width=logo_width,
                height=logo_height,
                mask="auto",
            )
            c.restoreState()
    except Exception:
        # Silently handle logo errors, not critical for PDF generation
        pass

    # Draw progress circle
    circle_radius = 80
    circle_x = width / 2
    circle_y = height * 0.6

    # Draw background circle
    c.setFillColorRGB(*colors.get("accent", (0.2, 0.6, 0.8)))
    c.circle(circle_x, circle_y, circle_radius, fill=1, stroke=0)

    # Modified approach for progress indicator
    if percentage > 0:
        c.saveState()

        # Create a progress indicator using basic shapes
        # Draw a pie/sector shape to represent progress
        c.setFillColorRGB(*colors.get("background", (1, 1, 1)))

        # Calculate angle for the progress arc
        progress_angle = percentage * 3.6  # 3.6 degrees per percentage (360/100)

        # Use a combination of basic shapes
        # Draw filled circle with smaller radius in background color
        c.setFillColorRGB(*colors.get("background", (1, 1, 1)))
        inner_radius = circle_radius * 0.7  # Inner circle is 70% of outer circle
        c.circle(circle_x, circle_y, inner_radius, fill=1, stroke=0)

        c.restoreState()

    # Draw percentage text
    percentage_text = f"{percentage}%"
    # Use primary color or accent color for text to ensure it's visible
    if colors.get("accent", (0.2, 0.6, 0.8)) == colors.get("background", (1, 1, 1)):
        # If accent is same as background (rare case), use primary
        c.setFillColorRGB(*colors.get("primary", (0, 0, 0.8)))
    else:
        # Use accent color for contrast with background
        c.setFillColorRGB(*colors.get("accent", (0.2, 0.6, 0.8)))

    # Use smaller font size for better visual appearance
    font_size = 36  # Reduced from 48
    c.setFont(fonts.get("title_font", "Helvetica-Bold"), font_size)

    # Center the text in the circle
    text_width = c.stringWidth(
        percentage_text, fonts.get("title_font", "Helvetica-Bold"), font_size
    )
    # Adjust vertical position slightly for better centering with smaller font
    c.drawString(circle_x - text_width / 2, circle_y - 18, percentage_text)

    # Format the milestone message
    max_width = width * 0.6
    formatted_lines = []
    current_line = ""
    words = milestone_message.split()

    for word in words:
        test_line = current_line + " " + word if current_line else word
        if (
            c.stringWidth(test_line, fonts.get("title_font", "Helvetica-Bold"), 24)
            < max_width
        ):
            current_line = test_line
        else:
            if current_line:
                formatted_lines.append(current_line)
            current_line = word

    if current_line:
        formatted_lines.append(current_line)

    # Draw a semi-transparent background for text
    text_box_height = len(formatted_lines) * 30 + 20
    text_bg_width = width * 0.8
    text_bg_x = (width - text_bg_width) / 2
    text_bg_y = height * 0.4 - text_box_height / 2

    # Draw a rounded rectangle with semi-transparency
    c.saveState()
    c.setFillColorRGB(1, 1, 1, 0.8)  # Semi-transparent white
    c.roundRect(
        text_bg_x, text_bg_y, text_bg_width, text_box_height, 10, fill=1, stroke=0
    )
    c.restoreState()

    # Draw milestone message text
    c.setFillColorRGB(0, 0, 0)  # Black text
    c.setFont(fonts.get("title_font", "Helvetica-Bold"), 24)
    line_y = text_bg_y + text_box_height - 35
    for line in formatted_lines:
        text_width = c.stringWidth(line, fonts.get("title_font", "Helvetica-Bold"), 24)
        c.drawString((width - text_width) / 2, line_y, line)
        line_y -= 30

    # Add a motivational quote if available
    if hasattr(pdf_gen, "progress_slides") and pdf_gen.progress_slides:
        milestone_data = pdf_gen.progress_slides.get(percentage, {})
        if isinstance(milestone_data, dict) and "quote" in milestone_data:
            quote = milestone_data["quote"]
            if quote and len(quote) == 2:
                try:
                    quote_text, author = quote

                    # Draw quote
                    quote_y = height * 0.2
                    c.setFont(
                        fonts.get("content_font", "Helvetica"),
                        fonts.get("content_size", 12),
                    )
                    c.setFillColorRGB(*colors.get("background", (1, 1, 1)))

                    # Wrap quote text to fit
                    max_quote_width = width * 0.6
                    quote_lines = []
                    current_line = ""
                    for word in quote_text.split():
                        test_line = current_line + " " + word if current_line else word
                        if (
                            c.stringWidth(
                                test_line,
                                fonts.get("content_font", "Helvetica"),
                                fonts.get("content_size", 12),
                            )
                            < max_quote_width
                        ):
                            current_line = test_line
                        else:
                            quote_lines.append(current_line)
                            current_line = word
                    if current_line:
                        quote_lines.append(current_line)

                    # Draw each line of the quote
                    for i, line in enumerate(quote_lines):
                        line_width = c.stringWidth(
                            line,
                            fonts.get("content_font", "Helvetica"),
                            fonts.get("content_size", 12),
                        )
                        c.drawString(width / 2 - line_width / 2, quote_y - i * 16, line)

                    # Draw author
                    author_y = quote_y - len(quote_lines) * 16 - 16
                    c.setFont(
                        fonts.get("content_font", "Helvetica"),
                        fonts.get("content_size", 12),
                    )
                    author_text = f"— {author}"
                    author_width = c.stringWidth(
                        author_text,
                        fonts.get("content_font", "Helvetica"),
                        fonts.get("content_size", 12),
                    )
                    c.drawString(width / 2 - author_width / 2, author_y, author_text)
                except Exception:
                    # Silently handle quote errors, not critical for PDF generation
                    pass

    c.showPage()


def create_ending_page(c, pdf_gen, completion_message=None):
    """Create a final thank you page"""
    try:
        # Extract parameters
        if hasattr(pdf_gen, "page_size"):
            width, height = pdf_gen.page_size
        else:
            width, height = pdf_gen["page_width"], pdf_gen["page_height"]

        if hasattr(pdf_gen, "colors"):
            colors = pdf_gen.colors
        else:
            colors = pdf_gen["colors"]

        if hasattr(pdf_gen, "fonts"):
            fonts = pdf_gen.fonts
        else:
            fonts = pdf_gen.get(
                "fonts",
                {
                    "title_font": "Helvetica-Bold",
                    "content_font": "Helvetica",
                    "title_size": 24,
                    "subtitle_size": 18,
                    "content_size": 12,
                },
            )

        if hasattr(pdf_gen, "title"):
            title = pdf_gen.title
        else:
            title = pdf_gen.get("title", "Interview Questions")

        # Draw a nice gradient background
        draw_smooth_gradient(
            c,
            0,
            0,
            width,
            height,
            colors.get("primary", (0, 0, 0.8)),
            colors.get("secondary", (0, 0, 0.6)),
            "vertical",
        )

        # Add decorative elements
        add_subtle_pattern(
            c, 0, 0, width, height, colors.get("primary", (0, 0, 0.8)), opacity=0.15
        )

        # Try to load and display a technology-specific logo first, then fall back to default
        logo_found = False
        logo_y = 0  # Initialize logo_y for QR code positioning

        # Check for technology-specific logo
        normalized_title = (
            title.lower().replace(" ", "").replace("-", "").replace("_", "")
        )

        # Common technology names and their variations
        tech_variations = {
            "python": ["python", "py", "django", "flask"],
            "javascript": ["javascript", "js", "typescript", "ts", "node", "nodejs"],
            "php": ["php", "laravel", "symfony", "wordpress"],
            "java": ["java", "springboot", "spring"],
            "kubernetes": ["kubernetes", "k8s", "kube"],
            "mysql": ["mysql", "sql", "database"],
            "bash": ["bash", "shell", "linux", "unix"],
            "vuejs": ["vue", "vuejs"],
            "next": ["next", "nextjs"],
        }

        # Try to find a matching logo
        for logo_file in os.listdir("logos"):
            # Skip non-image files
            if not logo_file.lower().endswith(
                (".png", ".jpg", ".jpeg", ".gif", ".webp")
            ):
                continue

            # Check if filename (without extension) matches the title
            logo_name = (
                os.path.splitext(logo_file)[0]
                .lower()
                .replace(" ", "")
                .replace("-", "")
                .replace("_", "")
            )

            # Direct match with title
            if logo_name in normalized_title or normalized_title in logo_name:
                try:
                    c.saveState()
                    # Calculate the logo size and position
                    logo_width = width * 0.2  # 20% of page width
                    # Use correct aspect ratio for GM Sunshine logo (556:200 or 2.78:1)
                    logo_height = logo_width / 2.78  # Original aspect ratio is 556:200
                    logo_x = width - logo_width - 30
                    logo_y = height - logo_height - 30

                    # Draw logo
                    c.drawImage(
                        f"logos/{logo_file}",
                        logo_x,
                        logo_y,
                        width=logo_width,
                        height=logo_height,
                        mask="auto",
                    )
                    c.restoreState()
                    logo_found = True
                    break
                except Exception:
                    # Silently handle logo errors, not critical for PDF generation
                    pass

            # Check for technology variations
            for tech, variations in tech_variations.items():
                if (
                    any(var in normalized_title for var in variations)
                    and tech in logo_name
                ):
                    try:
                        c.saveState()
                        # Calculate the logo size and position
                        logo_width = width * 0.2  # 20% of page width
                        # Use correct aspect ratio for GM Sunshine logo (556:200 or 2.78:1)
                        logo_height = (
                            logo_width / 2.78
                        )  # Original aspect ratio is 556:200
                        logo_x = width - logo_width - 30
                        logo_y = height - logo_height - 30

                        # Draw logo
                        c.drawImage(
                            f"logos/{logo_file}",
                            logo_x,
                            logo_y,
                            width=logo_width,
                            height=logo_height,
                            mask="auto",
                        )
                        c.restoreState()
                        logo_found = True
                        break
                    except Exception:
                        # Silently handle logo errors, not critical for PDF generation
                        pass

                if logo_found:
                    break

        # If no technology-specific logo found, use the default gm-sunshine logo
        if not logo_found:
            try:
                gm_logo_path = "logos/gm-sunshine.webp"
                if os.path.exists(gm_logo_path):
                    c.saveState()
                    # Calculate the logo size and position
                    logo_width = width * 0.15  # 15% of page width
                    # Use correct aspect ratio for GM Sunshine logo (556:200 or 2.78:1)
                    logo_height = logo_width / 2.78  # Original aspect ratio is 556:200
                    logo_x = width - logo_width - 30
                    logo_y = height - logo_height - 30

                    # Draw logo
                    c.drawImage(
                        gm_logo_path,
                        logo_x,
                        logo_y,
                        width=logo_width,
                        height=logo_height,
                        mask="auto",
                    )
                    c.restoreState()
            except Exception:
                # Silently handle logo errors, not critical for PDF generation
                pass

        # Add QR code linking to gm-sunshine.com below the logo
        if qrcode_available:
            try:
                # Generate QR code for gm-sunshine.com
                qr = qrcode.QRCode(
                    version=1,
                    error_correction=qrcode.constants.ERROR_CORRECT_L,
                    box_size=10,
                    border=4,
                )
                qr.add_data("https://gm-sunshine.com")
                qr.make(fit=True)

                # Create QR code image
                qr_img = qr.make_image(fill_color="black", back_color="white")

                # Save to a temporary file
                with tempfile.NamedTemporaryFile(
                    suffix=".png", delete=False
                ) as temp_file:
                    temp_filename = temp_file.name
                    qr_img.save(temp_filename)

                # Calculate QR code position - below the logo
                qr_size = width * 0.08  # 8% of page width

                # Position QR code centered below the logo
                if logo_found:
                    qr_x = logo_x + (logo_width - qr_size) / 2
                else:
                    # Default position if no logo
                    qr_x = width - qr_size - 30

                qr_y = (
                    height - logo_height - 60 - qr_size
                )  # Below logo with some spacing

                # Draw white background frame for QR code (for better contrast on dark backgrounds)
                c.saveState()
                c.setFillColorRGB(1, 1, 1)  # White
                padding = 5
                c.roundRect(
                    qr_x - padding,
                    qr_y - padding,
                    qr_size + (padding * 2),
                    qr_size + (padding * 2),
                    radius=5,
                    fill=1,
                    stroke=0,
                )

                # Draw QR code from the temp file
                c.drawImage(temp_filename, qr_x, qr_y, width=qr_size, height=qr_size)

                # Add URL text below QR code
                c.setFont(fonts.get("content_font", "Helvetica"), 9)
                c.setFillColorRGB(*colors.get("background", (1, 1, 1)))
                url_text = "gm-sunshine.com"
                url_width = c.stringWidth(
                    url_text, fonts.get("content_font", "Helvetica"), 9
                )
                c.drawString(qr_x + (qr_size - url_width) / 2, qr_y - 12, url_text)
                c.restoreState()

                # Clean up the temporary file
                try:
                    os.unlink(temp_filename)
                except:
                    pass
            except Exception:
                # Silently handle QR code errors, not critical for PDF generation
                pass

        # Draw "Thank You!" heading
        c.setFillColorRGB(*colors.get("background", (1, 1, 1)))
        c.setFont(
            fonts.get("title_font", "Helvetica-Bold"), fonts.get("title_size", 24) * 1.5
        )
        c.drawCentredString(width / 2, height * 0.6, "Thank You!")

        # Add decorative line
        c.setStrokeColorRGB(*colors.get("background", (1, 1, 1)))
        c.setLineWidth(2)
        c.line(width / 4, height * 0.58, width * 3 / 4, height * 0.58)

        # Draw completion message
        c.setFillColorRGB(*colors.get("background", (1, 1, 1)))
        c.setFont(
            fonts.get("content_font", "Helvetica"), fonts.get("subtitle_size", 18)
        )

        # Handle multi-line completion message
        message = completion_message or "You've completed all the interview questions!"
        lines = []
        words = message.split()
        current_line = ""
        max_width = width * 0.7

        for word in words:
            test_line = current_line + " " + word if current_line else word
            if (
                c.stringWidth(
                    test_line,
                    fonts.get("content_font", "Helvetica"),
                    fonts.get("subtitle_size", 18),
                )
                < max_width
            ):
                current_line = test_line
            else:
                lines.append(current_line)
                current_line = word

        if current_line:
            lines.append(current_line)

        # Draw each line centered
        line_y = height * 0.5
        for line in lines:
            c.drawCentredString(width / 2, line_y, line)
            line_y -= 25

        # Add a motivational quote for next steps
        try:
            from .motivational_quotes import get_random_quote

            quote, author = get_random_quote()

            # Draw quote
            quote_y = height * 0.35
            c.setFont(
                fonts.get("content_font", "Helvetica"), fonts.get("content_size", 12)
            )
            c.setFillColorRGB(*colors.get("background", (1, 1, 1)))

            # Wrap quote text to fit
            max_quote_width = width * 0.6
            quote_lines = []
            current_line = ""
            for word in quote.split():
                test_line = current_line + " " + word if current_line else word
                if (
                    c.stringWidth(
                        test_line,
                        fonts.get("content_font", "Helvetica"),
                        fonts.get("content_size", 12),
                    )
                    < max_quote_width
                ):
                    current_line = test_line
                else:
                    quote_lines.append(current_line)
                    current_line = word
            if current_line:
                quote_lines.append(current_line)

            # Draw each line of the quote
            for i, line in enumerate(quote_lines):
                line_width = c.stringWidth(
                    line,
                    fonts.get("content_font", "Helvetica"),
                    fonts.get("content_size", 12),
                )
                c.drawString(width / 2 - line_width / 2, quote_y - i * 16, line)

            # Draw author
            author_y = quote_y - len(quote_lines) * 16 - 16
            c.setFont(
                fonts.get("content_font", "Helvetica"), fonts.get("content_size", 12)
            )
            author_text = f"— {author}"
            author_width = c.stringWidth(
                author_text,
                fonts.get("content_font", "Helvetica"),
                fonts.get("content_size", 12),
            )
            c.drawString(width / 2 - author_width / 2, author_y, author_text)
        except Exception:
            # Silently handle quote errors, not critical for PDF generation
            pass

        # Add copyright notice
        c.setFont(fonts.get("content_font", "Helvetica"), 10)
        c.drawCentredString(
            width / 2, height * 0.1, "© Interview Toolkit - For personal use only"
        )

        c.showPage()
    except Exception as e:
        raise e
