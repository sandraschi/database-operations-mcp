# database-operations-mcp (MCPB Bundle)

Comprehensive FastMCP 3.3 server for database operations (SQL, NoSQL, Vector) and system tools.

## Usage

Add to \claude_desktop_config.json\:
\\\json
{
  "mcpServers": {
    "database-operations-mcp": {
      "command": "uv",
      "args": ["run", "--directory", "\D:\Dev\repos", "python", "-m", "database_operations_mcp"],
      "env": { "PYTHONPATH": "\D:\Dev\repos/src" }
    }
  }
}
\\\

## Tools

- **health**: health
- **_shutdown**: _shutdown
- **_import_handlers**: _import_handlers
- **portmanteau_stdio**: portmanteau(stdio)
- **portmanteau_http**: portmanteau(http)
- **portmanteau_dual**: portmanteau(dual)
- **main_stdio**: main(stdio)
- **main_http**: main(http)
- **main_sse**: main(sse)
- **api_health**: api_health
- **api_capabilities**: api_capabilities
- **list_tools**: list_tools
- **call_tool_endpoint**: call_tool_endpoint
- **activity_feed**: activity_feed
- **activity_clear**: activity_clear
- **logs_query**: logs_query
- **logs_stats**: logs_stats
- **logs_export**: logs_export
- **logs_clear**: logs_clear
- **agentic_workflow_tool**: agentic_workflow_tool
- **safety_guard_status**: safety_guard_status
- **calibre_list_books**: calibre_list_books
- **calibre_get_book_details**: calibre_get_book_details
- **calibre_query**: calibre_query
- **postgresql**: Advanced open-source relational database
- **db_analyzer**: db_analyzer
- **list_supported_databases**: list_supported_databases
- **register_database_connection**: register_database_connection
- **list_database_connections**: list_database_connections
- **test_database_connection**: test_database_connection
- **test_all_database_connections**: test_all_database_connections
- **close_database_connection**: close_database_connection
- **get_database_connection_info**: get_database_connection_info
- **restore_saved_database_connections**: restore_saved_database_connections
- **set_active_database_connection**: set_active_database_connection
- **get_active_database_connection**: get_active_database_connection
- **get_database_user_preferences**: get_database_user_preferences
- **set_database_user_preferences**: set_database_user_preferences
- **execute_database_transaction**: execute_database_transaction
- **execute_database_write**: execute_database_write
- **batch_insert_records**: batch_insert_records
- **execute_database_query**: execute_database_query
- **quick_table_data_sample**: quick_table_data_sample
- **export_database_query_results**: export_database_query_results
- **db_fts**: db_fts
- **db_management**: db_management
- **db_operations_extended**: db_operations_extended
- **db_schema**: db_schema
- **help_system**: help_system
- **media_library**: media_library
- **Query Results**: Query Results
- **read_registry_value**: read_registry_value
- **write_registry_value**: write_registry_value
- **sqlite_inspect_db**: sqlite_inspect_db
- **sqlite_get_table_data**: sqlite_get_table_data
- **sqlite_get_table_schema**: sqlite_get_table_schema
- **system_init**: system_init
- **test_db_tool**: Test database tool.
- **windows_system**: windows_system
- **db_connection_clean**: db_connection_clean
- **db_operations_clean**: db_operations_clean
- **firefox_bookmarks_clean**: firefox_bookmarks_clean
- **help_clean**: help_clean
- **db_connection**: db_connection
- **db_operations**: db_operations
- **browser_bookmarks**: browser_bookmarks
- **firefox_profiles**: firefox_profiles
- **Alice**: Alice
- **Bob**: Bob

## Requirements

- Python 3.12+
- uv
