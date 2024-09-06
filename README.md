# BrokerIO

This package contains BrokerIO, originally built for [CARE](https://github.com/UKPLab/CARE), but more and more used
standalone.
BrokerIO allows running multiple models in parallel and to distribute skill requests via websockets.
We currently support several skills out of the box:

- [OpenAI Azure API](https://learn.microsoft.com/en-us/azure/ai-services/openai)
- [Huggingface Pipeline](https://huggingface.co/docs/transformers/pipeline_tutorial)
- [Llama.cpp](https://github.com/ggerganov/llama.cpp)
  through [Python bindings](https://llama-cpp-python.readthedocs.io/en/latest/)
- [NLTK Vader Sentiment Analysis](https://www.nltk.org/_modules/nltk/sentiment/vader.html)

The original repository can be found [here](https://github.com/UKPLab/BrokerIO).
We provide a documentation of BrokerIO [here](https://care.ukp.informatik.tu-darmstadt.de/brokerIO/index.html).

## Requirements

* [ArangoDB](https://www.arangodb.com/download-major/)
* [Redis](https://redis.io/download)
* [Docker](https://docs.docker.com/get-docker/)

## Quickstart

Simple run ``pip install brokerio`` to install the package and find out more about it with ``brokerio --help``.

```bash
brokerio broker start --db_url "http://localhost:8529" --redis_url "redis://localhost:6379" --port 4852
```

or directly build brokerIO as a service with docker compose (all required databases included):

```bash
docker compose -f docker-compose.yml -p "brokerio" up --build -d
```

## Features

BrokerIO provides a set of features to manage and distribute requests to multiple Skills:

- **Quota System**: Limit the number of requests a client can make
- **NoSQL Database**: Store the results of the Skills in a NoSQL database (inclusive donation feature)
- **Authentication**: Secure the access to the BrokerIO API via Role based access control (RBAC)
- **CLI**: Manage the BrokerIO and the available Skills via the command line
- **Logging**: Log all requests and responses to the BrokerIO API
- **Build-in Skills**: Provide a set of build-in Skills to get started
- **Docker Environment**: Run the BrokerIO in a Docker container

## Contact

_Maintainers:_

* Dennis Zyska (dennis.zyska@tu-darmstadt.de)

_Contributors:_

* Nils Dycke (nils.dycke@tu-darmstadt.de)

Don't hesitate to send us an e-mail or report an issue, if something is broken (and it shouldn't be) or if you have
further questions.

https://www.ukp.tu-darmstadt.de \
https://www.tu-darmstadt.de

### Citation

If you use this software, please cite the following paper:

```bibtex
@inproceedings{zyska-etal-2023-care,
    title = "{CARE}: Collaborative {AI}-Assisted Reading Environment",
    author = "Zyska, Dennis  and
      Dycke, Nils  and
      Buchmann, Jan  and
      Kuznetsov, Ilia  and
      Gurevych, Iryna",
    booktitle = "Proceedings of the 61st Annual Meeting of the Association for Computational Linguistics (Volume 3: System Demonstrations)",
    month = jul,
    year = "2023",
    address = "Toronto, Canada",
    publisher = "Association for Computational Linguistics",
    url = "https://aclanthology.org/2023.acl-demo.28",
    doi = "10.18653/v1/2023.acl-demo.28",
    pages = "291--303",
    abstract = "Recent years have seen impressive progress in AI-assisted writing, yet the developments in AI-assisted reading are lacking. We propose inline commentary as a natural vehicle for AI-based reading assistance, and present CARE: the first open integrated platform for the study of inline commentary and reading. CARE facilitates data collection for inline commentaries in a commonplace collaborative reading environment, and provides a framework for enhancing reading with NLP-based assistance, such as text classification, generation or question answering. The extensible behavioral logging allows unique insights into the reading and commenting behavior, and flexible configuration makes the platform easy to deploy in new scenarios. To evaluate CARE in action, we apply the platform in a user study dedicated to scholarly peer review. CARE facilitates the data collection and study of inline commentary in NLP, extrinsic evaluation of NLP assistance, and application prototyping. We invite the community to explore and build upon the open source implementation of CARE.Github Repository: \url{https://github.com/UKPLab/CAREPublic} Live Demo: \url{https://care.ukp.informatik.tu-darmstadt.de}",
}
```

### Disclaimer

This repository contains experimental software and is published for the sole purpose of giving additional background
details on the respective publication.\
The software is only tested on unix systems and is not guaranteed to work on other operating systems.
