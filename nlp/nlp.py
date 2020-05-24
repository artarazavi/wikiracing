import spacy

from common.config import (
    get_celery_app,
    logger,
)

import sys

app = get_celery_app()

# Spacy setup
logger.info("Loading NLP Info...")
spacy_file = "assets/en_core_web_lg-2.2.5/en_core_web_lg/en_core_web_lg-2.2.5"


if "pytest" in sys.modules:
    spacy_file = (
        "../nlp/assets/en_core_web_lg-2.2.5/en_core_web_lg/en_core_web_lg-2.2.5"
    )
nlp = spacy.load(spacy_file)

# STOP_WORDS = spacy.lang.en.stop_words.STOP_WORDS
stop_list = set("for a of the and to in go list".split())


@app.task(name="tasks.nlp")
def nlp_score(end_path: str, query: str):
    logger.info(f"NLP TASK WHAT THE FUCK IS GOING ON HERE {end_path}")
    ep = " ".join([w for w in end_path.split() if w not in stop_list])
    sp = " ".join([w for w in query.split() if w not in stop_list])

    doc1 = nlp(ep.lower())
    doc2 = nlp(sp.lower())

    return [query, doc1.similarity(doc2)]
