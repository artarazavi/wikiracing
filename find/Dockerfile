FROM python:3.7

RUN python -m pip install --upgrade pip

COPY . /src/app/find
WORKDIR /src/app/find

RUN pip install -r requirements.txt

ENTRYPOINT celery -A find worker -Q find --loglevel=info --concurrency=10