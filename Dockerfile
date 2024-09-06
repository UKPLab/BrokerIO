FROM python:3.12.3-slim-bullseye
ARG ENV
ENV ENV=$ENV

# echo build type
RUN echo "ENV=$ENV"

# copy and install requirements
WORKDIR /
ADD requirements.txt requirements.txt
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# copy code and install
WORKDIR /
ADD . /broker
WORKDIR broker
RUN pip install .

# Generate private key if not exists
RUN if [ ! -f /broker/private_key.pem ]; then \
    openssl genrsa -out /broker/private_key.pem 2048; fi

# Add current dir to python path
ENV PYTHONPATH="${PYTHONPATH}:/broker"

CMD ["brokerio", "broker", "start"]