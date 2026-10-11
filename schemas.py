from typing import List, Optional
from pydantic import BaseModel, Field


class CodeIssue(BaseModel):
    severity: str = Field(description="Severity level: Critical, Warning, or Info")
    issue_type: str = Field(
        description="Category of the bug or smell (e.g., Security, Performance, Logic Error, Style)"
    )
    line_number_approximate: Optional[int] = Field(
        description="Approximate line number in the diff where the issue occurs, if discernible"
    )
    description: str = Field(
        description="Clear explanation of why this code pattern is problematic"
    )


class RefactorSuggestion(BaseModel):
    title: str = Field(description="Short title for the refactoring action")
    improved_code: str = Field(
        description="The clean, refactored code snippet fixing the issue"
    )
    rationale: str = Field(description="Why this refactored approach is superior")


class CodeReviewReport(BaseModel):
    overall_health_score: int = Field(description="Code health score from 0 to 100")
    summary: str = Field(description="High-level assessment of the code diff or patch")
    issues: List[CodeIssue] = Field(
        description="List of detected bugs, code smells, or security vulnerabilities"
    )
    refactorings: List[RefactorSuggestion] = Field(
        description="Actionable refactoring suggestions with improved code snippets"
    )
