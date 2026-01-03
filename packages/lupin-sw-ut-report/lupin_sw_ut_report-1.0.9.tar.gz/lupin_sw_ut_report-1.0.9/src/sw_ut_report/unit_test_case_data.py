import re
from dataclasses import dataclass, field
from typing import List, Optional

from sw_ut_report.test_status import TestStatus


@dataclass
class Requirement:
    id: str
    status: TestStatus


@dataclass
class AdditionalTest:
    """Represents an additional test line with its status."""
    label: str  # Test label (without status)
    status: TestStatus  # Normalized status


@dataclass
class Step:
    """Represents a single step (Given, When, Then, or And) with its status."""
    keyword: str  # "Given", "When", "Then", "And"
    label: str  # Step label (without status)
    status: TestStatus  # Normalized status


@dataclass
class StepBlock:
    """Represents a block of steps (Given-When-Then) with optional And steps."""
    given: Optional[Step] = None
    when: Optional[Step] = None
    then: Optional[Step] = None
    and_steps: List[Step] = field(default_factory=list)  # For "And:" steps


@dataclass
class SummaryRequirementsStatus:
    summary: List[Requirement] = field(default_factory=list)

    def __post_init__(self):
        self._requirements_dict = {req.id: req for req in self.summary}

    def add_requirement(self, new_requirement: Requirement):
        existing_requirement = self._requirements_dict.get(new_requirement.id)

        if existing_requirement:
            if existing_requirement.status == TestStatus.PASSED and new_requirement.status == TestStatus.FAILED:
                existing_requirement.status = TestStatus.FAILED
        else:
            self.summary.append(new_requirement)
            self._requirements_dict[new_requirement.id] = new_requirement

    def sort_summary(self):
        def sort_key(req: Requirement):
            match = re.search(r"(\d+)$", req.id)
            number = int(match.group(1)) if match else float("inf")
            return (req.id[: match.start()] if match else req.id, number)

        self.summary.sort(key=sort_key)


@dataclass
class UnitTestCaseData:
    scenario: str
    scenario_status: TestStatus
    requirements_covers: List[Requirement]
    step_blocks: List[StepBlock] = field(default_factory=list)
    additional_tests: List[AdditionalTest] = field(default_factory=list)

    @staticmethod
    def clean_test_name(test_name: str) -> str:
        """
        Clean test name by removing prefixes and status indicators.

        Removes:
        - "Test case: " prefix
        - "Scenario: " prefix
        - Status indicators (emoji + status text)

        This method is used both during parsing and for normalizing names from Jama.

        Args:
            test_name: The raw test name

        Returns:
            str: Cleaned test name without prefixes and status
        """
        # Remove "Test case: " prefix if present
        cleaned = test_name
        if cleaned.startswith("Test case: "):
            cleaned = cleaned[11:]  # Remove "Test case: "

        # Remove "Scenario: " prefix if present
        if cleaned.startswith("Scenario: "):
            cleaned = cleaned[10:]  # Remove "Scenario: "

        # Remove status indicators
        cleaned = TestStatus.remove_from_text(cleaned)

        # Strip whitespace
        cleaned = cleaned.strip()

        return cleaned

    def update_requirements_status(
        self, summary_requirements: SummaryRequirementsStatus
    ):
        for requirement in self.requirements_covers:
            requirement.status = self.scenario_status
            summary_requirements.add_requirement(requirement)

    def get_covers_list(self) -> List[str]:
        """Get list of requirement IDs."""
        return [req.id for req in self.requirements_covers]

    def get_test_case_name(self) -> str:
        """Get test case name."""
        return self.scenario

    def has_raw_lines(self) -> bool:
        """Check if this scenario has raw lines (for unstructured scenarios)."""
        return False  # UnitTestCaseData doesn't have raw lines

    def get_steps(self) -> List[dict]:
        """Convert step_blocks to steps format expected by other modules."""
        steps = []
        for block in self.step_blocks:
            step = {}
            if block.given:
                step['given'] = f"{block.given.label} {block.given.status.to_display_symbol()}"
            if block.when:
                step['when'] = f"{block.when.label} {block.when.status.to_display_symbol()}"
            if block.then:
                step['then'] = f"{block.then.label} {block.then.status.to_display_symbol()}"
            if step:  # Only add if step has content
                steps.append(step)
        return steps

    def has_test_case(self) -> bool:
        """Check if this scenario has a test case (structured scenario)."""
        return True  # UnitTestCaseData always has a test case (scenario)

    def has_steps(self) -> bool:
        """Check if this scenario has steps."""
        return len(self.step_blocks) > 0