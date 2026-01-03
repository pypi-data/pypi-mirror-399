from pydantic import BaseModel, Field
from typing import List, Optional


class DumpsterConfig(BaseModel, extra="allow"):
    extensions: Optional[List[str]] = Field(
        default=None, description="List of file extensions to include in the dump"
    )

    contents: List[str] = Field(default=[], description="Patterns of files to include")
    exclude: List[str] = Field(default=[], description="Patterns of files to exclude")

    output: str = Field(default="sources.txt", description="Output file path")

    prompt: Optional[str] = Field(default=None, description="sources prompt")

    header: Optional[str] = Field(
        default=None, description="Header text to include at the top of the dump"
    )
    footer: Optional[str] = Field(
        default=None, description="Footer text to include at the bottom of the dump"
    )
