# Environment prerequisites
Assume we are using:

https://github.com/pyenv/pyenv

https://github.com/pyenv/pyenv-virtualenv

# Development environment
To install the development environment:
```console
pyenv install 3.10.0
pyenv virtualenv 3.10.0 simu_tp1
pyenv local simu_tp1
```
All the following sections assume u are using the created venv.

# Development flow
Before commit run isort and black:
```console
isort .
black .
```

# Development mode
To install in development mode run:
```console
pip install -e .
```

## Testing
Run the test using:
```console
pytest
```