FROM python:3.11-slim
WORKDIR /app
RUN apt-get update && apt-get install -y --no-install-recommends libgl1 libglib2.0-0 && rm -rf /var/lib/apt/lists/*
COPY requirements.txt requirements-ai.txt ./
RUN pip install --no-cache-dir -r requirements-ai.txt
COPY . .
EXPOSE 5001
CMD ["gunicorn", "-b", "0.0.0.0:5001", "app:create_app()"]
