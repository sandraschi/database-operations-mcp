"""Core Firefox bookmark functionality with improved status checking."""

import base64
import configparser
import logging
import re
import shutil
import sqlite3
import tempfile
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import aiohttp
from bs4 import BeautifulSoup

# Import the global MCP instance from the central config
from database_operations_mcp.config.mcp_config import mcp

from ..help_tools import HelpSystem
from .bookmark_manager import BookmarkManager
from .curated_sources import CURATED_SOURCES, get_curated_source, list_curated_sources
from .links import add_bookmark
from .status import FirefoxStatusChecker
from .utils import get_profile_directory, get_profiles_ini_path, parse_profiles_ini

logger = logging.getLogger(__name__)


class FirefoxDatabaseUnlocker:
    """Dirty tricks to access Firefox database even when locked."""

    @staticmethod
    def copy_database_to_temp(db_path: Path) -> Optional[Path]:
        """Copy the locked database to a temporary location for reading."""
        try:
            with tempfile.NamedTemporaryFile(suffix=".sqlite", delete=False) as temp_file:
                temp_path = Path(temp_file.name)

            # Try to copy the database file
            shutil.copy2(db_path, temp_path)
            return temp_path

        except (PermissionError, OSError, shutil.Error) as e:
            logger.debug(f"Failed to copy database: {e}")
            # Clean up failed temp file
            if "temp_path" in locals():
                try:
                    temp_path.unlink(missing_ok=True)
                except Exception:
                    pass
            return None

    @staticmethod
    def try_sqlite_tricks(db_path: Path) -> Optional[sqlite3.Connection]:
        """Try various SQLite connection tricks to access locked database."""

        connection_attempts = [
            # Method 1: Read-only with immutable flag
            f"file:{db_path}?mode=ro&immutable=1",
            # Method 2: Read-only with nolock flag (if supported)
            f"file:{db_path}?mode=ro&nolock=1",
            # Method 3: Read-only with cache=shared
            f"file:{db_path}?mode=ro&cache=shared",
            # Method 4: Direct read-only URI
            f"file:{db_path}?mode=ro",
            # Method 5: Normal read-only (least likely to work)
            str(db_path),
        ]

        for uri in connection_attempts:
            try:
                if uri.startswith("file:"):
                    conn = sqlite3.connect(uri, uri=True, timeout=1.0)
                else:
                    conn = sqlite3.connect(uri, timeout=1.0)

                # Test the connection with a simple query
                cursor = conn.cursor()
                cursor.execute("SELECT 1")
                cursor.fetchone()
                cursor.close()

                logger.info(f"Successfully opened Firefox DB with: {uri}")
                return conn

            except sqlite3.Error as e:
                logger.debug(f"Failed SQLite method {uri}: {e}")
                continue

        return None

    @staticmethod
    def get_database_connection_bruteforce(
        db_path: Path,
    ) -> Tuple[Optional[sqlite3.Connection], str]:
        """
        Use dirty tricks to access Firefox database even when locked.

        Returns:
        Tuple of (connection, method_used) or (None, error_message)
        """
        if not db_path.exists():
            return None, "Database file does not exist"

        # Method 1: Try direct SQLite tricks first (fastest)
        logger.info("Attempting SQLite URI tricks...")
        conn = FirefoxDatabaseUnlocker.try_sqlite_tricks(db_path)
        if conn:
            return conn, "sqlite_uri_tricks"

        # Method 2: Copy database to temp location (more reliable)
        logger.info("Attempting database copy method...")
        temp_db_path = FirefoxDatabaseUnlocker.copy_database_to_temp(db_path)
        if temp_db_path:
            try:
                conn = sqlite3.connect(f"file:{temp_db_path}?mode=ro", uri=True)
                # Test connection
                cursor = conn.cursor()
                cursor.execute("SELECT 1")
                cursor.fetchone()
                cursor.close()

                logger.info(f"Successfully copied and opened Firefox DB: {temp_db_path}")
                # Store temp path in connection for cleanup
                conn.temp_db_path = temp_db_path
                return conn, "database_copy"

            except sqlite3.Error as e:
                logger.debug(f"Failed to use copied database: {e}")
                # Clean up temp file
                try:
                    temp_db_path.unlink(missing_ok=True)
                except Exception:
                    pass

        # Method 3: Last resort - try with longer timeout
        logger.info("Attempting extended timeout method...")
        try:
            conn = sqlite3.connect(f"file:{db_path}?mode=ro", uri=True, timeout=5.0)
            cursor = conn.cursor()
            cursor.execute("SELECT 1")
            cursor.fetchone()
            cursor.close()

            logger.info("Successfully opened Firefox DB with extended timeout")
            return conn, "extended_timeout"

        except sqlite3.Error as e:
            logger.debug(f"Extended timeout also failed: {e}")

        return None, "All brute force methods failed - database is locked"


@mcp.tool()
@HelpSystem.register_tool(category="firefox")
async def check_firefox_bruteforce_access() -> Dict[str, Any]:
    """Check if Firefox database can be accessed using brute force methods.

    This tool attempts various "dirty tricks" to access Firefox's places.sqlite
    database even when Firefox is running and has it locked. Useful for cases
    where you need to read Firefox data without closing the browser.

    Returns:
    Dictionary with access status and available methods
    """
    try:
        # Get Firefox profile path
        profile_path = get_default_profile_path()
        if not profile_path:
            return {"status": "error", "message": "No Firefox profile found"}

        db_path = profile_path / "places.sqlite"
        if not db_path.exists():
            return {"status": "error", "message": f"Firefox database not found at {db_path}"}

        # Check Firefox status
        firefox_status = FirefoxStatusChecker.is_firefox_running()

        # Try brute force access
        conn, method = FirefoxDatabaseUnlocker.get_database_connection_bruteforce(db_path)

        if conn:
            # Successfully got access - get some basic info
            try:
                cursor = conn.cursor()
                cursor.execute("SELECT COUNT(*) FROM moz_places")
                places_count = cursor.fetchone()[0]

                cursor.execute("SELECT COUNT(*) FROM moz_bookmarks")
                bookmarks_count = cursor.fetchone()[0]

                cursor.close()

                result = {
                    "status": "success",
                    "message": f"Successfully accessed Firefox database using {method}",
                    "access_method": method,
                    "firefox_running": firefox_status["is_running"],
                    "database_path": str(db_path),
                    "stats": {"places_count": places_count, "bookmarks_count": bookmarks_count},
                }

            finally:
                # Clean up connection and temp files
                if hasattr(conn, "temp_db_path"):
                    try:
                        conn.temp_db_path.unlink(missing_ok=True)
                    except Exception:
                        pass
                conn.close()

        else:
            result = {
                "status": "failed",
                "message": method,  # method contains the error message
                "firefox_running": firefox_status["is_running"],
                "firefox_processes": firefox_status.get("processes", []),
                "database_path": str(db_path),
            }

        return result

    except Exception as e:
        return {"status": "error", "message": f"Brute force access check failed: {str(e)}"}


def is_firefox_running() -> bool:
    """Legacy function for backward compatibility."""
    from .status import FirefoxStatusChecker
    return FirefoxStatusChecker.is_firefox_running()["is_running"]


def get_default_profile_path() -> Optional[Path]:
    """Get the path to the default Firefox profile."""
    return get_profile_directory()


@mcp.tool()
@HelpSystem.register_tool(category="firefox")
async def list_curated_bookmark_sources() -> Dict[str, Any]:
    """List available curated bookmark sources for profile creation.

    Returns a list of predefined bookmark collections that can be used to create
    loaded Firefox profiles with relevant bookmarks for different purposes.
    """
    return list_curated_sources()


@mcp.tool()
@HelpSystem.register_tool(category="firefox")
async def create_loaded_profile_from_preset(
    profile_name: str, preset_name: str, max_bookmarks: int = 50
) -> Dict[str, Any]:
    """Create a Firefox profile loaded with bookmarks from a predefined curated collection.

    This is a simplified version of create_loaded_profile that uses predefined collections
    instead of requiring custom configuration.

    Args:
        profile_name: Name for the new profile
        preset_name: Name of the predefined bookmark collection 
        (e.g., "developer_tools", "cooking", "ai_ml")
        max_bookmarks: Maximum number of bookmarks to add

    Available presets:
        - developer_tools: Essential tools for developers
        - ai_ml: AI and machine learning resources from GitHub awesome repos
        - cooking: Popular cooking and recipe websites
        - productivity: Tools to boost productivity and organization
        - news_media: Major news outlets and media sources
        - finance: Financial news, tools, and investment resources
        - entertainment: Streaming services, movies, music, and entertainment
        - shopping: Online shopping and deal-finding sites
    """
    # Get the curated source
    source_info = get_curated_source(preset_name)
    if not source_info:
        available_presets = list(CURATED_SOURCES.keys())
        return {
            "status": "error",
            "message": (
                f"Preset '{preset_name}' not found. "
                f"Available presets: {', '.join(available_presets)}"
            ),
            "available_presets": available_presets,
        }

    # Use the main function with the preset configuration
    return await create_loaded_profile(
        profile_name=profile_name,
        source_type=source_info["source_type"],
        source_config=source_info["config"],
        max_bookmarks=max_bookmarks,
    )


@mcp.tool()
@HelpSystem.register_tool(category="firefox")
async def check_firefox_status() -> Dict[str, Any]:
    """Check Firefox running status and database access safety.

    This tool helps determine if it's safe to access Firefox bookmark databases.
    Firefox locks its database files when running, so operations will fail if Firefox is open.
    """
    status = FirefoxStatusChecker.is_firefox_running()
    safety = FirefoxStatusChecker.check_database_access_safe()

    return {
        "status": "success",
        "firefox_status": status,
        "database_access": safety,
        "recommendation": "Close Firefox completely before running bookmark operations"
        if status["is_running"]
        else "Firefox is closed - safe to access bookmark databases",
    }


@mcp.tool()
@HelpSystem.register_tool(category="firefox")
async def get_firefox_profiles() -> Dict[str, Any]:
    """List all available Firefox profiles with detailed information.

    Returns profile names, paths, and bookmark database locations.
    Note: Firefox must be closed for accurate profile detection.
    """
    # Check if Firefox is running
    safety_check = FirefoxStatusChecker.check_database_access_safe()
    if not safety_check["safe"]:
        return {
            "status": "warning",
            "message": safety_check["message"],
            "safety_check": safety_check,
            "profiles": {},
        }

    try:
        profiles = parse_profiles_ini()
        if not profiles:
            return {
                "status": "error",
                "message": (
                    "No Firefox profiles found. Make sure Firefox has been "
                    "installed and run at least once."
                ),
                "safety_check": safety_check,
            }

        # Get detailed profile information
        detailed_profiles = {}
        for name, profile_data in profiles.items():
            profile_path = get_profile_directory(name)
            if profile_path and profile_path.exists():
                places_db = profile_path / "places.sqlite"
                detailed_profiles[name] = {
                    "name": name,
                    "path": str(profile_path),
                    "is_relative": profile_data.get("IsRelative", "1") == "1",
                    "is_default": profile_data.get("Default", "0") == "1",
                    "bookmarks_database": str(places_db) if places_db.exists() else None,
                    "database_exists": places_db.exists(),
                    "profile_info": profile_data,
                }

        return {
            "status": "success",
            "profile_count": len(detailed_profiles),
            "profiles": detailed_profiles,
            "safety_check": safety_check,
            "note": "Use profile names in other bookmark tools to specify which profile to access",
        }

    except Exception as e:
        return {
            "status": "error",
            "message": f"Error reading Firefox profiles: {str(e)}",
            "safety_check": safety_check,
        }


@mcp.tool()
@HelpSystem.register_tool(category="firefox")
async def create_firefox_profile(
    profile_name: str, template_profile: Optional[str] = None
) -> Dict[str, Any]:
    """Create a new Firefox profile.

    Args:
        profile_name: Name for the new profile
        template_profile: Optional existing profile to copy settings from

    Note: This creates a new profile directory but doesn't copy bookmarks.
    Firefox will create the profile when it first runs with this profile.
    """
    safety_check = FirefoxStatusChecker.check_database_access_safe()
    if not safety_check["safe"]:
        return {"status": "error", "message": safety_check["message"], "safety_check": safety_check}

    try:
        profiles_ini_path = get_profiles_ini_path()
        if not profiles_ini_path:
            return {"status": "error", "message": "Could not locate Firefox profiles.ini file"}

        # Parse existing profiles
        profiles = parse_profiles_ini()

        # Check if profile already exists
        if profile_name in profiles:
            return {"status": "error", "message": f"Profile '{profile_name}' already exists"}

        # Find the next available profile number
        existing_numbers = []
        for profile_data in profiles.values():
            if "Path" in profile_data:
                path = profile_data["Path"]
                if path.startswith("profile"):
                    try:
                        num = int(path.replace("profile", ""))
                        existing_numbers.append(num)
                    except ValueError:
                        continue

        next_num = max(existing_numbers) + 1 if existing_numbers else 0
        profile_dir_name = f"profile{next_num}"

        # Create the profile directory structure
        profiles_dir = profiles_ini_path.parent / "Profiles"
        profile_path = profiles_dir / profile_dir_name
        profile_path.mkdir(parents=True, exist_ok=True)

        # Update profiles.ini
        config = configparser.ConfigParser()
        if profiles_ini_path.exists():
            config.read(profiles_ini_path)

        # Find next profile section number
        profile_sections = [s for s in config.sections() if s.startswith("Profile")]
        next_profile_num = len(profile_sections) + 1

        section_name = f"Profile{next_profile_num}"
        config[section_name] = {
            "Name": profile_name,
            "IsRelative": "1",
            "Path": profile_dir_name,
            "Default": "0",
        }

        # Write back to profiles.ini
        with open(profiles_ini_path, "w") as f:
            config.write(f)

        return {
            "status": "success",
            "message": f"Profile '{profile_name}' created successfully",
            "profile_name": profile_name,
            "profile_path": str(profile_path),
            "profile_section": section_name,
            "note": (
                "Firefox will initialize the profile when you first use it. "
                "Bookmarks will be empty initially."
            ),
        }

    except Exception as e:
        return {"status": "error", "message": f"Failed to create profile: {str(e)}"}


@mcp.tool()
@HelpSystem.register_tool(category="firefox")
async def delete_firefox_profile(
    profile_name: str, confirm_deletion: bool = False
) -> Dict[str, Any]:
    """Delete a Firefox profile and all its data.

    Args:
        profile_name: Name of the profile to delete
        confirm_deletion: Must be True to actually delete the profile

    WARNING: This permanently deletes the profile and all bookmarks, history, and settings!
    """
    safety_check = FirefoxStatusChecker.check_database_access_safe()
    if not safety_check["safe"]:
        return {"status": "error", "message": safety_check["message"], "safety_check": safety_check}

    if not confirm_deletion:
        return {
            "status": "error",
            "message": "Profile deletion not confirmed. Set confirm_deletion=true to proceed.",
            "warning": "This will permanently delete the profile and all its data!",
        }

    try:
        profiles = parse_profiles_ini()
        if profile_name not in profiles:
            return {"status": "error", "message": f"Profile '{profile_name}' not found"}

        # Get profile path
        profile_path = get_profile_directory(profile_name)
        if not profile_path or not profile_path.exists():
            return {
                "status": "error",
                "message": f"Profile directory not found for '{profile_name}'",
            }

        # Delete the profile directory
        shutil.rmtree(profile_path)

        # Update profiles.ini
        profiles_ini_path = get_profiles_ini_path()
        if profiles_ini_path and profiles_ini_path.exists():
            config = configparser.ConfigParser()
            config.read(profiles_ini_path)

            # Find and remove the profile section
            for section in config.sections():
                if section.startswith("Profile") and config[section].get("Name") == profile_name:
                    config.remove_section(section)
                    break

            # Write back to profiles.ini
            with open(profiles_ini_path, "w") as f:
                config.write(f)

        return {
            "status": "success",
            "message": f"Profile '{profile_name}' deleted successfully",
            "deleted_path": str(profile_path),
        }

    except Exception as e:
        return {"status": "error", "message": f"Failed to delete profile: {str(e)}"}


@mcp.tool()
@HelpSystem.register_tool(category="firefox")
async def create_loaded_profile(
    profile_name: str, source_type: str, source_config: Dict[str, Any], max_bookmarks: int = 50
) -> Dict[str, Any]:
    """Create a new Firefox profile pre-loaded with curated bookmarks.

    This tool creates a new Firefox profile and populates it with bookmarks from various sources,
    making it easy to set up specialized profiles for different purposes.

    Args:
        profile_name: Name for the new profile
        source_type: Type of bookmark source 
        ("current_collection", "web_list", "github_awesome", "custom_list")
        source_config: Configuration for the source (varies by source_type)
        max_bookmarks: Maximum number of bookmarks to add

    Source Types:
        - "current_collection": Copy bookmarks from existing profiles
          config: {"from_profile": "source_profile_name", "filter_tags": ["tag1", "tag2"]}
        - "web_list": Scrape bookmarks from curated web pages
          config: {"url": "https://example.com/bookmarks", "selector": "css_selector"}
        - "github_awesome": Parse awesome-* repos from GitHub
          config: {"topic": "ai", "language": "en"}
        - "custom_list": User-provided list of bookmarks
          config: {"bookmarks": [{"title": "Site", "url": "https://example.com"}]}

    Examples:
        Create dev profile from GitHub awesome repos:
        await create_loaded_profile("dev-tools", "github_awesome", {"topic": "developer-tools"})

        Create cooking profile from web list:
        await create_loaded_profile("cooking", "web_list", {"url": "https://example.com/best-cooking-sites"})

        Create work profile from current collection:
        await create_loaded_profile(
            "work", "current_collection", 
            {"from_profile": "default", "filter_tags": ["work"]}
        )
    """
    safety_check = FirefoxStatusChecker.check_database_access_safe()
    if not safety_check["safe"]:
        return {"status": "error", "message": safety_check["message"], "safety_check": safety_check}

    try:
        # First create the basic profile
        create_result = await create_firefox_profile(profile_name)
        if create_result["status"] != "success":
            return create_result

        # Get the profile path
        profile_path = get_profile_directory(profile_name)
        if not profile_path:
            return {
                "status": "error",
                "message": f"Could not find path for newly created profile '{profile_name}'",
            }

        # Fetch bookmarks based on source type
        bookmarks = await _fetch_bookmarks_from_source(source_type, source_config, max_bookmarks)

        if not bookmarks:
            return {
                "status": "warning",
                "message": (
                    f"Profile '{profile_name}' created but no bookmarks were "
                    f"loaded from source '{source_type}'"
                ),
                "profile_name": profile_name,
                "profile_path": str(profile_path),
                "bookmarks_loaded": 0,
            }

        # Add bookmarks to the new profile
        bookmarks_added = await _populate_profile_with_bookmarks(profile_name, bookmarks)

        return {
            "status": "success",
            "message": (
                f"Profile '{profile_name}' created and loaded with "
                f"{bookmarks_added} bookmarks"
            ),
            "profile_name": profile_name,
            "profile_path": str(profile_path),
            "source_type": source_type,
            "bookmarks_loaded": bookmarks_added,
            "total_found": len(bookmarks),
        }

    except Exception as e:
        return {"status": "error", "message": f"Failed to create loaded profile: {str(e)}"}


async def _fetch_bookmarks_from_source(
    source_type: str, config: Dict[str, Any], max_bookmarks: int
) -> List[Dict[str, str]]:
    """Fetch bookmarks from various sources."""
    try:
        if source_type == "current_collection":
            return await _fetch_from_current_collection(config, max_bookmarks)
        elif source_type == "web_list":
            return await _fetch_from_web_list(config, max_bookmarks)
        elif source_type == "github_awesome":
            return await _fetch_from_github_awesome(config, max_bookmarks)
        elif source_type == "custom_list":
            return _fetch_from_custom_list(config, max_bookmarks)
        else:
            raise ValueError(f"Unknown source type: {source_type}")
    except Exception as e:
        logger = logging.getLogger(__name__)
        logger.error(f"Error fetching bookmarks from {source_type}: {str(e)}")
        return []


async def _fetch_from_current_collection(
    config: Dict[str, Any], max_bookmarks: int
) -> List[Dict[str, str]]:
    """Fetch bookmarks from existing profiles."""
    from_profile = config.get("from_profile")
    filter_tags = config.get("filter_tags", [])

    if not from_profile:
        return []

    # Get bookmarks from the source profile
    source_path = get_profile_directory(from_profile)
    if not source_path:
        return []

    manager = BookmarkManager(source_path)
    try:
        bookmarks = manager.get_bookmarks()
    except Exception:
        return []

    # Filter by tags if specified
    if filter_tags:
        # Note: This is a simplified filter - in a real implementation,
        # you'd need to check bookmark tags from the database
        filtered_bookmarks = bookmarks[:max_bookmarks]  # Simplified
    else:
        filtered_bookmarks = bookmarks[:max_bookmarks]

    # Convert to the expected format
    return [{"title": bm["title"], "url": bm["url"]} for bm in filtered_bookmarks]


async def _fetch_from_web_list(config: Dict[str, Any], max_bookmarks: int) -> List[Dict[str, str]]:
    """Fetch bookmarks from curated web pages."""
    url = config.get("url")
    selector = config.get("selector", "a[href]")

    if not url:
        return []

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, timeout=aiohttp.ClientTimeout(total=10)) as response:
                if response.status != 200:
                    return []

                html = await response.text()
                soup = BeautifulSoup(html, "html.parser")

                links = soup.select(selector)[:max_bookmarks]
                bookmarks = []

                for link in links:
                    href = link.get("href")
                    title = link.get_text(strip=True) or link.get("title", "") or href

                    if href and href.startswith(("http://", "https://")):
                        bookmarks.append(
                            {
                                "title": title[:100],  # Limit title length
                                "url": href,
                            }
                        )

                return bookmarks

    except Exception as e:
        logger = logging.getLogger(__name__)
        logger.error(f"Error scraping web list from {url}: {str(e)}")
        return []


async def _fetch_from_github_awesome(
    config: Dict[str, Any], max_bookmarks: int
) -> List[Dict[str, str]]:
    """Fetch bookmarks from GitHub awesome-* repositories."""
    topic = config.get("topic", "").lower().replace(" ", "-")
    config.get("language", "en")

    if not topic:
        return []

    try:
        # Search for awesome repos
        search_url = (
            f"https://api.github.com/search/repositories?q=awesome+{topic}&sort=stars&order=desc"
        )

        async with aiohttp.ClientSession() as session:
            async with session.get(search_url, timeout=aiohttp.ClientTimeout(total=10)) as response:
                if response.status != 200:
                    return []

                data = await response.json()
                repos = data.get("items", [])[:5]  # Top 5 repos

                bookmarks = []
                for repo in repos:
                    readme_url = f"https://api.github.com/repos/{repo['full_name']}/readme"

                    try:
                        async with session.get(
                            readme_url, timeout=aiohttp.ClientTimeout(total=5)
                        ) as readme_response:
                            if readme_response.status == 200:
                                readme_data = await readme_response.json()
                                readme_content = base64.b64decode(readme_data["content"]).decode(
                                    "utf-8"
                                )

                                # Extract links from README (simplified parsing)
                                link_pattern = r"\[([^\]]+)\]\((https?://[^\s)]+)\)"
                                matches = re.findall(link_pattern, readme_content)[
                                    : max_bookmarks // len(repos)
                                ]

                                for title, url in matches:
                                    bookmarks.append({"title": title[:100], "url": url})

                    except Exception:
                        continue

                return bookmarks[:max_bookmarks]

    except Exception as e:
        logger = logging.getLogger(__name__)
        logger.error(f"Error fetching GitHub awesome repos for {topic}: {str(e)}")
        return []


def _fetch_from_custom_list(config: Dict[str, Any], max_bookmarks: int) -> List[Dict[str, str]]:
    """Fetch bookmarks from user-provided custom list."""
    bookmarks_data = config.get("bookmarks", [])

    bookmarks = []
    for item in bookmarks_data[:max_bookmarks]:
        if isinstance(item, dict) and "url" in item:
            bookmarks.append({"title": item.get("title", item["url"]), "url": item["url"]})

    return bookmarks


async def _populate_profile_with_bookmarks(
    profile_name: str, bookmarks: List[Dict[str, str]]
) -> int:
    """Add bookmarks to a Firefox profile database."""
    try:
        added_count = 0
        for bookmark in bookmarks:
            try:
                # Use the existing add_bookmark function with profile name
                result = await add_bookmark(
                    url=bookmark["url"], title=bookmark["title"], profile_name=profile_name
                )
                if result.get("status") == "success":
                    added_count += 1
            except Exception:
                continue  # Skip failed bookmarks

        return added_count

    except Exception as e:
        logger = logging.getLogger(__name__)
        logger.error(f"Error populating profile with bookmarks: {str(e)}")
        return 0


@mcp.tool()
@HelpSystem.register_tool(category="firefox")
async def create_portmanteau_profile(
    profile_name: str,
    preset_combinations: List[str],
    max_bookmarks_per_source: int = 10,
    deduplicate: bool = True,
) -> Dict[str, Any]:
    """Create a Firefox profile that combines multiple bookmark collections (portmanteau style).

    This tool creates hybrid profiles by blending bookmarks from multiple preset collections,
    allowing you to create specialized profiles like "dev+cooking" or "ai+productivity".

    Args:
        profile_name: Name for the new hybrid profile
        preset_combinations: List of preset names to combine (e.g., ["developer_tools", "cooking"])
        max_bookmarks_per_source: Maximum bookmarks to take from each source
        deduplicate: Whether to remove duplicate URLs across sources

    Examples:
        Create a "dev+cooking" profile:
        await create_portmanteau_profile("dev-cooking", ["developer_tools", "cooking"])

        Create an "ai+productivity" research profile:
        await create_portmanteau_profile("ai-productivity", ["ai_ml", "productivity"])

        Create a comprehensive "work+news" profile:
        await create_portmanteau_profile("work-news", ["developer_tools", "news_media"])

    Available presets: developer_tools, ai_ml, cooking, productivity, 
    news_media, finance, entertainment, shopping
    """
    safety_check = FirefoxStatusChecker.check_database_access_safe()
    if not safety_check["safe"]:
        return {"status": "error", "message": safety_check["message"], "safety_check": safety_check}

    try:
        # Validate all presets exist
        invalid_presets = []
        valid_presets = []

        for preset in preset_combinations:
            if preset in CURATED_SOURCES:
                valid_presets.append(preset)
            else:
                invalid_presets.append(preset)

        if invalid_presets:
            available_presets = list(CURATED_SOURCES.keys())
            return {
                "status": "error",
                "message": (
                    f"Invalid presets: {', '.join(invalid_presets)}. "
                    f"Available: {', '.join(available_presets)}"
                ),
                "available_presets": available_presets,
            }

        if not valid_presets:
            return {"status": "error", "message": "No valid presets specified"}

        # Create the basic profile first
        create_result = await create_firefox_profile(profile_name)
        if create_result["status"] != "success":
            return create_result

        # Get the profile path
        profile_path = get_profile_directory(profile_name)
        if not profile_path:
            return {
                "status": "error",
                "message": f"Could not find path for newly created profile '{profile_name}'",
            }

        # Collect bookmarks from all sources
        all_bookmarks = []
        source_stats = {}

        for preset_name in valid_presets:
            source_config = CURATED_SOURCES[preset_name]
            bookmarks = await _fetch_bookmarks_from_source(
                source_config["source_type"], source_config["config"], max_bookmarks_per_source
            )

            if bookmarks:
                all_bookmarks.extend(bookmarks)
                source_stats[preset_name] = {
                    "count": len(bookmarks),
                    "description": source_config["description"],
                }
            else:
                source_stats[preset_name] = {
                    "count": 0,
                    "description": source_config["description"],
                    "error": "No bookmarks fetched",
                }

        # Deduplicate if requested
        if deduplicate:
            seen_urls = set()
            deduplicated_bookmarks = []
            duplicates_removed = 0

            for bookmark in all_bookmarks:
                if bookmark["url"] not in seen_urls:
                    seen_urls.add(bookmark["url"])
                    deduplicated_bookmarks.append(bookmark)
                else:
                    duplicates_removed += 1

            all_bookmarks = deduplicated_bookmarks
        else:
            duplicates_removed = 0

        if not all_bookmarks:
            return {
                "status": "warning",
                "message": (
                    f"Profile '{profile_name}' created but no bookmarks were "
                    f"collected from sources"
                ),
                "profile_name": profile_name,
                "profile_path": str(profile_path),
                "sources_attempted": valid_presets,
                "source_stats": source_stats,
            }

        # Add bookmarks to the profile
        bookmarks_added = await _populate_profile_with_bookmarks(profile_name, all_bookmarks)

        # Generate portmanteau-style description
        preset_names = [name.replace("_", "-") for name in valid_presets]
        portmanteau_desc = " + ".join(preset_names)

        return {
            "status": "success",
            "message": (
                f"Portmanteau profile '{profile_name}' created with "
                f"{portmanteau_desc} bookmarks"
            ),
            "profile_name": profile_name,
            "profile_path": str(profile_path),
            "portmanteau_description": portmanteau_desc,
            "sources_combined": valid_presets,
            "source_stats": source_stats,
            "bookmarks_collected": len(all_bookmarks),
            "bookmarks_added": bookmarks_added,
            "duplicates_removed": duplicates_removed if deduplicate else 0,
            "deduplication_enabled": deduplicate,
        }

    except Exception as e:
        return {"status": "error", "message": f"Failed to create portmanteau profile: {str(e)}"}


@mcp.tool()
@HelpSystem.register_tool(category="firefox")
async def suggest_portmanteau_profiles() -> Dict[str, Any]:
    """Suggest interesting portmanteau profile combinations.

    Returns a list of recommended profile combinations that blend different types
    of bookmarks for specialized use cases.
    """
    suggestions = [
        {
            "name": "dev-ai",
            "presets": ["developer_tools", "ai_ml"],
            "description": "Developer tools + AI resources for tech innovators",
            "use_case": "Full-stack development with AI assistance",
        },
        {
            "name": "research-productivity",
            "presets": ["ai_ml", "productivity"],
            "description": "AI research + productivity tools for researchers",
            "use_case": "Academic research and paper writing",
        },
        {
            "name": "work-life",
            "presets": ["productivity", "entertainment"],
            "description": "Work tools + entertainment for balanced professionals",
            "use_case": "Maintaining work-life balance",
        },
        {
            "name": "news-finance",
            "presets": ["news_media", "finance"],
            "description": "News outlets + financial information",
            "use_case": "Staying informed about world events and markets",
        },
        {
            "name": "cooking-productivity",
            "presets": ["cooking", "productivity"],
            "description": "Recipe sites + organization tools for food enthusiasts",
            "use_case": "Meal planning and recipe organization",
        },
        {
            "name": "shopping-news",
            "presets": ["shopping", "news_media"],
            "description": "Online shopping + news for consumer awareness",
            "use_case": "Informed shopping and consumer news",
        },
        {
            "name": "entertainment-news",
            "presets": ["entertainment", "news_media"],
            "description": "Streaming services + news outlets",
            "use_case": "Entertainment industry news and content",
        },
        {
            "name": "finance-productivity",
            "presets": ["finance", "productivity"],
            "description": "Investment tools + productivity apps",
            "use_case": "Personal finance management",
        },
    ]

    return {
        "status": "success",
        "count": len(suggestions),
        "suggestions": suggestions,
        "note": "Use these suggestions with create_portmanteau_profile() to create hybrid profiles",
    }
