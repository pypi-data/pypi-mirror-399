"""
Test Status Enum - Standardized status values for unit test results.

This module provides a centralized enum for test statuses to avoid inconsistencies
between "PASS"/"PASSED", "FAIL"/"FAILED", etc.
"""

import re
from enum import Enum


class TestStatus(Enum):
    """
    Enumeration of test status values.

    Values:
        PASSED: Test or step passed successfully
        FAILED: Test or step failed
        UNKNOWN: Status could not be determined
    """
    PASSED = "PASSED"
    FAILED = "FAILED"
    UNKNOWN = "UNKNOWN"

    def to_short_form(self) -> str:
        """Convert to short form (PASS, FAIL) for overall test status."""
        mapping = {
            TestStatus.PASSED: "PASS",
            TestStatus.FAILED: "FAIL",
            TestStatus.UNKNOWN: "UNKNOWN"
        }
        return mapping.get(self, "UNKNOWN")

    def to_jama_status(self) -> str:
        """Convert to Jama API status format (PASSED, FAILED)."""
        mapping = {
            TestStatus.PASSED: "PASSED",
            TestStatus.FAILED: "FAILED",
            TestStatus.UNKNOWN: "UNKNOWN"
        }
        return mapping.get(self, "UNKNOWN")

    def to_display_symbol(self) -> str:
        """Get display symbol for HTML formatting (e.g., '🟢 PASS')."""
        mapping = {
            TestStatus.PASSED: "🟢 PASS",
            TestStatus.FAILED: "🔴 FAIL",
            TestStatus.UNKNOWN: "❓ UNKNOWN"
        }
        return mapping.get(self, "❓ UNKNOWN")

    @classmethod
    def from_text(cls, text: str) -> 'TestStatus':
        """
        Extract status from text, handling both cases with and without emojis.

        Uses regex with word boundaries to avoid false matches (e.g., "password" won't match "PASS").
        Always returns normalized long form (PASSED, FAILED) regardless of emoji.
        This fixes the inconsistency where "PASS" vs "PASSED" was returned.

        Args:
            text: The text to analyze for status (may contain emojis)

        Returns:
            TestStatus: Detected status enum value (always normalized)
        """
        # Pattern: optional emoji + optional whitespace + status word (as whole word)
        # Uses word boundaries (\b) to avoid matching "PASS" in "password" or "FAIL" in "failure"
        # Always normalizes to PASSED/FAILED regardless of what's found in text
        if re.search(r'[🟢]\s*\bPASS\b', text, re.IGNORECASE):
            return cls.PASSED
        elif re.search(r'[🔴]\s*\bFAIL\b', text, re.IGNORECASE):
            return cls.FAILED
        elif re.search(r'\bPASS\b', text, re.IGNORECASE):
            return cls.PASSED
        elif re.search(r'\bFAIL\b', text, re.IGNORECASE):
            return cls.FAILED

        return cls.UNKNOWN

    def __str__(self) -> str:
        """Return the string value of the status."""
        return self.value

    @classmethod
    def remove_from_text(cls, text: str) -> str:
        """
        Remove status indicators (emoji + status text) from text.

        This method detects and removes status patterns from text, handling all variations:
        "🟢 PASS", "🔴 FAIL", "PASS", "FAIL", "PASSED", "FAILED", etc.

        Args:
            text: The text to clean

        Returns:
            str: Text with status indicators removed
        """
        if not text:
            return text

        # Pattern matches: optional emoji + whitespace + status word (as whole word) + optional whitespace at end
        # Uses word boundaries to avoid removing "PASS" in "password" or "FAIL" in "failure"
        # Matches all status variations: PASS, FAIL, SKIP, PASSED, FAILED
        cleaned = re.sub(r'\s*[🟢🔴⚪❌⏭️]?\s*\b(PASS|FAIL|SKIP|PASSED|FAILED)\b\s*$', '', text, flags=re.IGNORECASE).strip()

        return cleaned

