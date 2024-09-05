FROM python:3.9-slim

WORKDIR /app

COPY . /app

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 8192

CMD ["uvicorn", "core.app:app", "--host", "0.0.0.0", "--port", "8192", "--reload"]