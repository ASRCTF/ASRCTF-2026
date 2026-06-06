FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY flag.txt /flag.txt
COPY . .

EXPOSE 5000

CMD ["python", "app.py"]
