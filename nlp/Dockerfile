FROM python:3.7

RUN python -m pip install --upgrade pip
RUN pip3 install --upgrade pip setuptools

#############################################################
# spaCy
# Downloading spacy before the COPY assures it stays in the
# in the cache until you perform a dockere prune.
# Upon next dc up we wont have to grab the dictionary again
#############################################################
ARG SPACY_LANG
ARG SPACY_LOCAL
#ENV SPACY_LANG             en_core_web_lg
ENV SPACY_VERSION    2.2

RUN pip3 install spacy==${SPACY_VERSION}
RUN bash -c "echo \"spacy stored locally? $SPACY_LOCAL\"; if [[ \"$SPACY_LOCAL\" == 'remote' ]]; then echo \"Dowloading spacy\"; python3 -m spacy download ${SPACY_LANG}; else echo \"using local spacy\"; fi"

COPY . /src/app/nlp
WORKDIR /src/app/nlp

RUN pip3 install -r requirements.txt

ENTRYPOINT celery -A nlp worker -Q nlp --loglevel=info --concurrency=10