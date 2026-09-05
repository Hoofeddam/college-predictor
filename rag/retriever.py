import logging

from rag.embedder import create_embedding
from rag.qdrant_db import client, COLLECTION_NAME

logger = logging.getLogger(__name__)

# "text" is the only field without which a retrieved chunk is useless --
# there's nothing to cite or feed to the model. Everything else is
# citation/display metadata: missing it degrades what's shown (falls back
# to None, consistent with how "year" is already nullable by design in
# rag/loader.py), but the chunk itself is still usable.
OPTIONAL_FIELDS = ["source", "file", "year", "page", "chunk"]


def search_documents(query, limit=5):

    query_embedding = create_embedding(query)

    results = client.query_points(
        collection_name=COLLECTION_NAME,
        query=query_embedding,
        limit=limit
    )

    contexts = []

    for point in results.points:

        text = point.payload.get("text")

        if not text:
            logger.warning(
                "Skipping Qdrant point %s: missing required 'text' field. Payload keys present: %s",
                point.id,
                list(point.payload.keys())
            )
            continue

        context = {"text": text, "score": point.score}

        for field in OPTIONAL_FIELDS:
            context[field] = point.payload.get(field)

        contexts.append(context)

    return contexts
