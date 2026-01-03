import json
import sys
from pathlib import Path
from typing import List, Optional

import pandas as pd
import pathspec
from complexipy import file_complexity
from fastmcp import FastMCP
from pydantic import BaseModel, Field


# --- Domain Models ---

class FunctionComplexityRecord(BaseModel):
    """
    Represents the complexity of a single function.
    """
    name: str = Field(..., description="Name of the function")
    complexity: int = Field(..., description="Cognitive complexity score")
    line_start: int = Field(..., description="Start line number")
    line_end: int = Field(..., description="End line number")


class ComplexityRecord(BaseModel):
    """
    Represents a single cognitive complexity scan result.
    """
    file_path: str = Field(..., description="Absolute or relative path to the analyzed file")
    complexity: int = Field(..., description="Cognitive complexity score")
    functions: List[FunctionComplexityRecord] = Field(default_factory=list, description="List of functions in the file")
    status: Optional[str] = Field(None, description="Status relative to threshold")
    
    class Config:
        populate_by_name = True


# --- Service Layer ---

class ComplexityScanner:
    """
    Service responsible for running complexity scans using the complexipy Python API.
    """
    
    def _load_gitignore(self, directory_path: Path) -> Optional[pathspec.PathSpec]:
        """
        Loads .gitignore patterns from the directory if it exists.
        """
        gitignore_path = directory_path / ".gitignore"
        if gitignore_path.exists():
            try:
                with open(gitignore_path, "r", encoding="utf-8") as f:
                    return pathspec.PathSpec.from_lines("gitwildmatch", f)
            except Exception as e:
                print(f"Error reading .gitignore: {e}", file=sys.stderr)
        return None
    
    def scan_file(self, file_path: str) -> Optional[ComplexityRecord]:
        """
        Scans a single file using complexipy.file_complexity.
        """
        try:
            # complexipy.file_complexity returns a FileComplexity object
            # which has a 'complexity' attribute and 'functions' list.
            result = file_complexity(file_path)
            
            functions = []
            if hasattr(result, 'functions') and result.functions:
                for func in result.functions:
                    functions.append(FunctionComplexityRecord(
                        name=func.name,
                        complexity=func.complexity,
                        line_start=func.line_start,
                        line_end=func.line_end
                    ))
            
            return ComplexityRecord(
                file_path=str(file_path),
                complexity=result.complexity,
                functions=functions
            )
        except Exception as e:
            # If complexipy fails (e.g. syntax error in target file), we skip it or log it.
            # For this MCP, we will skip to avoid breaking the batch.
            print(f"Error scanning {file_path}: {e}", file=sys.stderr)
            return None
    
    def scan_directory(self, directory_path: str) -> List[ComplexityRecord]:
        """
        Recursively scans a directory for .py files and calculates their complexity.
        Respects .gitignore if present.
        """
        records = []
        path_obj = Path(directory_path)
        
        # Load .gitignore spec
        spec = self._load_gitignore(path_obj)
        
        # Walk through the directory
        for file_path in path_obj.rglob("*.py"):
            # Check if file matches .gitignore patterns
            if spec:
                # pathspec expects relative paths
                try:
                    rel_path = file_path.relative_to(path_obj)
                    if spec.match_file(str(rel_path)):
                        continue
                except ValueError:
                    # Should not happen if file_path is from rglob of path_obj
                    pass
            
            record = self.scan_file(str(file_path))
            if record:
                records.append(record)
        
        return records
    
    def filter_results(self, records: List[ComplexityRecord], threshold: int) -> pd.DataFrame:
        """
        Filters the results based on the complexity threshold using pandas.
        """
        if not records:
            return pd.DataFrame(columns=["file_path", "complexity", "functions", "status"])
        
        data = [r.model_dump() for r in records]
        df = pd.DataFrame(data)
        
        # Ensure correct types
        df['complexity'] = pd.to_numeric(df['complexity'])
        
        # Filter
        filtered = df[df['complexity'] > threshold].copy()
        
        if not filtered.empty:
            filtered['status'] = 'exceeds_threshold'
            # Sort by complexity descending for better readability
            filtered = filtered.sort_values(by='complexity', ascending=False)
        
        return filtered


# --- MCP Server Setup ---

mcp = FastMCP("complexipy")
scanner = ComplexityScanner()


@mcp.tool()
def scan_directory(directory_path: str, threshold: int = 15) -> str:
    """
    Scans a directory for cognitive complexity and returns files exceeding the threshold.

    Args:
        directory_path: Absolute path to the directory to scan.
        threshold: Complexity threshold (default: 15).

    Returns:
        JSON string list of objects with 'file_path', 'complexity', 'functions', and 'status'.
    """
    path_obj = Path(directory_path)
    if not path_obj.exists() or not path_obj.is_dir():
        return json.dumps([{"error": f"Directory not found: {directory_path}"}])
    
    # Run scan
    records = scanner.scan_directory(str(path_obj.absolute()))
    
    # Filter and process
    filtered_df = scanner.filter_results(records, threshold)
    
    # Return JSON
    return filtered_df.to_json(orient="records")


@mcp.tool()
def scan_file(file_path: str, threshold: int = 15) -> str:
    """
    Scans a single file for cognitive complexity.

    Args:
        file_path: Absolute path to the file to scan.
        threshold: Complexity threshold (default: 15).

    Returns:
        JSON string list of objects with 'file_path', 'complexity', 'functions', and 'status'.
    """
    path_obj = Path(file_path)
    if not path_obj.exists() or not path_obj.is_file():
        return json.dumps([{"error": f"File not found: {file_path}"}])
    
    # Run scan
    record = scanner.scan_file(str(path_obj.absolute()))
    records = [record] if record else []
    
    # Filter and process
    filtered_df = scanner.filter_results(records, threshold)
    
    # Return JSON
    return filtered_df.to_json(orient="records")


def main():
    """Entry point for the MCP server."""
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
