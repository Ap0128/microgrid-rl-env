---
title: Microgrid RL Environment
emoji: ⚡
colorFrom: yellow
colorTo: green
sdk: docker
pinned: false
---

# ⚡ Microgrid RL Environment

An OpenEnv-compliant reinforcement learning environment for microgrid
energy management. An agent controls a battery + flexible loads
to minimize cost and prevent blackouts across 3 difficulty tasks.

## Quick Start

### Reset
POST /reset
{"task_id": "sunny_day", "seed": 42}

### Step
POST /step
{"session_id": "<id>", "action": {"battery_kw": 5.0, "curtail_fraction": 0.0}}

### Grade
POST /grader
{"session_id": "<id>"}

## Tasks
- sunny_day (easy)
- volatile_market (medium)
- islanded_crisis (hard)

## Docs
Visit /docs for Swagger UI.