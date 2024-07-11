FROM python:3.10-slim
WORKDIR /support_bot

COPY requirements.txt /support_bot

RUN pip install -r requirements.txt --no-cache-dir

COPY . /support_bot

CMD ["python3", "main.py"]