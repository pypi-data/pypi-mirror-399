"""
Data models for AxMath API client.
"""

from typing import List, Optional
from pydantic import BaseModel, Field


class VerificationDetails(BaseModel):
    """LEAN verification details."""

    errors: List[str] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)
    sorry_count: int = 0
    exit_code: int = 0
    compilation_time: float = 0.0


class Premise(BaseModel):
    """Mathlib premise search result."""

    full_name: str
    statement: str
    similarity: float
    file_path: Optional[str] = None


class ProveResult(BaseModel):
    """Result from prove_theorem API call."""

    verified: bool
    lean_code: str
    iterations: int
    total_time: float
    premises_used: List[str] = Field(default_factory=list)
    verification_details: VerificationDetails


class SearchResult(BaseModel):
    """Result from search_premises API call."""

    count: int
    search_method: str
    premises: List[Premise]
    search_time: float = 0.0


class TaskResult(BaseModel):
    """Result from individual task in multi-agent solve."""

    task_type: str
    agent: str
    success: bool
    output: str
    execution_time: float


class SolveResult(BaseModel):
    """Result from solve_problem API call."""

    success: bool
    synthesis: str
    execution_time: float
    task_results: List[TaskResult] = Field(default_factory=list)
