FROM python:3.7

RUN python -m pip install --upgrade pip

ARG LOGGING_LEVEL
COPY . /src/app/find
WORKDIR /src/app/find

RUN pip install -r requirements.txt

ENTRYPOINT celery -A find worker -Q find --loglevel=${LOGGING_LEVEL} --concurrency=10