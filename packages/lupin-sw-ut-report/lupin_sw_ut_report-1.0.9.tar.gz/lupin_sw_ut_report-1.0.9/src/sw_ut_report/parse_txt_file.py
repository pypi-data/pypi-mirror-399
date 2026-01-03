import re
from typing import List, Tuple

from sw_ut_report.test_status import TestStatus
from sw_ut_report.unit_test_case_data import (
    AdditionalTest,
    Requirement,
    Step,
    StepBlock,
    SummaryRequirementsStatus,
    UnitTestCaseData,
)
from sw_ut_report.utils import remove_excess_space, apply_jama_prefix_replacement


def _clean_step_name(step_text: str) -> str:
    """
    Clean step name by removing status indicators (case-insensitive).

    Removes emoji + status (🟢 PASS, 🔴 FAIL, ⚪ SKIP) or status alone (PASS, FAIL, SKIP).

    Args:
        step_text: The step text to clean

    Returns:
        str: Cleaned step name without status indicators
    """
    return TestStatus.remove_from_text(step_text)


def _split_covers_line(line: str) -> List[str]:
    line = re.sub(r"Covers:\s*", "", line).strip()
    # Apply search and replace for Jama ID prefixes
    line = apply_jama_prefix_replacement(line)
    return re.findall(r"\[([^\]]+)\]", line)


def _parse_step(line: str, keyword: str) -> Step:
    """Parse a step line and extract label and status.

    Args:
        line: The step line (e.g., "Given: the software is running 🟢 PASS")
        keyword: The keyword ("given", "when", "then", "and")

    Returns:
        Step: Parsed step with keyword, label, and status
    """
    content = line.split(": ", 1)[1].strip() if ": " in line else line.strip()
    status = TestStatus.from_text(content)
    label = _clean_step_name(content)

    # Remove the keyword from the beginning of the label if present
    # (e.g., "Given software is running" -> "software is running")
    # This prevents duplication when _create_test_description adds "<strong>Given:</strong>" later
    keyword_lower = keyword.lower()
    keyword_capitalized = keyword.capitalize()
    if label.lower().startswith(keyword_lower + " "):
        label = label[len(keyword_capitalized) + 1:].strip()
    elif label.lower().startswith(keyword_lower):
        label = label[len(keyword_capitalized):].strip()

    return Step(keyword=keyword.capitalize(), label=label, status=status)


def _create_segments(lines: List[str]) -> List[List[str]]:
    """Create UnitTestCaseData segments from file lines."""
    segments = []
    current_segment = []
    i = 0

    while i < len(lines):
        line = lines[i].strip()

        # Check if this line is followed by "Covers:" (if not at the end)
        if i < len(lines) - 1:
            next_line = lines[i + 1].strip().lower()
        else:
            next_line = ""

        # Start a new UnitTestCaseData segment if line is not empty and followed by "Covers:"
        if line and next_line.startswith("covers:"):
            if current_segment:
                segments.append(current_segment)
            current_segment = [line, lines[i + 1].strip()]
            i += 2  # Skip both the scenario line and the covers line
        elif current_segment:
            # Add lines to current segment
            current_segment.append(line)
            i += 1
        else:
            i += 1

    # Add last segment if it exists
    if current_segment:
        segments.append(current_segment)

    return segments


def _process_segments(
    segments: List[List[str]], summary_requirements: SummaryRequirementsStatus
) -> List[UnitTestCaseData]:
    """Process each segment to create `UnitTestCaseData` instances.

    Args:
        segments (List[List[str]]): List of segments where each segment contains lines of a `UnitTestCaseData`.
        summary_requirements (SummaryRequirementsStatus): Summary of requirements status.

    Returns:
        List[UnitTestCaseData]: List of `UnitTestCaseData` instances."""
    test_cases = []

    for segment in segments:
        # The first two lines of the segment are scenario and covers line
        scenario_line = segment[0].strip()
        covers_line = segment[1].strip()

        # Extract status and clean scenario name
        scenario_status = TestStatus.from_text(scenario_line)
        scenario = UnitTestCaseData.clean_test_name(scenario_line)

        current_case = UnitTestCaseData(
            scenario=scenario,
            scenario_status=scenario_status,
            requirements_covers=[],
            step_blocks=[],
            additional_tests=[],
        )

        # Extract requirements from the covers line
        split_requirements = _split_covers_line(covers_line)
        current_case.requirements_covers.extend(
            Requirement(req, TestStatus.UNKNOWN) for req in split_requirements
        )

        # Extract `Given`, `When`, `Then` and `And` steps
        current_block = StepBlock()
        for line in segment[2:]:
            cleaned_line = line.strip().lower()

            if cleaned_line.startswith("given:"):
                # Finalize previous block if it has content
                if current_block.given or current_block.when or current_block.then or current_block.and_steps:
                    current_case.step_blocks.append(current_block)
                # Start new block
                current_block = StepBlock()
                current_block.given = _parse_step(line, "given")

            elif cleaned_line.startswith("when:"):
                current_block.when = _parse_step(line, "when")

            elif cleaned_line.startswith("then:"):
                current_block.then = _parse_step(line, "then")

            elif cleaned_line.startswith("and:"):
                current_block.and_steps.append(_parse_step(line, "and"))

            elif cleaned_line and not cleaned_line.startswith("covers:"):
                # Add additional tests lines who are not empty and not starts with "Covers:"
                detected_status = TestStatus.from_text(line)
                cleaned_label = _clean_step_name(line.strip())
                current_case.additional_tests.append(AdditionalTest(
                    label=cleaned_label,
                    status=detected_status
                ))

        # Finalize last block if it has content
        if current_block.given or current_block.when or current_block.then or current_block.and_steps:
            current_case.step_blocks.append(current_block)

        current_case.update_requirements_status(summary_requirements)
        test_cases.append(current_case)

    return test_cases


def generate_test_cases(
    file_content: str, summary: SummaryRequirementsStatus
) -> Tuple[List[UnitTestCaseData], SummaryRequirementsStatus]:
    lines = file_content.splitlines()
    lines = [remove_excess_space(line) for line in lines]

    segments = _create_segments(lines)

    test_cases = _process_segments(segments, summary)

    return test_cases, summary
