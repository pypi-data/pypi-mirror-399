"""
Shadai Tools - High-Level API Wrappers
---------------------------------------
Beautiful, Pythonic interfaces for Shadai AI tools.
"""

import asyncio
import base64
import json
import logging
import os
from pathlib import Path
from typing import TYPE_CHECKING, Any, AsyncIterator, Dict, List, Optional, Union

from dotenv import load_dotenv

from .analyzers import IngestionErrorAnalyzer, IngestionErrorType
from .client import ShadaiClient
from .exceptions import IngestionFailedError
from .models import AgentTool, EmbeddingModel, LanguageCode, LLMModel

logger = logging.getLogger(__name__)

if TYPE_CHECKING:
    from .session import Session

load_dotenv()


class EngineTool:
    """
    Shadai Engine Tool.

    Orchestrates multiple tools (knowledge base and web search) with built-in
    memory and summarization capabilities.

    Memory (use_memory) and summarization (use_summary) are always enabled
    and cannot be disabled, ensuring consistent conversation context and
    document understanding.

    Examples:
        >>> engine = EngineTool(client=client, session_uuid="...")
        >>> async for chunk in engine(
        ...     prompt="Compare my docs with current trends",
        ...     use_knowledge_base=True,
        ...     use_web_search=True
        ... ):
        ...     print(chunk, end="", flush=True)
    """

    def __init__(self, client: ShadaiClient, session_uuid: str) -> None:
        """
        Initialize Engine tool.

        Args:
            client: Shadai client instance
            session_uuid: Your session UUID
        """
        self.client = client
        self.session_uuid = session_uuid

    async def __call__(
        self,
        prompt: str,
        use_knowledge_base: bool = True,
        use_web_search: bool = True,
        system_prompt: Optional[str] = None,
        response_language: Optional[Union[str, "LanguageCode"]] = None,
    ) -> AsyncIterator[str]:
        """
        Execute engine with knowledge base and web search capabilities.

        Memory (use_memory) and summarization (use_summary) are always enabled
        internally to ensure conversation context and document understanding.

        Args:
            prompt: Your question or prompt
            use_knowledge_base: Enable knowledge base retrieval (default: True)
            use_web_search: Enable web search (default: True)
            system_prompt: Optional system prompt
            response_language: Optional language code for responses (e.g., LanguageCode.SPANISH, LanguageCode.ENGLISH)
        Yields:
            Text chunks from the engine

        Examples:
            >>> # Use both knowledge base and web search
            >>> async for chunk in engine_tool(
            ...     "What are ML trends?",
            ...     use_knowledge_base=True,
            ...     use_web_search=True
            ... ):
            ...     print(chunk, end="")
            >>>
            >>> # Use only knowledge base
            >>> async for chunk in engine_tool(
            ...     "Summarize my documents",
            ...     use_knowledge_base=True,
            ...     use_web_search=False
            ... ):
            ...     print(chunk, end="")
        """
        # Build arguments
        arguments = {
            "session_uuid": self.session_uuid,
            "prompt": prompt,
            "use_knowledge_base": use_knowledge_base,
            "use_summary": True,  # Always enabled
            "use_web_search": use_web_search,
            "use_memory": True,  # Always enabled
        }

        # Add optional parameters if provided
        if system_prompt is not None:
            arguments["system_prompt"] = system_prompt

        if response_language is not None:
            # Convert LanguageCode enum to string if needed
            response_lang_value = (
                response_language.value
                if hasattr(response_language, "value")
                else str(response_language)
            )
            arguments["response_language"] = response_lang_value

        async for chunk in self.client.stream_tool(
            tool_name="shadai_engine",
            arguments=arguments,
        ):
            yield chunk


class IngestTool:
    """
    Folder Ingesting Tool.

    Recursively processes all PDF and image files in a folder, uploading them
    to a RAG session for knowledge base ingestion. Supports nested folder structures.

    Provides intelligent error detection and clear feedback when ingestion fails
    due to plan limits (knowledge points, file size) or configuration issues.

    Examples:
        >>> ingest_tool = IngestTool(client=client, session_uuid="...")
        >>> results = await ingest_tool("/path/to/documents")
        >>> print(f"Processed {len(results['successful'])} files")

    Raises:
        IngestionFailedError: When all files fail due to plan limits or configuration
    """

    SUPPORTED_EXTENSIONS = {".pdf", ".jpg", ".jpeg", ".png", ".webp"}
    MAX_FILE_SIZE_MB = 35
    MAX_FILE_SIZE_BYTES = MAX_FILE_SIZE_MB * 1024 * 1024  # 35 MB in bytes
    MAX_BATCH_SIZE_MB = 110
    MAX_BATCH_SIZE_BYTES = MAX_BATCH_SIZE_MB * 1024 * 1024  # 110 MB in bytes

    def __init__(self, client: ShadaiClient, session_uuid: str) -> None:
        """
        Initialize Ingest tool.

        Args:
            client: Shadai client instance
            session_uuid: Your session UUID
        """
        self.client = client
        self.session_uuid = session_uuid
        self._error_analyzer = IngestionErrorAnalyzer()

    async def __call__(
        self,
        folder_path: str,
        max_concurrent: int = 5,
        raise_on_complete_failure: bool = True,
    ) -> Dict[str, Any]:
        """
        Ingest all PDF and image files in a folder (including nested folders).

        Args:
            folder_path: Path to the folder containing files to process
            max_concurrent: Maximum number of concurrent file uploads (default: 5)
            raise_on_complete_failure: If True, raises IngestionFailedError when all
                files fail due to plan limits (default: True). Set to False to get
                the results dict even on complete failure.

        Returns:
            Dictionary with successful uploads, failed uploads, and statistics:
            - successful: List of successfully ingested files
            - failed: List of failed files with error details
            - skipped: List of files skipped (too large for client-side limit)
            - total_files: Total number of files found
            - successful_count: Number of successful uploads
            - failed_count: Number of failed uploads
            - skipped_count: Number of skipped files

        Raises:
            ValueError: If folder path doesn't exist or is not a directory
            IngestionFailedError: When all files fail due to plan limits or
                configuration issues (only if raise_on_complete_failure=True)

        Examples:
            >>> results = await ingest_tool("/path/to/docs")
            >>> print(f"Success: {len(results['successful'])}")
            >>> print(f"Failed: {len(results['failed'])}")

            >>> # Handle failures gracefully
            >>> try:
            ...     results = await ingest_tool("/path/to/docs")
            ... except IngestionFailedError as e:
            ...     print(f"Ingestion failed: {e.message}")
            ...     print(f"Suggestion: {e.suggestion}")
        """
        folder = Path(folder_path)

        if not folder.exists():
            raise ValueError(f"Folder does not exist: {folder_path}")

        if not folder.is_dir():
            raise ValueError(f"Path is not a directory: {folder_path}")

        files_to_process = self._find_files(folder=folder)

        if not files_to_process:
            return {
                "successful": [],
                "failed": [],
                "skipped": [],
                "total_files": 0,
                "successful_count": 0,
                "failed_count": 0,
                "skipped_count": 0,
            }

        files_to_upload = []
        skipped_files = []

        for file_path in files_to_process:
            file_size = file_path.stat().st_size
            if file_size > self.MAX_FILE_SIZE_BYTES:
                size_mb = file_size / (1024 * 1024)
                skipped_files.append(
                    {
                        "file_path": str(file_path),
                        "filename": file_path.name,
                        "size": file_size,
                        "size_mb": f"{size_mb:.2f} MB",
                        "reason": (
                            f"File size ({size_mb:.2f} MB) exceeds maximum allowed "
                            f"size ({self.MAX_FILE_SIZE_MB} MB)"
                        ),
                    }
                )
            else:
                files_to_upload.append(file_path)

        results = await self._ingest_files(
            files=files_to_upload, max_concurrent=max_concurrent
        )
        results["skipped"] = skipped_files
        results["skipped_count"] = len(skipped_files)
        results["total_files"] = len(files_to_process)

        # Analyze results for complete failures
        if raise_on_complete_failure:
            self._check_for_critical_failures(results=results)

        # Log warnings if present (from server-side analysis)
        warnings = results.get("warnings", [])
        if warnings:
            for warning in warnings:
                if warning.get("severity") == "error":
                    # These are already handled by _check_for_critical_failures
                    pass
                else:
                    # Log non-critical warnings for visibility
                    logger.warning(
                        f"Ingestion warning [{warning.get('type')}]: "
                        f"{warning.get('message')}"
                    )

        return results

    def _check_for_critical_failures(self, results: Dict[str, Any]) -> None:
        """
        Analyze results and raise IngestionFailedError for critical failures.

        This method detects when all files failed due to systematic issues
        (like plan limits) and raises a clear exception with actionable feedback.

        Args:
            results: Ingestion results dictionary

        Raises:
            IngestionFailedError: When all files failed due to plan limits
        """
        failed_files = results.get("failed", [])
        successful_count = results.get("successful_count", 0)
        total_files = results.get("total_files", 0)

        if not failed_files:
            return

        # Use the analyzer to detect error patterns
        analysis = self._error_analyzer.analyze(
            failed_files=failed_files,
            successful_count=successful_count,
            total_files=total_files,
        )

        # Raise exception for complete failures due to known issues
        if analysis.is_complete_failure and analysis.primary_error_type in {
            IngestionErrorType.KNOWLEDGE_POINTS_LIMIT,
            IngestionErrorType.FILE_SIZE_LIMIT,
            IngestionErrorType.CONFIGURATION_ERROR,
        }:
            raise IngestionFailedError(
                message=analysis.message,
                failed_count=analysis.error_count,
                error_type=analysis.primary_error_type.value,
                failed_files=failed_files,
                suggestion=analysis.suggestion,
                context=analysis.context,
            )

    def _find_files(self, folder: Path) -> List[Path]:
        """
        Recursively find all supported files in folder.

        Args:
            folder: Folder path to search

        Returns:
            List of file paths with supported extensions
        """
        files = []
        for item in folder.rglob("*"):
            if item.is_file() and item.suffix.lower() in self.SUPPORTED_EXTENSIONS:
                files.append(item)
        return files

    def _create_batches(self, files: List[Path]) -> List[List[Path]]:
        """
        Batch files into groups with maximum total size of MAX_BATCH_SIZE_BYTES.

        Args:
            files: List of file paths to batch

        Returns:
            List of batches, where each batch is a list of file paths
        """
        batches: List[List[Path]] = []
        current_batch: List[Path] = []
        current_batch_size = 0

        for file_path in files:
            file_size = file_path.stat().st_size

            # If adding this file would exceed the batch limit, start a new batch
            if (
                current_batch
                and (current_batch_size + file_size) > self.MAX_BATCH_SIZE_BYTES
            ):
                batches.append(current_batch)
                current_batch = [file_path]
                current_batch_size = file_size
            else:
                current_batch.append(file_path)
                current_batch_size += file_size

        # Add the last batch if not empty
        if current_batch:
            batches.append(current_batch)

        return batches

    async def _ingest_files(
        self, files: List[Path], max_concurrent: int
    ) -> Dict[str, Any]:
        """
        Ingest multiple files concurrently with batching by size.

        Groups files into batches of up to MAX_BATCH_SIZE_MB (110MB) each,
        then processes each batch as a single API call.

        Args:
            files: List of file paths to process
            max_concurrent: Maximum concurrent batch uploads

        Returns:
            Dictionary with processing results
        """
        # Create batches of files (max 110MB per batch)
        batches = self._create_batches(files=files)

        semaphore = asyncio.Semaphore(max_concurrent)
        tasks = [
            self._ingest_batch(batch=batch, semaphore=semaphore) for batch in batches
        ]

        results = await asyncio.gather(*tasks, return_exceptions=True)

        successful = []
        failed = []

        # Flatten results from all batches
        for batch, result in zip(batches, results):
            if isinstance(result, Exception):
                # All files in the batch failed
                for file_path in batch:
                    failed.append(
                        {
                            "file_path": str(file_path),
                            "filename": file_path.name,
                            "error": str(result),
                        }
                    )
            elif isinstance(result, dict):
                # Extract successful and failed files from batch result
                successful.extend(result.get("successful", []))
                failed.extend(result.get("failed", []))

        return {
            "successful": successful,
            "failed": failed,
            "total_files": len(files),
            "successful_count": len(successful),
            "failed_count": len(failed),
        }

    async def _ingest_batch(
        self, batch: List[Path], semaphore: asyncio.Semaphore
    ) -> Dict[str, Any]:
        """
        Ingest a batch of files: read, encode, and upload as a single API call.

        Args:
            batch: List of file paths to process in this batch
            semaphore: Semaphore for concurrency control

        Returns:
            Dictionary with upload results including successful and failed files

        Raises:
            Exception: If batch processing fails
        """
        async with semaphore:
            try:
                # Prepare all files in the batch
                files_data = []
                for file_path in batch:
                    try:
                        file_data = file_path.read_bytes()
                        file_base64 = base64.b64encode(file_data).decode("utf-8")
                        files_data.append(
                            {
                                "file_base64": file_base64,
                                "filename": file_path.name,
                                "file_path": str(file_path),
                            }
                        )
                    except Exception as e:
                        # If a file fails to read, add it to failed list but continue with others
                        files_data.append(
                            {
                                "file_path": str(file_path),
                                "filename": file_path.name,
                                "error": f"Failed to read file: {str(e)}",
                            }
                        )

                # Call the batch ingest tool
                result = await self.client.call_tool(
                    tool_name="ingest_files_batch",
                    arguments={
                        "session_uuid": self.session_uuid,
                        "files": files_data,
                    },
                )
                return json.loads(result)

            except Exception as e:
                raise Exception(
                    f"Failed to process batch of {len(batch)} files: {str(e)}"
                ) from e


class ExtractionTool:
    """
    Structured Information Extraction Tool.

    Uses LangExtract to extract structured entities from documents with precise
    source grounding. Supports processing URLs and text with few-shot examples
    to define the extraction schema.

    Examples:
        >>> extraction = ExtractionTool(client=client, session_uuid="...", llm_model_uuid="...")
        >>> result = await extraction(
        ...     text_or_documents="https://example.com/invoice.pdf",
        ...     prompt_description="Extract invoice information",
        ...     examples=[{"text": "...", "extractions": [...]}]
        ... )
        >>> print(f"Found {result['extraction_count']} entities")
    """

    def __init__(
        self,
        client: ShadaiClient,
        session_uuid: str,
        llm_model_uuid: Optional[str] = None,
    ) -> None:
        """
        Initialize Extraction tool.

        Args:
            client: Shadai client instance
            session_uuid: Your session UUID
            llm_model_uuid: Optional LLM model UUID (uses session's model if not provided)
        """
        self.client = client
        self.session_uuid = session_uuid
        self.llm_model_uuid = llm_model_uuid

    async def __call__(
        self,
        text_or_documents: str | List[str],
        prompt_description: str,
        examples: List[Dict[str, Any]],
        extraction_passes: int = 1,
        max_workers: int = 10,
        max_char_buffer: int = 10000,
        use_schema_constraints: bool = False,
        generate_visualization: bool = False,
    ) -> Dict[str, Any]:
        """
        Extract structured information from documents.

        Args:
            text_or_documents: Text or URL(s) to process (supports Google Drive, web URLs)
            prompt_description: Clear description of what to extract
            examples: List of few-shot examples defining the extraction schema
            extraction_passes: Number of extraction passes for higher recall (default: 1)
            max_workers: Maximum parallel workers for long documents (default: 10)
            max_char_buffer: Character buffer size for chunking (default: 10000).
                Larger values = fewer chunks = faster but less precise.
                Smaller values = more chunks = slower but more precise.
            use_schema_constraints: Use strict schema constraints (default: False)
            generate_visualization: Generate HTML visualization (default: False)

        Returns:
            Dictionary with extraction results:
            - extraction_count: Number of entities extracted
            - model_used: LLM model name used for extraction
            - provider: LLM provider name
            - extractions: List of extracted entities with attributes and positions
            - metadata: Extraction configuration metadata
            - html_visualization: Optional HTML visualization (if generate_visualization=True)

        Examples:
            >>> # Extract from URL
            >>> result = await extraction_tool(
            ...     text_or_documents="https://example.com/invoice.pdf",
            ...     prompt_description="Extract invoice details",
            ...     examples=[
            ...         {
            ...             "text": "Invoice #123...",
            ...             "extractions": [
            ...                 {
            ...                     "extraction_class": "invoice_number",
            ...                     "extraction_text": "123",
            ...                     "attributes": {"field": "invoice_id"}
            ...                 }
            ...             ]
            ...         }
            ...     ],
            ...     generate_visualization=True
            ... )
        """
        arguments = {
            "text_or_documents": text_or_documents,
            "prompt_description": prompt_description,
            "examples": examples,
            "extraction_passes": extraction_passes,
            "max_workers": max_workers,
            "max_char_buffer": max_char_buffer,
            "use_schema_constraints": use_schema_constraints,
            "generate_visualization": generate_visualization,
        }

        # Add llm_model_uuid if provided
        if self.llm_model_uuid:
            arguments["llm_model_uuid"] = self.llm_model_uuid

        result = await self.client.call_tool(
            tool_name="shadai_extract",
            arguments=arguments,
        )
        return json.loads(result)


class _AgentOrchestrator:
    """
    Internal orchestrator for Shadai Agent workflow.

    The agent automatically:
    1. Plans which tools to use (via planner)
    2. Executes the selected tools with provided arguments
    3. Synthesizes all outputs into a unified answer (via synthesizer)

    This provides a complete agentic workflow where you provide tools with their
    implementations and arguments, and the agent handles the orchestration.
    """

    def __init__(self, client: ShadaiClient) -> None:
        """
        Initialize Agent orchestrator.

        Args:
            client: Shadai client instance
        """
        self.client = client

    async def __call__(
        self,
        prompt: str,
        tools: List[AgentTool],
        session_uuid: str,
    ) -> AsyncIterator[str]:
        """
        Execute agentic workflow: plan → execute → synthesize.

        Args:
            prompt: User's question or task
            tools: List of AgentTool objects with name, description, implementation, and arguments
            session_uuid: Session UUID for context and memory

        Yields:
            Text chunks from the synthesized final answer
        """
        import inspect
        import json

        # Convert list to dictionary for lookup
        tools_dict: Dict[str, AgentTool] = {tool.name: tool for tool in tools}

        # Step 1: Plan - Get tool selection from server
        tool_definitions = [
            {
                "name": tool.name,
                "description": tool.description,
                "parameters": tool.parameters,
            }
            for tool in tools_dict.values()
        ]

        plan_result = await self.client.call_tool(
            tool_name="shadai_planner",
            arguments={
                "prompt": prompt,
                "available_tools": tool_definitions,
                "session_uuid": session_uuid,
            },
        )
        plan = json.loads(plan_result)

        # Step 2: Execute - Run selected tools locally with inferred arguments
        tool_executions = []

        for tool_item in plan["tool_plan"]:
            tool_name = tool_item["name"]
            # Use inferred arguments from planner
            inferred_args = tool_item.get("arguments", {})

            if tool_name not in tools_dict:
                # Tool not available, record error
                tool_executions.append(
                    {
                        "tool_name": tool_name,
                        "arguments": inferred_args,
                        "output": f"Error: Tool '{tool_name}' not found in provided tools",
                    }
                )
                continue

            tool = tools_dict[tool_name]
            tool_impl = tool.implementation

            # Merge user-provided arguments with inferred arguments (inferred takes precedence)
            final_args = {**tool.arguments, **inferred_args}

            # Execute the tool implementation with final arguments
            try:
                if inspect.iscoroutinefunction(tool_impl):
                    result = await tool_impl(**final_args)
                else:
                    result = tool_impl(**final_args)

                tool_executions.append(
                    {
                        "tool_name": tool_name,
                        "arguments": final_args,
                        "output": str(result),
                    }
                )
            except Exception as e:
                tool_executions.append(
                    {
                        "tool_name": tool_name,
                        "arguments": final_args,
                        "output": f"Error executing tool: {str(e)}",
                    }
                )

        # Step 3: Synthesize - Combine outputs via server
        async for chunk in self.client.stream_tool(
            tool_name="shadai_synthesizer",
            arguments={
                "prompt": prompt,
                "tool_definitions": tool_definitions,
                "tool_executions": tool_executions,
                "session_uuid": session_uuid,
            },
        ):
            yield chunk


class Shadai:
    """
    Main entry point for Shadai AI client.

    Provides convenient access to all Shadai tools with a clean, intuitive API.

    Examples:
        >>> from client.shadai import Shadai, AgentTool
        >>>
        >>> shadai = Shadai(api_key="your-api-key")
        >>>
        >>> # Check server health
        >>> health = await shadai.health()
        >>> print(health)
        >>>
        >>> # Query knowledge base (one-step)
        >>> async for chunk in shadai.query(
        ...     query="What is AI?",
        ...     session_uuid="..."
        ... ):
        ...     print(chunk, end="")
        >>>
        >>> # Use intelligent agent (orchestrates plan → execute → synthesize)
        >>> tools = [
        ...     AgentTool(
        ...         name="my_tool",
        ...         description="Does something",
        ...         implementation=my_function,
        ...         arguments={"param": "value"}
        ...     )
        ... ]
        >>> async for chunk in shadai.agent(
        ...     prompt="Do task",
        ...     tools=tools
        ... ):
        ...     print(chunk, end="")
    """

    def __init__(
        self,
        name: Optional[str] = None,
        llm_model: Optional[Union[str, LLMModel]] = None,
        embedding_model: Optional[Union[str, EmbeddingModel]] = None,
        temporal: bool = False,
        api_key: Optional[str] = None,
        base_url: str = "https://apiv2.shadai.ai",
        timeout: int = 30,
        system_prompt: Optional[str] = None,
        response_language: Optional[Union[str, "LanguageCode"]] = None,
    ) -> None:
        """
        Initialize Shadai client with session management.

        Args:
            name: Optional session name to retrieve existing session
            temporal: If True, delete session on context exit (default: False)
            api_key: Your Shadai API key (defaults to SHADAI_API_KEY env var)
            base_url: Base URL of Shadai server
            timeout: Request timeout in seconds
            system_prompt: Optional system prompt for the session
            llm_model: Optional LLM model (e.g., LLMModel.OPENAI_GPT_4O_MINI)
            embedding_model: Optional embedding model (e.g., EmbeddingModel.OPENAI_TEXT_EMBEDDING_3_SMALL)
            response_language: Optional language code for responses (e.g., LanguageCode.SPANISH, LanguageCode.ENGLISH)

        Examples:
            >>> from shadai import Shadai, LLMModel, EmbeddingModel, LanguageCode
            >>>
            >>> # Use existing session
            >>> async with Shadai(name="my-session") as shadai:
            ...     async for chunk in shadai.query(query="What is AI?"):
            ...         print(chunk, end="")
            >>>
            >>> # Create temporal session (auto-deleted)
            >>> async with Shadai(temporal=True) as shadai:
            ...     async for chunk in shadai.query(query="What is AI?"):
            ...         print(chunk, end="")
            >>>
            >>> # Create session with custom models and language
            >>> async with Shadai(
            ...     name="my-session",
            ...     llm_model=LLMModel.OPENAI_GPT_4O_MINI,
            ...     embedding_model=EmbeddingModel.OPENAI_TEXT_EMBEDDING_3_SMALL,
            ...     system_prompt="You are a helpful assistant.",
            ...     response_language=LanguageCode.ENGLISH
            ... ) as shadai:
            ...     async for chunk in shadai.query(query="Hello!"):
            ...         print(chunk, end="")
        """
        if not api_key:
            api_key = os.getenv("SHADAI_API_KEY")
            if not api_key:
                raise ValueError("API key not provided")

        self.client = ShadaiClient(
            api_key=api_key,
            base_url=base_url,
            timeout=timeout,
        )
        self._session_name = name
        self._temporal = temporal
        self._system_prompt = system_prompt
        self._llm_model = llm_model
        self._embedding_model = embedding_model
        self._response_language = response_language
        self._session: Optional["Session"] = None

    async def __aenter__(self) -> "Shadai":
        """Enter context: initialize session.

        Returns:
            Shadai instance with active session
        """
        from .session import Session

        self._session = Session(
            name=self._session_name,
            temporal=self._temporal,
            client=self.client,
            system_prompt=self._system_prompt,
            llm_model=self._llm_model,
            embedding_model=self._embedding_model,
            response_language=self._response_language,
        )
        await self._session.__aenter__()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        """Exit context: cleanup session.

        Args:
            exc_type: Exception type if raised
            exc_val: Exception value if raised
            exc_tb: Exception traceback if raised
        """
        if self._session:
            await self._session.__aexit__(exc_type, exc_val, exc_tb)

    async def health(self) -> Dict[str, Any]:
        """
        Check server health.

        Returns:
            Server health information

        Examples:
            >>> health = await shadai.health()
            >>> print(f"Status: {health['status']}")
        """
        return await self.client.health_check()

    async def list_tools(self) -> List[Dict[str, Any]]:
        """
        List all available tools.

        Returns:
            List of tool definitions

        Examples:
            >>> tools = await shadai.list_tools()
            >>> for tool in tools:
            ...     print(tool["name"])
        """
        return await self.client.list_tools()

    async def engine(
        self,
        prompt: str,
        use_knowledge_base: bool = False,
        use_web_search: bool = False,
        system_prompt: Optional[str] = None,
        response_language: Optional[Union[str, "LanguageCode"]] = None,
    ) -> AsyncIterator[str]:
        """
        Execute unified engine with knowledge base and web search capabilities.

        Memory (use_memory) and summarization (use_summary) are always enabled
        internally to ensure conversation context and document understanding.

        Args:
            prompt: Your question or prompt
            use_knowledge_base: Enable knowledge base retrieval (default: False)
            use_web_search: Enable web search (default: False)
            system_prompt: Optional system prompt
            response_language: Optional language code for responses (e.g., LanguageCode.SPANISH, LanguageCode.ENGLISH)
        Yields:
            Text chunks from the engine

        Examples:
            >>> # Use both knowledge base and web search
            >>> async with Shadai(name="my-session") as shadai:
            ...     async for chunk in shadai.engine(
            ...         prompt="Analyze my docs and compare with current trends",
            ...         use_knowledge_base=False,
            ...         use_web_search=False,
            ...         system_prompt="You are a helpful assistant.",
            ...         response_language=LanguageCode.ENGLISH
            ...     ):
            ...         print(chunk, end="")
            >>>
            >>> # Use only knowledge base
            >>> async with Shadai(name="my-session") as shadai:
            ...     async for chunk in shadai.engine(
            ...         prompt="Summarize my documents",
            ...         use_knowledge_base=False,
            ...         use_web_search=False,
            ...         system_prompt="You are a helpful assistant.",
            ...         response_language=LanguageCode.ENGLISH
            ...     ):
            ...         print(chunk, end="")
        """
        if not self._session:
            raise ValueError("Shadai must be used as a context manager")

        engine_tool = EngineTool(client=self.client, session_uuid=self._session.uuid)
        async for chunk in engine_tool(
            prompt=prompt,
            use_knowledge_base=use_knowledge_base,
            use_web_search=use_web_search,
            system_prompt=system_prompt,
            response_language=response_language,
        ):
            yield chunk

    async def agent(
        self,
        prompt: str,
        tools: List[AgentTool],
    ) -> AsyncIterator[str]:
        """
        Execute intelligent agent workflow: plan → execute → synthesize.

        The agent orchestrates a complete workflow:
        1. Plans which tools to use (via planner API)
        2. Executes tools locally with provided arguments
        3. Synthesizes outputs (via synthesizer API)

        Args:
            prompt: User's question or task
            tools: List of AgentTool objects

        Yields:
            Text chunks from the synthesized response

        Examples:
            >>> from shadai import AgentTool
            >>>
            >>> # Define tools
            >>> tools = [
            ...     AgentTool(
            ...         name="search_database",
            ...         description="Search database",
            ...         implementation=search_func,
            ...         arguments={"query": "users", "limit": 10}
            ...     ),
            ...     AgentTool(
            ...         name="generate_report",
            ...         description="Generate report",
            ...         implementation=report_func,
            ...         arguments={"format": "markdown"}
            ...     )
            ... ]
            >>>
            >>> # Agent handles plan → execute → synthesize
            >>> async with Shadai(name="my-session") as shadai:
            ...     async for chunk in shadai.agent(
            ...         prompt="Find and analyze data",
            ...         tools=tools
            ...     ):
            ...         print(chunk, end="")
        """
        if not self._session:
            raise ValueError("Shadai must be used as a context manager")

        orchestrator = _AgentOrchestrator(client=self.client)
        async for chunk in orchestrator(
            prompt=prompt, tools=tools, session_uuid=self._session.uuid
        ):
            yield chunk

    async def ingest(
        self,
        folder_path: str,
        raise_on_complete_failure: bool = True,
    ) -> Dict[str, Any]:
        """
        Ingest all PDF and image files in a folder (including nested folders).

        Recursively finds all supported files and uploads them to the session
        for RAG knowledge base ingestion. Supports concurrent uploads.

        Provides intelligent error detection and raises clear exceptions when
        ingestion fails due to plan limits or configuration issues.

        Args:
            folder_path: Path to the folder containing files to process
            raise_on_complete_failure: If True (default), raises IngestionFailedError
                when all files fail due to plan limits. Set to False to always
                return results dict even on complete failure.

        Returns:
            Dictionary with processing results:
            - successful: List of successfully uploaded files
            - failed: List of files that failed to upload
            - skipped: List of files skipped (exceeding client-side size limit)
            - total_files: Total number of files processed
            - successful_count: Count of successful uploads
            - failed_count: Count of failed uploads
            - skipped_count: Count of skipped files

        Raises:
            ValueError: If Shadai is not used as context manager
            IngestionFailedError: When all files fail due to plan limits
                (only if raise_on_complete_failure=True)

        Examples:
            >>> async with Shadai(name="my-session") as shadai:
            ...     results = await shadai.ingest(
            ...         folder_path="/path/to/documents"
            ...     )
            ...     print(f"Uploaded {results['successful_count']} files")
            ...     print(f"Failed {results['failed_count']} files")

            >>> # Handle plan limit errors gracefully
            >>> from shadai import IngestionFailedError
            >>> async with Shadai(name="my-session") as shadai:
            ...     try:
            ...         results = await shadai.ingest("/path/to/docs")
            ...     except IngestionFailedError as e:
            ...         print(f"Error: {e.message}")
            ...         print(f"Suggestion: {e.suggestion}")
        """
        if not self._session:
            raise ValueError("Shadai must be used as a context manager")

        ingest_tool = IngestTool(client=self.client, session_uuid=self._session.uuid)
        return await ingest_tool(
            folder_path=folder_path,
            raise_on_complete_failure=raise_on_complete_failure,
        )

    async def get_plan_info(self) -> Dict[str, Any]:
        """
        Get current plan information and usage statistics.

        Returns comprehensive plan details including limits, current usage,
        and remaining quota for each resource type. Useful for checking
        available capacity before ingesting files.

        Returns:
            Dictionary with plan information:
            - has_plan: Whether a plan is assigned
            - plan_name: Name of the plan (e.g., "Pro", "Enterprise")
            - limits: Dict with knowledge_points, max_file_size_mb, max_api_calls
            - usage: Dict with current usage and remaining quota
            - period: Current billing period (year, month, display)

        Examples:
            >>> async with Shadai(name="my-session") as shadai:
            ...     plan_info = await shadai.get_plan_info()
            ...     print(f"Plan: {plan_info['plan_name']}")
            ...     print(f"Knowledge points remaining: "
            ...           f"{plan_info['usage']['knowledge_points']['remaining']}")
        """
        result = await self.client.call_tool(
            tool_name="get_plan_info",
            arguments={},
        )
        return json.loads(result)

    async def validate_ingestion(
        self,
        folder_path: str,
    ) -> Dict[str, Any]:
        """
        Pre-flight validation to check if files can be ingested within plan limits.

        Scans the folder for supported files, estimates the knowledge points cost,
        and checks against current plan limits. Use this before calling ingest()
        to get early feedback about potential limit issues.

        Args:
            folder_path: Path to the folder containing files to validate

        Returns:
            Dictionary with validation results:
            - can_ingest: True if all files can be ingested within limits
            - files_count: Number of supported files found
            - total_size_mb: Total size of files in MB
            - estimated_knowledge_points: Estimated cost in knowledge points
            - current_usage: Current knowledge points used this period
            - remaining_points: Knowledge points remaining
            - would_exceed_limit: True if ingestion would exceed limits
            - blocking_issues: List of issues preventing ingestion (if any)

        Raises:
            ValueError: If folder path doesn't exist or is not a directory

        Examples:
            >>> async with Shadai(name="my-session") as shadai:
            ...     validation = await shadai.validate_ingestion("/path/to/docs")
            ...     if validation["can_ingest"]:
            ...         results = await shadai.ingest("/path/to/docs")
            ...     else:
            ...         print(f"Cannot ingest: {validation['blocking_issues']}")
        """
        folder = Path(folder_path)

        if not folder.exists():
            raise ValueError(f"Folder does not exist: {folder_path}")

        if not folder.is_dir():
            raise ValueError(f"Path is not a directory: {folder_path}")

        # Find all supported files
        supported_extensions = {".pdf", ".jpg", ".jpeg", ".png", ".webp"}
        files = []
        for item in folder.rglob("*"):
            if item.is_file() and item.suffix.lower() in supported_extensions:
                files.append(item)

        if not files:
            return {
                "can_ingest": True,
                "files_count": 0,
                "total_size_mb": 0,
                "estimated_knowledge_points": 0,
                "message": "No supported files found in folder",
                "blocking_issues": [],
            }

        # Get file sizes
        file_sizes = [f.stat().st_size for f in files]
        total_size = sum(file_sizes)
        total_size_mb = total_size / (1024 * 1024)

        # Check for files exceeding client-side limit (35 MB)
        max_file_size_bytes = 35 * 1024 * 1024
        oversized_files = [
            {"filename": f.name, "size_mb": f.stat().st_size / (1024 * 1024)}
            for f in files
            if f.stat().st_size > max_file_size_bytes
        ]

        # Get server-side estimation
        result = await self.client.call_tool(
            tool_name="estimate_ingestion_cost",
            arguments={"file_sizes_bytes": file_sizes},
        )
        estimation = json.loads(result)

        # Build blocking issues list
        blocking_issues = []

        if oversized_files:
            blocking_issues.append(
                {
                    "type": "client_file_size_limit",
                    "message": f"{len(oversized_files)} file(s) exceed the 35 MB client limit",
                    "files": oversized_files,
                }
            )

        if estimation.get("would_exceed_limit"):
            blocking_issues.append(
                {
                    "type": "knowledge_points_limit",
                    "message": estimation.get(
                        "message", "Would exceed knowledge points limit"
                    ),
                    "suggestion": estimation.get("suggestion"),
                }
            )

        return {
            "can_ingest": len(blocking_issues) == 0,
            "files_count": len(files),
            "total_size_bytes": total_size,
            "total_size_mb": round(total_size_mb, 2),
            "estimated_knowledge_points": estimation.get(
                "estimated_knowledge_points", 0
            ),
            "current_usage": estimation.get("current_usage", 0),
            "remaining_points": estimation.get("remaining_points", 0),
            "points_after_ingestion": estimation.get("points_after_ingestion", 0),
            "would_exceed_limit": estimation.get("would_exceed_limit", False),
            "blocking_issues": blocking_issues,
            "oversized_files": oversized_files,
        }

    async def extract(
        self,
        text_or_documents: str | List[str],
        prompt_description: str,
        examples: List[Dict[str, Any]],
        extraction_passes: int = 1,
        max_workers: int = 10,
        max_char_buffer: int = 10000,
        use_schema_constraints: bool = False,
        generate_visualization: bool = False,
    ) -> Dict[str, Any]:
        """
        Extract structured information from documents using LangExtract.

        Uses few-shot examples to define extraction schema and extracts entities
        with precise source grounding (character positions). Supports processing
        URLs (including Google Drive) and text documents.

        Args:
            text_or_documents: Text or URL(s) to process
            prompt_description: Clear description of what to extract
            examples: List of few-shot examples defining the extraction schema.
                Each example should have:
                - "text": Sample text
                - "extractions": List of entity extractions with:
                    - "extraction_class": Entity type (e.g., "invoice_number")
                    - "extraction_text": Exact text to extract
                    - "attributes": Optional dict of entity attributes
            extraction_passes: Number of extraction passes for higher recall (default: 1)
            max_workers: Maximum parallel workers for long documents (default: 10)
            max_char_buffer: Character buffer size for chunking (default: 10000).
                Larger values = fewer chunks = faster but less precise.
                Smaller values = more chunks = slower but more precise.
            use_schema_constraints: Use strict schema constraints (default: False)
            generate_visualization: Generate HTML visualization (default: False)

        Returns:
            Dictionary with extraction results:
            - extraction_count: Number of entities extracted
            - model_used: LLM model name used for extraction
            - provider: LLM provider name
            - extractions: List of extracted entities with:
                - extraction_class: Entity type
                - extraction_text: Extracted text
                - attributes: Entity attributes
                - start_char: Starting character position
                - end_char: Ending character position
            - metadata: Extraction configuration metadata
            - html_visualization: Optional HTML with highlighted extractions

        Examples:
            >>> # Extract invoice information
            >>> async with Shadai(name="invoice-processing") as shadai:
            ...     result = await shadai.extract(
            ...         text_or_documents="https://example.com/invoice.pdf",
            ...         prompt_description="Extract invoice details",
            ...         examples=[
            ...             {
            ...                 "text": "Invoice #INV-001 dated 2024-01-15...",
            ...                 "extractions": [
            ...                     {
            ...                         "extraction_class": "invoice_number",
            ...                         "extraction_text": "INV-001",
            ...                         "attributes": {"field": "invoice_id"}
            ...                     },
            ...                     {
            ...                         "extraction_class": "date",
            ...                         "extraction_text": "2024-01-15",
            ...                         "attributes": {"field": "invoice_date"}
            ...                     }
            ...                 ]
            ...             }
            ...         ],
            ...         extraction_passes=2,
            ...         generate_visualization=True
            ...     )
            ...     print(f"Extracted {result['extraction_count']} entities")
        """
        if not self._session:
            raise ValueError("Shadai must be used as a context manager")

        extraction_tool = ExtractionTool(
            client=self.client,
            session_uuid=self._session.uuid,
            llm_model_uuid=self._session.llm_model_uuid,
        )
        return await extraction_tool(
            text_or_documents=text_or_documents,
            prompt_description=prompt_description,
            examples=examples,
            extraction_passes=extraction_passes,
            max_workers=max_workers,
            max_char_buffer=max_char_buffer,
            use_schema_constraints=use_schema_constraints,
            generate_visualization=generate_visualization,
        )
