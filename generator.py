"""
Main generator logic for release notes generation.
Uses OpenAI-compatible client (Ollama by default).
"""
import json
import logging
import time
from openai import OpenAI

import config
from prompts import SYSTEM_PROMPT, build_prompt

logging.basicConfig(
    level=getattr(logging, config.LOG_LEVEL, logging.INFO),
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
log = logging.getLogger(__name__)


def generate_release_notes(
    commits_text: str,
    pipeline_name: str,
    environment: str,
) -> dict:
    """
    Generate structured release notes from commit messages using an LLM.

    Args:
        commits_text: Formatted commit messages
        pipeline_name: Name of the pipeline
        environment: Deployment environment (e.g. prod, staging)

    Returns:
        Dictionary containing the release notes fields
    """
    user_message = build_prompt(commits_text, pipeline_name, environment)

    client = OpenAI(
        base_url=config.BASE_URL,
        api_key=config.API_KEY,
        timeout=config.TIMEOUT_SECONDS,
    )

    previous_outputs: list[str] = []
    retry_count = 0

    while retry_count < config.MAX_RETRIES:
        try:
            log.info("Calling LLM (attempt %d/%d)", retry_count + 1, config.MAX_RETRIES)
            response = client.chat.completions.create(
                model=config.MODEL,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": user_message},
                ],
                temperature=config.TEMPERATURE,
                max_tokens=config.MAX_TOKENS,
            )

            content = response.choices[0].message.content.strip()

            # Strip markdown fences if present
            if content.startswith("```json"):
                content = content[7:]
            elif content.startswith("```"):
                content = content[3:]
            if content.endswith("```"):
                content = content[:-3]
            content = content.strip()

            # Parse JSON
            try:
                release_notes = json.loads(content)
            except json.JSONDecodeError as exc:
                log.warning("JSON parse failed: %s. Retrying...", exc)
                retry_count += 1
                time.sleep(2 ** retry_count)
                continue

            # Validate required fields
            missing = [f for f in config.REQUIRED_FIELDS if f not in release_notes]
            if missing:
                log.warning("Missing required fields: %s. Retrying...", missing)
                retry_count += 1
                time.sleep(2 ** retry_count)
                continue

            # Loop detection
            content_key = json.dumps(release_notes, sort_keys=True)
            if content_key in previous_outputs:
                log.warning("Loop detected: identical output repeated. Retrying...")
                previous_outputs.clear()
                retry_count += 1
                time.sleep(2 ** retry_count)
                continue

            previous_outputs.append(content_key)
            if len(previous_outputs) >= config.LOOP_DETECTION_THRESHOLD:
                log.warning("Loop detection threshold reached. Using last output.")
                return release_notes

            log.info("Release notes generated successfully")
            return release_notes

        except Exception as exc:
            log.error("Error during generation: %s", exc)
            retry_count += 1
            if retry_count >= config.MAX_RETRIES:
                raise RuntimeError(
                    f"Failed after {config.MAX_RETRIES} retries: {exc}"
                ) from exc
            wait_time = 2 ** retry_count
            log.info("Retrying in %d seconds...", wait_time)
            time.sleep(wait_time)

    raise RuntimeError(
        f"Failed to generate valid release notes after {config.MAX_RETRIES} retries"
    )
