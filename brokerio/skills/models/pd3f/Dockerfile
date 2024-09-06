FROM broker_simple_skill

WORKDIR /app

RUN apt-get update && apt-get upgrade -y
RUN pip install pd3f

COPY Skill.py Skill.py