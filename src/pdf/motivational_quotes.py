"""
Motivational quotes for interview preparation PDFs.

This module provides motivational quotes for use in interview preparation materials.
"""

import random
from typing import Dict, List, Optional, Tuple

# List of motivational quotes and their authors
QUOTES = [
    ("The only way to do great work is to love what you do.", "Steve Jobs"),
    ("Success is not final, failure is not fatal: It is the courage to continue that counts.", "Winston Churchill"),
    ("Believe you can and you're halfway there.", "Theodore Roosevelt"),
    ("Opportunities don't happen. You create them.", "Chris Grosser"),
    ("Don't watch the clock; do what it does. Keep going.", "Sam Levenson"),
    ("The future belongs to those who believe in the beauty of their dreams.", "Eleanor Roosevelt"),
    ("Your talent determines what you can do. Your motivation determines how much you're willing to do. Your attitude determines how well you do it.", "Lou Holtz"),
    ("The only limit to our realization of tomorrow is our doubts of today.", "Franklin D. Roosevelt"),
    ("Act as if what you do makes a difference. It does.", "William James"),
    ("Quality is not an act, it is a habit.", "Aristotle"),
    ("The best way to predict the future is to create it.", "Peter Drucker"),
    ("What you get by achieving your goals is not as important as what you become by achieving your goals.", "Zig Ziglar"),
    ("The harder you work for something, the greater you'll feel when you achieve it.", "Anonymous"),
    ("Dream big and dare to fail.", "Norman Vaughan"),
    ("It's not whether you get knocked down, it's whether you get up.", "Vince Lombardi"),
    ("The question isn't who is going to let me; it's who is going to stop me.", "Ayn Rand"),
    ("Strive not to be a success, but rather to be of value.", "Albert Einstein"),
    ("If you can dream it, you can do it.", "Walt Disney"),
    ("The secret to getting ahead is getting started.", "Mark Twain"),
    ("You don't have to be great to start, but you have to start to be great.", "Zig Ziglar"),
    ("The only person you are destined to become is the person you decide to be.", "Ralph Waldo Emerson"),
    ("The expert in anything was once a beginner.", "Helen Hayes"),
    ("Your time is limited, don't waste it living someone else's life.", "Steve Jobs"),
    ("The journey of a thousand miles begins with one step.", "Lao Tzu"),
    ("Whether you think you can or you think you can't, you're right.", "Henry Ford"),
    ("Preparation is the key to success.", "Alexander Graham Bell"),
    ("The best preparation for tomorrow is doing your best today.", "H. Jackson Brown, Jr."),
    ("Before anything else, preparation is the key to success.", "Alexander Graham Bell"),
    ("By failing to prepare, you are preparing to fail.", "Benjamin Franklin"),
    ("Success is where preparation and opportunity meet.", "Bobby Unser")
]


def get_random_quote() -> Tuple[str, str]:
    """
    Get a random motivational quote.
    
    Returns:
        A tuple of (quote, author)
    """
    return random.choice(QUOTES)


def get_quote_by_theme(theme: str) -> Optional[Tuple[str, str]]:
    """
    Get a quote related to a specific theme.
    
    Args:
        theme: The theme to match (e.g., "success", "preparation")
        
    Returns:
        A tuple of (quote, author) or None if no matching quote is found
    """
    # Convert theme to lowercase for case-insensitive matching
    theme_lower = theme.lower()
    
    # Find quotes that match the theme
    matching_quotes = [
        quote for quote in QUOTES
        if theme_lower in quote[0].lower()
    ]
    
    # Return a random matching quote, or None if no matches
    if matching_quotes:
        return random.choice(matching_quotes)
    
    return None
