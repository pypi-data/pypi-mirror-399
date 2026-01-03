"""
LLM Metrics Aggregator Task

Separate Celery task that aggregates LLM metrics from Redis pub/sub
and stores them independently of workflow execution.

This prevents serialization issues and allows metrics to be tracked
asynchronously without affecting workflow performance.
"""

import os
import json
import logging
from typing import Dict, Any, Optional
from datetime import datetime

from dcisionai_mcp_server.jobs.tasks import celery_app
from dcisionai_mcp_server.jobs.storage import update_job_metrics
from dcisionai_mcp_server.jobs.schemas import LLMMetrics

logger = logging.getLogger(__name__)

# Redis configuration
# Railway provides both REDIS_URL (internal) and REDIS_PUBLIC_URL (external)
# Use REDIS_PUBLIC_URL if available (for external access), otherwise fall back to REDIS_URL
REDIS_URL = os.getenv("REDIS_PUBLIC_URL") or os.getenv("REDIS_URL", "redis://localhost:6379/0")


@celery_app.task(name="aggregate_llm_metrics", bind=True)
def aggregate_llm_metrics(self, job_id: str, session_id: str) -> Dict[str, Any]:
    """
    Aggregate LLM metrics for a job by subscribing to Redis pub/sub.

    This task:
    1. Subscribes to llm_metrics:{job_id} channel
    2. Collects all metric events until completion signal
    3. Aggregates metrics by step and model
    4. Stores aggregated metrics in database

    Args:
        job_id: Job identifier
        session_id: Session identifier

    Returns:
        Aggregated metrics dictionary
    """
    try:
        import redis
        redis_client = redis.from_url(REDIS_URL, decode_responses=True)
        pubsub = redis_client.pubsub()
        
        channel = f"llm_metrics:{job_id}"
        pubsub.subscribe(channel)
        logger.info(f"[MetricsAggregator] Subscribed to {channel} for job {job_id}")

        # Initialize aggregation structures
        calls: list[Dict[str, Any]] = []
        by_step: Dict[str, Dict[str, Any]] = {}
        by_model: Dict[str, Dict[str, Any]] = {}

        # Collect metrics until completion signal
        metrics_complete = False
        timeout_seconds = 7200  # 2 hours max
        start_time = datetime.utcnow()

        for message in pubsub.listen():
            # Check timeout
            elapsed = (datetime.utcnow() - start_time).total_seconds()
            if elapsed > timeout_seconds:
                logger.warning(f"[MetricsAggregator] Timeout waiting for metrics completion for job {job_id}")
                break

            if message["type"] == "message":
                try:
                    event = json.loads(message["data"])
                    event_type = event.get("type")

                    if event_type == "llm_metric":
                        # Aggregate metric
                        calls.append(event)
                        
                        # Update by_step aggregation
                        step_name = event.get("step_name")
                        if step_name:
                            if step_name not in by_step:
                                by_step[step_name] = {
                                    "calls": 0,
                                    "tokens_in": 0,
                                    "tokens_out": 0,
                                    "cost_usd": 0.0,
                                    "duration_seconds": 0.0,
                                }
                            by_step[step_name]["calls"] += 1
                            by_step[step_name]["tokens_in"] += event.get("tokens_in", 0)
                            by_step[step_name]["tokens_out"] += event.get("tokens_out", 0)
                            by_step[step_name]["cost_usd"] += event.get("cost_usd", 0.0)
                            if event.get("duration_seconds"):
                                by_step[step_name]["duration_seconds"] += event.get("duration_seconds", 0.0)

                        # Update by_model aggregation
                        model = event.get("model")
                        if model:
                            if model not in by_model:
                                by_model[model] = {
                                    "calls": 0,
                                    "tokens_in": 0,
                                    "tokens_out": 0,
                                    "cost_usd": 0.0,
                                }
                            by_model[model]["calls"] += 1
                            by_model[model]["tokens_in"] += event.get("tokens_in", 0)
                            by_model[model]["tokens_out"] += event.get("tokens_out", 0)
                            by_model[model]["cost_usd"] += event.get("cost_usd", 0.0)

                    elif event_type == "metrics_complete":
                        metrics_complete = True
                        logger.info(f"[MetricsAggregator] Received completion signal for job {job_id}")
                        break

                except json.JSONDecodeError as e:
                    logger.error(f"[MetricsAggregator] Failed to decode metric event: {e}")
                    continue
                except Exception as e:
                    logger.error(f"[MetricsAggregator] Error processing metric event: {e}", exc_info=True)
                    continue

        # Unsubscribe and close
        pubsub.unsubscribe(channel)
        pubsub.close()

        # Calculate totals
        total_calls = len(calls)
        total_tokens_in = sum(c.get("tokens_in", 0) for c in calls)
        total_tokens_out = sum(c.get("tokens_out", 0) for c in calls)
        total_cost_usd = round(sum(c.get("cost_usd", 0.0) for c in calls), 4)

        # Build aggregated metrics
        aggregated_metrics: LLMMetrics = {
            "total_calls": total_calls,
            "total_tokens_in": total_tokens_in,
            "total_tokens_out": total_tokens_out,
            "total_cost_usd": total_cost_usd,
            "by_step": by_step,
            "by_model": by_model,
        }

        # Store metrics in database
        try:
            update_job_metrics(job_id=job_id, metrics=aggregated_metrics)
            logger.info(
                f"[MetricsAggregator] ✅ Aggregated metrics for job {job_id}: "
                f"{total_calls} calls, {total_tokens_in:,} in, {total_tokens_out:,} out, "
                f"${total_cost_usd:.4f} USD"
            )
        except Exception as db_error:
            logger.error(f"[MetricsAggregator] ❌ Failed to store metrics for job {job_id}: {db_error}")

        return aggregated_metrics

    except Exception as e:
        logger.error(f"[MetricsAggregator] Failed to aggregate metrics for job {job_id}: {e}", exc_info=True)
        return {}

