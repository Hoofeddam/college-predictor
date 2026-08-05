import re


def clean_text(text):

    # Remove null characters
    text = text.replace("\x00", "")

    # Remove repeated blank lines
    text = re.sub(r"\n+", "\n", text)

    # Remove repeated spaces
    text = re.sub(r"[ \t]+", " ", text)

    # Remove page numbers on their own line
    text = re.sub(r"\n\d+\n", "\n", text)

    # Remove common "This page intentionally left blank"
    text = re.sub(
        r"THIS PAGE IS LEFT\s+BLANK\s+INTENTIONALLY",
        "",
        text,
        flags=re.IGNORECASE
    )

    # Remove standalone copyright lines
    text = re.sub(
        r"©.*?Information Brochure",
        "",
        text
    )

    return text.strip()