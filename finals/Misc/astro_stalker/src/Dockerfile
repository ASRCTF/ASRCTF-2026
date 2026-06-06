# ── Base image ─────────────────────────────────────────────────────────────── #
FROM python:3.11-slim

# ── Working directory ───────────────────────────────────────────────────────── #
WORKDIR /app

# ── Install dependencies first (layer-cached) ──────────────────────────────── #
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# ── Copy challenge files ────────────────────────────────────────────────────── #
COPY server.py      .
COPY index.html     .
COPY app.js         .
COPY css/           css/
COPY assets/        assets/
COPY config/        config/

# ── Expose port ─────────────────────────────────────────────────────────────── #
EXPOSE 8000

# ── Non-root user for security ──────────────────────────────────────────────── #
RUN useradd -m -u 1001 ctf && chown -R ctf:ctf /app
USER ctf

# ── Start server ─────────────────────────────────────────────────────────────── #
CMD ["python", "server.py"]
