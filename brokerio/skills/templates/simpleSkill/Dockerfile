FROM python:3.9

WORKDIR /broker
COPY . .

RUN pip install --upgrade pip
RUN pip install .

WORKDIR /app
COPY ./brokerio/skills/templates/simpleSkill .
RUN pip install -r ./requirements.txt

CMD ["python3", "/app/connect.py"]