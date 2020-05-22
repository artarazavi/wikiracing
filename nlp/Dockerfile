FROM python:3.7

COPY . /src/app/nlp
WORKDIR /src/app/nlp

RUN python -m pip install --upgrade pip

RUN pip install -r requirements.txt

ENV LANG             en_core_web_md
ENV SPACY_VERSION    2.2

RUN pip3 install --upgrade pip setuptools

########################################
# spaCy
########################################
RUN pip3 install spacy==${SPACY_VERSION}
RUN ls -lah
#RUN python3 -m spacy download ${LANG}

ENTRYPOINT celery -A nlp worker -Q nlp --loglevel=info --concurrency=10