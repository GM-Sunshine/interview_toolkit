"""
Progress messages for PDF generation.

This module provides motivational and progress messages for milestone pages in PDFs.
"""

import random
from typing import List, Tuple


# List of progress messages for different milestone percentages
PROGRESS_MESSAGES = {
    25: [
        "You're off to a great start!",
        "Keep up the good work!",
        "You're making excellent progress!",
        "25% complete - you're on your way!",
        "One quarter done - looking good!"
    ],
    50: [
        "Halfway there!",
        "You're doing great!",
        "50% complete - keep going!",
        "The halfway point - you've got this!",
        "Half the questions mastered!"
    ],
    75: [
        "Almost there!",
        "The finish line is in sight!",
        "75% complete - you're almost done!",
        "Just a few more questions to go!",
        "You're in the final stretch!"
    ]
}


def get_progress_message(current: int, total: int) -> str:
    """
    Get a progress message based on the current progress.
    
    Args:
        current: Current number of questions completed
        total: Total number of questions
        
    Returns:
        A motivational message for the current progress
    """
    # Calculate progress percentage
    percentage = int((current / total) * 100)
    
    # Round to nearest 25%
    milestone = 25 * round(percentage / 25)
    
    # Cap at 75% (since 100% would be the final page, not a milestone)
    if milestone > 75:
        milestone = 75
    elif milestone < 25:
        milestone = 25
    
    # Get messages for this milestone
    messages = PROGRESS_MESSAGES.get(milestone, [f"{milestone}% Complete"])
    
    # Return a random message from the list
    return random.choice(messages)
