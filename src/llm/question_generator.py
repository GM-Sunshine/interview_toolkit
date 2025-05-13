import argparse
import json
import os
import sys
from pathlib import Path
from typing import Dict, List, Optional, Union, Any

from src.llm.provider import LLMProvider, get_llm_provider
from src.utils.config import (DEFAULT_BATCH_SIZE, DEFAULT_JSON_DIR,
                              DEFAULT_OUTPUT_DIR, DEFAULT_QUESTION_COUNT)


def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Generate questions and answers for a technology stack or programming language."
    )
    parser.add_argument(
        "topic",
        type=str,
        help='Technology stack or programming language (e.g., "python", "react", "docker")',
    )
    parser.add_argument(
        "--count",
        type=int,
        default=DEFAULT_QUESTION_COUNT,
        help=f"Number of questions to generate (default: {DEFAULT_QUESTION_COUNT})",
    )
    parser.add_argument(
        "--output",
        type=str,
        help=f"Output JSON file path (default: {DEFAULT_JSON_DIR}/{{topic}}_questions.json)",
    )
    parser.add_argument(
        "--batch-size",
        type=int,
        default=DEFAULT_BATCH_SIZE,
        help=f"Number of questions to generate per API call (default: {DEFAULT_BATCH_SIZE})",
    )

    args = parser.parse_args()

    # Set default output path if not provided
    if not args.output:
        args.output = (
            f"{DEFAULT_JSON_DIR}/{args.topic.lower().replace(' ', '_')}_questions.json"
        )

    return args


def generate_questions(topic: str, num_questions: int, debug: bool = False) -> List[Dict[str, str]]:
    """Generate interview questions for a given topic."""
    # Validate inputs
    if not topic or not isinstance(topic, str) or not topic.strip():
        raise ValueError("Topic must be a non-empty string")

    if not isinstance(num_questions, int) or num_questions <= 0:
        raise ValueError("Number of questions must be a positive integer")

    provider = get_llm_provider()

    # Generate questions in batches
    questions = []
    batch_size = DEFAULT_BATCH_SIZE  # Use configured batch size
    remaining = num_questions
    max_retries = 3

    while remaining > 0:
        current_batch = min(batch_size, remaining)
        retry_count = 0

        while retry_count < max_retries:
            try:
                batch_questions = generate_questions_batch(provider, topic, current_batch, questions, debug=debug)
                if batch_questions:
                    questions.extend(batch_questions)
                    remaining -= len(batch_questions)
                    break
                retry_count += 1
                if debug:
                    print(f"Failed to generate a batch of questions. Retry {retry_count}/{max_retries}")
            except Exception as e:
                retry_count += 1
                if debug:
                    print(f"Error generating questions: {str(e)}")
                    print(f"Retry {retry_count}/{max_retries}")

        if retry_count >= max_retries:
            if not questions:  # If we have no questions at all
                raise ValueError(f"Failed to generate questions after {max_retries} attempts")
            break  # If we have some questions, return what we have

    return questions


def generate_questions_batch(provider: LLMProvider, topic: str, num_questions: int, 
                            existing_questions: Optional[List[Dict[str, str]]] = None, 
                            debug: bool = False) -> List[Dict[str, str]]:
    """Generate a batch of interview questions.
    
    Args:
        provider: The LLM provider to use for generation
        topic: The topic to generate questions for
        num_questions: The number of questions to generate
        existing_questions: Optional list of existing questions to avoid duplicates
        debug: Whether to print debug information
        
    Returns:
        A list of generated questions with answers
        
    Raises:
        ValueError: If the response cannot be parsed or is invalid
    """
    if debug:
        print(f"Generating batch of {num_questions} questions about {topic}...")
    
    system_prompt = """You are an expert interviewer. Generate interview questions and answers in JSON format.
Each question should be a dictionary with 'question' and 'answer' fields.
The answer should be detailed and comprehensive.
Return ONLY the JSON array, no other text or notes.
Make sure the response is valid JSON with no trailing commas."""

    # Add existing questions to avoid duplicates
    if existing_questions:
        existing_text = "\n".join([f"- {q['question']}" for q in existing_questions])
        system_prompt += f"\n\nHere are the existing questions that you should NOT repeat:\n{existing_text}"
    
    user_prompt = f"Generate {num_questions} new interview questions about {topic}. Return them as a JSON array of objects with 'question' and 'answer' fields. Make sure to provide detailed answers."
    
    try:
        response = provider.generate_completion(system_prompt, user_prompt, debug=debug)
        
        # Clean the response to ensure it's valid JSON
        # Find the first '[' and last ']'
        start = response.find('[')
        end = response.rfind(']') + 1
        if start == -1 or end == 0:
            raise ValueError("No JSON array found in response")
        
        json_str = response[start:end]
        questions = json.loads(json_str)
        
        if not isinstance(questions, list):
            raise ValueError("Response is not a list of questions")
        
        # Validate each question has required fields
        for q in questions:
            if not isinstance(q, dict):
                raise ValueError("Question is not a dictionary")
            if 'question' not in q or 'answer' not in q:
                raise ValueError("Question missing required fields (question and answer)")
            if not isinstance(q['question'], str) or not isinstance(q['answer'], str):
                raise ValueError("Question and answer fields must be strings")
        
        if debug:
            print(f"Successfully generated {len(questions)} questions")
        
        return questions
    except json.JSONDecodeError as e:
        if debug:
            print(f"JSON Parse Error: {str(e)}")
            print(f"Raw response:\n{response}")
        raise ValueError(f"Failed to parse questions: {str(e)}")
    except Exception as e:
        raise ValueError(f"Failed to generate questions: {str(e)}")


def save_questions(questions: List[Dict[str, str]], output_path: str) -> str:
    """Save questions to a JSON file.
    
    Args:
        questions: The list of questions to save
        output_path: The path to save the questions to
        
    Returns:
        The path to the saved file
        
    Raises:
        ValueError: If the questions cannot be saved
    """
    try:
        # Create parent directories if they don't exist
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        # Save the questions
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(questions, f, indent=2, ensure_ascii=False)
        
        print(f"Successfully saved {len(questions)} questions to {output_path}")
        return output_path
    except Exception as e:
        error_msg = f"Error saving questions: {str(e)}"
        print(error_msg)
        raise ValueError(error_msg)


def main():
    args = parse_arguments()

    try:
        # Generate questions
        questions = generate_questions(args.topic, args.count)

        if questions:
            # Create output filename if not provided
            if not args.output:
                args.output = f"{args.topic.lower().replace(' ', '_')}_questions.json"

            # Save questions to file
            output_path = save_questions(questions, args.output)
            print(
                f"You can now use this file with createPDFFromJson.py to generate a PDF."
            )
        else:
            print("Failed to generate questions. Please try again.")
    except Exception as e:
        print(f"Error: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
