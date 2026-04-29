"""
Explanation Module for Prompt Optimizer

Generates structured explanations comparing original vs optimized prompts.
"""

from optimizer import call_ollama
from prompts import EXPLANATION_PROMPT


def detect_changes(original: str, optimized: str) -> list:
    """
    Basic heuristic signals to ground the explanation
    (prevents fully hallucinated reasoning)
    """
    changes = []

    if len(optimized) > len(original):
        changes.append("Added more detail and clarity")

    if any(word in optimized.lower() for word in ["format", "json", "table", "bullet", "steps"]):
        changes.append("Specified output format")

    if any(word in optimized.lower() for word in ["only", "strictly", "must", "limit"]):
        changes.append("Added constraints to control output")

    if len(original.split()) < len(optimized.split()):
        changes.append("Expanded instructions for better guidance")

    if not changes:
        changes.append("Improved overall structure and clarity")

    return changes


def generate_explanation(original: str, optimized: str, model: str = "llama3") -> str:
    """
    Generate explanation using Ollama LLM
    """

    # Step 1: Get grounded signals
    changes = detect_changes(original, optimized)
    changes_text = "\n".join([f"- {c}" for c in changes])

    # Step 2: Format prompt
    prompt = EXPLANATION_PROMPT.format(
        original=original,
        optimized=optimized,
        changes=changes_text
    )

    return call_ollama(prompt, model= "mistral")

    try:
        # Step 3: Call model
        response = ollama.generate(
            model=model,
            prompt=prompt,
            options={
                "temperature": 0.3,   # low = more deterministic
            }
        )

        return response.get("response", "").strip()

    except Exception as e:
        return f"⚠️ Error generating explanation: {str(e)}"