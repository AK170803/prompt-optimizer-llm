import requests
import os
from dotenv import load_dotenv
from prompts import OPTIMIZER_SYSTEM_PROMPT

load_dotenv()

# Config from .env
OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434/api/generate")
DEFAULT_MODEL = os.getenv("OLLAMA_MODEL", "mistral")
TIMEOUT = int(os.getenv("TIMEOUT", 180))


def call_ollama(prompt, model="mistral"):
    """
    Sends prompt to local Ollama model.
    """
    try:
        response = requests.post(
            OLLAMA_URL,
            json={
                "model": model,
                "prompt": prompt,
                "stream": False
            },
            timeout=TIMEOUT
        )

        if response.status_code != 200:
            return f"❌ Ollama Error: {response.text}"

        data = response.json()
        return clean_output(data.get("response", ""))

    except requests.exceptions.ConnectionError:
        return "❌ Ollama not running. Make sure it's active."

    except requests.exceptions.Timeout:
        return "❌ Model timeout. Try smaller model like 'mistral'."

    except Exception as e:
        return f"❌ Error: {str(e)}"


def clean_output(text):
    """
    Remove unwanted prefixes from model output.
    """
    if not text:
        return ""

    unwanted_phrases = [
        "Here is the optimized prompt:",
        "Optimized Prompt:",
        "Sure,",
        "Here’s",
    ]

    for phrase in unwanted_phrases:
        text = text.replace(phrase, "")

    return text.strip()


def is_valid_output(text):
    """
    Ensure model follows required structure.
    """
    required_sections = ["Role:", "Task:", "Context:", "Constraints:", "Output Format:"]
    return all(section in text for section in required_sections)


def optimize_prompt(user_prompt, model="mistral"):
    """
    Optimize user prompt with strict structure.
    """
    if not user_prompt or not user_prompt.strip():
        return "⚠️ Please enter a valid prompt."

    full_prompt = f"""
{OPTIMIZER_SYSTEM_PROMPT}

Original Prompt:
{user_prompt}

CRITICAL RULES:
- Preserve ALL details (names, intent, constraints)
- Do NOT generalize
- Expand vague instructions into clearer steps WITHOUT inventing new details

Return ONLY the optimized prompt.
"""

    result = call_ollama(full_prompt, model)

    # Validate structure
    if not is_valid_output(result):
        return "⚠️ Model output invalid. Try again."

    return result


def evaluate_prompt(prompt):
    """
    Rule-based prompt evaluation (less biased).
    """
    if not prompt:
        return "Score: 0/10\nReason: Empty prompt"

    score = 0
    reasons = []
    p = prompt.lower()

    # --- Structure (max 5) ---
    sections = ["role:", "task:", "context:", "constraints:", "output format:"]
    structure_score = sum(1 for s in sections if s in p)
    score += structure_score

    # --- Clarity (max 2) ---
    if len(prompt.split()) > 20:
        score += 1
    else:
        reasons.append("Too brief")

    if any(word in p for word in ["write", "generate", "summarize", "create", "explain"]):
        score += 1
    else:
        reasons.append("No clear action")

    # --- Specificity (max 2) ---
    if any(word in p for word in ["must", "should", "ensure", "include"]):
        score += 1
    else:
        reasons.append("Weak instructions")

    if "-" in prompt:
        score += 1
    else:
        reasons.append("No structured constraints")

    # --- Anti-meta check ---
    if any(x in p for x in [
        "rewrite the user's prompt",
        "improve the prompt",
        "optimize the prompt",
        "the user provided"
    ]):
        return "Score: 3/10\nReason: Meta prompt instead of actionable instruction"

    # --- Cap score if no structure ---
    if structure_score < 3:
        score = min(score, 6)

    return f"Score: {min(score, 10)}/10\nReason: {', '.join(reasons) if reasons else 'Good prompt'}"


def iterative_optimize(prompt, iterations=2, model="mistral"):
    """
    Multiple optimization passes.
    """
    current = prompt

    for _ in range(iterations):
        current = optimize_prompt(current, model)

    return current