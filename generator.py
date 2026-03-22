"""
Main generator logic for release notes generation.
Uses OpenAI library pointing to Ollama at http://localhost:11434/v1
"""

import time
from openai import OpenAI

# Configuration constants
OLLAMA_BASE_URL = "http://localhost:11434/v1"
OLLAMA_API_KEY = "ollama"
OLLAMA_MODEL = "llama3.2"

# Required fields in output
REQUIRED_FIELDS = ['VERSION', 'DATE', 'TYPE', 'SUMMARY', 'CHANGES', 'TECHNICAL', 'IMPACT', 'ROLLBACK']

# Termination safety layers
TERMINATION_CONDITION_FIELDS = REQUIRED_FIELDS
MAX_RETRIES = 3
TIMEOUT_SECONDS = 90
LOOP_DETECTION_THRESHOLD = 3


def generate_release_notes(commits_text: str, pipeline_name: str, environment: str) -> dict:
    """
    Generate release notes from commit messages using Ollama.

    Args:
        commits_text: Formatted commit messages
        pipeline_name: Name of the pipeline
        environment: Deployment environment

    Returns:
        Dictionary containing the release notes fields
    """
    from prompts import SYSTEM_PROMPT, build_prompt

    # Build the user message
    user_message = build_prompt(commits_text, pipeline_name, environment)

    # Initialize the OpenAI client pointing to Ollama
    client = OpenAI(
        base_url=OLLAMA_BASE_URL,
        api_key=OLLAMA_API_KEY,
        timeout=TIMEOUT_SECONDS
    )

    # Track outputs for loop detection
    previous_outputs = []
    retry_count = 0

    while retry_count < MAX_RETRIES:
        try:
            # Make ONE LLM call
            response = client.chat.completions.create(
                model=OLLAMA_MODEL,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": user_message}
                ],
                temperature=0.2,
                max_tokens=2048
            )

            # Extract the generated content
            generated_content = response.choices[0].message.content

            # Clean up the response
            generated_content = generated_content.strip()

            # Parse the output into a dictionary
            notes = parse_release_notes(generated_content)

            # Layer 1: Check that all required fields are present
            missing_fields = [f for f in REQUIRED_FIELDS if f not in notes or not notes[f]]
            if missing_fields:
                print(f"Warning: Missing fields: {missing_fields}. Retrying...")
                retry_count += 1
                time.sleep(2 ** retry_count)  # Exponential backoff
                continue

            print("All required fields present!")
            print(f"VERSION: {notes.get('VERSION', 'N/A')}")
            print(f"TYPE: {notes.get('TYPE', 'N/A')}")

            # Layer 4: Loop detection
            output_str = str(notes)
            if output_str in previous_outputs:
                print("Loop detected: same output repeated. Retrying with different approach...")
                previous_outputs.clear()
                retry_count += 1
                time.sleep(2 ** retry_count)
                continue

            previous_outputs.append(output_str)

            # If we have 3 repeated outputs, break the loop
            if len(previous_outputs) >= LOOP_DETECTION_THRESHOLD:
                print("Loop detection threshold reached. Using last output.")
                break

            # Success - return the parsed notes
            return notes

        except Exception as e:
            print(f"Error during generation: {e}")
            retry_count += 1
            if retry_count >= MAX_RETRIES:
                raise Exception(f"Failed after {MAX_RETRIES} retries: {e}")
            # Exponential backoff
            wait_time = 2 ** retry_count
            print(f"Retrying in {wait_time} seconds...")
            time.sleep(wait_time)

    # If we exhaust retries, raise an exception
    raise Exception(f"Failed to generate valid release notes after {MAX_RETRIES} retries")


def parse_release_notes(content: str) -> dict:
    """
    Parse the release notes output from the LLM.

    Args:
        content: The raw output from the LLM

    Returns:
        Dictionary with release note fields
    """
    notes = {}
    lines = content.strip().split('\n')

    for line in lines:
        line = line.strip()
        if ':' in line:
            key = line.split(':')[0].strip()
            value = line.split(':', 1)[1].strip()
            notes[key] = value

    return notes