import re


def chunk_text(
    text,
    max_chars=1200,
):
    paragraphs = re.split(r"\n\s*\n", text)

    chunks = []

    current_chunk = ""

    for paragraph in paragraphs:

        paragraph = paragraph.strip()

        if not paragraph:
            continue

        if len(current_chunk) + len(paragraph) < max_chars:

            current_chunk += paragraph + "\n\n"

        else:

            chunks.append(current_chunk.strip())

            current_chunk = paragraph + "\n\n"

    if current_chunk:

        chunks.append(current_chunk.strip())

    return chunks