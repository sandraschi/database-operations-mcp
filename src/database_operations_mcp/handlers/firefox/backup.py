"""Backup and restore functionality for Firefox bookmarks."""
import shutil
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional
from fastmcp import tools
from .utils import get_places_db_path, get_profile_directory

@tool()
async def backup_firefox_data(
    backup_dir: Optional[str] = None,
    profile_name: Optional[str] = None
) -> Dict[str, Any]:
    """Create a backup of Firefox bookmarks and profile data.
    
    Args:
        backup_dir: Directory to store the backup (default: ~/firefox_backups)
        profile_name: Name of the Firefox profile to back up
        
    Returns:
        Dictionary with backup status and file path
    """
    profile_dir = get_profile_directory(profile_name)
    if not profile_dir:
        return {
            "status": "error",
            "message": f"Could not find Firefox profile: {profile_name or 'default'}"
        }
    
    # Set up backup directory
    if not backup_dir:
        backup_dir = Path.home() / "firefox_backups"
    else:
        backup_dir = Path(backup_dir)
    
    backup_dir.mkdir(parents=True, exist_ok=True)
    
    # Create timestamped backup
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_name = f"firefox_backup_{profile_name or 'default'}_{timestamp}"
    backup_path = backup_dir / backup_name
    
    try:
        # Create backup
        shutil.copytree(profile_dir, backup_path)
        
        return {
            "status": "success",
            "backup_path": str(backup_path),
            "backup_size": sum(f.stat().st_size for f in backup_path.rglob('*') if f.is_file())
        }
        
    except Exception as e:
        return {
            "status": "error",
            "message": f"Backup failed: {str(e)}"
        }

@tool()
async def restore_firefox_data(
    backup_path: str,
    profile_name: Optional[str] = None
) -> Dict[str, Any]:
    """Restore Firefox bookmarks from a backup.
    
    Args:
        backup_path: Path to the backup directory
        profile_name: Name of the Firefox profile to restore to
        
    Returns:
        Dictionary with restore status
    """
    profile_dir = get_profile_directory(profile_name)
    if not profile_dir:
        return {
            "status": "error",
            "message": f"Could not find Firefox profile: {profile_name or 'default'}"
        }
    
    backup_path = Path(backup_path)
    if not backup_path.exists():
        return {
            "status": "error",
            "message": f"Backup directory not found: {backup_path}"
        }
    
    try:
        # Backup current profile first
        backup_result = await backup_firefox_data(profile_name=profile_name)
        if backup_result["status"] != "success":
            return {
                "status": "error",
                "message": f"Failed to create backup before restore: {backup_result.get('message', 'Unknown error')}"
            }
        
        # Restore from backup
        for item in backup_path.glob('*'):
            dest = profile_dir / item.name
            if dest.exists():
                if dest.is_dir():
                    shutil.rmtree(dest)
                else:
                    dest.unlink()
            shutil.move(str(item), str(profile_dir))
        
        return {
            "status": "success",
            "message": f"Successfully restored Firefox profile from {backup_path}"
        }
        
    except Exception as e:
        return {
            "status": "error",
            "message": f"Restore failed: {str(e)}"
        }