FROM python:3.8

WORKDIR /app

COPY requirements.txt .
RUN pip install --upgrade pip
RUN pip install -r requirements.txt
RUN pip install openai

COPY connect.py connect.py

CMD ["python", "connect.py"]