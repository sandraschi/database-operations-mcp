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
