"""
Main entry point for the AI Release Notes Generator.
Runs all four commit batches and generates release notes.
"""

import os
import sys

# Add the current directory to path to allow imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from mock_commits import get_commits, format_commits_for_prompt
from generator import generate_release_notes
from slack_notifier import post_release_to_slack


# Pipeline and environment configurations for each batch
BATCH_CONFIG = {
    "feature_release": {
        "pipeline_name": "my-app-pipeline",
        "environment": "production"
    },
    "hotfix_release": {
        "pipeline_name": "payment-service-pipeline",
        "environment": "production"
    },
    "infra_release": {
        "pipeline_name": "infra-pipeline",
        "environment": "staging"
    },
    "security_release": {
        "pipeline_name": "security-pipeline",
        "environment": "production"
    }
}

# List of batches to process
BATCHES = ["feature_release", "hotfix_release", "infra_release", "security_release"]


def main():
    """
    Run all four commit batches and generate release notes.
    """
    print("\n" + "=" * 70)
    print("AI RELEASE NOTES GENERATOR")
    print("=" * 70 + "\n")

    for batch in BATCHES:
        config = BATCH_CONFIG[batch]
        pipeline_name = config["pipeline_name"]
        environment = config["environment"]

        print(f"\n{'='*70}")
        print(f"BATCH: {batch}")
        print(f"Pipeline: {pipeline_name} | Environment: {environment}")
        print(f"{'='*70}\n")

        # Get commits for this batch
        commits = get_commits(batch)
        commits_text = format_commits_for_prompt(commits)

        print("Commits in this release:")
        print("-" * 70)
        print(commits_text)
        print("-" * 70)

        print("\nGenerating release notes...")

        try:
            # Generate release notes
            notes = generate_release_notes(commits_text, pipeline_name, environment)

            # Print raw release notes
            print("\nGenerated Release Notes:")
            print("-" * 70)
            for key in ['VERSION', 'DATE', 'TYPE', 'SUMMARY', 'CHANGES', 'TECHNICAL', 'IMPACT', 'ROLLBACK']:
                if key in notes:
                    print(f"{key}: {notes[key]}")
            print("-" * 70)

            # Post to Slack
            post_release_to_slack(notes, pipeline_name, environment)

        except Exception as e:
            print(f"\nERROR: Failed to generate release notes for {batch}")
            print(f"Error details: {e}\n")
            continue

        # Print separator between batches
        print("\n" + "=" * 70)
        print("BATCH COMPLETED")
        print("=" * 70 + "\n")

    print("\n" + "=" * 70)
    print("ALL BATCHES COMPLETED")
    print("=" * 70 + "\n")


if __name__ == "__main__":
    main()