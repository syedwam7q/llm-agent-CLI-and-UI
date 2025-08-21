"""
Data analysis and processing tools.
"""
import pandas as pd
import numpy as np
import json
from typing import Dict, Any, List, Optional
from pathlib import Path
import matplotlib.pyplot as plt
import seaborn as sns
import io
import base64

import sys
from pathlib import Path

# Ensure proper path setup
current_dir = Path(__file__).parent
src_dir = current_dir.parent
sys.path.insert(0, str(src_dir))
sys.path.insert(0, str(current_dir))

from base import BaseTool, ToolResult, ToolCategory, register_tool
from config import settings
from utils.file_utils import find_file


@register_tool
class DataAnalysisTool(BaseTool):
    """Analyze data from CSV files or JSON data."""
    
    def __init__(self):
        super().__init__()
        self.category = ToolCategory.DATA_ANALYSIS
        self.description = "Analyze data from CSV files or structured data"
    
    async def execute(self, data_source: str, analysis_type: str = "summary") -> ToolResult:
        """Execute data analysis."""
        try:
            # Load data
            if data_source.endswith('.csv'):
                path = find_file(data_source)
                if not path:
                    return ToolResult(
                        success=False,
                        error=f"File not found: {data_source} (searched in uploads/, data/, and project directories)"
                    )
                df = pd.read_csv(path)
            elif data_source.endswith('.json'):
                path = find_file(data_source)
                if not path:
                    return ToolResult(
                        success=False,
                        error=f"File not found: {data_source} (searched in uploads/, data/, and project directories)"
                    )
                with open(path, 'r') as f:
                    data = json.load(f)
                
                # Handle different JSON structures
                metadata = {}
                if isinstance(data, list):
                    df = pd.DataFrame(data)
                elif isinstance(data, dict):
                    # If it's a dict with a list inside, try to find the main data
                    list_keys = [k for k, v in data.items() if isinstance(v, list)]
                    if list_keys:
                        # Use the first list found as the main data
                        main_key = list_keys[0]
                        df = pd.DataFrame(data[main_key])
                        # Store metadata for later use
                        metadata = {k: v for k, v in data.items() if k != main_key}
                    else:
                        # Convert dict to single-row DataFrame
                        df = pd.DataFrame([data])
                else:
                    return ToolResult(
                        success=False,
                        error="JSON data must be a list or dictionary"
                    )
            else:
                # Try to parse as JSON string
                try:
                    data = json.loads(data_source)
                    metadata = {}
                    if isinstance(data, list):
                        df = pd.DataFrame(data)
                    elif isinstance(data, dict):
                        list_keys = [k for k, v in data.items() if isinstance(v, list)]
                        if list_keys:
                            main_key = list_keys[0]
                            df = pd.DataFrame(data[main_key])
                            metadata = {k: v for k, v in data.items() if k != main_key}
                        else:
                            df = pd.DataFrame([data])
                    else:
                        df = pd.DataFrame([data])
                except:
                    return ToolResult(
                        success=False,
                        error="Invalid data source format"
                    )
            
            result_data = {
                "shape": df.shape,
                "columns": df.columns.tolist(),
                "dtypes": df.dtypes.to_dict()
            }
            
            # Add metadata if available
            if 'metadata' in locals() and metadata:
                result_data["file_metadata"] = metadata
            
            if analysis_type == "summary":
                result_data["summary"] = df.describe().to_dict()
                result_data["null_counts"] = df.isnull().sum().to_dict()
                
            elif analysis_type == "correlation":
                numeric_df = df.select_dtypes(include=[np.number])
                if not numeric_df.empty:
                    result_data["correlation"] = numeric_df.corr().to_dict()
                else:
                    result_data["error"] = "No numeric columns for correlation"
            
            elif analysis_type == "head":
                result_data["head"] = df.head(10).to_dict('records')
            
            elif analysis_type == "info":
                buffer = io.StringIO()
                df.info(buf=buffer)
                result_data["info"] = buffer.getvalue()
            
            return ToolResult(
                success=True,
                data=result_data,
                metadata={"analysis_type": analysis_type}
            )
        
        except Exception as e:
            return ToolResult(
                success=False,
                error=f"Data analysis failed: {str(e)}"
            )


@register_tool
class DataVisualizationTool(BaseTool):
    """Create visualizations from data."""
    
    def __init__(self):
        super().__init__()
        self.category = ToolCategory.DATA_ANALYSIS
        self.description = "Create charts and visualizations from data"
    
    async def execute(
        self, 
        data_source: str, 
        chart_type: str = "histogram",
        x_column: Optional[str] = None,
        y_column: Optional[str] = None
    ) -> ToolResult:
        """Execute data visualization."""
        try:
            # Load data (similar to DataAnalysisTool)
            if data_source.endswith('.csv'):
                path = find_file(data_source)
                if not path:
                    return ToolResult(
                        success=False,
                        error=f"File not found: {data_source} (searched in uploads/, data/, and project directories)"
                    )
                df = pd.read_csv(path)
            elif data_source.endswith('.json'):
                path = find_file(data_source)
                if not path:
                    return ToolResult(
                        success=False,
                        error=f"File not found: {data_source} (searched in uploads/, data/, and project directories)"
                    )
                with open(path, 'r') as f:
                    data = json.load(f)
                df = pd.DataFrame(data)
            else:
                try:
                    data = json.loads(data_source)
                    df = pd.DataFrame(data)
                except:
                    return ToolResult(
                        success=False,
                        error="Invalid data source format"
                    )
            
            plt.figure(figsize=(10, 6))
            
            if chart_type == "histogram":
                if x_column and x_column in df.columns:
                    plt.hist(df[x_column].dropna(), bins=20)
                    plt.xlabel(x_column)
                else:
                    # Use first numeric column
                    numeric_cols = df.select_dtypes(include=[np.number]).columns
                    if len(numeric_cols) > 0:
                        plt.hist(df[numeric_cols[0]].dropna(), bins=20)
                        plt.xlabel(numeric_cols[0])
                    else:
                        return ToolResult(
                            success=False,
                            error="No numeric columns found for histogram"
                        )
                plt.ylabel("Frequency")
                plt.title(f"Histogram of {x_column or numeric_cols[0]}")
            
            elif chart_type == "scatter":
                if x_column and y_column and x_column in df.columns and y_column in df.columns:
                    plt.scatter(df[x_column], df[y_column])
                    plt.xlabel(x_column)
                    plt.ylabel(y_column)
                    plt.title(f"Scatter plot: {x_column} vs {y_column}")
                else:
                    numeric_cols = df.select_dtypes(include=[np.number]).columns
                    if len(numeric_cols) >= 2:
                        plt.scatter(df[numeric_cols[0]], df[numeric_cols[1]])
                        plt.xlabel(numeric_cols[0])
                        plt.ylabel(numeric_cols[1])
                        plt.title(f"Scatter plot: {numeric_cols[0]} vs {numeric_cols[1]}")
                    else:
                        return ToolResult(
                            success=False,
                            error="Need at least 2 numeric columns for scatter plot"
                        )
            
            elif chart_type == "bar":
                if x_column and x_column in df.columns:
                    value_counts = df[x_column].value_counts().head(10)
                    plt.bar(range(len(value_counts)), value_counts.values)
                    plt.xticks(range(len(value_counts)), value_counts.index, rotation=45)
                    plt.xlabel(x_column)
                    plt.ylabel("Count")
                    plt.title(f"Bar chart of {x_column}")
                else:
                    return ToolResult(
                        success=False,
                        error="Need to specify x_column for bar chart"
                    )
            
            plt.tight_layout()
            
            # Save plot to base64 string
            buffer = io.BytesIO()
            plt.savefig(buffer, format='png', dpi=150, bbox_inches='tight')
            buffer.seek(0)
            image_base64 = base64.b64encode(buffer.getvalue()).decode()
            plt.close()
            
            return ToolResult(
                success=True,
                data={
                    "chart_type": chart_type,
                    "image_base64": image_base64,
                    "columns_used": {
                        "x_column": x_column,
                        "y_column": y_column
                    }
                },
                metadata={"format": "png"}
            )
        
        except Exception as e:
            return ToolResult(
                success=False,
                error=f"Data visualization failed: {str(e)}"
            )


@register_tool
class JSONProcessorTool(BaseTool):
    """Process and manipulate JSON data."""
    
    def __init__(self):
        super().__init__()
        self.category = ToolCategory.DATA_ANALYSIS
        self.description = "Process, filter, and manipulate JSON data"
    
    async def execute(
        self, 
        json_data: str, 
        operation: str = "pretty_print",
        filter_key: Optional[str] = None,
        filter_value: Optional[str] = None
    ) -> ToolResult:
        """Execute JSON processing."""
        try:
            # Parse JSON
            data = json.loads(json_data)
            
            if operation == "pretty_print":
                result = json.dumps(data, indent=2, ensure_ascii=False)
                
            elif operation == "keys":
                if isinstance(data, dict):
                    result = list(data.keys())
                elif isinstance(data, list) and len(data) > 0 and isinstance(data[0], dict):
                    result = list(data[0].keys())
                else:
                    result = "Data is not a dictionary or list of dictionaries"
            
            elif operation == "filter":
                if not filter_key:
                    return ToolResult(
                        success=False,
                        error="filter_key is required for filter operation"
                    )
                
                if isinstance(data, list):
                    if filter_value:
                        result = [item for item in data if item.get(filter_key) == filter_value]
                    else:
                        result = [item for item in data if filter_key in item]
                elif isinstance(data, dict):
                    if filter_key in data:
                        result = {filter_key: data[filter_key]}
                    else:
                        result = {}
                else:
                    result = "Cannot filter this data type"
            
            elif operation == "count":
                if isinstance(data, list):
                    result = len(data)
                elif isinstance(data, dict):
                    result = len(data.keys())
                else:
                    result = 1
            
            elif operation == "flatten":
                if isinstance(data, list):
                    result = []
                    for item in data:
                        if isinstance(item, dict):
                            for key, value in item.items():
                                result.append({"key": key, "value": value})
                        else:
                            result.append({"value": item})
                else:
                    result = "Cannot flatten non-list data"
            
            else:
                return ToolResult(
                    success=False,
                    error=f"Unknown operation: {operation}"
                )
            
            return ToolResult(
                success=True,
                data={
                    "operation": operation,
                    "result": result,
                    "original_type": type(data).__name__
                }
            )
        
        except json.JSONDecodeError as e:
            return ToolResult(
                success=False,
                error=f"Invalid JSON: {str(e)}"
            )
        except Exception as e:
            return ToolResult(
                success=False,
                error=f"JSON processing failed: {str(e)}"
            )