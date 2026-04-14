"""
Main entry point for AI Release Notes Generator.
Supports CLI args to select pipelines and export results.
"""
import argparse
import json
import logging
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import config
from mock_commits import get_commits, get_pipeline_info
from generator import generate_release_notes
from slack_notifier import send_slack_notification

logging.basicConfig(
    level=getattr(logging, config.LOG_LEVEL, logging.INFO),
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
log = logging.getLogger(__name__)

ALL_PIPELINES = ["backend_api", "frontend_app", "data_pipeline", "mobile_app"]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="AI Release Notes Generator — convert Git commits to structured release notes"
    )
    parser.add_argument(
        "--pipelines",
        nargs="+",
        default=ALL_PIPELINES,
        choices=ALL_PIPELINES,
        help="Pipelines to generate release notes for (default: all)",
    )
    parser.add_argument(
        "--output-json",
        metavar="FILE",
        help="Write results summary to a JSON file",
    )
    parser.add_argument(
        "--no-slack",
        action="store_true",
        help="Skip Slack notification",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    pipelines = args.pipelines

    log.info("AI RELEASE NOTES GENERATOR")
    log.info("Processing %d pipeline(s): %s", len(pipelines), pipelines)

    results = []

    for pipeline in pipelines:
        log.info("--- Pipeline: %s ---", pipeline)

        try:
            commits_text = get_commits(pipeline)
            pipeline_name, environment = get_pipeline_info(pipeline)

            release_notes = generate_release_notes(commits_text, pipeline_name, environment)

            log.info(
                "Generated notes for %s: %s (%s)",
                pipeline,
                release_notes.get("TYPE", "UNKNOWN"),
                release_notes.get("VERSION", "v?.?.?"),
            )

            if not args.no_slack and config.SLACK_WEBHOOK_URL:
                send_slack_notification(release_notes, pipeline_name, environment)
                log.info("Slack notification sent")

            results.append({
                "pipeline": pipeline,
                "status": "success",
                "type": release_notes.get("TYPE"),
                "version": release_notes.get("VERSION"),
            })

        except Exception as exc:
            log.error("Failed for pipeline '%s': %s", pipeline, exc)
            results.append({"pipeline": pipeline, "status": "error", "error": str(exc)})

    success_count = sum(1 for r in results if r["status"] == "success")
    log.info("Completed: %d/%d succeeded", success_count, len(results))

    if args.output_json:
        with open(args.output_json, "w") as f:
            json.dump(results, f, indent=2)
        log.info("Results written to %s", args.output_json)


if __name__ == "__main__":
    main()
