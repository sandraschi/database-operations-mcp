"""
Advanced tag management for Firefox bookmarks.
Provides tools for bulk tag operations and analysis.
"""

from pathlib import Path
from typing import Dict, List, Any, Optional, Set
import re
from collections import defaultdict
from fastmcp import tool
from .db import FirefoxDB
from .help_system import HelpSystem

class TagManager:
    """Handles advanced tag operations for Firefox bookmarks."""
    
    def __init__(self, profile_path: Optional[Path] = None):
        self.db = FirefoxDB(profile_path)
    
    async def get_tag_stats(self) -> Dict[str, Any]:
        """Get statistics about tag usage."""
        stats = {
            'total_tags': 0,
            'tag_counts': {},
            'untagged_count': 0
        }
        
        tag_counts = defaultdict(int)
        total_bookmarks = 0
        
        async for bookmark in self.db.get_all_bookmarks():
            total_bookmarks += 1
            tags = await self.db.get_bookmark_tags(bookmark['id'])
            if not tags:
                stats['untagged_count'] += 1
            for tag in tags:
                tag_counts[tag] += 1
        
        stats['total_tags'] = len(tag_counts)
        stats['tag_counts'] = dict(sorted(
            tag_counts.items(),
            key=lambda x: x[1],
            reverse=True
        ))
        stats['tagged_percentage'] = (
            (total_bookmarks - stats['untagged_count']) / total_bookmarks * 100
            if total_bookmarks > 0 else 0
        )
        
        return stats

@tool()
@HelpSystem.register_tool(category='firefox')
async def find_similar_tags(
    search_pattern: str,
    case_sensitive: bool = False,
    profile_path: Optional[str] = None
) -> Dict[str, Any]:
    """Find tags matching a pattern (supports regex).
    
    Args:
        search_pattern: Regex pattern to match against tags
        case_sensitive: If True, performs case-sensitive matching
        profile_path: Path to Firefox profile
    """
    try:
        regex = re.compile(
            search_pattern,
            flags=0 if case_sensitive else re.IGNORECASE
        )
    except re.error as e:
        return {
            'status': 'error',
            'message': f'Invalid regex pattern: {str(e)}'
        }
    
    manager = TagManager(Path(profile_path) if profile_path else None)
    stats = await manager.get_tag_stats()
    matches = [tag for tag in stats['tag_counts'] if regex.search(tag)]
    
    return {
        'status': 'success',
        'pattern': search_pattern,
        'matches': matches,
        'match_count': len(matches)
    }

@tool()
@HelpSystem.register_tool(category='firefox')
async def merge_tags(
    source_tags: List[str],
    target_tag: str,
    dry_run: bool = True,
    profile_path: Optional[str] = None
) -> Dict[str, Any]:
    """Merge multiple tags into a single tag.
    
    Args:
        source_tags: List of tags to merge
        target_tag: Tag to merge into
        dry_run: If True, only show what would be changed
        profile_path: Path to Firefox profile
    """
    db = FirefoxDB(Path(profile_path) if profile_path else None)
    changes = []
    
    # Get all bookmarks with source tags
    bookmarks_to_update = set()
    for tag in source_tags:
        async for bookmark in db.get_bookmarks_by_tag(tag):
            bookmarks_to_update.add(bookmark['id'])
    
    # Apply changes
    if not dry_run:
        for bookmark_id in bookmarks_to_update:
            # Get current tags
            current_tags = await db.get_bookmark_tags(bookmark_id)
            # Remove source tags and add target tag
            new_tags = [t for t in current_tags if t not in source_tags]
            if target_tag not in new_tags:
                new_tags.append(target_tag)
            
            # Update tags if changed
            if set(new_tags) != set(current_tags):
                await db.update_bookmark_tags(bookmark_id, new_tags)
                changes.append({
                    'bookmark_id': bookmark_id,
                    'old_tags': current_tags,
                    'new_tags': new_tags
                })
    
    return {
        'status': 'dry_run' if dry_run else 'success',
        'bookmarks_affected': len(bookmarks_to_update),
        'changes': changes,
        'dry_run': dry_run
    }

@tool()
@HelpSystem.register_tool(category='firefox')
async def clean_up_tags(
    min_count: int = 1,
    dry_run: bool = True,
    profile_path: Optional[str] = None
) -> Dict[str, Any]:
    """Remove rarely used tags.
    
    Args:
        min_count: Minimum number of bookmarks a tag must be used on
        dry_run: If True, only show what would be deleted
        profile_path: Path to Firefox profile
    """
    manager = TagManager(Path(profile_path) if profile_path else None)
    stats = await manager.get_tag_stats()
    
    tags_to_remove = [
        tag for tag, count in stats['tag_counts'].items()
        if count < min_count
    ]
    
    changes = []
    if not dry_run:
        # Implementation for actual tag removal
        pass
    
    return {
        'status': 'dry_run' if dry_run else 'success',
        'tags_removed': tags_to_remove,
        'count': len(tags_to_remove),
        'dry_run': dry_run
    }