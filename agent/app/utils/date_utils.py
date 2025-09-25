"""Date parsing and filtering utilities for task management."""

from datetime import datetime, timedelta
from typing import Optional, Dict, Any


def parse_date(date_str: str) -> datetime:
    """Parse date string to datetime object"""
    if not date_str:
        return datetime.now()
    
    # Handle relative dates
    date_str = date_str.lower().strip()
    now = datetime.now()
    
    if date_str in ["today", "now"]:
        return now
    elif date_str == "tomorrow":
        return now + timedelta(days=1)
    elif date_str == "yesterday":
        return now - timedelta(days=1)
    elif "next week" in date_str:
        return now + timedelta(weeks=1)
    elif "this week" in date_str:
        return now
    
    # Try to parse specific date formats
    try:
        for fmt in ["%Y-%m-%d", "%m/%d/%Y", "%d/%m/%Y", "%Y-%m-%d %H:%M", "%m/%d/%Y %H:%M"]:
            try:
                return datetime.strptime(date_str, fmt)
            except ValueError:
                continue
    except:
        pass
    
    return now


def build_date_filter(date_range: str) -> Optional[Dict[str, Any]]:
    """Build MongoDB date filter from date range string"""
    if not date_range:
        return None
    
    date_range = date_range.lower().strip()
    now = datetime.now()
    
    if date_range == "today":
        start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        end = start + timedelta(days=1)
        return {"$gte": start, "$lt": end}
    elif date_range == "tomorrow":
        start = (now + timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
        end = start + timedelta(days=1)
        return {"$gte": start, "$lt": end}
    elif date_range == "this week":
        # Get start of week (Monday)
        days_since_monday = now.weekday()
        start = (now - timedelta(days=days_since_monday)).replace(hour=0, minute=0, second=0, microsecond=0)
        end = start + timedelta(weeks=1)
        return {"$gte": start, "$lt": end}
    elif date_range == "next week":
        days_since_monday = now.weekday()
        start = (now - timedelta(days=days_since_monday) + timedelta(weeks=1)).replace(hour=0, minute=0, second=0, microsecond=0)
        end = start + timedelta(weeks=1)
        return {"$gte": start, "$lt": end}
    
    # Try to parse as specific date
    try:
        target_date = parse_date(date_range)
        start = target_date.replace(hour=0, minute=0, second=0, microsecond=0)
        end = start + timedelta(days=1)
        return {"$gte": start, "$lt": end}
    except:
        return None