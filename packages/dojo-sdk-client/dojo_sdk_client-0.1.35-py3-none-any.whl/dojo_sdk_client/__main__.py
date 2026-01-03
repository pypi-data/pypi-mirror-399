import argparse
import asyncio
import logging
import os
import uuid

from .agents.seed_cua import SeedCUA, ThinkingMode
from .dojo_eval_client import DojoEvalClient
from .engines import Engine, select_engine
from .utils import DojoBenchClient, exclude_tasks, load_tasks_from_hf_dataset
from .utils.bench import BenchmarkTasks, BenchmarkTaskType, retry_bench, run_eval

API_KEY = os.getenv("DOJO_API_KEY")

logger = logging.getLogger(__name__)


##TODO: Run Anthropic 4 then Unrestricted Think
# claude-4-sonnet-20250514
# claude-sonnet-4-5-20250929
# agent = AnthropicCUA(model="claude-sonnet-4-5-20250929", image_context_length=4, verbose=False)
## agent = ExampleAgent()
model_name = os.getenv("MODEL_NAME")
api_key = os.getenv("MODEL_API_KEY")
model_base_url = os.getenv("MODEL_BASE_URL")
agent = SeedCUA(
    model=model_name,
    api_key=api_key,
    base_url=model_base_url,
    image_context_length=3,
    verbose=True,
    screen_size=(1920, 1080),
    thinking_mode=ThinkingMode.UNRESTRICTED_THINK,
)


async def main():
    """Main entry point for the dojo package."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(filename)s:%(lineno)s - %(message)s",
    )
    logger.info(f"Agent model: {agent.model}")

    parser = argparse.ArgumentParser(description="Dojo Client - Run AI agent evaluations")
    parser.add_argument(
        "--hf-dataset",
        type=str,
        help="HuggingFace dataset name to load tasks from (e.g., 'chakra-labs/dojo-bench-customer-colossus')",
    )
    parser.add_argument("--tasks", nargs="*", help="Specific tasks to run (e.g., 'action-tester/must-click')")
    parser.add_argument(
        "-p",
        action="store_true",
        help="Enable pass@k evaluation mode",
    )
    parser.add_argument(
        "-retry",
        action="store_true",
        default=False,
        help="Retry failed tasks (default: False)",
    )
    parser.add_argument(
        "--job-id",
        type=str,
        help="Job ID to retry (required when using -retry)",
    )
    parser.add_argument(
        "-k",
        type=int,
        default=5,
        help="Number of rollouts per task for pass@k evaluation (default: 5)",
    )
    parser.add_argument(
        "-r",
        type=str,
        default="main",
        help="Revision of the HuggingFace dataset to load tasks from (default: main)",
    )

    args = parser.parse_args()

    engine = select_engine(API_KEY)

    if args.retry:
        if not args.job_id:
            print("Job ID is required when using -retry")
            exit(1)
        print(f"Retrying failed tasks for job {args.job_id}")
        tasks = load_tasks_from_hf_dataset(args.hf_dataset, revision=args.r)
        tasks = exclude_tasks(tasks)
        tasks_to_retry = retry_bench(args.job_id, tasks, args.k, model_name=agent.model, provider=agent.provider)
        if not tasks_to_retry:
            print(f"No tasks to retry for job {args.job_id}")
            exit(1)
        print(f"Need to retry {len(tasks_to_retry)} tasks")
        client = DojoEvalClient(agent, verbose=False, engine=engine)
        await client.evaluate(tasks=tasks_to_retry, job_id=args.job_id, num_runners=min(40, len(tasks_to_retry)))
    elif args.p:
        print("Evaluating pass@k")
        tasks = load_tasks_from_hf_dataset(args.hf_dataset, revision=args.r)
        tasks = exclude_tasks(tasks)
        benchmark_tasks = BenchmarkTasks(tasks, BenchmarkTaskType.PASS_AT_K, args.k)
        await run_eval(agent, engine, benchmark_tasks, num_runners=min(50, len(tasks)))
    elif args.hf_dataset:
        print(f"Loading tasks from HuggingFace dataset: {args.hf_dataset}")
        tasks = exclude_tasks(args.tasks)
        await run_hf_dataset_tasks(args.hf_dataset, args.tasks, engine, revision=args.r)
    else:
        print("Evaluating by dojos")
        await by_task_name(args.tasks, engine, revision=args.r)


async def run_hf_dataset_tasks(
    dataset_name: str, specific_tasks: list[str] = None, engine: Engine = None, revision: str = "main"
):
    """Run tasks from HuggingFace dataset."""
    client = DojoEvalClient(agent, verbose=True, engine=engine, revision=revision)
    job_id = None

    if specific_tasks:
        # Use the specific tasks provided
        task_names = specific_tasks
        logger.info(f"Running {len(task_names)} specific tasks from HF dataset")
    else:
        # Load all tasks from the dataset
        task_names = load_tasks_from_hf_dataset(dataset_name)
        logger.info(f"Running all {len(task_names)} tasks from HF dataset")
        job_id = str(uuid.uuid4())

    logger.info("Tasks to run:")
    for task_name in task_names:
        logger.info(f"  - {task_name}")

    results = await client.evaluate(tasks=task_names, num_runners=50, job_id=job_id)
    bench_client = DojoBenchClient(api_key=os.getenv("DOJO_API_KEY"))
    score = sum(result.score for result in results)

    if job_id:
        bench_client.submit_benchmark_score(
            job_id=job_id,
            score=score / len(task_names),
            bench_name="dojo-bench-customer-colossus",
            bench_version="1.0.0",
            model_name=agent.model,
            provider=agent.provider,
            score_config={
                "num_tasks": len(task_names),
                "num_rollouts": 1,
                "successful": len([result for result in results if result.score > 0]),
            },
        )


async def by_task_name(specific_tasks: list[str] = None, engine: Engine = None, revision: str = "main"):
    """Run tasks using the traditional dojo loader."""
    client = DojoEvalClient(agent, verbose=True, engine=engine, revision=revision)

    if specific_tasks:
        task_names = specific_tasks
    else:
        # Default tasks for backward compatibility
        task_names = ["action-tester/must-complete-all-actions", "2048/get-256-tile", "tic-tac-toe/lose-game"]

    logger.info(f"Running {len(task_names)} tasks using traditional dojo loader")

    await client.evaluate(tasks=task_names, num_runners=1)


if __name__ == "__main__":
    asyncio.run(main())
