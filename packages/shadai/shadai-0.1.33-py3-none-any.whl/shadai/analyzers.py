"""
Ingestion Error Analyzers
-------------------------
Analyzers for detecting and classifying ingestion failure patterns.

These analyzers provide intelligent error detection to give users
clear feedback when file ingestion fails due to plan limits or
other systematic issues.
"""

import re
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Tuple


class IngestionErrorType(Enum):
    """Types of ingestion errors that can be detected."""

    KNOWLEDGE_POINTS_LIMIT = "knowledge_points_limit"
    FILE_SIZE_LIMIT = "file_size_limit"
    CONFIGURATION_ERROR = "configuration_error"
    BATCH_SIZE_LIMIT = "batch_size_limit"
    MIXED_ERRORS = "mixed_errors"
    UNKNOWN = "unknown"


@dataclass
class ErrorPattern:
    """Pattern definition for detecting specific error types."""

    error_type: IngestionErrorType
    patterns: List[str]
    suggestion: str
    extract_context: bool = True


@dataclass
class AnalysisResult:
    """Result of analyzing ingestion failures."""

    is_complete_failure: bool
    primary_error_type: IngestionErrorType
    error_count: int
    total_files: int
    message: str
    suggestion: str
    context: Dict[str, Any] = field(default_factory=dict)
    affected_files: List[str] = field(default_factory=list)


class IngestionErrorAnalyzer:
    """
    Analyzes ingestion failures to detect patterns and provide clear feedback.

    This analyzer examines failed file entries from the server response and
    determines if there's a systematic issue (like plan limits) that caused
    all files to fail, providing actionable feedback to users.

    Example:
        >>> analyzer = IngestionErrorAnalyzer()
        >>> result = analyzer.analyze(
        ...     failed_files=[
        ...         {"filename": "doc1.pdf", "error": "Knowledge points limit exceeded..."},
        ...         {"filename": "doc2.pdf", "error": "Knowledge points limit exceeded..."},
        ...     ],
        ...     successful_count=0,
        ...     total_files=2,
        ... )
        >>> if result.is_complete_failure:
        ...     raise IngestionFailedError(result.message, ...)
    """

    # Error patterns for detection - ordered by priority
    ERROR_PATTERNS: List[ErrorPattern] = [
        ErrorPattern(
            error_type=IngestionErrorType.KNOWLEDGE_POINTS_LIMIT,
            patterns=[
                r"knowledge\s*points?\s*limit",
                r"Knowledge points limit exceeded",
                r"points_needed",
                r"monthly\s*knowledge\s*points",
            ],
            suggestion="Upgrade your plan to increase your monthly knowledge points limit, "
            "or wait until next month when your quota resets.",
        ),
        ErrorPattern(
            error_type=IngestionErrorType.FILE_SIZE_LIMIT,
            patterns=[
                r"file\s*size\s*limit",
                r"File size exceeds plan limit",
                r"exceeds\s*maximum\s*allowed\s*size",
                r"max_file_size",
            ],
            suggestion="Upgrade your plan to allow larger file uploads, "
            "or split large files into smaller parts.",
        ),
        ErrorPattern(
            error_type=IngestionErrorType.CONFIGURATION_ERROR,
            patterns=[
                r"configuration\s*error",
                r"not\s*configured",
                r"missing\s*model",
                r"provider\s*credentials?",
                r"embedding\s*model.*not\s*configured",
                r"llm\s*model.*not\s*configured",
            ],
            suggestion="Configure your LLM and embedding models in your account settings "
            "before uploading files.",
        ),
        ErrorPattern(
            error_type=IngestionErrorType.BATCH_SIZE_LIMIT,
            patterns=[
                r"batch\s*size\s*limit",
                r"Batch size exceeds",
                r"maximum.*batch",
            ],
            suggestion="Reduce the number of files per batch or use smaller files.",
        ),
    ]

    def analyze(
        self,
        failed_files: List[Dict[str, Any]],
        successful_count: int,
        total_files: int,
    ) -> AnalysisResult:
        """
        Analyze failed files to detect error patterns.

        Args:
            failed_files: List of failed file entries with 'error' field
            successful_count: Number of successfully processed files
            total_files: Total number of files attempted

        Returns:
            AnalysisResult with detected error type and actionable feedback
        """
        if not failed_files:
            return AnalysisResult(
                is_complete_failure=False,
                primary_error_type=IngestionErrorType.UNKNOWN,
                error_count=0,
                total_files=total_files,
                message="No files failed during ingestion.",
                suggestion="",
            )

        # Classify each error
        error_classifications = self._classify_errors(failed_files=failed_files)

        # Determine if this is a complete failure
        is_complete_failure = successful_count == 0 and len(failed_files) > 0

        # Find the primary error type
        primary_type, type_count = self._get_primary_error_type(
            classifications=error_classifications
        )

        # Extract context from error messages
        context = self._extract_context(
            failed_files=failed_files,
            error_type=primary_type,
        )

        # Build appropriate message and suggestion
        message, suggestion = self._build_message(
            primary_type=primary_type,
            failed_count=len(failed_files),
            total_files=total_files,
            context=context,
            is_complete_failure=is_complete_failure,
        )

        # Get affected filenames
        affected_files = [
            f.get("filename", f.get("file_path", "unknown")) for f in failed_files
        ]

        return AnalysisResult(
            is_complete_failure=is_complete_failure,
            primary_error_type=primary_type,
            error_count=len(failed_files),
            total_files=total_files,
            message=message,
            suggestion=suggestion,
            context=context,
            affected_files=affected_files,
        )

    def _classify_errors(
        self,
        failed_files: List[Dict[str, Any]],
    ) -> List[IngestionErrorType]:
        """Classify each failed file's error into an error type."""
        classifications = []

        for failed_file in failed_files:
            error_msg = str(failed_file.get("error", "")).lower()
            classified = False

            for pattern in self.ERROR_PATTERNS:
                for regex in pattern.patterns:
                    if re.search(regex, error_msg, re.IGNORECASE):
                        classifications.append(pattern.error_type)
                        classified = True
                        break
                if classified:
                    break

            if not classified:
                classifications.append(IngestionErrorType.UNKNOWN)

        return classifications

    def _get_primary_error_type(
        self,
        classifications: List[IngestionErrorType],
    ) -> Tuple[IngestionErrorType, int]:
        """Determine the primary error type from classifications."""
        if not classifications:
            return IngestionErrorType.UNKNOWN, 0

        # Count occurrences of each error type
        type_counts: Dict[IngestionErrorType, int] = {}
        for error_type in classifications:
            type_counts[error_type] = type_counts.get(error_type, 0) + 1

        # Find the most common error type
        primary_type = max(type_counts, key=lambda t: type_counts[t])
        primary_count = type_counts[primary_type]

        # If there are multiple different error types, mark as mixed
        unique_types = set(classifications) - {IngestionErrorType.UNKNOWN}
        if len(unique_types) > 1:
            # If the primary type accounts for less than 80% of errors, it's mixed
            if primary_count / len(classifications) < 0.8:
                return IngestionErrorType.MIXED_ERRORS, len(classifications)

        return primary_type, primary_count

    def _extract_context(
        self,
        failed_files: List[Dict[str, Any]],
        error_type: IngestionErrorType,
    ) -> Dict[str, Any]:
        """Extract relevant context from error messages."""
        context: Dict[str, Any] = {}

        if not failed_files:
            return context

        # Take the first error message as reference
        first_error = str(failed_files[0].get("error", ""))

        if error_type == IngestionErrorType.KNOWLEDGE_POINTS_LIMIT:
            # Try to extract knowledge points values
            context.update(self._extract_knowledge_points_context(first_error))

        elif error_type == IngestionErrorType.FILE_SIZE_LIMIT:
            # Try to extract file size values
            context.update(self._extract_file_size_context(first_error))

        elif error_type == IngestionErrorType.CONFIGURATION_ERROR:
            # Extract what's missing
            context.update(self._extract_configuration_context(first_error))

        return context

    def _extract_knowledge_points_context(
        self,
        error_msg: str,
    ) -> Dict[str, Any]:
        """Extract knowledge points related context from error message."""
        context: Dict[str, Any] = {}

        # Try to extract plan name
        plan_match = re.search(r"'([^']+)'\s*plan", error_msg)
        if plan_match:
            context["plan_name"] = plan_match.group(1)

        # Try to extract current/max points
        points_match = re.search(
            r"used\s*(\d+(?:,\d+)?)\s*\((\d+(?:,\d+)?)\s*remaining\)", error_msg
        )
        if points_match:
            context["current_points"] = int(points_match.group(1).replace(",", ""))
            context["remaining_points"] = int(points_match.group(2).replace(",", ""))

        # Try to extract max points
        max_match = re.search(
            r"includes?\s*(\d+(?:,\d+)?)\s*knowledge\s*points", error_msg
        )
        if max_match:
            context["max_points"] = int(max_match.group(1).replace(",", ""))

        # Try to extract points needed
        needed_match = re.search(r"requires?\s*(\d+(?:,\d+)?)\s*points", error_msg)
        if needed_match:
            context["points_needed"] = int(needed_match.group(1).replace(",", ""))

        return context

    def _extract_file_size_context(
        self,
        error_msg: str,
    ) -> Dict[str, Any]:
        """Extract file size related context from error message."""
        context: Dict[str, Any] = {}

        # Try to extract plan name
        plan_match = re.search(r"'([^']+)'\s*plan", error_msg)
        if plan_match:
            context["plan_name"] = plan_match.group(1)

        # Try to extract file size values
        size_match = re.search(
            r"up\s*to\s*([\d.]+)\s*MB.*this\s*file\s*is\s*([\d.]+)\s*MB", error_msg
        )
        if size_match:
            context["max_size_mb"] = float(size_match.group(1))
            context["file_size_mb"] = float(size_match.group(2))

        return context

    def _extract_configuration_context(
        self,
        error_msg: str,
    ) -> Dict[str, Any]:
        """Extract configuration error context from error message."""
        context: Dict[str, Any] = {}

        # Check what's missing
        if "embedding" in error_msg.lower():
            context["missing_config"] = "embedding_model"
        elif "llm" in error_msg.lower():
            context["missing_config"] = "llm_model"
        elif "credential" in error_msg.lower() or "api key" in error_msg.lower():
            context["missing_config"] = "provider_credentials"

        return context

    def _build_message(
        self,
        primary_type: IngestionErrorType,
        failed_count: int,
        total_files: int,
        context: Dict[str, Any],
        is_complete_failure: bool,
    ) -> Tuple[str, str]:
        """Build user-friendly message and suggestion based on error analysis."""
        # Find the matching pattern for suggestion
        suggestion = "Please check your account settings and try again."
        for pattern in self.ERROR_PATTERNS:
            if pattern.error_type == primary_type:
                suggestion = pattern.suggestion
                break

        # Build message based on error type
        if primary_type == IngestionErrorType.KNOWLEDGE_POINTS_LIMIT:
            message = self._build_knowledge_points_message(
                failed_count=failed_count,
                total_files=total_files,
                context=context,
                is_complete_failure=is_complete_failure,
            )
        elif primary_type == IngestionErrorType.FILE_SIZE_LIMIT:
            message = self._build_file_size_message(
                failed_count=failed_count,
                total_files=total_files,
                context=context,
                is_complete_failure=is_complete_failure,
            )
        elif primary_type == IngestionErrorType.CONFIGURATION_ERROR:
            message = self._build_configuration_message(
                failed_count=failed_count,
                context=context,
            )
        elif primary_type == IngestionErrorType.MIXED_ERRORS:
            message = (
                f"Ingestion failed: {failed_count} of {total_files} files failed "
                f"due to multiple different errors. Please check each file's error "
                f"message for details."
            )
            suggestion = "Review the failed files list for specific error details."
        else:
            message = (
                f"Ingestion failed: {failed_count} of {total_files} files "
                f"could not be processed."
            )

        return message, suggestion

    def _build_knowledge_points_message(
        self,
        failed_count: int,
        total_files: int,
        context: Dict[str, Any],
        is_complete_failure: bool,
    ) -> str:
        """Build knowledge points limit message."""
        plan_name = context.get("plan_name", "your")

        if is_complete_failure:
            base_msg = (
                f"Ingestion failed: All {failed_count} files were rejected because "
                f"your monthly knowledge points limit has been exceeded."
            )
        else:
            base_msg = (
                f"Ingestion partially failed: {failed_count} of {total_files} files "
                f"were rejected due to knowledge points limit."
            )

        # Add context if available
        if "current_points" in context and "max_points" in context:
            base_msg += (
                f" Your '{plan_name}' plan allows {context['max_points']:,} points/month, "
                f"and you have used {context['current_points']:,}."
            )
        elif "remaining_points" in context:
            base_msg += f" You have {context['remaining_points']:,} points remaining."

        if "points_needed" in context:
            base_msg += f" This operation requires {context['points_needed']:,} points."

        return base_msg

    def _build_file_size_message(
        self,
        failed_count: int,
        total_files: int,
        context: Dict[str, Any],
        is_complete_failure: bool,
    ) -> str:
        """Build file size limit message."""
        plan_name = context.get("plan_name", "your")

        if is_complete_failure:
            base_msg = (
                f"Ingestion failed: All {failed_count} files exceed the maximum "
                f"file size allowed by your plan."
            )
        else:
            base_msg = (
                f"Ingestion partially failed: {failed_count} of {total_files} files "
                f"exceed the file size limit."
            )

        # Add context if available
        if "max_size_mb" in context:
            base_msg += (
                f" Your '{plan_name}' plan allows files up to "
                f"{context['max_size_mb']:.1f} MB."
            )

        return base_msg

    def _build_configuration_message(
        self,
        failed_count: int,
        context: Dict[str, Any],
    ) -> str:
        """Build configuration error message."""
        missing = context.get("missing_config", "configuration")

        return (
            f"Ingestion failed: {failed_count} files could not be processed because "
            f"your account {missing} is not properly configured."
        )
