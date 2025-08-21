"""
Base classes and utilities for the tool system.
"""
import asyncio
import inspect
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Callable, Type
from dataclasses import dataclass, field
from enum import Enum
import json


class ToolCategory(Enum):
    """Categories for organizing tools."""
    SEARCH = "search"
    COMPUTATION = "computation"
    FILE_OPERATIONS = "file_operations"
    DATA_ANALYSIS = "data_analysis"
    WEB_SCRAPING = "web_scraping"
    COMMUNICATION = "communication"
    SYSTEM = "system"
    CUSTOM = "custom"


@dataclass
class ToolParameter:
    """Represents a tool parameter."""
    name: str
    type: str
    description: str
    required: bool = True
    default: Any = None
    enum_values: Optional[List[str]] = None


@dataclass
class ToolResult:
    """Represents the result of a tool execution."""
    success: bool
    data: Any = None
    error: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "success": self.success,
            "data": self.data,
            "error": self.error,
            "metadata": self.metadata
        }


class BaseTool(ABC):
    """Abstract base class for all tools."""
    
    def __init__(self):
        self.name = self.__class__.__name__.lower().replace('tool', '')
        self.description = self.__doc__ or "No description available"
        self.category = ToolCategory.CUSTOM
        self.parameters = self._extract_parameters()
    
    @abstractmethod
    async def execute(self, **kwargs) -> ToolResult:
        """Execute the tool with given parameters."""
        pass
    
    def _extract_parameters(self) -> List[ToolParameter]:
        """Extract parameters from the execute method signature."""
        sig = inspect.signature(self.execute)
        parameters = []
        
        # Type mapping for OpenAI function calling schema
        type_mapping = {
            'int': 'integer',
            'float': 'number',
            'bool': 'boolean',
            'str': 'string',
            'list': 'array',
            'dict': 'object'
        }
        
        for param_name, param in sig.parameters.items():
            if param_name == 'kwargs':
                continue
                
            param_type = "string"  # default
            if param.annotation != inspect.Parameter.empty:
                # Handle typing constructs first (before checking __name__)
                if hasattr(param.annotation, '__origin__'):
                    origin = param.annotation.__origin__
                    if origin is list:
                        param_type = 'array'
                    elif origin is dict:
                        param_type = 'object'
                    elif hasattr(param.annotation, '__args__') and param.annotation.__args__:
                        # Handle Union types (including Optional which is Union[T, None])
                        args = param.annotation.__args__
                        # For Optional[T], get the first non-None type
                        for arg in args:
                            if arg is not type(None):
                                if hasattr(arg, '__name__'):
                                    raw_type = arg.__name__
                                    param_type = type_mapping.get(raw_type, 'string')
                                    break
                        else:
                            param_type = 'string'  # fallback if all args are None
                    else:
                        param_type = 'string'
                elif hasattr(param.annotation, '__name__'):
                    # Handle simple types like str, int, float, etc.
                    raw_type = param.annotation.__name__
                    param_type = type_mapping.get(raw_type, raw_type)
                else:
                    param_type = 'string'
            
            required = param.default == inspect.Parameter.empty
            default = None if required else param.default
            
            parameters.append(ToolParameter(
                name=param_name,
                type=param_type,
                description=f"Parameter {param_name}",
                required=required,
                default=default
            ))
        
        return parameters
    
    def to_function_schema(self) -> Dict[str, Any]:
        """Convert tool to OpenAI function calling schema."""
        properties = {}
        required = []
        
        for param in self.parameters:
            prop = {
                "type": param.type,
                "description": param.description
            }
            
            if param.enum_values:
                prop["enum"] = param.enum_values
            
            properties[param.name] = prop
            
            if param.required:
                required.append(param.name)
        
        schema = {
            "name": self.name,
            "description": self.description,
            "parameters": {
                "type": "object",
                "properties": properties,
            }
        }
        
        # ✅ Only include "required" if it's not empty
        if required:
            schema["parameters"]["required"] = required
        
        return schema
    
    def validate_parameters(self, **kwargs) -> Dict[str, Any]:
        """Validate and process parameters."""
        validated = {}
        
        for param in self.parameters:
            if param.name in kwargs:
                validated[param.name] = kwargs[param.name]
            elif param.required:
                raise ValueError(f"Required parameter '{param.name}' is missing")
            elif param.default is not None:
                validated[param.name] = param.default
        
        return validated


class ToolRegistry:
    """Registry for managing available tools."""
    
    def __init__(self):
        self.tools: Dict[str, BaseTool] = {}
        self.categories: Dict[ToolCategory, List[str]] = {
            category: [] for category in ToolCategory
        }
    
    def register(self, tool: BaseTool) -> None:
        """Register a tool."""
        self.tools[tool.name] = tool
        self.categories[tool.category].append(tool.name)
    
    def unregister(self, tool_name: str) -> None:
        """Unregister a tool."""
        if tool_name in self.tools:
            tool = self.tools[tool_name]
            self.categories[tool.category].remove(tool_name)
            del self.tools[tool_name]
    
    def get_tool(self, name: str) -> Optional[BaseTool]:
        """Get a tool by name."""
        return self.tools.get(name)
    
    def list_tools(self, category: Optional[ToolCategory] = None) -> List[str]:
        """List available tools, optionally filtered by category."""
        if category:
            return self.categories.get(category, [])
        return list(self.tools.keys())
    
    def get_tools_by_category(self, category: ToolCategory) -> List[BaseTool]:
        """Get all tools in a specific category."""
        return [self.tools[name] for name in self.categories[category]]
    
    def to_function_schemas(self) -> List[Dict[str, Any]]:
        """Convert all tools to OpenAI function calling schemas."""
        return [tool.to_function_schema() for tool in self.tools.values()]
    
    async def execute_tool(self, name: str, **kwargs) -> ToolResult:
        """Execute a tool by name."""
        tool = self.get_tool(name)
        if not tool:
            return ToolResult(
                success=False,
                error=f"Tool '{name}' not found"
            )
        
        try:
            validated_params = tool.validate_parameters(**kwargs)
            result = await tool.execute(**validated_params)
            return result
        except Exception as e:
            return ToolResult(
                success=False,
                error=f"Tool execution failed: {str(e)}"
            )


# Global tool registry
tool_registry = ToolRegistry()


def register_tool(tool_class: Type[BaseTool]) -> Type[BaseTool]:
    """Decorator to register a tool class."""
    tool_instance = tool_class()
    tool_registry.register(tool_instance)
    return tool_class


def get_tool_registry() -> ToolRegistry:
    """Get the global tool registry."""
    return tool_registry
