FROM python:3.12-slim-bullseye

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV PYTHONIOENCODING=UTF-8

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV QUIZ_URL="https://jsonkeeper.com/b/LLQT" \
    SUBMISSION_URL="https://api.jsonserve.com/rJvd7g" \
    HISTORICAL_URL="https://api.jsonserve.com/XgAgFJ" \
    GROQ_API_KEY="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"

CMD ["python", "./task1.py"]