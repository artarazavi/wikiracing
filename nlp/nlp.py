import sys

import spacy

from common.config import (
    get_celery_app,
    logger,
    SPACY_LANG
)

app = get_celery_app()

#############################################################
# SpaCy setup

logger.info("Loading NLP Info...")
# spacy file if downloaded and stored locally
spacy_file = "assets/en_core_web_lg-2.2.5/en_core_web_lg/en_core_web_lg-2.2.5"

if "pytest" in sys.modules:
    spacy_file = (
        "../nlp/assets/en_core_web_lg-2.2.5/en_core_web_lg/en_core_web_lg-2.2.5"
    )

# use this if you downloaded spacy and stored it locally
# nlp = spacy.load(spacy_file)

# reads spacy model downloaded upon build
nlp = spacy.load(SPACY_LANG)

stop_list = set("for a of the and to in go list".split())

#############################################################


@app.task(name="tasks.nlp")
def nlp_score(end_path: str, query: str):
    """Celery task that calculates nlp based similarity scores.

    Uses Spacy nlp library to calculate vector similarity scores:
        Similarity between(current query page, wiki race end path).

    Args:
        end_path: Wiki race end path.
        query: Page being queried.

    Returns: ["page title", float(similarity score w/r/t end path)]

    """
    ep = " ".join([w for w in end_path.split() if w not in stop_list])
    sp = " ".join([w for w in query.split() if w not in stop_list])

    doc1 = nlp(ep.lower())
    doc2 = nlp(sp.lower())

    return [query, doc1.similarity(doc2)]
