"""
Slack notifier for posting release announcements.
"""


def post_release_to_slack(notes: dict, pipeline_name: str, environment: str) -> None:
    """
    Print formatted Slack-style release announcement.

    Args:
        notes: Dictionary containing release notes fields
        pipeline_name: Name of the pipeline
        environment: Deployment environment
    """
    # Determine channel based on environment
    channel = f"#releases-{environment}" if environment != "production" else "#releases-prod"

    # Get release type for styling
    release_type = notes.get('TYPE', 'UNKNOWN')

    # Print Slack-style header
    print("\n" + "=" * 60)
    print("  SLACK RELEASE ANNOUNCEMENT")
    print("=" * 60)
    print(f"Channel: {channel}")
    print("-" * 60)

    # Special headers based on release type
    if release_type == "SECURITY" or release_type == "HOTFIX":
        print("\n  URGENT RELEASE NOTIFICATION")
        print(f"Pipeline: {pipeline_name} | Environment: {environment}")
    elif release_type == "FEATURE":
        print("\n  NEW FEATURE RELEASE")
        print(f"Pipeline: {pipeline_name} | Environment: {environment}")
    elif release_type == "INFRA":
        print("\n  INFRASTRUCTURE UPDATE")
        print(f"Pipeline: {pipeline_name} | Environment: {environment}")
    else:
        print(f"\n  RELEASE: {pipeline_name} | {environment}")

    print("-" * 60)

    # Print release details
    version = notes.get('VERSION', 'N/A')
    date = notes.get('DATE', 'N/A')
    summary = notes.get('SUMMARY', 'N/A')
    impact = notes.get('IMPACT', 'N/A')

    print(f"\n*Version:* {version}")
    print(f"*Date:* {date}")
    print(f"*Type:* {release_type}")
    print(f"*Impact:* {impact}")

    print("\n*_Summary:_*")
    print(f"_{summary}_")

    # Print CHANGES section
    changes = notes.get('CHANGES', '')
    if changes:
        print("\n*_Changes:_*")
        # Handle numbered list
        for line in changes.split('\n'):
            line = line.strip()
            if line:
                print(f"  - {line.lstrip('0123456789. ')}")

    # Print TECHNICAL section
    technical = notes.get('TECHNICAL', '')
    if technical:
        print("\n*_Technical Details:_*")
        for line in technical.split('\n'):
            line = line.strip()
            if line:
                print(f"  > {line.lstrip('0123456789. ')}")

    # Print ROLLBACK section
    rollback = notes.get('ROLLBACK', '')
    if rollback:
        print("\n*_Rollback:_*")
        print(f"_{rollback}_")

    print("\n" + "=" * 60)