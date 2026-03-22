"""
Mock Git commit batches simulating what CodePipeline passes after a merge.
Each commit is a dict with: id (short 7-char hash), message, author, timestamp, files_changed.
"""

from datetime import datetime, timedelta

# Base timestamp for generating realistic timestamps
BASE_TIME = datetime(2024, 3, 15, 10, 30, 0)

# Batch: feature_release - 5 commits adding a new payment feature
FEATURE_RELEASE = [
    {
        "id": "a1b2c3d",
        "message": "feat(payments): add Stripe payment integration for checkout",
        "author": "alice@company.com",
        "timestamp": (BASE_TIME - timedelta(hours=5)).isoformat(),
        "files_changed": [
            "src/payments/stripe_client.py",
            "src/payments/views.py",
            "src/payments/urls.py",
            "requirements.txt"
        ]
    },
    {
        "id": "e4f5g6h",
        "message": "fix(api): resolve null pointer in payment callback handler",
        "author": "bob@company.com",
        "timestamp": (BASE_TIME - timedelta(hours=4)).isoformat(),
        "files_changed": [
            "src/payments/callbacks.py",
            "tests/payments/test_callbacks.py"
        ]
    },
    {
        "id": "i7j8k9l",
        "message": "chore(deps): upgrade stripe library to v24.0.0",
        "author": "alice@company.com",
        "timestamp": (BASE_TIME - timedelta(hours=3)).isoformat(),
        "files_changed": [
            "requirements.txt",
            "package-lock.json"
        ]
    },
    {
        "id": "m0n1o2p",
        "message": "test(payments): add unit tests for refund flow",
        "author": "charlie@company.com",
        "timestamp": (BASE_TIME - timedelta(hours=2)).isoformat(),
        "files_changed": [
            "tests/payments/test_refund.py",
            "tests/payments/conftest.py"
        ]
    },
    {
        "id": "q3r4s5t",
        "message": "docs: update API docs with payment endpoints",
        "author": "diana@company.com",
        "timestamp": (BASE_TIME - timedelta(hours=1)).isoformat(),
        "files_changed": [
            "docs/api/payments.md",
            "docs/swagger.yaml"
        ]
    }
]

# Batch: hotfix_release - 2 commits for critical production bug fix
HOTFIX_RELEASE = [
    {
        "id": "u6v7w8x",
        "message": "hotfix(auth): fix token expiry causing immediate logout",
        "author": "bob@company.com",
        "timestamp": (BASE_TIME - timedelta(minutes=30)).isoformat(),
        "files_changed": [
            "src/auth/jwt_handler.py",
            "src/auth/middleware.py"
        ]
    },
    {
        "id": "y9z0a1b",
        "message": "fix(config): update production JWT secret from env",
        "author": "bob@company.com",
        "timestamp": (BASE_TIME - timedelta(minutes=15)).isoformat(),
        "files_changed": [
            "config/production.yaml",
            ".env.example"
        ]
    }
]

# Batch: infra_release - 4 commits for Terraform and K8s changes
INFRA_RELEASE = [
    {
        "id": "c2d3e4f",
        "message": "terraform: add RDS read replica for reporting database",
        "author": "ops@company.com",
        "timestamp": (BASE_TIME - timedelta(hours=8)).isoformat(),
        "files_changed": [
            "terraform/modules/database/main.tf",
            "terraform/modules/database/variables.tf",
            "terraform/prod/main.tf"
        ]
    },
    {
        "id": "g5h6i7j",
        "message": "kubernetes: update ingress controller to v1.9.0",
        "author": "ops@company.com",
        "timestamp": (BASE_TIME - timedelta(hours=7)).isoformat(),
        "files_changed": [
            "k8s/base/ingress-controller.yaml",
            "k8s/overlays/prod/kustomization.yaml"
        ]
    },
    {
        "id": "k8l9m0n",
        "message": "ci: add CodePipeline stage for security scanning",
        "author": "devops@company.com",
        "timestamp": (BASE_TIME - timedelta(hours=6)).isoformat(),
        "files_changed": [
            "codepipeline.yaml",
            "buildspecs/security-scan.yaml"
        ]
    },
    {
        "id": "o1p2q3r",
        "message": "terraform: configure auto-scaling for ECS tasks",
        "author": "ops@company.com",
        "timestamp": (BASE_TIME - timedelta(hours=5)).isoformat(),
        "files_changed": [
            "terraform/modules/ecs/main.tf",
            "terraform/modules/ecs/autoscaling.tf"
        ]
    }
]

# Batch: security_release - 3 commits patching CVE and security updates
SECURITY_RELEASE = [
    {
        "id": "s4t5u6v",
        "message": "security: patch CVE-2024-1234 in lodash dependency",
        "author": "security@company.com",
        "timestamp": (BASE_TIME - timedelta(hours=2)).isoformat(),
        "files_changed": [
            "package.json",
            "package-lock.json",
            "requirements.txt"
        ]
    },
    {
        "id": "w7x8y9z",
        "message": "security: rotate IAM keys and update secrets in Secrets Manager",
        "author": "security@company.com",
        "timestamp": (BASE_TIME - timedelta(hours=1)).isoformat(),
        "files_changed": [
            "terraform/iam/main.tf",
            "terraform/secrets/main.tf"
        ]
    },
    {
        "id": "a0b1c2d",
        "message": "security: add WAF rules to block SQL injection attacks",
        "author": "security@company.com",
        "timestamp": (BASE_TIME - timedelta(minutes=30)).isoformat(),
        "files_changed": [
            "terraform/waf/main.tf",
            "terraform/waf/rules.sql injection.tf"
        ]
    }
]

# Commit batches dictionary
COMMIT_BATCHES = {
    "feature_release": FEATURE_RELEASE,
    "hotfix_release": HOTFIX_RELEASE,
    "infra_release": INFRA_RELEASE,
    "security_release": SECURITY_RELEASE
}


def get_commits(batch: str) -> list:
    """
    Get the list of commit dicts for a given batch.

    Args:
        batch: The batch name (e.g., 'feature_release', 'hotfix_release')

    Returns:
        List of commit dictionaries
    """
    return COMMIT_BATCHES.get(batch, [])


def format_commits_for_prompt(commits: list) -> str:
    """
    Format commits for inclusion in prompt.
    Each commit shown as: [hash] message (author, timestamp)

    Args:
        commits: List of commit dictionaries

    Returns:
        Formatted string with one commit per line
    """
    lines = []
    for commit in commits:
        timestamp = commit['timestamp'].replace('T', ' ').split('.')[0]
        line = f"[{commit['id']}] {commit['message']} ({commit['author']}, {timestamp})"
        lines.append(line)
    return '\n'.join(lines)