FROM continuumio/miniconda3:23.3.1-0-alpine
ARG ENV
ENV ENV=$ENV
RUN apk update
RUN apk add --no-cache make

RUN conda --version

# COPY SERVER CODE
WORKDIR /
ADD . /broker
WORKDIR broker

RUN set -x && \
    #conda install -n base -c defaults conda=4.* && \
    conda env create -f environment.yaml # Installs environment.yml && \
    conda clean -a \

SHELL ["conda", "run", "-n", "nlp_api", "/bin/bash", "-c"]
RUN conda init bash

ENV PATH /opt/conda/envs/condaenv/bin:$PATH
# echo build type
RUN echo $ENV

CMD ["conda", "run", "-n", "nlp_api", "make", "broker"]

