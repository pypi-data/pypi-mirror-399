"""
REST API Endpoints for Async Job Queue

This module provides FastAPI endpoints for:
- Job submission (POST /api/jobs/optimize)
- Job status polling (GET /api/jobs/{job_id}/status)
- Job result retrieval (GET /api/jobs/{job_id}/result)
- Job listing (GET /api/jobs)
- Job cancellation (POST /api/jobs/{job_id}/cancel)

Following MCP Protocol:
- HATEOAS links for navigation
- Job resources exposed via job:// URIs
- Compatible with existing MCP tools

Following LangGraph Best Practices:
- Jobs execute Dame Workflow with TypedDict state
- Progress callbacks update JobState
- Checkpointing supports resumable workflows
"""

import json
import logging
import uuid
from typing import Dict, Any, Optional, List
from datetime import datetime, timezone

from fastapi import APIRouter, HTTPException, Query, Request
from fastapi.responses import Response
from pydantic import BaseModel, Field

from dcisionai_mcp_server.jobs import (
    # Schemas
    JobStatus,
    JobPriority,
    # Tasks
    run_optimization_job,
    cancel_job,
    get_task_status,
    # Storage
    create_job_record,
    get_job,
    get_all_jobs,
    get_jobs_by_session,
    get_jobs_by_status,
    get_job_statistics,
    get_job_files,
)

from dcisionai_mcp_server.resources.jobs import (
    read_job_resource,
    list_job_resources,
)

logger = logging.getLogger(__name__)

# Create FastAPI router
router = APIRouter(prefix="/api/jobs", tags=["jobs"])


# ========== REQUEST/RESPONSE MODELS ==========

class JobSubmitRequest(BaseModel):
    """Request body for job submission"""
    user_query: str = Field(..., description="Natural language optimization query")
    session_id: str = Field(..., description="Session identifier for context")
    priority: str = Field(default="normal", description="Job priority: low, normal, high, urgent")
    use_case: Optional[str] = Field(None, description="Optional use case hint (e.g., 'VRP', 'client_advisor_matching')")
    parameters: Optional[Dict[str, Any]] = Field(None, description="Optional additional parameters")


class JobSubmitResponse(BaseModel):
    """Response for job submission"""
    job_id: str = Field(..., description="Unique job identifier")
    status: str = Field(..., description="Current job status")
    priority: str = Field(..., description="Job priority")
    created_at: str = Field(..., description="Job creation timestamp (ISO 8601)")
    links: Dict[str, str] = Field(..., description="HATEOAS navigation links")


class JobStatusResponse(BaseModel):
    """Response for job status polling"""
    job_id: str
    session_id: str
    status: str
    priority: str
    created_at: str
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    user_query: str
    use_case: Optional[str] = None
    progress: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    links: Dict[str, str]


class JobResultResponse(BaseModel):
    """Response for job result retrieval"""
    job_id: str
    status: str
    completed_at: str
    result: Dict[str, Any]
    links: Dict[str, str]


class JobListResponse(BaseModel):
    """Response for job listing"""
    jobs: List[Dict[str, Any]]
    total: int
    page: int
    page_size: int
    links: Dict[str, str]


class JobCancelResponse(BaseModel):
    """Response for job cancellation"""
    job_id: str
    status: str
    cancelled_at: str
    message: str


# ========== ENDPOINTS ==========

@router.post("/submit", response_model=JobSubmitResponse, status_code=202)
async def submit_workflow_job(request: Request):
    """
    Submit a new optimization job (simplified endpoint for React client).

    This endpoint accepts workflow parameters from the React MCP client and dispatches
    them to the async job queue for background processing.

    **Expected Request Body from React Client:**
    ```json
    {
        "problem_description": "Optimize delivery routes...",
        "enabled_features": ["vagueness_detection", "template_matching"],
        "enabled_tools": ["intent_discovery", "data_preparation", "solver"],
        "reasoning_model": "claude-3-5-haiku-20241022",
        "code_model": "claude-3-5-sonnet-20241022",
        "enable_validation": false,
        "enable_templates": true,
        "use_claude_sdk_for_pyomo": true,
        "use_parallel_execution": false,
        "template_hint": null,
        "priority": "normal",
        "use_case": null
    }
    ```

    **Response (202 Accepted):**
    ```json
    {
        "job_id": "550e8400-e29b-41d4-a716-446655440000",
        "status": "queued",
        "priority": "normal",
        "created_at": "2025-12-08T12:00:00Z",
        "links": {
            "self": "/api/jobs/550e8400-e29b-41d4-a716-446655440000",
            "status": "/api/jobs/550e8400-e29b-41d4-a716-446655440000/status",
            "progress": "/api/jobs/550e8400-e29b-41d4-a716-446655440000/progress",
            "result": "/api/jobs/550e8400-e29b-41d4-a716-446655440000/result"
        }
    }
    ```
    """
    import json
    body = await request.json()

    logger.info(f"Received workflow job submission: {body.get('problem_description', '')[:100]}...")

    # Extract fields from request body
    problem_description = body.get("problem_description", "")
    if not problem_description:
        raise HTTPException(status_code=400, detail="problem_description is required")

    # Generate unique job ID
    job_id = str(uuid.uuid4())

    # Use a default session ID if not provided (React client doesn't send this)
    # Format: session_{job_id} so we can extract full job_id later
    session_id = body.get("session_id", f"session_{job_id}")

    # Validate priority
    priority_str = body.get("priority", "normal")
    try:
        priority = JobPriority[priority_str.upper()]
    except KeyError:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid priority: {priority_str}. Must be one of: low, normal, high, urgent"
        )

    # Prepare workflow parameters
    parameters = {
        "enabled_features": body.get("enabled_features", []),
        "enabled_tools": body.get("enabled_tools", []),
        "reasoning_model": body.get("reasoning_model", "claude-3-5-haiku-20241022"),
        "code_model": body.get("code_model", "claude-3-5-sonnet-20241022"),
        "enable_validation": body.get("enable_validation", False),
        "enable_templates": body.get("enable_templates", True),
        "use_claude_sdk_for_pyomo": body.get("use_claude_sdk_for_pyomo", True),
        "use_parallel_execution": body.get("use_parallel_execution", False),
        "template_hint": body.get("template_hint"),
    }

    use_case = body.get("use_case")

    # Create job record in database
    try:
        job_record = create_job_record(
            job_id=job_id,
            session_id=session_id,
            user_query=problem_description,
            priority=priority,
            use_case=use_case,
            parameters=parameters,
        )
        logger.info(f"Job record created: {job_id}")
    except Exception as e:
        logger.error(f"Failed to create job record: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to create job record: {str(e)}")

    # Dispatch to Celery (use job_id as task_id for consistency)
    try:
        task = run_optimization_job.apply_async(
            args=(job_id, problem_description, session_id),
            kwargs={
                "use_case": use_case,
                "parameters": parameters,
            },
            task_id=job_id,  # Use job_id as Celery task_id
            priority=priority.value,
        )
        logger.info(f"Job dispatched to Celery: {job_id} (task_id: {task.id})")
    except Exception as e:
        logger.error(f"Failed to dispatch job to Celery: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to dispatch job: {str(e)}")

    # Build HATEOAS links
    base_url = str(request.base_url).rstrip("/")
    links = {
        "self": f"{base_url}/api/jobs/{job_id}",
        "status": f"{base_url}/api/jobs/{job_id}/status",
        "progress": f"{base_url}/api/jobs/{job_id}/progress",
        "result": f"{base_url}/api/jobs/{job_id}/result",
    }

    return JobSubmitResponse(
        job_id=job_id,
        status=JobStatus.QUEUED.value,
        priority=priority.value,
        created_at=job_record["created_at"],
        links=links,
    )


@router.post("/optimize", response_model=JobSubmitResponse, status_code=202)
async def submit_optimization_job(request: JobSubmitRequest, http_request: Request):
    """
    Submit a new optimization job to the async queue.

    This endpoint accepts a natural language query and dispatches it to Celery
    for background processing. The job executes the Dame Workflow asynchronously,
    allowing the client to poll for status or subscribe to WebSocket updates.

    **Request Body:**
    ```json
    {
        "user_query": "Optimize delivery routes for 150 packages",
        "session_id": "user_session_123",
        "priority": "normal",
        "use_case": "VRP",
        "parameters": {}
    }
    ```

    **Response (202 Accepted):**
    ```json
    {
        "job_id": "550e8400-e29b-41d4-a716-446655440000",
        "status": "queued",
        "priority": "normal",
        "created_at": "2025-12-08T12:00:00Z",
        "links": {
            "self": "/api/jobs/550e8400-e29b-41d4-a716-446655440000",
            "status": "/api/jobs/550e8400-e29b-41d4-a716-446655440000/status",
            "stream": "/api/jobs/550e8400-e29b-41d4-a716-446655440000/stream",
            "cancel": "/api/jobs/550e8400-e29b-41d4-a716-446655440000/cancel"
        }
    }
    ```

    **HATEOAS Links:**
    - `self`: Job details endpoint
    - `status`: Job status polling endpoint
    - `stream`: WebSocket streaming endpoint
    - `cancel`: Job cancellation endpoint
    """
    logger.info(f"Received job submission: {request.user_query[:100]}...")

    # Generate unique job ID
    job_id = str(uuid.uuid4())

    # Validate priority
    try:
        priority = JobPriority[request.priority.upper()]
    except KeyError:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid priority: {request.priority}. Must be one of: low, normal, high, urgent"
        )

    # Create job record in database
    try:
        job_record = create_job_record(
            job_id=job_id,
            session_id=request.session_id,
            user_query=request.user_query,
            priority=priority,
            use_case=request.use_case,
            parameters=request.parameters,
        )
        logger.info(f"Job record created: {job_id}")
    except Exception as e:
        logger.error(f"Failed to create job record: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to create job record: {str(e)}")

    # Dispatch to Celery (use job_id as task_id for consistency)
    try:
        task = run_optimization_job.apply_async(
            args=(job_id, request.user_query, request.session_id),
            kwargs={
                "use_case": request.use_case,
                "parameters": request.parameters,
            },
            task_id=job_id,  # Use job_id as Celery task_id
            priority=priority.value,
        )
        logger.info(f"Job dispatched to Celery: {job_id} (task_id: {task.id})")
    except Exception as e:
        logger.error(f"Failed to dispatch job to Celery: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to dispatch job: {str(e)}")

    # Build HATEOAS links
    base_url = str(http_request.base_url).rstrip("/")
    links = {
        "self": f"{base_url}/api/jobs/{job_id}",
        "status": f"{base_url}/api/jobs/{job_id}/status",
        "stream": f"{base_url}/api/jobs/{job_id}/stream",
        "cancel": f"{base_url}/api/jobs/{job_id}/cancel",
    }

    return JobSubmitResponse(
        job_id=job_id,
        status=JobStatus.QUEUED.value,
        priority=priority.value,
        created_at=job_record["created_at"],
        links=links,
    )


@router.get("", response_model=JobListResponse)
async def list_jobs(
    session_id: Optional[str] = Query(None, description="Filter by session ID"),
    status: Optional[str] = Query(None, description="Filter by status"),
    page: int = Query(1, ge=1, description="Page number (1-indexed)"),
    page_size: int = Query(20, ge=1, le=100, description="Number of jobs per page"),
    http_request: Request = None,
):
    """
    List jobs with optional filtering and pagination.

    **Query Parameters:**
    - `session_id`: Filter jobs by session ID
    - `status`: Filter jobs by status (queued, running, completed, failed, cancelled)
    - `page`: Page number (1-indexed)
    - `page_size`: Number of jobs per page (max 100)

    **Example Request:**
    ```
    GET /api/jobs?session_id=user_session_123&status=completed&page=1&page_size=20
    ```

    **Response:**
    ```json
    {
        "jobs": [
            {
                "job_id": "550e8400-e29b-41d4-a716-446655440000",
                "status": "completed",
                "priority": "normal",
                "created_at": "2025-12-08T12:00:00Z",
                "completed_at": "2025-12-08T12:05:00Z",
                "user_query": "Optimize delivery routes..."
            },
            ...
        ],
        "total": 45,
        "page": 1,
        "page_size": 20,
        "links": {
            "self": "/api/jobs?session_id=user_session_123&page=1&page_size=20",
            "next": "/api/jobs?session_id=user_session_123&page=2&page_size=20"
        }
    }
    ```
    """
    logger.info(f"Listing jobs: session_id={session_id}, status={status}, page={page}, page_size={page_size}")

    # Get jobs based on filters
    if session_id and status:
        # Filter by both session and status
        all_jobs = get_jobs_by_session(session_id, limit=1000)
        jobs = [j for j in all_jobs if j["status"] == status]
    elif session_id:
        # Filter by session only
        jobs = get_jobs_by_session(session_id, limit=1000)
    elif status:
        # Filter by status only
        try:
            status_enum = JobStatus[status.upper()]
            jobs = get_jobs_by_status(status_enum, limit=1000)
        except KeyError:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid status: {status}. Must be one of: queued, running, completed, failed, cancelled"
            )
    else:
        # No filters - get all jobs
        jobs = get_all_jobs(limit=1000)

    # Pagination
    total = len(jobs)
    start_idx = (page - 1) * page_size
    end_idx = start_idx + page_size
    page_jobs = jobs[start_idx:end_idx]

    # Simplify job records for list response
    simplified_jobs = []
    for job in page_jobs:
        simplified_jobs.append({
            "job_id": job["job_id"],
            "status": job["status"],
            "priority": job["priority"],
            "created_at": job["created_at"],
            "started_at": job["started_at"],
            "completed_at": job["completed_at"],
            "user_query": job["user_query"],
            "use_case": job["use_case"],
        })

    # Build HATEOAS links
    base_url = str(http_request.base_url).rstrip("/")
    query_params = []
    if session_id:
        query_params.append(f"session_id={session_id}")
    if status:
        query_params.append(f"status={status}")

    query_string = "&".join(query_params)
    links = {
        "self": f"{base_url}/api/jobs?{query_string}&page={page}&page_size={page_size}",
    }

    # Add next/prev links
    if end_idx < total:
        links["next"] = f"{base_url}/api/jobs?{query_string}&page={page + 1}&page_size={page_size}"
    if page > 1:
        links["prev"] = f"{base_url}/api/jobs?{query_string}&page={page - 1}&page_size={page_size}"

    return JobListResponse(
        jobs=simplified_jobs,
        total=total,
        page=page,
        page_size=page_size,
        links=links,
    )


@router.get("/{job_id}/status", response_model=JobStatusResponse)
async def get_job_status(job_id: str, http_request: Request):
    """
    Get current job status (polling endpoint).

    This endpoint returns the current status, progress, and metadata for a job.
    Clients can poll this endpoint periodically to check job progress, or use
    the WebSocket endpoint for real-time updates.

    **Response:**
    ```json
    {
        "job_id": "550e8400-e29b-41d4-a716-446655440000",
        "session_id": "user_session_123",
        "status": "running",
        "priority": "normal",
        "created_at": "2025-12-08T12:00:00Z",
        "started_at": "2025-12-08T12:00:05Z",
        "completed_at": null,
        "user_query": "Optimize delivery routes...",
        "progress": {
            "current_step": "data_generation",
            "progress_percentage": 45,
            "step_details": {"tables": 3},
            "updated_at": "2025-12-08T12:00:30Z"
        },
        "error": null,
        "links": {
            "self": "/api/jobs/550e8400-e29b-41d4-a716-446655440000/status",
            "stream": "/api/jobs/550e8400-e29b-41d4-a716-446655440000/stream",
            "cancel": "/api/jobs/550e8400-e29b-41d4-a716-446655440000/cancel"
        }
    }
    ```

    **Status Values:**
    - `queued`: Job is waiting to be processed
    - `running`: Job is currently executing
    - `completed`: Job finished successfully
    - `failed`: Job encountered an error
    - `cancelled`: Job was cancelled by user
    """
    logger.info(f"Getting status for job: {job_id}")

    # Get job from storage
    job_record = get_job(job_id)
    if not job_record:
        raise HTTPException(status_code=404, detail=f"Job not found: {job_id}")

    # Parse progress if available
    import json
    progress = None
    if job_record["progress"]:
        progress = json.loads(job_record["progress"])

    # Build HATEOAS links
    base_url = str(http_request.base_url).rstrip("/")
    links = {
        "self": f"{base_url}/api/jobs/{job_id}/status",
        "stream": f"{base_url}/api/jobs/{job_id}/stream",
    }

    # Add result link if completed
    if job_record["status"] == JobStatus.COMPLETED.value:
        links["result"] = f"{base_url}/api/jobs/{job_id}/result"
    elif job_record["status"] in [JobStatus.QUEUED.value, JobStatus.RUNNING.value]:
        links["cancel"] = f"{base_url}/api/jobs/{job_id}/cancel"

    return JobStatusResponse(
        job_id=job_id,
        session_id=job_record["session_id"],
        status=job_record["status"],
        priority=job_record["priority"],
        created_at=job_record["created_at"],
        started_at=job_record["started_at"],
        completed_at=job_record["completed_at"],
        user_query=job_record["user_query"],
        use_case=job_record["use_case"],
        progress=progress,
        error=job_record["error"],
        links=links,
    )


@router.get("/{job_id}/progress")
async def get_job_progress(job_id: str):
    """
    Get job progress for real-time updates (simplified endpoint for React client).

    Returns the progress field from the job record, if available.

    **Response:**
    ```json
    {
        "job_id": "550e8400-e29b-41d4-a716-446655440000",
        "progress_percentage": 45,
        "current_step": "data_generation",
        "step_details": {"tables": 3},
        "updated_at": "2025-12-08T12:00:30Z"
    }
    ```
    """
    logger.info(f"Getting progress for job: {job_id}")

    # Get job from storage
    job_record = get_job(job_id)
    if not job_record:
        raise HTTPException(status_code=404, detail=f"Job not found: {job_id}")

    # Parse progress if available
    import json
    progress = None
    if job_record["progress"]:
        progress = json.loads(job_record["progress"])

    if not progress:
        # Return minimal progress if none available
        return {
            "job_id": job_id,
            "progress_percentage": 0,
            "current_step": None,
            "step_details": None,
            "updated_at": job_record["created_at"]
        }

    # Add job_id to progress response
    progress["job_id"] = job_id
    return progress


@router.get("/{job_id}/result", response_model=JobResultResponse)
async def get_job_result(job_id: str, http_request: Request):
    """
    Get final job result (only available for completed jobs).

    This endpoint returns the complete workflow result including intent discovery,
    data generation, solver optimization, and business explanation.

    **Response:**
    ```json
    {
        "job_id": "550e8400-e29b-41d4-a716-446655440000",
        "status": "completed",
        "completed_at": "2025-12-08T12:05:00Z",
        "result": {
            "status": "completed",
            "workflow_state": {
                "intent": {...},
                "data_pack": {...},
                "solver_output": {...},
                "explanation": {...}
            },
            "mcp_resources": {
                "status": "job://550e8400-e29b-41d4-a716-446655440000/status",
                "result": "job://550e8400-e29b-41d4-a716-446655440000/result",
                "intent": "job://550e8400-e29b-41d4-a716-446655440000/intent",
                "data": "job://550e8400-e29b-41d4-a716-446655440000/data",
                "solver": "job://550e8400-e29b-41d4-a716-446655440000/solver",
                "explanation": "job://550e8400-e29b-41d4-a716-446655440000/explanation"
            }
        },
        "links": {
            "self": "/api/jobs/550e8400-e29b-41d4-a716-446655440000/result",
            "status": "/api/jobs/550e8400-e29b-41d4-a716-446655440000/status"
        }
    }
    ```

    **MCP Resources:**
    All job artifacts are exposed as MCP resources using the `job://` URI scheme.
    """
    logger.info(f"Getting result for job: {job_id}")

    # Get job from storage
    job_record = get_job(job_id)
    if not job_record:
        raise HTTPException(status_code=404, detail=f"Job not found: {job_id}")

    # Check if job is completed
    if job_record["status"] != JobStatus.COMPLETED.value:
        raise HTTPException(
            status_code=409,
            detail=f"Job not completed (status: {job_record['status']}). Result not available."
        )

    # Parse result
    import json
    if not job_record["result"]:
        raise HTTPException(
            status_code=500,
            detail=f"Job marked as completed but has no result"
        )

    result = json.loads(job_record["result"])
    
    # CRITICAL: Include thinking_history from progress if not already in workflow_state
    # This ensures CoT is restored on page reload (same logic as MCP resource handler)
    workflow_state = result.get("workflow_state", {})
    if not workflow_state.get("thinking_history"):
        # Try to get thinking_history from progress field
        progress_data = job_record.get("progress")
        if progress_data:
            # Progress might be stored as JSON string or dict
            if isinstance(progress_data, str):
                try:
                    progress = json.loads(progress_data)
                except (json.JSONDecodeError, TypeError):
                    progress = None
            else:
                progress = progress_data
            
            if progress and isinstance(progress, dict):
                thinking_history = progress.get("thinking_history", {})
                if thinking_history:
                    # Add thinking_history to workflow_state
                    workflow_state["thinking_history"] = thinking_history
                    result["workflow_state"] = workflow_state
                    logger.debug(f"✅ Added thinking_history to REST API result for job {job_id} ({len(thinking_history)} steps)")
    
    # CRITICAL: Include llm_metrics from database if not already in result
    # Metrics are stored separately in llm_metrics column
    if not result.get("llm_metrics") and job_record.get("llm_metrics"):
        try:
            llm_metrics_data = job_record.get("llm_metrics")
            if isinstance(llm_metrics_data, str):
                llm_metrics = json.loads(llm_metrics_data)
            else:
                llm_metrics = llm_metrics_data
            if llm_metrics:
                result["llm_metrics"] = llm_metrics
                logger.debug(f"✅ Added llm_metrics to REST API result for job {job_id}: {llm_metrics.get('total_calls', 0)} calls")
        except (json.JSONDecodeError, TypeError) as metrics_error:
            logger.warning(f"⚠️ Failed to parse llm_metrics for job {job_id}: {metrics_error}")

    # Build HATEOAS links
    base_url = str(http_request.base_url).rstrip("/")
    links = {
        "self": f"{base_url}/api/jobs/{job_id}/result",
        "status": f"{base_url}/api/jobs/{job_id}/status",
    }

    return JobResultResponse(
        job_id=job_id,
        status=job_record["status"],
        completed_at=job_record["completed_at"],
        result=result,
        links=links,
    )


class DeployModelRequest(BaseModel):
    """Request body for model deployment"""
    name: str = Field(..., description="Model name (e.g., 'Portfolio Optimization')")
    description: str = Field(..., description="Model description")
    domain: str = Field(default="general", description="Domain (e.g., 'private_equity', 'ria', 'logistics')")


class DeployModelResponse(BaseModel):
    """Response for model deployment"""
    status: str = Field(..., description="Deployment status")
    model_id: str = Field(..., description="Deployed model ID")
    message: str = Field(..., description="Deployment message")
    file_path: Optional[str] = Field(None, description="Path to deployed model file")
    version: Optional[str] = Field(None, description="Model version number")
    all_versions: Optional[list[str]] = Field(None, description="All versions of this model")


@router.get("/{job_id}/files")
async def get_job_files_endpoint(job_id: str):
    """
    Get all files for a job.
    
    Returns:
        Dict with:
        - file_contents: Dict mapping filename to content (small files <100KB stored in JSONB)
        - file_urls: Dict mapping filename to Supabase Storage URL (large files >=100KB)
        - saved_files_path: Local filesystem path (if available)
        - total_files: Total number of files
    """
    try:
        files = get_job_files(job_id)
        
        if not files or files.get('total_files', 0) == 0:
            raise HTTPException(
                status_code=404,
                detail=f"No files found for job {job_id}"
            )
        
        return {
            "job_id": job_id,
            "file_contents": files.get('file_contents', {}),
            "file_urls": files.get('file_urls', {}),
            "signed_urls": files.get('signed_urls', {}),  # Include signed URLs for private bucket files
            "saved_files_path": files.get('saved_files_path'),
            "total_files": files.get('total_files', 0),
            "files_in_jsonb": len(files.get('file_contents', {})),
            "files_in_storage": len(files.get('file_urls', {})),
            "bucket_is_private": files.get('bucket_is_private', True)
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get files for job {job_id}: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve files: {str(e)}"
        )


@router.post("/{job_id}/deploy", response_model=DeployModelResponse)
async def deploy_job_model(job_id: str, request: DeployModelRequest, http_request: Request):
    """
    Deploy a model from a completed job as a reusable model endpoint.
    
    This endpoint extracts the Pyomo model code from a completed job and registers it
    as a deployed model that can be invoked directly via the model registry.
    
    **Request Body:**
    ```json
    {
        "name": "Portfolio Optimization",
        "description": "Optimize multi-asset portfolio allocation",
        "domain": "private_equity"
    }
    ```
    
    **Response:**
    ```json
    {
        "status": "success",
        "model_id": "portfolio_optimization_v1",
        "message": "Model deployed successfully",
        "file_path": "dcisionai_workflow/models/portfolio_optimization_model.py"
    }
    ```
    """
    import json
    import os
    from pathlib import Path
    
    logger.info(f"🔍 Deploying model from job: {job_id}")
    
    # Query database directly to get fresh data and avoid cache issues
    from dcisionai_mcp_server.jobs.storage import supabase_client
    
    if not supabase_client:
        logger.error("❌ Supabase client not initialized")
        raise HTTPException(status_code=500, detail="Database not available")
    
    try:
        # Query database directly
        response = supabase_client.table("async_jobs").select("*").eq("job_id", job_id).execute()
        
        if not response.data or len(response.data) == 0:
            logger.error(f"❌ Job not found in database: {job_id}")
            raise HTTPException(status_code=404, detail=f"Job not found: {job_id}")
        
        row = response.data[0]
        logger.info(f"✅ Job found in database: {job_id}, status: {row.get('status')}")
        
        # Check if job is completed
        if row["status"] != JobStatus.COMPLETED.value:
            logger.warning(f"⚠️ Job {job_id} not completed (status: {row['status']})")
            raise HTTPException(
                status_code=409,
                detail=f"Job not completed (status: {row['status']}). Only completed jobs can be deployed."
            )
        
        # Get result from database (Supabase returns JSONB as dict)
        result = row.get("result")
        if not result:
            logger.error(f"❌ Job {job_id} marked as completed but has no result field")
            raise HTTPException(
                status_code=500,
                detail=f"Job marked as completed but has no result. The job may have completed with an error."
            )
        
        # Supabase returns JSONB as dict, but handle both cases
        if isinstance(result, str):
            try:
                result = json.loads(result)
            except (json.JSONDecodeError, TypeError) as e:
                logger.error(f"❌ Failed to parse job result JSON: {e}")
                raise HTTPException(status_code=500, detail=f"Failed to parse job result: {str(e)}")
        elif not isinstance(result, dict):
            logger.error(f"❌ Job result is not a dict or string: {type(result)}")
            raise HTTPException(status_code=500, detail=f"Job result has unexpected type: {type(result)}")
        
        logger.info(f"✅ Retrieved job result from database, type: {type(result)}, keys: {list(result.keys())}")
        workflow_state = result.get("workflow_state", {})
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Failed to query database for job {job_id}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to retrieve job from database: {str(e)}")
    
    if not workflow_state:
        logger.error(f"❌ No workflow_state in job result for {job_id}")
        logger.error(f"Result keys: {list(result.keys())}")
        raise HTTPException(
            status_code=500,
            detail=f"Job result does not contain workflow_state. Result keys: {list(result.keys())}"
        )
    
    # Log full structure for debugging
    logger.info(f"🔍 Deploying model from job {job_id}")
    logger.debug(f"Workflow state keys: {list(workflow_state.keys())}")
    
    # Extract model code from solver result
    model_code = None
    
    # Get solver_result (most common location)
    solver_result = workflow_state.get("solver_result") or workflow_state.get("claude_sdk_solver") or {}
    logger.info(f"Checking solver_result: type={type(solver_result)}, is_dict={isinstance(solver_result, dict)}")
    
    if isinstance(solver_result, dict):
        solver_keys = list(solver_result.keys())
        logger.info(f"Solver result keys: {solver_keys}")
        
        # Check solver status first
        solver_status = solver_result.get("status", "unknown")
        logger.info(f"🔍 Solver status: {solver_status}")
        
        # Log detailed structure for debugging
        logger.info(f"🔍 Detailed solver_result structure:")
        for key in solver_keys:
            value = solver_result.get(key)
            if isinstance(value, str):
                logger.info(f"  - {key}: str (length={len(value)})")
                if len(value) > 0 and key != "model_code":  # Don't preview model_code if it's huge
                    logger.info(f"    Preview: {value[:100]}...")
            elif isinstance(value, (list, dict)):
                logger.info(f"  - {key}: {type(value).__name__} (size={len(value)})")
            else:
                logger.info(f"  - {key}: {type(value).__name__} = {value}")
        
        model_code = solver_result.get("model_code")
        if model_code:
            logger.info(f"✅ Found model_code in solver_result.model_code: length={len(model_code)}")
        else:
            logger.warning(f"⚠️ solver_result exists but no model_code key. Available keys: {solver_keys}")
            logger.warning(f"⚠️ Solver status: {solver_status} - may indicate why model_code is missing")
    
    # 2. Check solver_output (alternative location)
    if not model_code:
        solver_output = workflow_state.get("solver_output", {})
        logger.info(f"Checking solver_output: type={type(solver_output)}")
        if isinstance(solver_output, dict):
            model_code = solver_output.get("model_code")
            if model_code:
                logger.info(f"✅ Found model_code in solver_output.model_code: length={len(model_code)}")
    
    # 3. Check claude_agent_work_dir - model code might be in a file
    if not model_code:
        work_dir = workflow_state.get("claude_agent_work_dir")
        if work_dir:
            logger.info(f"Checking work_dir for model files: {work_dir}")
            try:
                from pathlib import Path
                work_path = Path(work_dir)
                
                # Check if directory exists
                if not work_path.exists():
                    logger.warning(f"⚠️ Work directory does not exist: {work_dir}")
                else:
                    logger.info(f"✅ Work directory exists: {work_dir}")
                    # List all files in the directory
                    try:
                        all_files = list(work_path.iterdir())
                        logger.info(f"Files in work_dir: {[f.name for f in all_files if f.is_file()]}")
                    except Exception as list_error:
                        logger.warning(f"⚠️ Could not list work_dir files: {list_error}")
                
                model_file = work_path / "model.py"
                if model_file.exists():
                    model_code = model_file.read_text()
                    logger.info(f"✅ Read model code from file: {model_file}, length={len(model_code)}")
                else:
                    logger.warning(f"⚠️ Model file not found at {model_file}")
                    # Try other possible filenames
                    for filename in ["solve.py", "model_relaxed.py", "model_bounded.py"]:
                        alt_file = work_path / filename
                        if alt_file.exists():
                            model_code = alt_file.read_text()
                            logger.info(f"✅ Read model code from {filename}: length={len(model_code)}")
                            break
            except Exception as file_error:
                logger.error(f"❌ Error reading model file from work_dir {work_dir}: {file_error}", exc_info=True)
        else:
            logger.warning(f"⚠️ No claude_agent_work_dir in workflow_state")
    
    # 4. Check saved_files_path in solver_result
    if not model_code and isinstance(solver_result, dict):
        saved_files_path = solver_result.get("saved_files_path")
        if saved_files_path:
            logger.info(f"Checking saved_files_path: {saved_files_path}")
            try:
                from pathlib import Path
                saved_path = Path(saved_files_path)
                if saved_path.exists() and saved_path.is_dir():
                    model_file = saved_path / "model.py"
                    if model_file.exists():
                        model_code = model_file.read_text()
                        logger.info(f"✅ Read model code from saved_files_path: {model_file}, length={len(model_code)}")
            except Exception as file_error:
                logger.warning(f"⚠️ Could not read from saved_files_path {saved_files_path}: {file_error}")
    
    # 5. Check generated_files in solver_result
    if not model_code and isinstance(solver_result, dict):
        generated_files = solver_result.get("generated_files", [])
        logger.info(f"Checking generated_files: {generated_files}")
        for file_path in generated_files:
            if 'model.py' in file_path or 'solve.py' in file_path:
                try:
                    from pathlib import Path
                    # Handle both absolute and relative paths
                    if os.path.isabs(file_path):
                        full_path = Path(file_path)
                    else:
                        # Try relative to work_dir if available
                        work_dir = workflow_state.get("claude_agent_work_dir")
                        if work_dir:
                            full_path = Path(work_dir) / file_path
                        else:
                            full_path = Path(file_path)
                    
                    if full_path.exists():
                        model_code = full_path.read_text()
                        logger.info(f"✅ Read model code from generated_files: {file_path}, length={len(model_code)}")
                        break
                except Exception as file_error:
                    logger.warning(f"⚠️ Could not read generated file {file_path}: {file_error}")
    
    # 6. Check nested structures in solver_result
    if not model_code and isinstance(solver_result, dict):
        logger.info("Checking nested structures in solver_result...")
        for key in ['result', 'output', 'data', 'claude_agent_result', 'execution_result']:
            nested = solver_result.get(key, {})
            if isinstance(nested, dict):
                nested_keys = list(nested.keys())
                logger.debug(f"  Checking solver_result.{key}: keys={nested_keys}")
                if nested.get("model_code"):
                    model_code = nested.get("model_code")
                    logger.info(f"✅ Found model_code in solver_result.{key}: length={len(model_code)}")
                    break
    
    # 7. Check if model_code is stored directly in workflow_state
    if not model_code:
        model_code = workflow_state.get("model_code")
        if model_code:
            logger.info(f"✅ Found model_code directly in workflow_state: length={len(model_code)}")
    
    # Final check - log what we found
    if not model_code:
        logger.error(f"❌ No model_code found in job {job_id}")
        logger.error(f"Workflow state keys: {list(workflow_state.keys())}")
        if solver_result:
            solver_keys = list(solver_result.keys()) if isinstance(solver_result, dict) else []
            logger.error(f"Solver result keys: {solver_keys}")
            # Log a sample of solver_result to see structure
            if isinstance(solver_result, dict):
                logger.error(f"Solver result sample (first 3 keys): {dict(list(solver_result.items())[:3])}")
        
        raise HTTPException(
            status_code=400,
            detail=(
                f"No model code found in job result. "
                f"The job may not have generated a Pyomo model. "
                f"Solver result keys: {list(solver_result.keys()) if isinstance(solver_result, dict) else 'N/A'}"
            )
        )
    
    logger.info(f"✅ Model code extracted successfully: {len(model_code)} characters")
    
    # Extract default data/parameters from the successful job run
    default_data = {}
    try:
        # Look for data in various locations in workflow_state
        # 1. Check solver_result for fitted_data or data_pack
        if isinstance(solver_result, dict):
            default_data = solver_result.get("fitted_data") or solver_result.get("data_pack") or solver_result.get("data") or {}
        
        # 2. Check workflow_state for generated_data or data_pack
        if not default_data:
            default_data = workflow_state.get("generated_data") or workflow_state.get("data_pack") or workflow_state.get("data") or {}
        
        # 3. Check claude_agent_work_dir for problem_data.json (Claude SDK solver saves data here)
        if not default_data:
            work_dir = workflow_state.get("claude_agent_work_dir")
            if work_dir:
                try:
                    from pathlib import Path
                    work_path = Path(work_dir)
                    data_file = work_path / "problem_data.json"
                    if data_file.exists():
                        with open(data_file, 'r') as f:
                            default_data = json.load(f)
                        logger.info(f"✅ Read default data from problem_data.json in work_dir: {len(default_data)} keys")
                except Exception as file_error:
                    logger.warning(f"⚠️ Could not read problem_data.json from work_dir: {file_error}")
        
        # 4. Check for parameters in workflow_state
        if not default_data:
            params = workflow_state.get("parameters") or {}
            if params:
                default_data = {"parameters": params}
        
        # 5. Check data_pack in workflow_state (may be nested)
        if not default_data:
            # Check nested locations
            if isinstance(workflow_state.get("data_pack"), dict):
                default_data = workflow_state["data_pack"]
            # Check in entities or other nested structures
            entities = workflow_state.get("entities", {})
            if isinstance(entities, dict) and entities:
                # Entities might contain data
                default_data = entities
        
        # Ensure default_data has the expected structure
        # Don't wrap in 'parameters' if it's already structured or if model expects direct access
        if default_data and isinstance(default_data, dict):
            # Check if it's already wrapped
            if "parameters" not in default_data and len(default_data) > 0:
                # Check if keys look like they should be wrapped (scalars, indexed, etc.)
                has_structured_keys = any(key in default_data for key in ['scalars', 'indexed', 'sets', 'matrices'])
                if not has_structured_keys:
                    # For models that expect data['parameters'], wrap it
                    # But we'll detect this in _prepare_data_for_model based on model code
                    # So keep it as-is for now
                    pass
        
        logger.info(f"✅ Extracted default data with keys: {list(default_data.keys())[:10] if isinstance(default_data, dict) else 'N/A'}")
        if isinstance(default_data, dict) and "parameters" in default_data:
            params = default_data["parameters"]
            logger.info(f"   Parameters keys: {list(params.keys())[:10] if isinstance(params, dict) else 'N/A'}")
        elif isinstance(default_data, dict):
            logger.info(f"   Direct data keys (first 10): {list(default_data.keys())[:10]}")
    except Exception as e:
        logger.warning(f"⚠️ Failed to extract default data from job result: {e}", exc_info=True)
        default_data = {}
    
    # Generate model ID from name with versioning support
    base_name = request.name.lower().replace(' ', '_').replace('-', '_')
    
    # Check for existing versions and determine next version number
    from dcisionai_workflow.models.model_registry import MODEL_REGISTRY
    
    # Find all existing versions of this model
    existing_versions = []
    for existing_id in MODEL_REGISTRY.keys():
        if existing_id.startswith(f"{base_name}_v"):
            try:
                # Extract version number
                version_part = existing_id.rsplit('_v', 1)[1]
                version_num = int(version_part)
                existing_versions.append(version_num)
            except (ValueError, IndexError):
                # If version parsing fails, treat as v1
                if existing_id == f"{base_name}_v1":
                    existing_versions.append(1)
    
    # Determine next version number
    if existing_versions:
        next_version = max(existing_versions) + 1
    else:
        next_version = 1
    
    model_id = f"{base_name}_v{next_version}"
    
    logger.info(f"Deploying model as {model_id} (existing versions: {sorted(existing_versions) if existing_versions else 'none'})")
    
    # Generate file path (include version in filename to avoid conflicts)
    base_name = model_id.rsplit('_v', 1)[0]
    version = model_id.rsplit('_v', 1)[1] if '_v' in model_id else '1'
    model_filename = f"{base_name}_v{version}_model.py"
    model_file_path = f"dcisionai_workflow/models/{model_filename}"
    
    # Get project root (go up from dcisionai_mcp_server/api to project root)
    current_file = Path(__file__).resolve()
    project_root = current_file.parent.parent.parent
    full_model_path = project_root / model_file_path
    
    # Ensure models directory exists
    full_model_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Create model class wrapper
    class_name = "".join(word.capitalize() for word in model_id.rsplit('_v', 1)[0].split('_'))
    
    # Clean up model code - extract Python code if it's in markdown
    cleaned_code = model_code
    if "```python" in cleaned_code:
        start = cleaned_code.find("```python") + 9
        end = cleaned_code.find("```", start)
        if end > start:
            cleaned_code = cleaned_code[start:end].strip()
    elif "```" in cleaned_code:
        start = cleaned_code.find("```") + 3
        end = cleaned_code.find("```", start)
        if end > start:
            cleaned_code = cleaned_code[start:end].strip()
    
    # Store cleaned code as a class variable for retrieval
    # We'll embed it in the class definition
    model_code_repr = repr(cleaned_code)
    
    # Indent model code for use in build_model method
    indented_code = "\n".join("        " + line if line.strip() else line for line in cleaned_code.split("\n"))
    
    # Wrap model code in a class
    model_class_code = f'''"""
{request.description}

Deployed from job: {job_id}
Domain: {request.domain}
"""

import pyomo.environ as pyo
from typing import Dict, Any, Optional


class {class_name}:
    """
    {request.description}
    
    This model was deployed from job {job_id}.
    """
    
    def __init__(self, solver: str = "scip", **kwargs):
        """
        Initialize the model.
        
        Args:
            solver: Solver to use (default: scip)
            **kwargs: Additional model parameters (stored for use in build_model)
        """
        self.solver = solver
        self.model = None
        self.kwargs = kwargs
        self.is_ortools_model = False
        self.model_code_str = None
    
    def get_model_code(self) -> str:
        """
        Get the raw model code (Pyomo or OR-Tools).
        
        Returns:
            The original model code string
        """
        if self.model_code_str is None:
            # Store the actual model code using triple quotes to avoid quote issues
            # This handles code that contains single or double quotes
            self.model_code_str = {repr(cleaned_code)}
            # If it's a repr() string (starts and ends with quotes), eval it
            if isinstance(self.model_code_str, str) and len(self.model_code_str) > 2:
                if (self.model_code_str.startswith("'") and self.model_code_str.endswith("'")) or \
                   (self.model_code_str.startswith('"') and self.model_code_str.endswith('"')):
                    try:
                        self.model_code_str = eval(self.model_code_str)
                    except:
                        # If eval fails, it's already the actual code string
                        pass
        return self.model_code_str
    
    def build_model(self, data: Optional[Dict[str, Any]] = None):
        """
        Build the model from the deployed code (Pyomo or OR-Tools).
        
        This method executes the model code to create a model instance.
        For deployed models, this skips intent discovery and model generation.
        
        Args:
            data: Optional data dictionary for model parameters
        """
        # Store data for use in solve()
        self.build_data = data if data is not None else {{}}
        
        # Import pyomo - use a different name to avoid local variable shadowing
        import pyomo.environ as _pyomo_module
        
        # Execute the original model code
        # Reference module-level pyo explicitly to avoid UnboundLocalError
        exec_globals = {{"pyo": _pyomo_module, "data": data}}
        exec_globals.update(self.kwargs)
        
        # Execute the model code
        exec_locals = {{}}
        exec(
            {repr(cleaned_code)},
            exec_globals,
            exec_locals
        )
        
        # Extract model from executed code
        # Check for Pyomo model first
        if 'model' in exec_locals:
            self.model = exec_locals['model']
            self.is_ortools_model = False
        elif 'create_model' in exec_locals:
            create_model_func = exec_locals['create_model']
            # Always pass data, even if empty - create_model requires it
            # Use dict() instead of {{}} to avoid f-string syntax issues
            self.model = create_model_func(data if data is not None else dict())
            self.is_ortools_model = False
        else:
            # Check if code uses OR-Tools (ortools imports)
            model_code_str = self.get_model_code()
            if 'ortools' in model_code_str.lower() or 'from ortools' in model_code_str or 'main' in exec_locals:
                # OR-Tools model - store functions for later execution
                self.is_ortools_model = True
                # Store relevant functions from exec_locals
                self.ortools_functions = {k: v for k, v in exec_locals.items() if callable(v)}
                self.ortools_locals = exec_locals
                # For OR-Tools, we'll execute the main function or the entire script in solve()
                self.model = exec_locals.get('main') or exec_locals
            else:
                raise RuntimeError("Model code did not create a 'model' variable, 'create_model' function, or OR-Tools 'main' function")
    
    def solve(self, verbose: bool = False, time_limit: int = 60) -> Dict[str, Any]:
        """
        Solve the optimization model.
        
        Args:
            verbose: Print solver output
            time_limit: Time limit in seconds
            
        Returns:
            Dictionary with solution status and results
        """
        if not self.model and not self.is_ortools_model:
            raise RuntimeError("Model not built. Call build_model() first.")
        
        # Handle OR-Tools models differently
        if self.is_ortools_model:
            # For OR-Tools, we need to execute the code with data injected
            # The code expects data to be available, so we'll modify it to use the passed data
            import json
            import tempfile
            import os
            
            # Create a temporary file with the data
            # Use data from build_model() or fallback to empty dict
            data_to_use = getattr(self, 'build_data', {{}}) or {{}}
            temp_data_file = tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False)
            json.dump(data_to_use, temp_data_file, indent=2)
            temp_data_file.close()
            
            try:
                # Modify the model code to use the temp file
                model_code = self.get_model_code()
                # Replace hardcoded file paths with our temp file
                modified_code = model_code.replace(
                    "with open('/var/folders/",
                    f"with open('{temp_data_file.name}',"
                )
                # Also handle other common patterns
                modified_code = modified_code.replace(
                    "problem_data.json'",
                    f"{temp_data_file.name}'"
                )
                
                # Execute the modified code
                exec_globals = {{"__name__": "__main__"}}
                exec_locals = {{}}
                exec(modified_code, exec_globals, exec_locals)
                
                # Try to get results from main() if it exists
                if 'main' in exec_locals:
                    result = exec_locals['main']()
                    if isinstance(result, dict):
                        return {{
                            "status": result.get('status', 'optimal').lower(),
                            "objective_value": result.get('objective_value'),
                            "solution": result.get('routes') or result.get('solution', {{}}),
                            "solve_time": result.get('solve_time', 0),
                            "solver_used": "ortools"
                        }}
                
                # If no result from main(), return error
                return {{
                    "status": "error",
                    "message": "OR-Tools model execution did not return results",
                    "solve_time": 0,
                    "solver_used": "ortools"
                }}
            except Exception as e:
                return {{
                    "status": "error",
                    "message": str(e),
                    "solve_time": 0,
                    "solver_used": "ortools"
                }}
            finally:
                # Clean up temp file
                if os.path.exists(temp_data_file.name):
                    os.unlink(temp_data_file.name)
        
        # Pyomo model execution
        solver = pyo.SolverFactory(self.solver)
        if not solver.available():
            raise RuntimeError(f"Solver {{self.solver}} not available")
        
        solver.options['time_limit'] = time_limit
        
        result = solver.solve(self.model, tee=verbose)
        
        status = str(result.solver.status)
        termination_condition = str(result.solver.termination_condition)
        
        if status == "ok" and termination_condition in ["optimal", "feasible"]:
            return {{
                "status": "optimal" if termination_condition == "optimal" else "feasible",
                "objective_value": pyo.value(self.model.objective) if hasattr(self.model, 'objective') else None,
                "solution": {{}},
                "solve_time": result.solver.time if hasattr(result.solver, 'time') else 0,
                "solver_used": self.solver
            }}
        else:
            return {{
                "status": "error",
                "message": f"Solver status: {{status}}, termination: {{termination_condition}}",
                "solve_time": result.solver.time if hasattr(result.solver, 'time') else 0,
                "solver_used": self.solver
            }}
'''
    
    # Write model file
    try:
        with open(full_model_path, 'w') as f:
            f.write(model_class_code)
        logger.info(f"✅ Model file written: {full_model_path}")
    except Exception as e:
        logger.error(f"❌ Failed to write model file: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to write model file: {str(e)}")
    
    # Register model in registry with metadata and default data
    try:
        from dcisionai_workflow.models.model_registry import register_model
        register_model(
            model_id=model_id,
            file_path=model_file_path,
            class_name=class_name,
            module_name=model_filename.replace('.py', ''),
            name=request.name,
            description=request.description,
            domain=request.domain,
            default_data=default_data
        )
        logger.info(f"✅ Model registered: {model_id} (with metadata and default data)")
    except Exception as e:
        logger.error(f"❌ Failed to register model: {e}")
        # Try to clean up file
        try:
            os.remove(full_model_path)
        except:
            pass
        raise HTTPException(status_code=500, detail=f"Failed to register model: {str(e)}")
    
    # Get version info
    from dcisionai_workflow.models.model_registry import get_model_versions
    all_versions = get_model_versions(base_name)
    
    return DeployModelResponse(
        status="success",
        model_id=model_id,
        message=f"Model '{request.name}' deployed successfully as {model_id} (version {version} of {len(all_versions)} total versions)",
        file_path=model_file_path,
        version=version,
        all_versions=all_versions
    )


@router.get("/models/{model_id}/csv-template")
async def download_model_csv_template(model_id: str):
    """
    Download CSV template for a deployed model.
    
    Returns a CSV file showing the required data format with example values
    from the successful job run that created the model.
    
    Args:
        model_id: Model identifier (e.g., 'pharma_v1')
        
    Returns:
        CSV file download
    """
    try:
        from dcisionai_workflow.models.csv_template_generator import generate_csv_template_from_model_id
        
        csv_content = generate_csv_template_from_model_id(model_id)
        
        if not csv_content:
            raise HTTPException(
                status_code=404,
                detail=f"Model {model_id} not found or CSV template generation failed"
            )
        
        # Get model name for filename
        from dcisionai_workflow.models.model_registry import MODEL_METADATA
        metadata = MODEL_METADATA.get(model_id, {})
        model_name = metadata.get('name', model_id).replace(' ', '_').lower()
        
        filename = f"{model_name}_data_template.csv"
        
        return Response(
            content=csv_content,
            media_type="text/csv",
            headers={
                "Content-Disposition": f"attachment; filename={filename}"
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to generate CSV template for {model_id}: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate CSV template: {str(e)}"
        )


@router.post("/{job_id}/cancel", response_model=JobCancelResponse)
async def cancel_optimization_job(job_id: str):
    """
    Cancel a running or queued job.

    This endpoint terminates the Celery task and updates the job status to cancelled.
    Only jobs in `queued` or `running` status can be cancelled.

    **Response:**
    ```json
    {
        "job_id": "550e8400-e29b-41d4-a716-446655440000",
        "status": "cancelled",
        "cancelled_at": "2025-12-08T12:02:30Z",
        "message": "Job cancelled successfully"
    }
    ```
    """
    logger.info(f"Cancelling job: {job_id}")

    # Get job from storage
    job_record = get_job(job_id)
    if not job_record:
        raise HTTPException(status_code=404, detail=f"Job not found: {job_id}")

    # Check if job can be cancelled
    if job_record["status"] not in [JobStatus.QUEUED.value, JobStatus.RUNNING.value]:
        raise HTTPException(
            status_code=409,
            detail=f"Job cannot be cancelled (status: {job_record['status']}). Only queued/running jobs can be cancelled."
        )

    # Cancel via Celery
    try:
        cancel_job.apply_async(args=(job_id,))
        logger.info(f"Job cancellation dispatched: {job_id}")
    except Exception as e:
        logger.error(f"Failed to cancel job: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to cancel job: {str(e)}")

    return JobCancelResponse(
        job_id=job_id,
        status=JobStatus.CANCELLED.value,
        cancelled_at=datetime.now(timezone.utc).isoformat(),
        message="Job cancellation requested. Job will be terminated shortly.",
    )


@router.get("/workers/status")
async def get_worker_status():
    """
    Get Celery worker status for debugging.
    
    Returns information about active Celery workers and their status.
    """
    logger.info("Getting Celery worker status")
    
    try:
        from dcisionai_mcp_server.jobs.tasks import celery_app, get_active_jobs
        
        inspect = celery_app.control.inspect()
        
        # Get worker information
        active_workers = inspect.active() or {}
        registered_workers = inspect.registered() or {}
        scheduled_tasks = inspect.scheduled() or {}
        reserved_tasks = inspect.reserved() or {}
        
        # Get active jobs from our helper
        active_jobs_info = get_active_jobs()
        
        return {
            "workers": {
                "active_count": len(active_workers),
                "registered_count": len(registered_workers),
                "active_worker_names": list(active_workers.keys()),
                "registered_worker_names": list(registered_workers.keys()),
            },
            "tasks": {
                "active": {worker: len(tasks) for worker, tasks in active_workers.items()},
                "scheduled": {worker: len(tasks) for worker, tasks in scheduled_tasks.items()},
                "reserved": {worker: len(tasks) for worker, tasks in reserved_tasks.items()},
            },
            "active_jobs": active_jobs_info,
        }
    except Exception as e:
        logger.error(f"Failed to get worker status: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get worker status: {str(e)}")


@router.get("/statistics")
async def get_statistics():
    """
    Get job queue statistics.

    Returns aggregated statistics about jobs across all statuses.

    **Response:**
    ```json
    {
        "total_jobs": 145,
        "by_status": {
            "queued": 5,
            "running": 3,
            "completed": 120,
            "failed": 15,
            "cancelled": 2
        },
        "avg_completion_time_seconds": 285.5
    }
    ```
    """
    logger.info("Getting job statistics")

    try:
        stats = get_job_statistics()
        return stats
    except Exception as e:
        logger.error(f"Failed to get statistics: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get statistics: {str(e)}")


# ========== MCP RESOURCE ENDPOINTS ==========

@router.get("/{job_id}/resources")
async def get_job_mcp_resources(job_id: str):
    """
    List all available MCP resources for a job.

    Returns a list of MCP resource URIs (`job://job_id/resource_type`) that
    can be used to access job artifacts.

    **Response:**
    ```json
    {
        "job_id": "550e8400-e29b-41d4-a716-446655440000",
        "status": "completed",
        "resources": {
            "status": "job://550e8400-e29b-41d4-a716-446655440000/status",
            "progress": "job://550e8400-e29b-41d4-a716-446655440000/progress",
            "result": "job://550e8400-e29b-41d4-a716-446655440000/result",
            "intent": "job://550e8400-e29b-41d4-a716-446655440000/intent",
            "data": "job://550e8400-e29b-41d4-a716-446655440000/data",
            "solver": "job://550e8400-e29b-41d4-a716-446655440000/solver",
            "explanation": "job://550e8400-e29b-41d4-a716-446655440000/explanation"
        }
    }
    ```
    """
    logger.info(f"Getting MCP resources for job: {job_id}")

    try:
        resources = list_job_resources(job_id)
        return resources
    except KeyError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to get resources: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get resources: {str(e)}")


if __name__ == "__main__":
    # For testing the router independently
    import uvicorn
    from fastapi import FastAPI

    app = FastAPI(title="DcisionAI Job Queue API")
    app.include_router(router)

    logger.info("Starting job API test server...")
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
