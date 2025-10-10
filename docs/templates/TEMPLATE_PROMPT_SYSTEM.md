# MCP Template Prompt System

## Overview

The MCP Template Prompt System provides a structured way to manage, document, and utilize prompt templates within MCP servers. This system addresses the challenge of making large collections of prompts discoverable and usable.

## Why This System?

1. **Discoverability**: Users can easily find available prompts
2. **Documentation**: Each prompt is self-documenting
3. **Consistency**: Standardized structure across all prompts
4. **Maintainability**: Easy to update and extend
5. **Integration**: Works seamlessly with MCP tools and commands

## Core Components

### 1. Template Registry

All prompts are defined in a central registry with this structure:

```python
PROMPT_TEMPLATES = {
    "category_name": {
        "description": "Description of this category",
        "templates": {
            "template_name": {
                "description": "What this prompt does",
                "parameters": {
                    "param_name": {
                        "type": "str|int|float|bool",
                        "description": "Parameter description",
                        "required": True,
                        "default": None,
                        "options": ["list", "of", "options"]  # Optional
                    }
                },
                "example": "Example usage",
                "tags": ["list", "of", "tags"]
            }
        }
    }
}
```

### 2. Available Commands

#### List Available Prompts
```
/show_template_prompts [category=] [search=] [format=markdown|json]
```

**Examples:**
```
# List all avatar control prompts
/show_template_prompts category=avatar_control

# Search for wave-related prompts
/show_template_prompts search=wave

# Get output as JSON
/show_template_prompts format=json
```

#### Generate Documentation
```
/generate_prompt_docs [output_format=markdown|html] [output_file=path/to/file]
```

**Examples:**
```
# Generate markdown docs in console
/generate_prompt_docs

# Save as HTML file
/generate_prompt_docs output_format=html output_file=prompts.html
```

### 3. Example Implementation

```python
# Example template definition
PROMPT_TEMPLATES = {
    "avatar_control": {
        "description": "Control avatar movements and expressions",
        "templates": {
            "happy_wave": {
                "description": "Make the avatar wave happily",
                "parameters": {
                    "intensity": {
                        "type": "int",
                        "range": "1-10",
                        "default": 5,
                        "description": "Enthusiasm level of the wave"
                    },
                    "duration": {
                        "type": "float",
                        "unit": "seconds",
                        "default": 2.0,
                        "description": "How long the wave should last"
                    }
                },
                "example": "make my avatar wave happily with high intensity",
                "tags": ["greeting", "happy", "wave"]
            },
            "nod_head": {
                "description": "Make the avatar nod in agreement",
                "parameters": {
                    "count": {
                        "type": "int",
                        "default": 1,
                        "min": 1,
                        "max": 5,
                        "description": "Number of nods"
                    },
                    "speed": {
                        "type": "str",
                        "default": "normal",
                        "options": ["slow", "normal", "fast"],
                        "description": "Speed of the nod"
                    }
                },
                "example": "nod your head twice quickly",
                "tags": ["gesture", "agreement"]
            }
        }
    }
}
```

## Implementation Details

### Template Registration

1. **Define Templates**: Add your prompt templates to the `PROMPT_TEMPLATES` dictionary
2. **Register Tools**: The system automatically registers the template commands
3. **Access in Code**: Use the template system to generate prompts dynamically

### Template Resolution

1. **Lookup**: Find template by category and name
2. **Validation**: Check required parameters
3. **Substitution**: Fill in template variables
4. **Formatting**: Apply any necessary formatting

## Best Practices

1. **Be Specific**: Use clear, descriptive names for templates and parameters
2. **Document Thoroughly**: Include examples and detailed descriptions
3. **Use Tags**: Add relevant tags for better searchability
4. **Version Control**: Include version information for templates
5. **Test Extensively**: Verify all templates work as expected

## Example Workflow

1. **Discover Available Prompts**
   ```
   /show_template_prompts category=avatar_control
   ```

2. **View Template Details**
   ```
   /show_template_prompts category=avatar_control search=wave
   ```

3. **Generate Documentation**
   ```
   /generate_prompt_docs output_format=markdown output_file=prompts.md
   ```

4. **Use in Code**
   ```python
   from mcp.templates import get_template
   
   # Get a template
   template = get_template("avatar_control", "happy_wave")
   
   # Generate prompt
   prompt = template.render(intensity=8, duration=1.5)
   ```

## Integration with MCP

The template system integrates with MCP's existing tool system, making it easy to expose templates as tools that can be called by the MCP client.

## Future Enhancements

1. **Templates Versioning**: Track changes to templates over time
2. **Template Validation**: Validate templates against schemas
3. **Template Testing**: Automated testing of templates
4. **Template Sharing**: Share templates between MCP instances
5. **Template Marketplace**: Discover and install community templates
