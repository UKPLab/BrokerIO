FROM python:3.9

WORKDIR /app

COPY . .
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

CMD ["python3", "/app/connect.py"]