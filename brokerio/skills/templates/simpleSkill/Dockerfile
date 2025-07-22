FROM python:3.12

RUN pip install --upgrade pip

WORKDIR /app
COPY ./brokerio/skills/templates/simpleSkill .
RUN pip install -r ./requirements.txt

WORKDIR /broker
COPY ./brokerio ./brokerio
COPY ./setup.cfg ./setup.cfg
COPY ./pyproject.toml ./pyproject.toml
RUN pip install .

CMD ["python3", "/app/connect.py"]