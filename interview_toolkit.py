#!/usr/bin/env python3
"""
Interview Toolkit - A comprehensive tool for generating and managing interview questions

This script provides a central entry point for:
1. Generating new interview questions using AI
2. Creating beautiful PDF presentations from existing question sets
"""

import argparse
import json
import os
import platform
import re
import subprocess
import sys
import time
import random
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

# Make sure we can find our packages
sys.path.append(os.path.dirname(__file__))
sys.path.append(
    os.path.join(os.path.dirname(__file__), "venv/lib/python3.12/site-packages")
)
sys.path.append(os.path.join(os.path.dirname(__file__), "src"))

from rich import print as rprint
from rich.console import Console
from rich.panel import Panel
from rich.progress import (BarColumn, Progress, SpinnerColumn, TextColumn,
                           TimeElapsedColumn)

# Import our modules
try:
    from src.llm.question_generator import generate_questions, save_questions
    from src.pdf.color_schemes import COLOR_SCHEMES
    from src.pdf.pdf_creator import (create_pdf, get_default_title,
                                     get_output_filename)
    from src.pdf.question_loader import QuestionLoader
    from src.utils.config import validate_config, get_config
    from src.llm.provider import (
        LLMProviderException, ConfigurationError, ConnectionError, 
        APIError, ParseError
    )
except ImportError as e:
    print(f"Error importing required modules: {e}")
    print("Please ensure all required files are in the correct locations.")
    sys.exit(1)

# Initialize Rich console
console = Console()


def validate_environment() -> bool:
    """
    Validate that the environment is properly configured.
    
    Returns:
        True if the environment is valid, False otherwise
    """
    # Check configuration
    errors = validate_config()
    if errors:
        console.print("[bold red]Configuration Error:[/bold red]")
        for key, error in errors.items():
            console.print(f"  - {key}: {error}")
        
        console.print("\n[yellow]Please check your .env file and fix these issues.[/yellow]")
        return False
    
    # Check for required directories
    required_dirs = ["json", "pdf", "fonts"]
    for directory in required_dirs:
        if not os.path.exists(directory):
            try:
                os.makedirs(directory)
                console.print(f"[yellow]Created missing directory: {directory}[/yellow]")
            except Exception as e:
                console.print(f"[bold red]Error creating directory {directory}: {str(e)}[/bold red]")
                return False
    
    return True


def display_welcome_banner() -> None:
    """Display a welcome banner for the application"""
    console.print(
        Panel.fit(
            "[bold blue]Interview Toolkit[/bold blue]\n"
            "[italic]Generate questions and create beautiful PDFs for interview preparation[/italic]",
            border_style="blue",
            padding=(1, 10),
        )
    )
    console.print()


def display_menu() -> str:
    """
    Display the main menu and get user choice.
    
    Returns:
        The selected menu option
    """
    console.print("\nPlease choose an option:")
    console.print("1. Generate new interview questions")
    console.print("2. Create a PDF from existing questions")
    console.print("3. List existing question sets")
    console.print("4. Exit")

    while True:
        try:
            choice = input("\nEnter your choice (1-4): ")
            if choice in ["1", "2", "3", "4"]:
                return {
                    "1": "Generate new interview questions",
                    "2": "Create a PDF from existing questions",
                    "3": "List existing question sets",
                    "4": "Exit",
                }[choice]
            else:
                console.print(
                    "[red]Invalid choice. Please enter a number between 1 and 4.[/red]"
                )
        except (KeyboardInterrupt, EOFError):
            return "Exit"


def validate_topic(topic: str) -> Tuple[bool, str]:
    """
    Validate that a topic is safe to use as a filename and not empty.
    
    Args:
        topic: The topic to validate
        
    Returns:
        A tuple of (is_valid, error_message)
    """
    if not topic:
        return False, "Topic cannot be empty."
    
    # Check for potentially dangerous characters
    if re.search(r'[\\/:*?"<>|]', topic):
        return False, "Topic contains invalid characters. Please avoid using: \\ / : * ? \" < > |"
    
    # Prevent path traversal
    if ".." in topic or topic.startswith("/") or topic.startswith("~"):
        return False, "Topic contains unsafe path components."
    
    return True, ""


def validate_filename(filename: str) -> Tuple[bool, str]:
    """
    Validate that a filename is safe to use.
    
    Args:
        filename: The filename to validate
        
    Returns:
        A tuple of (is_valid, error_message)
    """
    if not filename:
        return False, "Filename cannot be empty."
    
    # Normalize path to prevent directory traversal
    norm_path = os.path.normpath(filename)
    
    # Check if the normalized path tries to access parent directories
    if ".." in norm_path or norm_path.startswith("/") or norm_path.startswith("~"):
        return False, "Filename contains unsafe path components."
    
    # Check for potentially dangerous characters
    if re.search(r'[\\:*?"<>|]', os.path.basename(norm_path)):
        return False, "Filename contains invalid characters. Please avoid using: \\ : * ? \" < > |"
    
    return True, ""


def sanitize_filename(filename: str) -> str:
    """
    Sanitize a filename to make it safe for file operations.
    
    Args:
        filename: The filename to sanitize
        
    Returns:
        A sanitized filename
    """
    # Replace potentially dangerous characters with underscores
    safe_filename = re.sub(r'[\\/:*?"<>|]', '_', filename)
    
    # Ensure the filename doesn't start with a path separator or tilde
    if safe_filename.startswith("/") or safe_filename.startswith("~"):
        safe_filename = safe_filename.lstrip("/~")
    
    # Prevent path traversal
    safe_filename = safe_filename.replace("..", "")
    
    return safe_filename


def safe_join_path(directory: str, filename: str) -> str:
    """
    Safely join a directory and filename to prevent path traversal.
    
    Args:
        directory: The directory to join
        filename: The filename to join
        
    Returns:
        A safe path
    """
    # Sanitize the filename first
    safe_name = sanitize_filename(filename)
    
    # Use os.path.join and then normalize to remove any path traversal attempts
    path = os.path.normpath(os.path.join(directory, safe_name))
    
    # Ensure the result is still within the intended directory
    if not path.startswith(os.path.abspath(directory)):
        # If it's not, just use the filename in the directory
        path = os.path.join(directory, os.path.basename(safe_name))
    
    return path


def generate_new_questions(debug: bool = False) -> None:
    """
    Generate new interview questions using AI.
    
    Args:
        debug: Whether to print debug information
    """
    try:
        # Get topic from user
        console.print(
            "\n[bold]What topic would you like to generate questions for?[/bold]"
        )
        topic = input("Enter topic: ").strip()

        # Validate topic
        is_valid, error_message = validate_topic(topic)
        if not is_valid:
            console.print(f"[red]{error_message}[/red]")
            return

        # Get number of questions
        while True:
            try:
                num_questions_input = input(
                        "\nHow many questions would you like to generate? (minimum 1): "
                ).strip()
                
                # Check if the input is a valid number
                if not num_questions_input.isdigit():
                    console.print("[red]Please enter a valid number.[/red]")
                    continue
                    
                num_questions = int(num_questions_input)
                if num_questions < 1:
                    console.print("[red]Please enter a number greater than 0.[/red]")
                    continue
                    
                # Warn about large numbers but don't restrict
                if num_questions > 100:
                    console.print(
                        f"[yellow]Warning: Requesting a large number of questions ({num_questions}).[/yellow]"
                    )
                    confirm = input(f"Do you want to continue? This may take a while and use significant API quota. (y/n): ").lower()
                    if confirm != 'y':
                        console.print("[yellow]Operation cancelled.[/yellow]")
                        return
                
                break
            except ValueError:
                console.print("[red]Please enter a valid number.[/red]")

        # Create variables for progress tracking outside the progress context
        questions = []
        successful = False
        output_path = ""
        error_message = ""

        # Show progress
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TimeElapsedColumn(),
            console=console,
        ) as progress:
            task = progress.add_task(
                "[cyan]Generating questions...", total=num_questions
            )

            try:
                # Generate questions
                questions = generate_questions(topic, num_questions, debug=debug)

                # Create sanitized output filename
                safe_topic = sanitize_filename(topic.lower().replace(' ', '_'))
                output_filename = f"{safe_topic}_questions.json"
                
                # Make sure the output path is within the json directory
                output_path = safe_join_path("json", output_filename)

                # Save questions
                save_questions(questions, output_path)

                # Update progress
                progress.update(task, completed=num_questions)
                successful = True

            except ConfigurationError as e:
                error_message = f"Configuration Error: {str(e)}\n\nPlease check your API configuration in the .env file and try again."
            except ConnectionError as e:
                error_message = f"Connection Error: {str(e)}\n\nPlease check your network connection and the API service status."
            except APIError as e:
                error_message = f"API Error: {str(e)}\n\nThere was an error when calling the API. Please try again later."
            except ParseError as e:
                error_message = f"Parse Error: {str(e)}\n\nFailed to parse the API response. Try again or adjust your query."
            except LLMProviderException as e:
                error_message = f"LLM Provider Error: {str(e)}"
            except ValueError as e:
                error_message = f"Error: {str(e)}"
            except Exception as e:
                error_message = f"Unexpected error: {str(e)}"
                if debug:
                    import traceback
                    error_message += f"\n\n{traceback.format_exc()}"

        # Now, outside the progress context, display results or errors
        if successful:
            console.print(
                f"\n[green]Successfully generated {num_questions} questions about {topic}![/green]"
            )
            console.print(f"Questions saved to: [blue]{output_path}[/blue]")

            # Ask if user wants to create a PDF
            create_pdf_choice = input(
                "\nWould you like to create a PDF from these questions? (y/n): "
            ).lower()
            if create_pdf_choice == "y":
                create_pdf_from_questions(output_path, debug=debug)
        else:
            console.print(f"\n[red]{error_message}[/red]")

    except KeyboardInterrupt:
        console.print("\n[yellow]Operation cancelled by user.[/yellow]")


def create_pdf_from_questions(filename: Optional[str] = None, debug: bool = False) -> None:
    """
    Create a PDF from existing questions.
    
    Args:
        filename: Optional filename of the question file to use
        debug: Whether to print debug information
    """
    try:
        # If no filename provided, ask user to select one
        if not filename:
            # List available question sets
            question_sets = list_existing_questions()
            if not question_sets:
                return

            # Get user choice
            while True:
                try:
                    choice_input = input(
                            "\nEnter the number of the question set to use (0 to cancel): "
                    ).strip()
                    
                    # Validate input is a number
                    if not choice_input.isdigit():
                        console.print("[red]Please enter a valid number.[/red]")
                        continue
                        
                    choice = int(choice_input)
                    if choice == 0:
                        return
                    if 1 <= choice <= len(question_sets):
                        filename = question_sets[choice - 1]
                        break
                    console.print(f"[red]Invalid choice. Please enter a number between 0 and {len(question_sets)}.[/red]")
                except ValueError:
                    console.print("[red]Please enter a valid number.[/red]")

        # Validate filename
        is_valid, error_message = validate_filename(filename)
        if not is_valid:
            console.print(f"[red]{error_message}[/red]")
            return

        # Make sure to look in the json directory if the path doesn't include it
        if not os.path.exists(filename) and not filename.startswith('json/'):
            json_path = safe_join_path('json', filename)
            if os.path.exists(json_path):
                filename = json_path

        # Check if file exists
        if not os.path.exists(filename):
            console.print(f"[red]File not found: {filename}[/red]")
            return

        # Load questions
        loader = QuestionLoader()
        questions = loader.load_questions(filename)

        if not questions:
            console.print("[red]No questions found in the selected file.[/red]")
            return

        # Get title
        default_title = get_default_title(filename)
        console.print(f"\nEnter a title for the PDF (press Enter to use '{default_title}'):")
        custom_title = input().strip()
        
        # Sanitize the title
        title = sanitize_filename(custom_title) if custom_title else default_title

        # Get color scheme
        console.print("\nAvailable color schemes:")
        for i, scheme in enumerate(COLOR_SCHEMES.keys(), 1):
            console.print(f"{i}. {scheme.title()}")

        selected_color_scheme = "blue"  # Default
        while True:
            try:
                choice_input = input(
                    f"\nSelect a color scheme (1-{len(COLOR_SCHEMES)}): "
                ).strip()
                
                # Validate input is a number
                if not choice_input.isdigit():
                    console.print("[red]Please enter a valid number.[/red]")
                    continue
                    
                choice = int(choice_input)
                if 1 <= choice <= len(COLOR_SCHEMES):
                    selected_color_scheme = list(COLOR_SCHEMES.keys())[choice - 1]
                    break
                console.print(f"[red]Invalid choice. Please enter a number between 1 and {len(COLOR_SCHEMES)}.[/red]")
            except ValueError:
                console.print("[red]Please enter a valid number.[/red]")

        # Create a new progress context for PDF creation
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TimeElapsedColumn(),
            console=console,
        ) as progress:
            task = progress.add_task("[cyan]Creating PDF...", total=100)

            # Create PDF in a safe location
            pdf_dir = os.path.abspath("pdf")
            os.makedirs(pdf_dir, exist_ok=True)
            
            # Generate output filename
            from datetime import datetime
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = f"pdf/{title.lower().replace(' ', '_')}_{timestamp}.pdf"

            # Create PDF
            try:
                pdf_path = create_pdf(
                    questions, 
                    output_file, 
                    title,
                    color_scheme=selected_color_scheme
                )
                progress.update(task, completed=100)

                console.print(f"[green]PDF created successfully: {pdf_path}[/green]")
                
                # Automatically open the PDF if possible
                if platform.system() == "Darwin":  # macOS
                    try:
                        subprocess.run(["open", pdf_path], check=True)
                    except subprocess.SubprocessError:
                        console.print("[yellow]Could not automatically open the PDF.[/yellow]")
                elif platform.system() == "Windows":
                    try:
                        os.startfile(pdf_path)
                    except Exception:
                        console.print("[yellow]Could not automatically open the PDF.[/yellow]")
                elif platform.system() == "Linux":
                    try:
                        subprocess.run(["xdg-open", pdf_path], check=True)
                    except subprocess.SubprocessError:
                        console.print("[yellow]Could not automatically open the PDF.[/yellow]")
            except Exception as e:
                console.print(f"[red]Error creating PDF: {str(e)}[/red]")
                if debug:
                    import traceback
                    console.print(traceback.format_exc())

    except Exception as e:
        console.print(f"[red]Error creating PDF: {str(e)}[/red]")
        if debug:
            import traceback
            console.print(traceback.format_exc())


def list_existing_questions() -> List[str]:
    """
    List existing question sets and return them.
    
    Returns:
        A list of filenames for existing question sets
    """
    question_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "json"))
    if not os.path.exists(question_dir):
        console.print("[yellow]Question directory not found. Creating it now...[/yellow]")
        try:
            os.makedirs(question_dir)
            console.print("[green]Created directory: json/[/green]")
        except Exception as e:
            console.print(f"[red]Error creating directory: {str(e)}[/red]")
        return []

    question_files = [f for f in os.listdir(question_dir) if f.endswith(".json")]
    
    if not question_files:
        console.print("[yellow]No question sets found. Generate some questions first.[/yellow]")
        return []
    
    console.print("\n[bold]Available question sets:[/bold]")
    for i, filename in enumerate(question_files, 1):
        # Get number of questions in the file
        try:
            file_path = os.path.join(question_dir, filename)
            with open(file_path, "r", encoding="utf-8") as f:
                try:
                    questions = json.load(f)
                    count = len(questions)
                    # Get a readable name from the filename
                    name = " ".join(filename.replace("_questions.json", "").split("_")).title()
                    console.print(f"{i}. {name} ({count} questions)")
                except json.JSONDecodeError:
                    console.print(f"{i}. {filename} (Invalid JSON format)")
        except Exception as e:
            console.print(f"{i}. {filename} (Error: {str(e)})")
    
    return [os.path.join("json", f) for f in question_files]


def parse_arguments() -> argparse.Namespace:
    """
    Parse command line arguments.
    
    Returns:
        The parsed arguments
    """
    parser = argparse.ArgumentParser(
        description="Interview Toolkit - Generate questions and create PDFs"
    )
    parser.add_argument(
        "--generate", action="store_true", help="Generate new interview questions"
    )
    parser.add_argument(
        "--pdf", action="store_true", help="Create a PDF from existing questions"
    )
    parser.add_argument(
        "--list", action="store_true", help="List available question sets"
    )
    parser.add_argument(
        "--debug", action="store_true", help="Enable debug output"
    )
    parser.add_argument(
        "--version", action="store_true", help="Show version information"
    )
    parser.add_argument(
        "--test-pdf", action="store_true", help="Generate a test PDF with sample questions"
    )
    
    return parser.parse_args()


def main() -> None:
    """Main entry point for the application."""
    # Display welcome banner
    display_welcome_banner()
    
    # Parse command line arguments
    args = parse_arguments()
    
    # Show version if requested
    if args.version:
        from src.utils.version import get_version
        version = get_version()
        console.print(f"[green]Interview Toolkit version: {version}[/green]")
        return
    
    # Generate test PDF if requested
    if args.test_pdf:
        generate_test_pdf(debug=args.debug)
        return
    
    # Validate environment
    if not validate_environment():
        console.print("\n[red]Failed to validate environment. Exiting...[/red]")
        sys.exit(1)
    
    # If no arguments provided, run in interactive mode
    if not (args.generate or args.pdf or args.list):
        interactive_mode(args.debug)
        return
    
    # Handle command line mode
    if args.list:
        list_existing_questions()
        
    if args.generate:
        generate_new_questions(debug=args.debug)
        
    if args.pdf:
        create_pdf_from_questions()


def interactive_mode(debug: bool = False) -> None:
    """
    Run the application in interactive mode.
    
    Args:
        debug: Whether to enable debug output
    """
    while True:
        choice = display_menu()
        
        if choice == "Generate new interview questions":
            generate_new_questions(debug=debug)
        elif choice == "Create a PDF from existing questions":
            create_pdf_from_questions()
        elif choice == "List existing question sets":
            list_existing_questions()
        elif choice == "Exit":
            console.print("[green]Thank you for using Interview Toolkit. Goodbye![/green]")
            break
        
        # Add a small delay before showing the menu again
        time.sleep(0.5)


def generate_test_pdf(debug: bool = False) -> None:
    """
    Generate a test PDF with sample questions.
    
    Args:
        debug: Whether to print debug information
    """
    console.print("[cyan]Generating test PDF with sample questions...[/cyan]")
    
    # Sample questions with properly formatted code blocks
    sample_questions = [
        {
            "question": "What is Python's Global Interpreter Lock (GIL) and how does it affect multithreaded programs?",
            "answer": "The Global Interpreter Lock (GIL) is a mutex that protects access to Python objects, preventing multiple threads from executing Python bytecode at once. This means that even though you can create multiple threads in Python, only one thread can execute Python code at any given time, which effectively prevents true CPU-bound parallelism in multithreaded Python code. The GIL exists because Python's memory management is not thread-safe. It affects multithreaded programs by limiting CPU-bound tasks to run sequentially, not in parallel, even on multi-core systems. However, I/O-bound threads still benefit from multithreading because they release the GIL during I/O operations. For CPU-bound parallel tasks, developers often use multiprocessing instead of threading to work around the GIL's limitations."
        },
        {
            "question": "Explain the difference between lists and tuples in Python.",
            "answer": "Lists and tuples are both sequence data types in Python, but they have several key differences:\n\n1. Mutability: Lists are mutable, meaning their elements can be changed after creation (adding, removing, or modifying elements). Tuples are immutable, so once created, their elements cannot be changed.\n\n2. Syntax: Lists are defined using square brackets `[]`, while tuples use parentheses `()`.\n\n3. Methods: Lists have more built-in methods like append(), remove(), extend(), etc., because they're designed to be modified. Tuples have fewer methods since they can't be changed after creation.\n\n4. Performance: Tuples are slightly more memory-efficient and perform better than lists for larger sequences, partly because of their immutability.\n\n5. Usage: Lists are typically used when you have a collection of similar items that might need to grow or change. Tuples are used when the data should remain constant, like coordinates, database records, or as dictionary keys (which lists cannot be used for).\n\n6. Packing and unpacking: Tuple packing and unpacking is more common than with lists, making tuples useful for returning multiple values from functions."
        },
        {
            "question": "What is a decorator in Python and how do you create one?",
            "answer": "A decorator in Python is a design pattern that allows you to modify the functionality of a function or class without directly changing its source code. Decorators are functions that take another function as an argument, add some functionality, and return the modified function.\n\nTo create a decorator:\n\n1. Define a wrapper function inside the decorator function\n2. The wrapper function will contain the modified behavior\n3. Return the wrapper function\n\nExample of a basic decorator:\n\n```python\ndef my_decorator(func):\n    def wrapper(*args, **kwargs):\n        print(\"Something is happening before the function is called.\")\n        result = func(*args, **kwargs)\n        print(\"Something is happening after the function is called.\")\n        return result\n    return wrapper\n\n@my_decorator\ndef say_hello():\n    print(\"Hello!\")\n\n# When you call say_hello(), it's actually calling wrapper()\nsay_hello()\n```\n\nPython also has the `@functools.wraps` decorator which should be used in your custom decorators to preserve the metadata of the original function, such as its name and docstring.\n\n```python\nfrom functools import wraps\n\ndef my_decorator(func):\n    @wraps(func)\n    def wrapper(*args, **kwargs):\n        # Decorator logic\n        return func(*args, **kwargs)\n    return wrapper\n```\n\nDecorators can also accept arguments, which requires an additional level of nesting."
        }
    ]
    
    # Save sample questions to a temporary file
    temp_file = "json/python_test_questions.json"
    os.makedirs("json", exist_ok=True)
    with open(temp_file, "w") as f:
        json.dump(sample_questions, f, indent=2)
    
    # Create PDF with progress indicator
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TimeElapsedColumn(),
        console=console,
    ) as progress:
        task = progress.add_task("[cyan]Creating test PDF...", total=100)
        
        # Create output directory
        os.makedirs("pdf", exist_ok=True)
        
        # Create output filename
        from datetime import datetime
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = f"pdf/python_test_{timestamp}.pdf"
        
        # Get a random color scheme for testing
        color_schemes = list(COLOR_SCHEMES.keys())
        test_color_scheme = random.choice(color_schemes)
        
        # Create PDF
        try:
            pdf_path = create_pdf(
                sample_questions, 
                output_file, 
                "Python Test",
                color_scheme=test_color_scheme
            )
            
            progress.update(task, completed=100)
            
            console.print(f"[green]Test PDF created successfully: {pdf_path}[/green]")
            console.print(f"[green]Used color scheme: {test_color_scheme}[/green]")
        except Exception as e:
            console.print(f"[red]Error creating test PDF: {str(e)}[/red]")
            if debug:
                import traceback
                console.print("[yellow]Debug traceback:[/yellow]")
                console.print(traceback.format_exc())


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        console.print("\n[yellow]Program interrupted by user. Exiting...[/yellow]")
        sys.exit(0)
    except Exception as e:
        console.print(f"\n[bold red]Unhandled error: {str(e)}[/bold red]")
        console.print("[yellow]Please report this issue on GitHub.[/yellow]")
        sys.exit(1)
