"""
Tests for the QuestionLoader class
"""

import json
import os
from unittest.mock import mock_open, patch

import pytest

from src.pdf.question_loader import QuestionLoader

# Sample valid questions
VALID_QUESTIONS = [
    {
        "question": "What is Python?",
        "answer": "Python is a high-level programming language.",
    },
    {
        "question": "What are decorators in Python?",
        "answer": "Decorators are a design pattern in Python that allow a user to add new functionality to an existing object without modifying its structure.",
    },
]

# Sample invalid questions
INVALID_QUESTIONS_NOT_LIST = {"questions": VALID_QUESTIONS}
INVALID_QUESTIONS_NOT_DICT = ["Question 1", "Question 2"]
INVALID_QUESTIONS_MISSING_FIELDS = [{"question": "What is Python?"}]
INVALID_QUESTIONS_WRONG_TYPES = [{"question": 123, "answer": "Python is a language."}]


def test_load_questions_valid(tmp_path):
    """Test loading valid questions"""
    # Create a temporary file with valid questions
    file_path = tmp_path / "valid_questions.json"
    with open(file_path, "w") as f:
        json.dump(VALID_QUESTIONS, f)

    # Load the questions
    loader = QuestionLoader()
    questions = loader.load_questions(str(file_path))

    # Check the results
    assert questions is not None
    assert len(questions) == 2
    assert questions[0]["question"] == "What is Python?"
    assert (
        questions[1]["answer"]
        == "Decorators are a design pattern in Python that allow a user to add new functionality to an existing object without modifying its structure."
    )


def test_load_questions_file_not_found():
    """Test loading questions from a non-existent file"""
    with patch("os.path.exists", return_value=False):
        loader = QuestionLoader()
        questions = loader.load_questions("non_existent_file.json")
        assert questions is None


def test_load_questions_invalid_json():
    """Test loading questions from a file with invalid JSON"""
    with patch("os.path.exists", return_value=True), patch(
        "builtins.open", mock_open(read_data='{"invalid json')
    ):
        loader = QuestionLoader()
        questions = loader.load_questions("invalid_json.json")
        assert questions is None


def test_load_questions_not_list():
    """Test loading questions that are not in a list format"""
    with patch("os.path.exists", return_value=True), patch(
        "builtins.open", mock_open(read_data=json.dumps(INVALID_QUESTIONS_NOT_LIST))
    ):
        loader = QuestionLoader()
        questions = loader.load_questions("not_list.json")
        assert questions is None


def test_load_questions_not_dict():
    """Test loading questions that are not dictionaries"""
    with patch("os.path.exists", return_value=True), patch(
        "builtins.open", mock_open(read_data=json.dumps(INVALID_QUESTIONS_NOT_DICT))
    ):
        loader = QuestionLoader()
        questions = loader.load_questions("not_dict.json")
        assert questions is None


def test_load_questions_missing_fields():
    """Test loading questions with missing required fields"""
    with patch("os.path.exists", return_value=True), patch(
        "builtins.open",
        mock_open(read_data=json.dumps(INVALID_QUESTIONS_MISSING_FIELDS)),
    ):
        loader = QuestionLoader()
        questions = loader.load_questions("missing_fields.json")
        assert questions is None


def test_load_questions_wrong_types():
    """Test loading questions with wrong field types"""
    with patch("os.path.exists", return_value=True), patch(
        "builtins.open", mock_open(read_data=json.dumps(INVALID_QUESTIONS_WRONG_TYPES))
    ):
        loader = QuestionLoader()
        questions = loader.load_questions("wrong_types.json")
        assert questions is None


def test_load_questions_exception():
    """Test handling of general exceptions during loading"""
    with patch("os.path.exists", return_value=True), patch(
        "builtins.open", side_effect=Exception("Test exception")
    ):
        loader = QuestionLoader()
        questions = loader.load_questions("exception.json")
        assert questions is None
