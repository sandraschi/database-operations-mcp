## 1.6.0 - 2025-12-19

### Fixed
- **Database Analysis Tool Critical Fixes**:
  - Fixed SQL injection vulnerabilities in database analysis services (structure_analyzer, content_analyzer, error_detector)
  - Corrected PRAGMA syntax errors (removed invalid parentheses from PRAGMA statements)
  - Renamed `db_analysis` tool to `db_analyzer` to resolve FastMCP framework conflicts
  - Updated type annotations for better compatibility (Optional[str] instead of str | None)
  - Fixed table name quoting in SQL queries for security and correctness
- **MCP Tool Registration Issues**:
  - Resolved "near ")": syntax error" when calling db_analysis tool
  - Fixed "TypeError: 'FunctionTool' object is not callable" errors
  - Ensured all database analysis operations work correctly through MCP interface
  - Added comprehensive testing scripts for isolation and verification

### Changed
- **Tool Name Standardization**: Renamed `db_analysis` portmanteau tool to `db_analyzer` across all documentation and code
- **Documentation Updates**: Updated README.md, CHANGELOG.md, and STATUS_REPORT.md with current status
- **Code Quality**: Enhanced database query security and syntax correctness

### Added
- **Security Improvements**: Parameterized queries throughout database analysis services
- **Testing Infrastructure**: Multiple test scripts for verifying database analysis functionality
- **Error Handling**: Better error messages and validation in database operations

## 1.5.0 - 2025-01-27

### Changed
- **Phase 4 & 5 - Comprehensive Portmanteau Documentation**:
  - Enhanced all portmanteau tool docstrings to meet cursor rules standards
  - Added Prerequisites, detailed Parameters (format/examples/validation), Returns structure, Usage scenarios, Errors sections, See Also
  - Enhanced database tools: `db_connection`, `db_operations`, `db_schema`, `db_management`, `db_fts`, `db_analyzer`
  - Enhanced support tools: `help_system`, `media_library`, `windows_system`
  - Enhanced browser tools: `firefox_bookmarks`, `firefox_profiles`, `browser_bookmarks`, `chromium_portmanteau`
  - Enhanced remaining tools: `system_init`, `firefox_backup`, `firefox_curated`, `firefox_tagging`
- **Tool Consolidation Completion**:
  - All individual tools successfully consolidated into portmanteau tools
  - Deprecated modules marked with clear migration paths
  - Reduced tool count from 124+ individual tools to 23 portmanteau tools
- **README.md Updates**:
  - Updated tool overview to reflect portmanteau structure
  - Added deprecated tools section with migration paths
  - Clarified operations available in each portmanteau tool

### Fixed
- Fixed syntax error in `db_operations.py` (ternary expression in list comprehension)
- Fixed all line length linting errors in enhanced docstrings
- Resolved dependency conflict with `py-key-value-aio[disk]` (removed explicit requirement, managed by fastmcp)

### Added
- Comprehensive docstring sections following cursor rules:
  - Prerequisites for each operation type
  - Detailed parameter documentation with format, validation, ranges, examples
  - Complete Returns structure documentation
  - Usage scenarios and best practices
  - Common errors with cause/fix/workaround patterns
  - See Also cross-references

## 1.4.0 - 2025-10-30
- Add unified Chromium portmanteau tool (`chromium_bookmarks`) for list/add/edit/delete
- README: add Chromium portmanteau usage; version badge updated
- Ops: GitLab CE eval docs and Tailscale Serve/Funnel notes (non-code)

## 1.3.0 - 2025-10-30
- Add Chrome/Edge/Brave write tools and cross-browser sync writes
- Descriptive Firefox write failure errors ("error. firefox must be closed")
- README restructured: database first, bookmark tools second; badges on top
- Add MCPB package installation instructions; dual stdio/HTTP docs
- Ruff config updated; all lint checks pass
- Tests updated; all tests pass on Windows

# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased] - 2025-10-25

### Added
- Consolidated Firefox portmanteau tools for better organization
- Comprehensive portmanteau tools with extensive FastMCP 2.12 docstrings
- Standardized CI/CD workflows across all GitHub Actions

### Changed
- **Firefox Tools Consolidation**: Reduced from 6 separate tools to 2 comprehensive portmanteau tools
  - `firefox_bookmarks`: Consolidates all bookmark operations (bookmarks, tagging, curated, backup)
  - `firefox_profiles`: Consolidates all profile operations (profiles, utilities, system)
- **CI/CD Improvements**: 
  - Fixed test paths to use `tests/unit/` directory
  - Removed duplicate workflow files (`release-workflow.yml`, `build-and-release.yml`)
  - Standardized on `uv` package manager and Python 3.12
  - Fixed pytest availability issues in beta testing workflow
- **Tool Count**: Reduced from 15 to 11 comprehensive portmanteau tools
- Updated README to reflect new consolidated Firefox tools structure

### Fixed
- Pytest conflicts in beta testing workflow (test files no longer start MCP server)
- Removed redundant GitHub workflow files
- Test path standardization across all workflows
- Security workflow semgrep dependency handling

## [1.2.0] - 2025-10-15

### Added
- Comprehensive tool docstring standards and migration
- MCPB packaging system to replace obsolete DXT
- Firefox Portmanteau Tools & Dual Interface Support
- Complete CI/CD pipeline with modern GitHub Actions
- Enhanced documentation and testing frameworks

### Fixed
- CI/CD workflow failures resolved
- MCP Server Startup Issues & Firefox Database Access
- Import and dependency issues resolved
- Error handling and logging enhancements

### Changed
- Reorganized MCPB files into mcpb/ folder tree
- Updated CI workflows and build processes
- Improved code structure and organization

## [1.1.0] - 2025-01-15

### Added
- Comprehensive tool docstring standards and migration
- MCPB packaging system to replace obsolete DXT
- Firefox Portmanteau Tools & Dual Interface Support
- Complete CI/CD pipeline with modern GitHub Actions
- Enhanced documentation and testing frameworks

### Fixed
- CI/CD workflow failures resolved
- MCP Server Startup Issues & Firefox Database Access
- Import and dependency issues resolved
- Error handling and logging enhancements

### Changed
- Reorganized MCPB files into mcpb/ folder tree
- Updated CI workflows and build processes
- Improved code structure and organization

## [1.1.0] - 2025-01-15

### Added
- Gold Status achievement for Glama.ai integration
- Enhanced MCP server stability and performance

## [Unreleased]

## [1.0.0] - 2025-01-01

### Added
- Initial release with core database operations functionality
- Basic MCP server structure and tool registration
- Windows integration capabilities
- Documentation and setup instructions

---

**Repository**: database-operations-mcp
**Last Updated**: 2025-01-01
