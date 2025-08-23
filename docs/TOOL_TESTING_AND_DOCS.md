# MCP Tool Testing and Documentation System

## Overview

This document outlines our approach to testing MCP tools and generating comprehensive documentation automatically. These systems work together to ensure tool reliability and usability.

## 1. Tool Testing Framework

### Why Test Tools?

1. **Reliability**: Ensure tools work as expected
2. **Regression Prevention**: Catch breaking changes early
3. **Documentation**: Tests serve as living documentation
4. **Quality**: Maintain high standards across all tools

### Test Commands

#### Test a Specific Tool
```
/test_tool tool_name [--verbose] [--params '{"param1": "value1"}']
```

**Examples:**
```
# Basic test
/test_tool do_cartwheels

# With custom parameters
/test_tool serve_coffee --params '{"size": "large", "temperature": "hot"}'

# Verbose output
/test_tool make_sandwich --verbose
```

#### Test All Tools
```
/test_all_tools [--category=category_name] [--parallel]
```

**Examples:**
```
# Test all tools
/test_all_tools

# Test tools in a specific category
/test_all_tools --category=kitchen

# Run tests in parallel (faster)
/test_all_tools --parallel
```

### Test Definition

Tests are defined alongside tool definitions:

```python
@tool("do_cartwheels")
async def do_cartwheels(count: int = 1) -> dict:
    """Perform cartwheels.
    
    Args:
        count: Number of cartwheels to perform (1-10)
        
    Returns:
        dict: Result with cartwheel count and success status
    """
    return {"cartwheels_done": min(max(1, count), 10), "status": "success"}

# Test cases for the tool
do_cartwheels.tests = [
    {
        "name": "single_cartwheel",
        "params": {"count": 1},
        "validate": lambda r: r["cartwheels_done"] == 1
    },
    {
        "name": "multiple_cartwheels",
        "params": {"count": 3},
        "validate": lambda r: r["cartwheels_done"] == 3
    },
    {
        "name": "boundary_check",
        "params": {"count": 15},  # Should be limited to 10
        "validate": lambda r: r["cartwheels_done"] == 10
    }
]
```

## 2. Documentation Generation

### Why Auto-Generated Docs?

1. **Accuracy**: Always up-to-date with the code
2. **Consistency**: Uniform documentation style
3. **Efficiency**: No manual doc updates needed
4. **Completeness**: Automatic coverage of all tools

### Documentation Commands

#### Generate HTML Documentation
```
/make_docs --format=html [--output=docs/] [--theme=light|dark]
```

#### Generate Markdown Documentation
```
/make_docs --format=markdown [--output=README.md]
```

### Documentation Features

1. **Tool Signatures**: Auto-generated from function definitions
2. **Examples**: Pulled from test cases
3. **Parameter Details**: Types, defaults, and constraints
4. **Error Cases**: Documented error conditions
5. **Usage Examples**: Real-world examples

### Example Output Structure

```markdown
# Tool Documentation

## Category: Movement

### do_cartwheels

Perform cartwheels.

**Signature:**
```python
async def do_cartwheels(count: int = 1) -> dict
```

**Parameters:**
- `count` (int, default=1): Number of cartwheels to perform (1-10)

**Returns:**
- dict: Contains 'cartwheels_done' and 'status' keys

**Examples:**
```python
# Single cartwheel
result = await do_cartwheels(1)

# Multiple cartwheels
result = await do_cartwheels(3)
```

**Test Cases:**
1. single_cartwheel: PASS
2. multiple_cartwheels: PASS
3. boundary_check: PASS
```

## 3. Implementation Details

### Test Runner Features

1. **Isolated Testing**: Each test runs in a clean environment
2. **Parallel Execution**: Speed up test suites
3. **Test Discovery**: Automatically find and run tests
4. **Result Reporting**: Detailed pass/fail information
5. **Performance Metrics**: Track test execution time

### Documentation Generator Features

1. **Multiple Formats**: HTML, Markdown, JSON output
2. **Theming Support**: Customizable appearance
3. **Search Functionality**: Full-text search in HTML output
4. **Cross-References**: Links between related tools
5. **Versioning**: Document different tool versions

## 4. Best Practices

### Writing Good Tests

1. **Test Edge Cases**: Include boundary conditions
2. **Keep Tests Focused**: One assertion per test case
3. **Use Descriptive Names**: Clearly indicate test purpose
4. **Mock External Dependencies**: Keep tests fast and reliable
5. **Document Test Assumptions**: Explain non-obvious test logic

### Maintaining Documentation

1. **Update with Code Changes**: Keep docs in sync
2. **Add Examples**: Show common use cases
3. **Document Limitations**: Be clear about edge cases
4. **Include Error Cases**: Document how failures are handled
5. **Keep It Concise**: Focus on useful information

## 5. Example Workflow

1. **Development**
   ```bash
   # Write tool and tests
   # Test locally
   /test_tool my_new_tool
   ```

2. **Documentation**
   ```bash
   # Generate docs
   /make_docs --format=html --output=docs/
   ```

3. **CI/CD Integration**
   ```yaml
   # .github/workflows/test.yml
   jobs:
     test:
       runs-on: ubuntu-latest
       steps:
         - uses: actions/checkout@v2
         - run: /test_all_tools --parallel
         - run: /make_docs --format=markdown --output=README.md
   ```

## 6. Integration with MCP

Both systems integrate seamlessly with MCP's existing tool system, providing:

1. **Automatic Discovery**: Tools are automatically included in testing
2. **Unified Interface**: Consistent commands across all MCP instances
3. **Extensible**: Easy to add new test types or doc formats
4. **Pluggable Architecture**: Replace components as needed
