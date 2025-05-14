"""
PDF Generator for Interview Questions
Creates beautiful PDF presentations from question sets
"""

import os

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import PageBreak, SimpleDocTemplate

from .color_schemes import COLOR_SCHEMES
from .motivational_quotes import get_random_quote
from .page_generators import (
    create_answer_page,
    create_question_page,
    create_quote_page,
    create_title_page,
)
from .progress_messages import get_progress_message
from .question_loader import QuestionLoader
from .text_renderer import TextRenderer


class PDFGenerator:
    def __init__(self, title, color_scheme="blue"):
        self.title = title
        self.color_scheme = COLOR_SCHEMES.get(color_scheme, COLOR_SCHEMES["blue"])
        self.styles = getSampleStyleSheet()
        self.text_renderer = TextRenderer(self.color_scheme)

        # Add custom styles
        self.styles.add(
            ParagraphStyle(
                name="Question",
                parent=self.styles["Heading1"],
                textColor=self.color_scheme["primary"],
                spaceAfter=30,
            )
        )

        self.styles.add(
            ParagraphStyle(
                name="Answer",
                parent=self.styles["Normal"],
                textColor=self.color_scheme["text"],
                spaceAfter=12,
            )
        )

    def generate_pdf(self, questions, output_path):
        """Generate a PDF from the given questions"""
        try:
            # Create the PDF document
            doc = SimpleDocTemplate(
                output_path,
                pagesize=letter,
                rightMargin=72,
                leftMargin=72,
                topMargin=72,
                bottomMargin=72,
            )

            # Build the document content
            story = []

            # Add title page
            story.extend(create_title_page(self.title, self.color_scheme))
            story.append(PageBreak())

            # Add a motivational quote
            quote = get_random_quote()
            story.extend(create_quote_page(quote, self.color_scheme))
            story.append(PageBreak())

            # Add questions and answers
            total_questions = len(questions)
            for i, q in enumerate(questions, 1):
                # Add question page
                story.extend(
                    create_question_page(
                        q["question"],
                        i,
                        total_questions,
                        self.color_scheme,
                        self.styles,
                    )
                )
                story.append(PageBreak())

                # Add answer page
                story.extend(
                    create_answer_page(
                        q["answer"],
                        i,
                        total_questions,
                        self.color_scheme,
                        self.styles,
                        self.text_renderer,
                    )
                )
                story.append(PageBreak())

                # Add progress message every 5 questions
                if i % 5 == 0:
                    story.extend(
                        create_quote_page(
                            get_progress_message(i, total_questions), self.color_scheme
                        )
                    )
                    story.append(PageBreak())

            # Build the PDF
            doc.build(story)

            return output_path, None

        except Exception as e:
            return None, str(e)
