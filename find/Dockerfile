FROM python:3.7

COPY . /src/app/find
WORKDIR /src/app/find

RUN python -m pip install --upgrade pip

RUN pip install -r requirements.txt

ENTRYPOINT celery -A find worker -Q find --loglevel=info --concurrency=10