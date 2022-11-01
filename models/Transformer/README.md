# Transformer Docker Models for Inference

This model contains Dockerfiles for the deployment of the Transformer models for inference. 
Also included is the connection to the NLP API and deployment of the skillset.

## Requirements

* Docker
* Docker Compose

## Usage

Before you can use the Dockerfiles, change the ENV variables in .env to your needs.

### Build the Docker images

```bash
make build
```

### Start the Docker containers

```bash
make run
```

### Rebuild the Docker images

The containers will be rebuilt without using the cache.

```bash
make rebuild
```

### Clean the Docker images

```bash
make clean
```

## References

* [PythonSocketIO](https://python-socketio.readthedocs.io)