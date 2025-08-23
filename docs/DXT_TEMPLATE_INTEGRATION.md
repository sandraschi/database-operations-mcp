# DXT Template Integration Guide

## Overview

This document explains how DXT prompt templates integrate with the MCP Template Prompt System, providing a seamless way to manage and use templates across the platform.

## DXT Template Structure

DXT packages include prompt templates in the following structure:

```
dxt_package/
├── prompts/
│   ├── category1/
│   │   ├── template1.json
│   │   └── template2.json
│   └── category2/
│       └── template3.json
└── dxt.json
```

### Template File Format

Each template file (e.g., `template1.json`) follows this structure:

```json
{
  "name": "friendly_greeting",
  "description": "Generate a friendly greeting message",
  "version": "1.0.0",
  "parameters": {
    "name": {
      "type": "string",
      "description": "Name of the person to greet",
      "required": true
    },
    "time_of_day": {
      "type": "string",
      "enum": ["morning", "afternoon", "evening"],
      "default": "day"
    }
  },
  "template": "Hello {name}! Have a wonderful {time_of_day}!",
  "examples": [
    {
      "input": {"name": "Alice", "time_of_day": "morning"},
      "output": "Hello Alice! Have a wonderful morning!"
    }
  ]
}
```

## Integration with MCP Template System

### Automatic Discovery

DXT templates are automatically discovered and loaded when a DXT package is installed. They're integrated into the MCP template registry under their respective categories.

### Template Resolution Order

1. User-defined templates (highest priority)
2. DXT package templates (alphabetical by package name)
3. System templates (lowest priority)

### Using DXT Templates

#### List Available Templates
```
/show_template_prompts --source=dxt
```

#### Use a Specific Template
```python
from mcp.templates import get_dxt_template

template = get_dxt_template("package_name", "category", "template_name")
result = template.render(name="Alice", time_of_day="morning")
```

## Template Overrides

### Overriding DXT Templates

Create a template with the same category and name in your MCP server to override a DXT template:

```python
# In your MCP server code
@register_template("greetings", "friendly_greeting")
async def custom_greeting(name: str, time_of_day: str = "day"):
    return f"👋 Hey {name}! Hope you're having a great {time_of_day}!"
```

### Extending DXT Templates

```python
from mcp.templates import get_dxt_template

# Get the original template
original = get_dxt_template("greetings", "friendly_greeting")

# Create an enhanced version
@register_template("greetings", "enhanced_greeting")
async def enhanced_greeting(**kwargs):
    result = await original.render(**kwargs)
    return f"✨ {result} ✨"
```

## Best Practices

### For Template Consumers
1. Always check for template existence before use
2. Handle missing parameters gracefully
3. Cache template instances when possible
4. Validate template outputs

### For Template Authors
1. Use semantic versioning for templates
2. Document all parameters and their types
3. Include usage examples
4. Keep templates focused and reusable

## Example: Using DXT Templates in MCP Tools

```python
@tool("greet_user")
async def greet_user(name: str):
    """Greet a user using a template."""
    from mcp.templates import get_template
    
    try:
        template = get_template("greetings", "friendly_greeting")
        greeting = await template.render(name=name)
        return {"status": "success", "message": greeting}
    except Exception as e:
        return {"status": "error", "message": str(e)}
```

## Template Development

### Creating DXT-Compatible Templates

1. **Define Parameters**
   - Use clear, descriptive names
   - Specify types and constraints
   - Mark required parameters

2. **Write the Template**
   - Use f-string style placeholders
   - Keep it concise and focused
   - Include variables for all variable parts

3. **Add Examples**
   - Show common use cases
   - Demonstrate edge cases
   - Include expected outputs

### Testing Templates

```python
def test_template():
    template = load_template("greetings/friendly_greeting.json")
    result = template.render(name="Test", time_of_day="afternoon")
    assert "Test" in result
    assert "afternoon" in result
```

## Integration with Existing DXT Packages

### Available DXT Templates

| Package | Category | Template | Description |
|---------|----------|----------|-------------|
| dxt-core | system | status_check | Basic system status template |
| dxt-ai | chat | friendly_response | Friendly AI response template |
| dxt-ai | chat | technical_response | Technical AI response template |

### Example: Using dxt-ai Templates

```python
# Get a friendly AI response template
template = get_dxt_template("dxt-ai", "chat", "friendly_response")
response = await template.render(
    user_input="Hello!",
    context="casual conversation"
)
```

## Advanced Topics

### Template Inheritance

```json
{
  "name": "professional_greeting",
  "extends": "greetings/friendly_greeting",
  "template": "Dear {name},\n\n{_super_}\n\nBest regards,\nThe Team"
}
```

### Template Localization

```json
{
  "name": "greeting",
  "locales": {
    "en": "Hello {name}!",
    "es": "¡Hola {name}!",
    "fr": "Bonjour {name} !"
  }
}
```

## Troubleshooting

### Common Issues

1. **Template Not Found**
   - Verify the DXT package is installed
   - Check template path and name
   - Ensure proper file permissions

2. **Missing Parameters**
   - Check required parameters
   - Verify parameter names match exactly
   - Ensure all placeholders are defined

3. **Template Rendering Errors**
   - Check for syntax errors in templates
   - Validate parameter types
   - Review template inheritance

## Conclusion

This integration provides a powerful way to leverage DXT prompt templates within the MCP ecosystem, combining the flexibility of DXT packages with the robustness of the MCP template system.
