FROM python:3.7

RUN python -m pip install --upgrade pip
RUN pip3 install --upgrade pip setuptools

ARG SPACY_LANG
ARG SPACY_LOCAL
#ENV LANG             en_core_web_lg
ENV SPACY_VERSION    2.2

RUN pip3 install spacy==${SPACY_VERSION}
RUN bash -c "echo \"spacy stored locally? $SPACY_LOCAL\"; if [[ \"$SPACY_LOCAL\" == 'remote' ]]; then echo \"Dowloading spacy\"; python3 -m spacy download ${SPACY_LANG}; else echo \"using local spacy\"; fi"

COPY . /src/app
WORKDIR /src/app/tests

RUN pip3 install -r requirements.txt

