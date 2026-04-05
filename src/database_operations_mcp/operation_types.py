"""Literal aliases for portmanteau `operation` parameters (schema-friendly enums)."""

from __future__ import annotations

from typing import Literal

DbConnectionOperation = Literal[
    "list_supported",
    "register",
    "init",
    "list",
    "test",
    "test_all",
    "close",
    "get_info",
    "restore",
    "set_active",
    "get_active",
    "get_preferences",
    "set_preferences",
]

DbOperationsOperation = Literal[
    "execute_transaction",
    "execute_write",
    "batch_insert",
    "execute_query",
    "quick_data_sample",
    "export_query_results",
]

DbSchemaOperation = Literal[
    "list_databases",
    "list_tables",
    "describe_table",
    "get_schema_diff",
]

DbManagementOperation = Literal[
    "init_database",
    "list_connections",
    "close_connection",
    "test_connection",
    "get_connection_info",
    "database_health_check",
    "get_database_metrics",
    "vacuum_database",
    "disconnect_database",
]

DbFtsOperation = Literal["fts_search", "fts_tables", "fts_suggest"]

DbAnalyzerOperation = Literal["structure", "analyze", "content", "health", "errors", "report"]

DbOperationsExtendedOperation = Literal[
    "execute_query",
    "execute_non_query",
    "get_tables",
    "get_table_structure",
    "health_check",
    "get_keys",
    "get_value",
    "set_value",
]

HelpSystemOperation = Literal[
    "help",
    "tool_help",
    "list_categories",
    "search_help",
    "get_tool_examples",
    "get_parameter_info",
    "format_help_output",
]

MediaLibraryOperation = Literal[
    "search_calibre_library",
    "get_calibre_book_metadata",
    "search_calibre_fts",
    "search_calibre_fts_db",
    "find_plex_database",
    "optimize_plex_database",
    "export_database_schema",
    "get_plex_library_stats",
    "manage_plex_metadata",
    "get_plex_library_sections",
]

WindowsSystemOperation = Literal[
    "list_windows_databases",
    "query_windows_database",
    "clean_windows_database",
    "read_registry_value",
    "write_registry_value",
    "list_registry_keys",
    "list_registry_values",
    "monitor_registry",
    "delete_registry_value",
    "delete_registry_key",
    "registry_key_exists",
]

ChromeProfilesOperation = Literal[
    "get_chrome_profiles",
    "get_profile_info",
    "validate_profile",
    "is_chrome_running",
    "get_profile_directory",
    "get_bookmarks_db_path",
    "get_chrome_platform",
    "get_database_info",
    "check_chrome_status",
    "backup_profile",
    "restore_profile",
    "create_profile",
    "delete_profile",
    "switch_profile",
]

FirefoxProfilesOperation = Literal[
    "get_firefox_profiles",
    "create_firefox_profile",
    "delete_firefox_profile",
    "create_loaded_profile",
    "create_portmanteau_profile",
    "suggest_portmanteau_profiles",
    "create_loaded_profile_from_preset",
    "check_firefox_status",
]

FirefoxCuratedOperation = Literal[
    "get_curated_source",
    "list_curated_sources",
    "list_curated_bookmark_sources",
]

BrowserBookmarkOperation = Literal[
    "list_bookmarks",
    "get_bookmark",
    "add_bookmark",
    "edit_bookmark",
    "delete_bookmark",
    "search",
    "search_bookmarks",
    "sync_bookmarks",
    "find_duplicates",
    "export_bookmarks",
    "batch_update_tags",
    "remove_unused_tags",
    "list_tags",
    "find_similar_tags",
    "merge_tags",
    "clean_up_tags",
    "find_old_bookmarks",
    "find_forgotten_bookmarks",
    "refresh_bookmarks",
    "get_bookmark_stats",
    "find_broken_links",
]
