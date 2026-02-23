FROM python:3.10-slim

WORKDIR /app

# Copy the requirements first to speed up building
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of your code
COPY . .

# Match your filename: API_Ultimate_Final.py
CMD ["uvicorn", "main_api:app", "--host", "0.0.0.0", "--port", "8080"]