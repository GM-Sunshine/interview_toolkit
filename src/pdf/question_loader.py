"""
Question loader for PDF generation
"""

import json
import os
from typing import Any, Dict, List, Optional


class QuestionLoader:
    @staticmethod
    def load_questions(file_path: str) -> Optional[List[Dict[str, Any]]]:
        """
        Load questions from a JSON file

        Args:
            file_path: Path to the JSON file containing questions

        Returns:
            List of question dictionaries or None if there was an error
        """
        try:
            # Try several possible file paths if the file doesn't exist at the given path
            if not os.path.exists(file_path):
                # Try with json/ prefix
                if not file_path.startswith("json/"):
                    json_path = os.path.join("json", file_path)
                    if os.path.exists(json_path):
                        file_path = json_path
                    else:
                        print(f"Error: File not found: {file_path}")
                        print(f"Also checked: {json_path}")
                        return None
                else:
                    print(f"Error: File not found: {file_path}")
                    return None

            with open(file_path, "r", encoding="utf-8") as f:
                questions = json.load(f)

            if not isinstance(questions, list):
                print("Error: Questions must be a list")
                return None

            # Validate each question
            for i, q in enumerate(questions):
                if not isinstance(q, dict):
                    print(f"Error: Question {i+1} must be a dictionary")
                    return None

                if "question" not in q or "answer" not in q:
                    print(
                        f"Error: Question {i+1} must have 'question' and 'answer' fields"
                    )
                    return None

                if not isinstance(q["question"], str) or not isinstance(
                    q["answer"], str
                ):
                    print(
                        f"Error: Question {i+1} must have string values for 'question' and 'answer'"
                    )
                    return None

            return questions

        except json.JSONDecodeError:
            print(f"Error: Invalid JSON in file: {file_path}")
            return None
        except Exception as e:
            print(f"Error loading questions: {str(e)}")
            return None
