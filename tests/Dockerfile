FROM python:3.7

RUN python -m pip install --upgrade pip

COPY . /src/app
WORKDIR /src/app/tests

RUN pip install -r requirements.txt

