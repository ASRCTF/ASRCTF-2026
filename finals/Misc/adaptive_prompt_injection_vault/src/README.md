# Adaptive Prompt Injection Vault (V2 External)

Welcome to the Organizer Guide for the Adaptive Prompt Injection Vault V2 challenge. 

## Overview
This challenge uses a **Dual-LLM architecture** where the participant attempts to prompt inject the Vault to leak a secret flag.

The architecture uses `llama-3.1-8b-instant` via the Groq API for both roles:
- **Target AI** (`llama-3.1-8b-instant`): The primary vault model that generates responses.
- **Security Judge AI** (`llama-3.1-8b-instant`): The overseer. It evaluates the Target AI's output to detect if any secrets or instructions were leaked.

## Active Guardrails
There are three stages of defense:
1. **Semantic Guardrail (TF-IDF)**: Detects high similarity to known prompt injection vectors.
2. **Admin Blocklist**: A dynamic list that automatically blocks prompts that successfully bypassed the filters in previous attempts.
3. **Security Judge AI**: A multi-part output judge:
   - **Static regex**: Catches verbatim flag strings.
   - **Static token detector**: Catches scattered individual flag tokens (e.g., the "fun facts" attack).
   - **Dynamic AI judge**: An LLM evaluator with flag-format-aware prompting.
   - **Grace Period**: The first flagged leak is allowed through to reward the fastest player. All subsequent flagged leaks are blocked.

## Deployment

### Docker (Recommended)
```bash
# Build the image
docker build -t asrctf-vault ./src

# Copy and edit the env file (API keys are pre-configured in challenge.json)
cp src/.env.example src/.env
# Edit .env with your admin token

# Run with env vars
docker run -p 5000:5000 --env-file src/.env asrctf-vault
```

### Local Development
```bash
cd src
pip install -r requirements.txt
# Set admin token (API keys are already in config/challenge.json)
export ASRCTF_ADMIN_TOKEN="your_token"
python main.py
```

## Prompt Logging & Diagnostics
Every prompt submitted to the Vault is classified and securely logged. You can view the comprehensive log of all interactions at:
`logs/all_prompts.jsonl`

The logs classify every interaction into one of the following categories:
- `SEMANTIC_GUARDRAIL_BLOCKED`: Caught by the initial filter.
- `ADMIN_BLOCKLIST_BLOCKED`: Blocked by the dynamic exact-match list.
- `JUDGE_AI_DENIED`: Flagged and blocked by the Security Judge AI.
- `JUDGE_AI_GRACE_ALLOWED`: Leaked the exact flag but allowed through because the grace period was not exceeded.
- `BENIGN_OR_BYPASS`: Standard conversation, or an obfuscated bypass that successfully tricked the Judge.

## Folder Structure
- `app/`: Contains the core Flask web server and backend runtime logic.
- `config/`: Contains the `challenge.json` configuration and the `prompt_bank.json` used by the Semantic Guardrail.
- `logs/`: Directory where all system logs, events, and prompt classifications are stored.
- `static/` & `templates/`: Frontend UI files for the Challenge interface and Organizer Dashboard.
- `tests/`: Unit test suite.
