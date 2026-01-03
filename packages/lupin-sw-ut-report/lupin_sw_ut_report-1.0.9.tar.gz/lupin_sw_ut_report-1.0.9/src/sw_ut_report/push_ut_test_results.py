"""
Push UT Test Results to Jama - Processes UT test results and updates Jama test runs.

This module handles the complete workflow for pushing UT test results to Jama:
1. Find test plan by version
2. Find UT test group containing UT-1
3. Create test cycle with UT group
4. Parse txt files for test results and status
5. Update test runs with results
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple

from sw_ut_report.jama_common import (
    JamaUTManager, JamaConnectionError, JamaValidationError,
    validate_environment, clean_log_message, find_test_plan_by_version_and_prefix,
    find_test_group_containing_case, create_filtered_test_cycle_with_group,
    update_test_run_status, get_test_runs_from_cycle, is_jama_ut_id,
    draw_table
)
from sw_ut_report.parse_txt_file import SummaryRequirementsStatus, generate_test_cases, _clean_step_name
from sw_ut_report.config import GlobalConfig
from sw_ut_report.test_status import TestStatus


def extract_status_from_raw_lines(raw_lines: List[str]) -> Tuple[str, str]:
    """
    Extract status and description from raw lines of a test result.

    Args:
        raw_lines: List of raw lines from the test result

    Returns:
        Tuple[str, str]: (status, description)
    """
    status = TestStatus.UNKNOWN.to_short_form()
    description_lines = []
    step_results = []

    for line in raw_lines:
        clean_line = line.strip()
        if not clean_line:
            continue

        # Check for status indicators (case-insensitive)
        detected_status = TestStatus.from_text(clean_line)
        # Normalize to simple status format (PASS, FAIL) for overall status
        if detected_status != TestStatus.UNKNOWN:
            status = detected_status.to_short_form()

        # Collect description lines (skip covers lines)
        if not clean_line.lower().startswith("covers:"):
            description_lines.append(clean_line)

        # Extract step results (Given-When-Then)
        if any(keyword in clean_line for keyword in ["Given:", "When:", "Then:"]):
            step_keyword = ""
            step_name = ""
            step_status = "UNKNOWN"

            # Extract keyword and name
            for keyword in ["Given:", "When:", "Then:"]:
                if keyword in clean_line:
                    step_keyword = keyword.replace(":", "")
                    step_name = clean_line.split(keyword, 1)[1].strip()
                    break

            # Extract status from the line (case-insensitive)
            step_status = TestStatus.from_text(step_name)

            # Clean step name (remove status indicators - case-insensitive)
            step_name = _clean_step_name(step_name)

            if step_keyword and step_name:
                step_results.append({
                    'keyword': step_keyword,
                    'name': step_name,
                    'status': step_status
                })

    # Format description with HTML formatting similar to IT results
    if step_results:
        # Create detailed HTML-formatted description similar to IT results
        html_lines = []
        html_lines.append("<strong>UNIT TEST EXECUTION RESULTS - " + status.upper() + "</strong>")
        html_lines.append("=" * 60)

        # Count total steps and statuses
        total_steps = len(step_results)
        passed_steps = sum(1 for step in step_results if step['status'] == TestStatus.PASSED)
        failed_steps = sum(1 for step in step_results if step['status'] == TestStatus.FAILED)

        html_lines.append(f"<strong>Total Steps:</strong> {total_steps}")
        html_lines.append(f"✅ <strong>Passed:</strong> {passed_steps}")
        html_lines.append(f"❌ <strong>Failed:</strong> {failed_steps}")
        html_lines.append("")

        # Detailed step-by-step breakdown
        html_lines.append("<strong>STEPS EXECUTION:</strong>")
        html_lines.append("")

        for i, step in enumerate(step_results, 1):
            step_keyword = step['keyword']
            step_name = step['name']
            step_status = step['status']

            # Format step status with clear symbols
            status_symbol = step_status.to_display_symbol()

            # Main step line with HTML formatting
            full_step = f"{step_keyword} {step_name}"
            html_lines.append(f"{i:2d}. <strong>{status_symbol}</strong> | {full_step}")
            html_lines.append("")  # Space between steps

        # Add execution summary footer
        html_lines.append("<br/>")
        html_lines.append("=" * 60)
        html_lines.append("<strong>EXECUTION COMPLETED</strong>")
        html_lines.append("=" * 60)

        description = "<br/>".join(html_lines)
    elif description_lines:
        # Fallback for simple test cases (like mock_random_txt_report.txt)
        html_lines = []
        html_lines.append("<strong>UNIT TEST EXECUTION RESULTS</strong>")
        html_lines.append("=" * 50)

        for line in description_lines:
            # Use TestStatus to detect status from line (case-insensitive, handles emojis)
            detected_status = TestStatus.from_text(line)

            if detected_status != TestStatus.UNKNOWN:
                # Status detected - check if line already contains emoji
                has_emoji = any(emoji in line for emoji in ["🟢", "🔴", "⚪"])

                if has_emoji:
                    # Line already has emoji - keep as is
                    html_lines.append(f"<em>{line}</em>")
                else:
                    # Format with display symbol and clean line
                    display_symbol = detected_status.to_display_symbol()
                    cleaned_line = _clean_step_name(line)
                    html_lines.append(f"{display_symbol} - {cleaned_line}")
            else:
                # Regular description line (no status detected)
                html_lines.append(f"<em>{line}</em>")

        html_lines.append("=" * 50)
        html_lines.append("<strong>EXECUTION COMPLETED</strong>")

        description = "<br/>".join(html_lines)
    else:
        description = "No detailed description available"

    return status, description


def parse_ut_test_results_from_txt_files(input_folder: str) -> List[Dict]:
    """
    Parse UT test results from txt files in the input folder.

    Args:
        input_folder: Path to folder containing txt files

    Returns:
        List[Dict]: List of parsed test results with UT IDs and status

    Raises:
        JamaConnectionError: If the input folder doesn't exist or is not accessible
    """
    import os

    test_results = []

    try:
        file_list = os.listdir(input_folder)
    except FileNotFoundError:
        error_msg = f"Input folder '{input_folder}' does not exist."
        logging.error(error_msg)
        return []
    except PermissionError:
        error_msg = f"Permission denied for the folder '{input_folder}'."
        logging.error(error_msg)
        raise JamaConnectionError(error_msg)
    except Exception as e:
        error_msg = f"Error accessing folder '{input_folder}': {e}"
        logging.error(error_msg)
        raise JamaConnectionError(error_msg)

    # Check if there are any txt files
    txt_files = [f for f in file_list if f.lower().endswith('.txt')]
    if not txt_files:
        logging.warning(f"No txt files found in folder '{input_folder}'")
        return []

    for filename in file_list:
        if not filename.lower().endswith('.txt'):
            continue

        input_file = os.path.join(input_folder, filename)

        try:
            with open(input_file, 'r', encoding='utf-8') as f:
                file_content = f.read()

            summary_requirements = SummaryRequirementsStatus()
            scenarios, summary_requirements = generate_test_cases(file_content, summary_requirements)

            logging.debug(f"Scenarios: {scenarios}")

            for scenario in scenarios:
                # Extract UT ID from covers_list
                covers_list = scenario.get_covers_list()
                logging.debug(f"Scenario covers_list: {covers_list}")
                ut_ids = [c for c in covers_list if is_jama_ut_id(c)]
                logging.debug(f"Filtered UT IDs: {ut_ids}")

                if len(ut_ids) > 1:
                    logging.warning(f"Multiple UT IDs found in {filename}: {ut_ids}. Skipping.")
                    continue
                elif len(ut_ids) == 1:
                    ut_id = ut_ids[0].replace("SmlPrep", "BAR_SmilePrep")
                    logging.debug(f"UT ID: {ut_id}")
                else:
                    logging.warning(f"No UT ID found in {filename}. Skipping.")
                    continue

                # Extract status and description based on scenario type
                if scenario.has_steps():
                    # Structured scenario with Given-When-Then steps
                    status, description = extract_status_from_structured_scenario(scenario)
                else:
                    # Fallback for other scenario types - use scenario status
                    status = scenario.scenario_status.to_short_form()
                    description = f"Test case: {scenario.get_test_case_name()}"

                test_results.append({
                    'ut_id': ut_id,
                    'status': status,
                    'description': description,
                    'filename': filename,
                    'scenario': scenario
                })

        except Exception as e:
            logging.error(f"Error processing file {filename}: {e}")
            continue

    logging.info(f"Parsed {len(test_results)} UT test results")
    return test_results


def extract_status_from_structured_scenario(scenario) -> Tuple[str, str]:
    """
    Extract status and description from a structured scenario with Given-When-Then steps.

    Args:
        scenario: Structured scenario (UnitTestCaseData object) with steps

    Returns:
        Tuple[str, str]: (status, description)
    """
    test_case = scenario.get_test_case_name()

    if not scenario.has_steps():
        # Use scenario_status if no steps available
        return scenario.scenario_status.to_short_form(), f"Test case: {test_case}"

    # Determine overall status based on step statuses
    overall_status = TestStatus.PASSED
    failed_steps = 0

    # Process each step block using the structured data directly
    processed_steps = []
    for block in scenario.step_blocks:
        # Process Given step
        if block.given:
            given_status = block.given.status  # Use status directly from Step object
            if given_status == TestStatus.FAILED:
                overall_status = TestStatus.FAILED
                failed_steps += 1

            processed_steps.append({
                'keyword': 'Given',
                'name': block.given.label,  # Use label directly (already cleaned)
                'status': given_status,
                'indent': False  # Given is not indented
            })

        # Process When step
        if block.when:
            when_status = block.when.status  # Use status directly from Step object
            if when_status == TestStatus.FAILED:
                overall_status = TestStatus.FAILED
                failed_steps += 1

            processed_steps.append({
                'keyword': 'When',
                'name': block.when.label,  # Use label directly (already cleaned)
                'status': when_status,
                'indent': True  # When is indented
            })

        # Process Then step
        if block.then:
            then_status = block.then.status  # Use status directly from Step object
            if then_status == TestStatus.FAILED:
                overall_status = TestStatus.FAILED
                failed_steps += 1

            processed_steps.append({
                'keyword': 'Then',
                'name': block.then.label,  # Use label directly (already cleaned)
                'status': then_status,
                'indent': True  # Then is indented
            })

        # Process And steps
        for and_step in block.and_steps:
            and_status = and_step.status  # Use status directly from Step object
            if and_status == TestStatus.FAILED:
                overall_status = TestStatus.FAILED
                failed_steps += 1

            processed_steps.append({
                'keyword': 'And',
                'name': and_step.label,  # Use label directly (already cleaned)
                'status': and_status,
                'indent': True  # And is indented
            })

    # Create detailed HTML-formatted description similar to IT results
    html_lines = []
    html_lines.append("<strong>UNIT TEST EXECUTION RESULTS - " + overall_status.to_short_form().upper() + "</strong>")
    html_lines.append("=" * 60)

    # Count total steps and statuses
    total_steps = len(processed_steps)
    passed_steps = sum(1 for step in processed_steps if step['status'] == TestStatus.PASSED)

    html_lines.append(f"<strong>Total Steps:</strong> {total_steps}")
    html_lines.append(f"✅ <strong>Passed:</strong> {passed_steps}")
    html_lines.append(f"❌ <strong>Failed:</strong> {failed_steps}")
    html_lines.append("")

    # Detailed step-by-step breakdown
    html_lines.append("<strong>STEPS EXECUTION:</strong>")
    html_lines.append("")

    for i, step in enumerate(processed_steps):
        step_keyword = step['keyword']
        step_name = step['name']
        step_status = step['status']
        step_indent = step['indent']

        # Format step status with clear symbols
        status_symbol = step_status.to_display_symbol()

        # Main step line with HTML formatting
        full_step = f"{step_keyword} {step_name}"

        # Add indentation for When and Then steps
        if step_indent:
            html_lines.append(f"&nbsp;&nbsp;&nbsp;&nbsp;<strong>{status_symbol}</strong> | {full_step}")
        else:
            html_lines.append(f"<strong>{status_symbol}</strong> | {full_step}")

        # Add blank line after each Then step (end of a Given-When-Then block)
        if step_keyword == 'Then' and i < len(processed_steps) - 1:
            html_lines.append("")

    # Add execution summary footer
    html_lines.append("<br/>")
    html_lines.append("=" * 60)
    html_lines.append(f"<strong>Overall Status:</strong> {overall_status.to_short_form().upper()}")

    description = "<br/>".join(html_lines)
    return overall_status.to_short_form(), description


def push_ut_test_results_to_jama(version: str, input_folder: str, project_id: Optional[str] = None, test_set_id: Optional[str] = None, ut_test_case_id: Optional[str] = None) -> int:
    """
    Main function to push UT test results to Jama.

    Args:
        version: Version string for test plan naming
        input_folder: Path to folder containing txt files with test results

    Returns:
        int: Exit code (0 for success, 1 for errors, 2 for warnings only)

    Raises:
        JamaConnectionError: If any critical step fails
    """
    logging.info(f"=== Starting UT Test Results Push for Version: {version} ===")

    # Validate environment first
    if not validate_environment():
        raise JamaConnectionError("Jama environment not properly configured")

    # Validate input folder exists before any Jama operations
    import os
    try:
        if not os.path.exists(input_folder):
            raise JamaConnectionError(f"Input folder '{input_folder}' does not exist.")
        if not os.path.isdir(input_folder):
            raise JamaConnectionError(f"'{input_folder}' is not a directory.")
    except Exception as e:
        raise JamaConnectionError(f"Error accessing input folder '{input_folder}': {e}")

    try:
        # Initialize Jama manager
        jama_manager = JamaUTManager.get_instance()
        logging.info("Jama UT Manager initialized successfully")

        # Step 1: Find test plan by version
        logging.info("=== Step 1: Finding Test Plan ===")
        test_plan = find_test_plan_by_version_and_prefix(version)

        if not test_plan:
            raise JamaConnectionError(f"No test plan found for version: {version}")

        test_plan_id = test_plan['id']
        test_plan_name = test_plan['fields']['name']
        logging.info(f"Found test plan: {test_plan_name} (ID: {test_plan_id})")

        # Step 2: Find UT test group containing configured test case
        logging.info("=== Step 2: Finding UT Test Group ===")
        config = GlobalConfig.get_config()
        target_group = find_test_group_containing_case(test_plan_id, config['ut_test_case_id'])

        if not target_group:
            raise JamaConnectionError(f"Could not find test group containing {config['ut_test_case_id']}")

        group_id = target_group['id']
        group_name = target_group['name']
        logging.info(f"Found target group: {group_name} (ID: {group_id})")

        # Step 3: Create test cycle with UT group
        logging.info("=== Step 3: Creating Test Cycle ===")
        cycle_name = f"Unit Test Results - {version} - {datetime.now().strftime('%Y-%m-%d %H:%M')}"
        start_date = datetime.now().strftime('%Y-%m-%d')
        end_date = (datetime.now() + timedelta(days=7)).strftime('%Y-%m-%d')

        test_cycle_id = create_filtered_test_cycle_with_group(
            test_plan_id=test_plan_id,
            cycle_name=cycle_name,
            start_date=start_date,
            end_date=end_date,
            group_ids=[group_id]
        )

        if not test_cycle_id:
            raise JamaConnectionError("Failed to create test cycle")

        logging.info(f"Created test cycle: {cycle_name} (ID: {test_cycle_id})")

        # Step 4: Get test runs from the created cycle
        logging.info("=== Step 4: Getting Test Runs from Cycle ===")
        test_runs = get_test_runs_from_cycle(test_cycle_id)

        if not test_runs:
            raise JamaConnectionError(f"No test runs found in test cycle {test_cycle_id}")

        logging.info(f"Found {len(test_runs)} test runs in the cycle")

        # Step 5: Parse UT test results from txt files
        logging.info("=== Step 5: Parsing UT Test Results ===")
        try:
            ut_test_results = parse_ut_test_results_from_txt_files(input_folder)
        except JamaConnectionError as e:
            raise JamaConnectionError(f"Failed to parse UT test results: {e}")

        if not ut_test_results:
            logging.warning("No UT test results found in input folder")
            return True

        logging.info(f"Parsed {len(ut_test_results)} UT test results")

        # Step 6: Create mapping of UT test results to document keys
        logging.info("=== Step 6: Creating Test Results Mapping ===")
        ut_results_map = {}
        for test_result in ut_test_results:
            ut_id = test_result['ut_id']
            ut_results_map[ut_id] = test_result

        logging.info(f"UT test results available: {list(ut_results_map.keys())}")

        # Step 7: Process each test run and update with UT results
        logging.info("=== Step 7: Updating Test Run Results ===")
        success_count = 0
        error_count = 0
        not_found_count = 0
        warnings = []
        errors = []

        for run in test_runs:
            try:
                run_id = run['id']
                run_name = run['fields'].get('name', 'Unknown')

                # Get test case information to find document key
                test_case_id = run['fields'].get('testCase')
                if not test_case_id:
                    logging.warning(f"No test case ID found for test run {run_id}")
                    error_count += 1
                    continue

                # Get the test case to find its document key
                test_case = jama_manager.get_client().get_item(test_case_id)
                test_case_doc_key = test_case.get('documentKey', 'Unknown')
                test_case_name = test_case['fields'].get('name', 'Unknown')

                logging.debug(f"Processing test run: {run_name}")
                logging.debug(f"  Test case: {test_case_name} (Doc Key: {test_case_doc_key})")

                # Check if we have a matching UT result
                if test_case_doc_key in ut_results_map:
                    # Found matching UT result
                    ut_result = ut_results_map[test_case_doc_key]
                    status = ut_result['status']
                    description = ut_result['description']

                    # Update the test run
                    success = update_test_run_status(run_id, status, description)

                    if success:
                        logging.info(f"✅ Updated test run: {test_case_name} -> Status: {status}")
                        success_count += 1
                    else:
                        error_msg = f"Failed to update test run: {test_case_name}"
                        logging.error(f"❌ {error_msg}")
                        errors.append({
                            'test_case': test_case_name,
                            'doc_key': test_case_doc_key,
                            'error': error_msg
                        })
                        error_count += 1
                else:
                    # No matching UT result found
                    logging.warning(f"⚠️  No UT result found for test case: {test_case_doc_key}")
                    not_found_count += 1
                    warnings.append({
                        'test_case': test_case_name,
                        'doc_key': test_case_doc_key,
                        'message': 'No UT result found in input files'
                    })

            except Exception as e:
                error_msg = f"Error processing test run {run.get('id', 'Unknown')}: {e}"
                logging.error(error_msg)
                errors.append({
                    'test_case': 'Unknown',
                    'doc_key': 'Unknown',
                    'error': error_msg
                })
                error_count += 1
                continue

        # Report final summary
        total_runs = len(test_runs)
        logging.info("=== Processing Summary ===")
        logging.info(f"Total test runs processed: {total_runs}")
        logging.info(f"Successfully updated: {success_count}")
        logging.info(f"Errors: {error_count}")
        logging.info(f"Not found: {not_found_count}")

        # Report warnings
        if warnings:
            warning_data = []
            for warning in warnings:
                warning_data.append([
                    clean_log_message(warning['test_case']),
                    warning['doc_key'],
                    warning['message']
                ])

            warning_table = draw_table(
                headers=["Test Case", "Document Key", "Message"],
                data=warning_data,
                column_ratios="Test Case,3;Document Key,2;Message,4",
                title="WARNING: No UT result found for test cases"
            )
            print(f"\n{warning_table}")

        # Report errors
        if errors:
            error_data = []
            for error in errors:
                error_data.append([
                    clean_log_message(error['test_case']),
                    error['doc_key'],
                    error['error']
                ])

            error_table = draw_table(
                headers=["Test Case", "Document Key", "Error"],
                data=error_data,
                column_ratios="Test Case,3;Document Key,2;Error,4",
                title="ERROR: Failed to update test runs"
            )
            print(f"\n{error_table}")

        # Determine exit code based on warnings and errors
        has_warnings = bool(warnings)
        has_errors = bool(errors)

        if has_errors:
            logging.warning(f"Processed {success_count} test runs but {error_count} had failures")
            return 1  # Error exit code
        elif has_warnings:
            logging.info(f"Successfully processed {success_count} test runs for version {version} with warnings")
            return 2  # Warning exit code
        else:
            logging.info(f"Successfully processed {success_count} test runs for version {version}")
            return 0  # Success

    except (JamaConnectionError, JamaValidationError):
        # Re-raise Jama errors (these are expected and should stop execution)
        raise
    except Exception as e:
        logging.error(f"Unexpected error in UT test results push: {e}")
        raise JamaConnectionError(f"UT test results push failed: {e}")


def validate_jama_environment_for_ut_push() -> bool:
    """
    Validate that the Jama environment is properly configured for UT push operations.

    Returns:
        bool: True if environment is valid, False otherwise
    """
    try:
        # Check environment variables
        if not validate_environment():
            return False

        # Try to initialize manager
        jama_manager = JamaUTManager.get_instance()

        logging.info("Jama environment validation successful for UT push")
        return True

    except JamaConnectionError as e:
        logging.error(f"Jama environment validation failed: {e}")
        return False
    except Exception as e:
        logging.error(f"Unexpected error during environment validation: {e}")
        return False