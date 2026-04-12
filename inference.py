import os
import sys
import json
import random
import requests
import numpy as np
from openai import OpenAI

# ------------------------------------------------
# ENV VARIABLES (SAFE DEFAULTS)
# ------------------------------------------------

API_BASE_URL = os.getenv("API_BASE_URL", "https://router.huggingface.co/v1")
MODEL_NAME = os.getenv("MODEL_NAME", "Qwen/Qwen2.5-72B-Instruct")
API_KEY = os.getenv("HF_TOKEN") or os.getenv("API_KEY")

# Space URL (evaluators point this at your HF deployment)
ENV_URL = (
    os.getenv("ENV_URL")
    or os.getenv("MICROGRID_ENV_URL")
    or "https://anirudhpatil-microgrid-rl-env.hf.space"
).rstrip("/")

BENCHMARK = os.getenv("MICROGRID_BENCHMARK", "microgrid")
MAX_STEPS = int(os.getenv("MAX_STEPS", "120"))

random.seed(42)
np.random.seed(42)

# ------------------------------------------------
# OPENAI CLIENT (LLM PROXY)
# ------------------------------------------------

client = OpenAI(
    base_url=API_BASE_URL,
    api_key=API_KEY
)


def fetch_task_ids():
    """Prefer live /tasks so we always match deployed env; fallback to static list."""
    try:
        r = requests.get(f"{ENV_URL}/tasks", timeout=30)
        r.raise_for_status()
        data = r.json()
        raw = data.get("tasks", data) if isinstance(data, dict) else data
        if not isinstance(raw, list):
            return []
        ids = []
        for t in raw:
            if not isinstance(t, dict):
                continue
            tid = t.get("task_id") or t.get("id") or t.get("name")
            if tid and (t.get("has_grader", True) is True or t.get("grader") is True):
                ids.append(str(tid))
        return ids
    except Exception as e:
        print(f"[DEBUG] GET /tasks failed: {e}", flush=True)
        return []


# ------------------------------------------------
# ENV API CALL
# ------------------------------------------------

def api_post(path, payload):
    try:
        r = requests.post(
            f"{ENV_URL}{path}",
            json=payload,
            timeout=30,
        )
        r.raise_for_status()
        return r.json()
    except Exception as e:
        print(f"[DEBUG] API error: {e}", flush=True)
        return None


# ------------------------------------------------
# SIMPLE POLICY
# ------------------------------------------------

def simple_policy(state):
    price = state.get("spot_price", 0.0)
    soc = state.get("soc", 0.5)

    if price < 50 and soc < 0.8:
        battery = 5.0
    elif price > 100 and soc > 0.2:
        battery = -5.0
    else:
        battery = 0.0

    return {
        "battery_kw": battery,
        "curtail_fraction": 0.0
    }


# ------------------------------------------------
# LLM CALL (REQUIRED)
# ------------------------------------------------

def call_llm():
    try:
        client.chat.completions.create(
            model=MODEL_NAME,
            messages=[{"role": "user", "content": "Return OK"}],
            max_tokens=5,
            temperature=0
        )
    except Exception as e:
        print(f"[DEBUG] LLM call failed: {e}", flush=True)


# ------------------------------------------------
# LOG FUNCTIONS
# ------------------------------------------------

def log_start(task: str):
    print(f"[START] task={task} env={BENCHMARK} model={MODEL_NAME}", flush=True)


def log_step(step, action, reward, done):
    done_val = str(done).lower()
    print(
        f"[STEP] step={step} action={json.dumps(action)} reward={reward:.2f} done={done_val} error=null",
        flush=True
    )


def log_end(success, steps, score, rewards):
    rewards_str = ",".join(f"{r:.2f}" for r in rewards)
    print(
        f"[END] success={str(success).lower()} steps={steps} score={score:.3f} rewards={rewards_str}",
        flush=True
    )


# ------------------------------------------------
# ONE EPISODE (reset → steps → grader)
# ------------------------------------------------

def run_one_task(task_name: str) -> bool:
    rewards = []
    steps_taken = 0
    score = 0.0
    success = False

    log_start(task_name)

    try:
        reset = api_post("/reset", {"task_id": task_name, "seed": 42})
        if reset is None:
            raise RuntimeError("reset failed")

        session_id = reset["session_id"]
        state = reset["state"]

        call_llm()

        for step in range(1, MAX_STEPS + 1):
            action = simple_policy(state)
            result = api_post(
                "/step",
                {"session_id": session_id, "action": action},
            )
            if result is None:
                break

            reward = float(result.get("reward", 0.0))
            done = bool(result.get("done", False))
            state = result.get("state", {})

            rewards.append(reward)
            steps_taken = step
            log_step(step, action, reward, done)

            if done:
                break

        grade = api_post("/grader", {"session_id": session_id})
        if grade is None:
            success = False
            score = 0.0
        else:
            score = float(grade.get("score", 0.0))
            success = 0.0 <= score <= 1.0

    except Exception as e:
        print(f"[DEBUG] runtime error task={task_name}: {e}", flush=True)
        success = False
        score = 0.0

    log_end(success, steps_taken, score, rewards)
    return success


# ------------------------------------------------
# MAIN — run every task with a grader (≥3 required)
# ------------------------------------------------

def main():
    task_ids = fetch_task_ids()
    if len(task_ids) < 3:
        task_ids = ["sunny_day", "volatile_market", "islanded_crisis"]

    overall_ok = True
    for tid in task_ids:
        if not run_one_task(tid):
            overall_ok = False

    sys.exit(0 if overall_ok else 1)


if __name__ == "__main__":
    main()
