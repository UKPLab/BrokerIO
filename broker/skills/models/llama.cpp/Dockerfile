FROM python:3.8

WORKDIR /app

COPY requirements.txt requirements.txt

RUN pip install --upgrade pip
RUN pip install -r requirements.txt

COPY app.py app.py

CMD ["python", "app.py"]