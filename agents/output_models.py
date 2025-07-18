from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, Field


class TestScenario(BaseModel):
    scenario_name: str = Field(description="A brief title for the scenario.")
    given: str = Field(description="The initial context or preconditions for the scenario.")
    when: str = Field(description="The specific action or event that triggers the change in the scenario.")
    then: str = Field(description="The expected outcome or post-conditions after the action occurs.")


class TestCases(BaseModel):
    test_cases: List[TestScenario] = Field(description="A list of test scenarios in GIVEN/WHEN/THEN format.")


class GeneratedCode(BaseModel):
    filename: str = Field(description="The suggested filename for the generated code (e.g., 'main.py').")
    language: str = Field(description="The programming language of the generated code (e.g., 'python', 'java').")
    code: str = Field(description="The complete and executable source code.")
    explanation: str = Field(description="A brief explanation of the generated code and how to run it.")

class UpdateType(str, Enum):
    CREATE = "CREATE"
    UPDATE = "UPDATE"
    DELETE = "DELETE"

class FileUpdate(BaseModel):
    update_type: UpdateType = Field(..., description="The type of update to perform (CREATE, UPDATE, or DELETE).")
    file_path: str = Field(..., description="The path of the file to be updated.")
    content: Optional[str] = Field(..., description="The content of the file to be updated.")

class FileUpdateList(BaseModel):
    updates: List[FileUpdate] = Field(..., description="A list of file update operations.")