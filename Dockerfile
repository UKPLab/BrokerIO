FROM continuumio/miniconda3
ARG ENV
ENV ENV=$ENV

# COPY SERVER CODE
WORKDIR /
ADD . /broker

# INSTALL REQUIREMENTS
WORKDIR broker

# Install make
RUN apt update && apt install make

RUN set -x && \
#   apt-get update && apt-get -y install gcc && \
    conda install -n base -c defaults conda=4.* && \
    conda env create -f environment.yaml # Installs environment.yml && \
    conda clean -a \

SHELL ["conda", "run", "-n", "nlp_api", "/bin/bash", "-c"]
RUN conda init bash

ENV PATH /opt/conda/envs/condaenv/bin:$PATH

# add celery
RUN pip install celery

# echo build type
RUN echo $ENV