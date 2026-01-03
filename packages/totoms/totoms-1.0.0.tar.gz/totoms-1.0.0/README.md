# Toto Microservice SDK - Python

Python framework for building cloud-agnostic microservices with FastAPI.

## Installation

```bash
pip install totoms
```

## Quick Start

```python
from totoms import TotoMicroservice, TotoMicroserviceConfiguration

config = TotoMicroserviceConfiguration()
microservice = TotoMicroservice(config)
```

## Features

- **API Controller**: FastAPI-based REST API framework
- **Message Bus**: Event-driven architecture with PubSub and Queue support
- **Cloud Support**: AWS, GCP, and Azure
- **Secrets Management**: Secure secrets handling
- **Token Verification**: Built-in JWT token verification
- **Logging**: Structured logging with correlation IDs

## Documentation

For full documentation, visit the [Toto SDK repository](https://github.com/nicolasances/toto-microservice-sdk).

## License

MIT License - see LICENSE file for details
