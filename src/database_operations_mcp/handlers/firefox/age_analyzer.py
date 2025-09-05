"""
Age analysis for Firefox bookmarks.
Helps identify and manage old or outdated bookmarks.
"""

from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from fastmcp import tool
from .db import FirefoxDB
from .help_system import HelpSystem

@tool()
@HelpSystem.register_tool(category='firefox')
async def find_old_bookmarks(
    days_old: int = 365,
    include_visited: bool = False,
    profile_path: Optional[str] = None
) -> Dict[str, Any]:
    """Find bookmarks older than specified number of days.
    
    Args:
        days_old: Minimum age in days to consider a bookmark "old"
        include_visited: Include bookmarks that have been recently visited
        profile_path: Path to Firefox profile
    """
    db = FirefoxDB(Path(profile_path) if profile_path else None)
    cutoff_date = datetime.now() - timedelta(days=days_old)
    old_bookmarks = []
    
    async for bookmark in db.get_all_bookmarks():
        if not bookmark.get('date_added'):
            continue
            
        added_date = datetime.fromtimestamp(bookmark['date_added'] / 1000000)
        last_visited = bookmark.get('last_visit_date')
        
        is_old = added_date < cutoff_date
        recently_visited = last_visited and datetime.fromtimestamp(last_visited / 1000000) > cutoff_date
        
        if is_old and (not recently_visited or include_visited):
            old_bookmarks.append({
                'id': bookmark['id'],
                'title': bookmark.get('title', 'Untitled'),
                'url': bookmark.get('url', ''),
                'date_added': added_date.isoformat(),
                'last_visited': datetime.fromtimestamp(last_visited / 1000000).isoformat() if last_visited else None,
                'age_days': (datetime.now() - added_date).days
            })
    
    return {
        'status': 'success',
        'cutoff_date': cutoff_date.isoformat(),
        'bookmark_count': len(old_bookmarks),
        'bookmarks': sorted(old_bookmarks, key=lambda x: x['age_days'], reverse=True)
    }

@tool()
@HelpSystem.register_tool(category='firefox')
async def get_bookmark_stats(
    profile_path: Optional[str] = None
) -> Dict[str, Any]:
    """Get statistics about bookmark ages and usage.
    
    Args:
        profile_path: Path to Firefox profile
    """
    db = FirefoxDB(Path(profile_path) if profile_path else None)
    now = datetime.now()
    stats = {
        'total': 0,
        'by_age': {
            'week': 0,
            'month': 0,
            'year': 0,
            'older': 0
        },
        'recently_used': 0
    }
    
    async for bookmark in db.get_all_bookmarks():
        if not bookmark.get('date_added'):
            continue
            
        stats['total'] += 1
        added_date = datetime.fromtimestamp(bookmark['date_added'] / 1000000)
        age = now - added_date
        
        if age < timedelta(days=7):
            stats['by_age']['week'] += 1
        elif age < timedelta(days=30):
            stats['by_age']['month'] += 1
        elif age < timedelta(days=365):
            stats['by_age']['year'] += 1
        else:
            stats['by_age']['older'] += 1
            
        # Check if visited in last 30 days
        if (bookmark.get('last_visit_date') and 
            (now - datetime.fromtimestamp(bookmark['last_visit_date'] / 1000000)) < timedelta(days=30)):
            stats['recently_used'] += 1
    
    # Calculate percentages
    if stats['total'] > 0:
        stats['recently_used_pct'] = (stats['recently_used'] / stats['total']) * 100
        for key in stats['by_age']:
            stats['by_age'][f'{key}_pct'] = (stats['by_age'][key] / stats['total']) * 100
    
    return {
        'status': 'success',
        'stats': stats
    }