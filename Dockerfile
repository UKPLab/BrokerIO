FROM continuumio/miniconda3

#ARG env=.env

# COPY SERVER CODE
# ASSUMING ENTRYPOINT: ../nlp
WORKDIR /
ADD . /nlp-server
#ADD ./$env /nlp-server/$env

# INSTALL REQUIREMENTS
WORKDIR nlp-server

RUN set -x && \
#   apt-get update && apt-get -y install gcc && \
    conda install -n base -c defaults conda=4.* && \
    conda env create -f environment.yaml # Installs environment.yml && \
    conda clean -a \

ENV PATH /opt/conda/envs/condaenv/bin:$PATH
ENTRYPOINT ["python", "-m", "/nlp-server/broker/app.py"]