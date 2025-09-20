"""
Utility Helper Functions for Social Media Campaign Generator
"""

import re
import json
from typing import List, Dict, Any, Optional, Union
from datetime import datetime, timedelta
import hashlib
import logging
from urllib.parse import urlparse

logger = logging.getLogger(__name__)

def extract_hashtags(text: str) -> List[str]:
    """Extract hashtags from text"""
    hashtag_pattern = r'#(\w+)'
    hashtags = re.findall(hashtag_pattern, text)
    return [f"#{tag}" for tag in hashtags]

def clean_hashtags(hashtags: List[str]) -> List[str]:
    """Clean and validate hashtags"""
    cleaned = []
    for tag in hashtags:
        # Remove # if present and clean
        clean_tag = tag.strip().replace('#', '')
        
        # Validate hashtag (alphanumeric + underscores, no spaces)
        if re.match(r'^[a-zA-Z0-9_]+$', clean_tag) and len(clean_tag) > 0:
            cleaned.append(f"#{clean_tag}")
    
    return list(set(cleaned))  # Remove duplicates

def truncate_text(text: str, max_length: int, suffix: str = "...") -> str:
    """Truncate text to specified length with suffix"""
    if len(text) <= max_length:
        return text
    
    return text[:max_length - len(suffix)].rstrip() + suffix

def format_platform_content(content: str, platform: str) -> str:
    """Format content according to platform-specific requirements"""
    platform_limits = {
        "twitter": 280,
        "instagram": 2200,  # Caption limit
        "facebook": 8000,
        "linkedin": 3000,
        "tiktok": 2200,
        "youtube": 5000,
        "pinterest": 500
    }
    
    max_length = platform_limits.get(platform.lower(), 2000)
    
    if len(content) > max_length:
        content = truncate_text(content, max_length)
    
    return content

def validate_url(url: str) -> bool:
    """Validate if a string is a valid URL"""
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except Exception:
        return False

def generate_session_id() -> str:
    """Generate a unique session ID"""
    timestamp = datetime.utcnow().isoformat()
    hash_object = hashlib.sha256(timestamp.encode())
    return hash_object.hexdigest()[:16]

def format_currency(amount: Union[int, float], currency: str = "USD") -> str:
    """Format currency amount"""
    try:
        if currency.upper() == "USD":
            return f"${amount:,.2f}"
        else:
            return f"{amount:,.2f} {currency}"
    except (ValueError, TypeError):
        return str(amount)

def extract_mentions(text: str) -> List[str]:
    """Extract @mentions from text"""
    mention_pattern = r'@(\w+)'
    mentions = re.findall(mention_pattern, text)
    return [f"@{mention}" for mention in mentions]

def calculate_reading_time(text: str, words_per_minute: int = 200) -> int:
    """Calculate estimated reading time in minutes"""
    word_count = len(text.split())
    reading_time = max(1, round(word_count / words_per_minute))
    return reading_time

def sanitize_filename(filename: str) -> str:
    """Sanitize filename for safe file system storage"""
    # Remove or replace invalid characters
    sanitized = re.sub(r'[<>:"/\\|?*]', '_', filename)
    # Remove multiple underscores
    sanitized = re.sub(r'_+', '_', sanitized)
    # Trim and remove leading/trailing underscores
    sanitized = sanitized.strip('_')
    
    return sanitized or "untitled"

def parse_business_hours(hours_text: str) -> Dict[str, str]:
    """Parse business hours text into structured format"""
    try:
        # Simple parsing - in production would use more sophisticated NLP
        hours_dict = {}
        
        # Common patterns
        if "24/7" in hours_text.lower() or "24 hours" in hours_text.lower():
            for day in ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]:
                hours_dict[day] = "24 hours"
        elif "9-5" in hours_text or "9am-5pm" in hours_text:
            for day in ["monday", "tuesday", "wednesday", "thursday", "friday"]:
                hours_dict[day] = "9:00 AM - 5:00 PM"
        
        return hours_dict
    except Exception:
        return {}

def extract_contact_info(text: str) -> Dict[str, List[str]]:
    """Extract contact information from text"""
    contact_info = {
        "emails": [],
        "phones": [],
        "websites": []
    }
    
    try:
        # Email pattern
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        contact_info["emails"] = re.findall(email_pattern, text)
        
        # Phone pattern (simple)
        phone_pattern = r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b'
        contact_info["phones"] = re.findall(phone_pattern, text)
        
        # Website pattern
        url_pattern = r'https?://[^\s<>"{}|\\^`[\]]+'
        contact_info["websites"] = re.findall(url_pattern, text)
        
    except Exception as e:
        logger.error(f"Contact info extraction error: {e}")
    
    return contact_info

def format_social_handle(handle: str, platform: str) -> str:
    """Format social media handle for specific platform"""
    # Remove @ if present
    clean_handle = handle.strip().lstrip('@')
    
    platform_formats = {
        "twitter": f"@{clean_handle}",
        "instagram": f"@{clean_handle}",
        "tiktok": f"@{clean_handle}",
        "facebook": clean_handle,  # Usually just the name
        "linkedin": clean_handle,
        "youtube": clean_handle
    }
    
    return platform_formats.get(platform.lower(), f"@{clean_handle}")

def calculate_engagement_rate(likes: int, comments: int, shares: int, followers: int) -> float:
    """Calculate engagement rate percentage"""
    try:
        total_engagement = likes + comments + shares
        if followers == 0:
            return 0.0
        
        engagement_rate = (total_engagement / followers) * 100
        return round(engagement_rate, 2)
    except (TypeError, ZeroDivisionError):
        return 0.0

def get_optimal_posting_times(platform: str, timezone: str = "UTC") -> List[str]:
    """Get optimal posting times for each platform"""
    # General best practices - in production, would be more sophisticated
    optimal_times = {
        "instagram": ["11:00 AM", "2:00 PM", "5:00 PM"],
        "facebook": ["9:00 AM", "1:00 PM", "6:00 PM"],
        "twitter": ["8:00 AM", "12:00 PM", "7:00 PM"],
        "linkedin": ["8:00 AM", "12:00 PM", "5:00 PM"],
        "tiktok": ["6:00 AM", "10:00 AM", "7:00 PM"],
        "youtube": ["2:00 PM", "8:00 PM", "9:00 PM"],
        "pinterest": ["8:00 PM", "9:00 PM", "10:00 PM"]
    }
    
    return optimal_times.get(platform.lower(), ["12:00 PM", "6:00 PM"])

def validate_campaign_data(data: Dict[str, Any]) -> Dict[str, List[str]]:
    """Validate campaign data and return errors"""
    errors = {}
    
    # Required fields
    required_fields = ["company_name", "target_audience", "primary_objective"]
    
    for field in required_fields:
        if not data.get(field):
            if "missing_fields" not in errors:
                errors["missing_fields"] = []
            errors["missing_fields"].append(field)
    
    # Validate budget if provided
    if data.get("budget") and not isinstance(data["budget"], (int, float)):
        if "invalid_values" not in errors:
            errors["invalid_values"] = []
        errors["invalid_values"].append("budget must be a number")
    
    # Validate platforms
    valid_platforms = ["facebook", "instagram", "twitter", "linkedin", "tiktok", "youtube", "pinterest"]
    if data.get("platforms"):
        for platform in data["platforms"]:
            if platform.lower() not in valid_platforms:
                if "invalid_platforms" not in errors:
                    errors["invalid_platforms"] = []
                errors["invalid_platforms"].append(platform)
    
    return errors

def generate_content_calendar(posts: List[Dict], start_date: datetime, 
                            posting_frequency: str = "daily") -> List[Dict]:
    """Generate a content calendar from posts"""
    calendar = []
    current_date = start_date
    
    frequency_delta = {
        "daily": timedelta(days=1),
        "every_other_day": timedelta(days=2),
        "weekly": timedelta(days=7),
        "bi_weekly": timedelta(days=14)
    }
    
    delta = frequency_delta.get(posting_frequency, timedelta(days=1))
    
    for i, post in enumerate(posts):
        # Get optimal time for platform
        optimal_times = get_optimal_posting_times(post.get("platform", "instagram"))
        post_time = optimal_times[0]  # Use first optimal time
        
        calendar_entry = {
            "date": current_date.strftime("%Y-%m-%d"),
            "time": post_time,
            "platform": post.get("platform"),
            "content": post.get("content"),
            "hashtags": post.get("hashtags", []),
            "image_url": post.get("image_url"),
            "status": "scheduled"
        }
        
        calendar.append(calendar_entry)
        current_date += delta
    
    return calendar

def compress_image_url(url: str, quality: int = 80) -> str:
    """Add compression parameters to image URL (placeholder)"""
    # This would integrate with actual image optimization service
    if not url or not validate_url(url):
        return url
    
    # Add quality parameter (example implementation)
    separator = "&" if "?" in url else "?"
    return f"{url}{separator}quality={quality}&format=webp"

def analyze_hashtag_performance(hashtags: List[str]) -> Dict[str, Any]:
    """Analyze hashtag performance (placeholder for real analytics)"""
    # This would integrate with social media APIs for real data
    performance = {}
    
    for hashtag in hashtags:
        # Simulate performance data
        performance[hashtag] = {
            "popularity": "medium",  # low, medium, high
            "competition": "moderate",  # low, moderate, high
            "reach_estimate": 1000,  # estimated reach
            "recommendation": "use"  # use, avoid, test
        }
    
    return performance

def create_campaign_report(campaign_data: Dict[str, Any]) -> Dict[str, Any]:
    """Create a comprehensive campaign report"""
    report = {
        "campaign_summary": {
            "company": campaign_data.get("company_name"),
            "objective": campaign_data.get("primary_objective"),
            "platforms": campaign_data.get("platforms", []),
            "duration": campaign_data.get("duration_weeks", 4),
            "posts_created": len(campaign_data.get("posts", [])),
            "generated_at": datetime.utcnow().isoformat()
        },
        "content_analysis": {
            "total_posts": len(campaign_data.get("posts", [])),
            "platform_distribution": {},
            "hashtag_count": 0,
            "average_content_length": 0
        },
        "recommendations": [],
        "next_steps": [
            "Review and approve all content",
            "Schedule posts in your social media management tool",
            "Monitor engagement and adjust strategy as needed",
            "Create additional content for ongoing campaigns"
        ]
    }
    
    # Calculate platform distribution
    posts = campaign_data.get("posts", [])
    for post in posts:
        platform = post.get("platform", "unknown")
        report["content_analysis"]["platform_distribution"][platform] = \
            report["content_analysis"]["platform_distribution"].get(platform, 0) + 1
    
    # Calculate average content length
    if posts:
        total_length = sum(len(post.get("content", "")) for post in posts)
        report["content_analysis"]["average_content_length"] = round(total_length / len(posts))
    
    # Count hashtags
    all_hashtags = []
    for post in posts:
        all_hashtags.extend(post.get("hashtags", []))
    report["content_analysis"]["hashtag_count"] = len(set(all_hashtags))
    
    return report