import logging
import os
import uuid
from collections import defaultdict
from enum import Enum
from typing import Any

import requests

from dojo_sdk_client.base_dojo_client import BaseDojoClient
from dojo_sdk_client.dojo_eval_client import DojoEvalClient, EvaluationResult
from dojo_sdk_client.engines import Engine

logger = logging.getLogger(__name__)


class BenchmarkTaskType(Enum):
    PASS_AT_K = "pass_at_k"
    PASS_POWER_K = "pass_power_k"


class BenchmarkTasks:
    def __init__(self, tasks: list[str], type: BenchmarkTaskType, k: int = 1):
        self.tasks = tasks
        self.type = type
        self.k = k
        if type is BenchmarkTaskType.PASS_AT_K:
            self.score_calc = pass_at_k_score
        elif type is BenchmarkTaskType.PASS_POWER_K:
            self.score_calc = pass_power_k_score
        else:
            raise ValueError(f"Invalid benchmark task type: {type}")

    def get_k_tasks(self) -> list[str]:
        """Expand tasks list to k copies of each task."""
        k_tasks = []
        for task in self.tasks:
            k_tasks.extend([task] * self.k)
        return k_tasks

    def get_score(self, results: list[EvaluationResult]) -> dict[str, float]:
        """Calculate scores for each task based on benchmark type."""
        return self.score_calc(results, self.k)

    def get_retry_tasks(self, task_completions: dict[str, dict]) -> list[str]:
        """Calculate which tasks need retry attempts to reach k successful completions."""
        tasks_to_retry = []
        for task in self.tasks:
            successful_count = task_completions[task]["successful"]
            needed = self.k - successful_count
            if needed > 0:
                tasks_to_retry.extend([task] * needed)
        return tasks_to_retry


class DojoBenchClient(BaseDojoClient):
    def submit_benchmark_score(
        self,
        job_id: str,
        score: float,
        bench_name: str,
        bench_version: str,
        model_name: str,
        provider: str,
        score_config: dict[str, Any],
    ) -> float:
        response = requests.post(
            f"{self.http_endpoint}/benchmarks/score",
            json={
                "job_id": job_id,
                "score": score,
                "score_config": score_config,
                "bench_name": bench_name,
                "bench_version": bench_version,
                "model_name": model_name,
                "model_provider": provider,
            },
            headers=self._get_headers(),
        )
        response.raise_for_status()
        return response.json()

    def get_job_tasks(self, job_id: str) -> dict:
        response = requests.get(
            f"{self.http_endpoint}/benchmarks/{job_id}/tasks",
            headers=self._get_headers(),
        )
        response.raise_for_status()
        return response.json()


def get_task_completions(job_tasks: dict) -> dict[str, dict]:
    """Group task executions by task_id and count successful vs failed completions."""
    task_completions = defaultdict(lambda: {"successful": 0, "failed": 0})
    failed_statuses = {"FAILED", "CANCELED", "TIMEOUT"}

    for task_exec in job_tasks["tasks"]:
        task_id = task_exec["task_id"]
        if task_exec["status"] in failed_statuses:
            task_completions[task_id]["failed"] += 1
        else:
            task_completions[task_id]["successful"] += 1

    return task_completions


def retry_bench(job_id: str, tasks: list[str], k: int = 1, model_name: str = None, provider: str = None) -> list[str]:
    """Check if any failed tasks need to be rerun for a benchmark job.

    Args:
        job_id: The job ID to check
        tasks: List of tasks to check for retries
        k: The number of successful completions required per task (default: 1)
        model_name: The model name to use for retry (optional, will validate against original)
        provider: The provider to use for retry (optional, will validate against original)

    Returns:
        List of task IDs that need to be retried to reach k successful completions

    Raises:
        ValueError: If model_name/provider is provided but doesn't match the original benchmark
    """
    bench_client = DojoBenchClient(api_key=os.getenv("DOJO_API_KEY"))

    # Get job tasks from server
    job_tasks = bench_client.get_job_tasks(job_id)
    print(f"job_tasks: {job_tasks}")
    if len(job_tasks) == 0:
        raise ValueError(f"No tasks found for job {job_id}")

    # Validate model and provider if provided
    benchmark_metadata = job_tasks.get("benchmark_metadata")
    if benchmark_metadata:
        original_model = benchmark_metadata.get("model_name")
        original_provider = benchmark_metadata.get("model_provider")

        if model_name is not None and original_model and model_name != original_model:
            raise ValueError(
                f"Model mismatch: attempting to retry with model '{model_name}' but original benchmark used '{original_model}'"
            )

        if provider is not None and original_provider and provider != original_provider:
            raise ValueError(
                f"Provider mismatch: attempting to retry with provider '{provider}' "
                f"but original benchmark used '{original_provider}'"
            )

        if model_name or provider:
            logger.info(
                f"Validated retry parameters match original benchmark: model='{original_model}', provider='{original_provider}'"
            )
    elif model_name or provider:
        logger.warning(
            f"No benchmark metadata found for job {job_id}. Cannot validate model/provider (may not be submitted yet)"
        )

    task_completions = get_task_completions(job_tasks)
    print(f"task_completions: {task_completions}")

    # Check all tasks for retries
    tasks_to_retry = []
    for task in tasks:
        if task in task_completions:
            successful_count = task_completions[task]["successful"]
            failed_count = task_completions[task]["failed"]
            needed = k - successful_count

            logger.info(
                f"Task '{task}' in job {job_id}: {successful_count} successful, "
                f"{failed_count} failed. Needs {max(0, needed)} more attempts to reach k={k}"
            )

            if needed > 0:
                tasks_to_retry.extend([task] * needed)
        else:
            logger.warning(f"Task '{task}' not found in job {job_id}")

    return tasks_to_retry


def pass_at_k_score(results: list[EvaluationResult], k: int) -> dict[str, float]:
    task_scores = {}
    for result in results:
        if result.task_id not in task_scores:
            task_scores[result.task_id] = result.score
        else:
            task_scores[result.task_id] = max(task_scores[result.task_id], result.score)
    return task_scores


def pass_power_k_score(results: list[EvaluationResult], k: int) -> dict[str, float]:
    task_scores = {}
    for result in results:
        if result.task_id not in task_scores:
            task_scores[result.task_id] = [result.score]
        task_scores[result.task_id].append(result.score)
    for task_id, scores in task_scores.items():
        task_scores[task_id] = 1.0 if all(score == 1.0 for score in scores) else 0.0
    return task_scores


async def run_eval(
    agent,
    engine: Engine,
    benchmark_tasks: BenchmarkTasks,
    bench_name: str = "dojo-bench-customer-colossus",
    bench_version: str = "1.0.0",
    num_runners: int = 50,
    max_retries: int = 2,
) -> float:
    """Run evaluation for a benchmark.

    Uses BenchmarkTasks abstraction to:
    - Expand tasks to k copies each
    - Calculate scores based on benchmark type
    - Determine retry tasks
    - Track successful/failed completions

    Retries failed/cancelled tasks to ensure k successful completions per task.
    """
    client = DojoEvalClient(agent, verbose=False, engine=engine)
    bench_client = DojoBenchClient(api_key=os.getenv("DOJO_API_KEY"))
    job_id = str(uuid.uuid4())

    logger.info(
        f"Running evaluation job {job_id} for {len(benchmark_tasks.tasks)} tasks "
        f"with {benchmark_tasks.k} rollouts per task ({benchmark_tasks.type.value})"
    )

    # Get k copies of each task
    k_tasks = benchmark_tasks.get_k_tasks()
    print(f"k_tasks: {k_tasks}")

    # Initial run
    results = await client.evaluate(tasks=k_tasks, num_runners=num_runners, job_id=job_id)

    # Retry loop for failed/cancelled tasks
    retry_attempt = 0
    while retry_attempt < max_retries:
        # Get actual task execution statuses from the server
        job_tasks = bench_client.get_job_tasks(job_id)
        logger.info(f"Job {job_id} tasks: {job_tasks}")
        task_completions = get_task_completions(job_tasks)

        # Calculate which tasks need retry attempts
        tasks_to_retry = benchmark_tasks.get_retry_tasks(task_completions)

        total_successful = sum(tc["successful"] for tc in task_completions.values())
        total_failed = sum(tc["failed"] for tc in task_completions.values())

        logger.info(
            f"Job {job_id}: {total_successful} successful, {total_failed} failed/cancelled. "
            f"{len(tasks_to_retry)} attempts needed to reach {benchmark_tasks.k} successful per task"
        )

        # If all tasks have k successful completions, we're done
        if not tasks_to_retry:
            logger.info(f"Job {job_id}: All {len(benchmark_tasks.tasks)} tasks have {benchmark_tasks.k} successful completions")
            break

        # Retry tasks that need more successful completions
        retry_attempt += 1
        logger.info(
            f"Job {job_id}: Retry attempt {retry_attempt}/{max_retries} - running {len(tasks_to_retry)} additional attempts"
        )
        retry_results = await client.evaluate(tasks=tasks_to_retry, num_runners=num_runners, job_id=job_id)
        results.extend(retry_results)

    # Final check - verify we have k successful completions per task
    job_tasks = bench_client.get_job_tasks(job_id)
    final_task_completions = get_task_completions(job_tasks)

    incomplete_tasks = [
        task for task in benchmark_tasks.tasks if final_task_completions[task]["successful"] < benchmark_tasks.k
    ]

    if incomplete_tasks:
        logger.error(
            f"Job {job_id}: {len(incomplete_tasks)} tasks do not have {benchmark_tasks.k} successful completions "
            f"after {retry_attempt} retries. Incomplete tasks: {incomplete_tasks[:5]}"
        )

    # Calculate final stats
    total_successful_attempts = sum(tc["successful"] for tc in final_task_completions.values())
    total_failed_attempts = sum(tc["failed"] for tc in final_task_completions.values())
    expected_attempts = len(benchmark_tasks.tasks) * benchmark_tasks.k

    # Calculate scores using benchmark's scoring function
    task_scores = benchmark_tasks.get_score(results)

    # Sum the scores across all tasks
    score = sum(task_scores.values())
    successful = len([s for s in task_scores.values() if s == 1.0])

    # Submission attempt is retry_attempt + 1 (1 = initial run, 2 = after 1 retry, etc.)
    submission_attempt = retry_attempt + 1

    bench_client.submit_benchmark_score(
        job_id=job_id,
        score=score / len(benchmark_tasks.tasks),
        bench_name=bench_name,
        bench_version=bench_version,
        model_name=agent.model,
        provider=agent.provider,
        score_config={
            "num_tasks": len(benchmark_tasks.tasks),
            "num_rollouts": benchmark_tasks.k,
            "successful": successful,
            "total_successful_attempts": total_successful_attempts,
            "total_failed_attempts": total_failed_attempts,
            "expected_attempts": expected_attempts,
            "retry_cycles": retry_attempt,
            "submission_attempt": submission_attempt,
            "metrics": {
                "type": benchmark_tasks.type.value,
                "k": benchmark_tasks.k,
                "version": f"v2.0-attempt{submission_attempt}",
            },
        },
    )
