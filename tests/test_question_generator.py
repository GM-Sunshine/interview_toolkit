"""
Tests for the question generator module.
"""

import json
import os
from unittest.mock import MagicMock, patch

import pytest

from src.llm.question_generator import generate_questions, save_questions

# Skip OpenAI tests if no API key is available or on CI
skip_openai = pytest.mark.skipif(
    os.environ.get("OPENAI_API_KEY") is None or os.environ.get("CI") == "true",
    reason="OpenAI API key not available or running in CI environment",
)


@skip_openai
def test_generate_questions():
    """Test question generation with mock API response."""
    mock_response = {
        "choices": [
            {
                "message": {
                    "content": """
                    [
                        {
                            "question": "What is Python?",
                            "answer": "Python is a high-level programming language.",
                            "difficulty": "beginner"
                        }
                    ]
                    """
                }
            }
        ]
    }

    with patch("openai.ChatCompletion.create", return_value=mock_response):
        questions = generate_questions("Python", 1)
        assert len(questions) == 1
        assert isinstance(questions[0], dict)
        assert "question" in questions[0]
        assert "answer" in questions[0]
        assert isinstance(questions[0]["question"], str)
        assert isinstance(questions[0]["answer"], str)
        assert len(questions[0]["question"]) > 0
        assert len(questions[0]["answer"]) > 0


def test_save_questions(tmp_path):
    """Test saving questions to a file."""
    questions = [
        {
            "question": "What is Python?",
            "answer": "Python is a high-level programming language.",
            "difficulty": "beginner",
        }
    ]

    output_file = tmp_path / "test_questions.json"
    save_questions(questions, str(output_file))

    assert output_file.exists()
    with open(output_file, "r") as f:
        saved_questions = json.load(f)
        assert saved_questions == questions


def test_generate_questions_invalid_topic():
    """Test question generation with invalid topic."""
    with pytest.raises(ValueError):
        generate_questions("", 1)


def test_generate_questions_invalid_count():
    """Test question generation with invalid count."""
    with pytest.raises(ValueError):
        generate_questions("Python", 0)
