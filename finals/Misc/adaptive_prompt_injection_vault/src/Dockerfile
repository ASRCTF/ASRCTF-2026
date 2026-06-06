FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 5000

# ── Environment Variables ───────────────────────────────────────────
#
#   ASRCTF_ADMIN_TOKEN       Token for the organizer dashboard (required)
#   OPENAI_API_KEYS          (optional) Override API keys in challenge.json
#   ASRCTF_SECRET_FLAG       (optional) Override the flag at runtime
#   OPENAI_BASE_URL          (optional) Override the API base URL
#   ASRCTF_BASE_MODEL        (optional) Override target model name
#   ASRCTF_JUDGE_MODEL       (optional) Override judge model name
#
# Example:
#   docker run -p 5000:5000 \
#     -e ASRCTF_ADMIN_TOKEN="changeme" \
#     asrctf-vault


CMD ["python", "main.py", "--host", "0.0.0.0", "--port", "5000"]
