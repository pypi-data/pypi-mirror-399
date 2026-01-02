from omnidoc.postprocess.headings import is_heading
from omnidoc.postprocess.bullets import merge_bullets


def restructure_sections(sections):
    """
    Converts slide-style sections into report-style paragraphs.
    """
    out = []
    buffer = []

    for sec in sections:
        text = sec.text.strip()

        if is_heading(text):
            if buffer:
                out.append(" ".join(buffer))
                buffer = []
            out.append(text.upper())
        else:
            buffer.append(text)

    if buffer:
        out.append(" ".join(buffer))

    return "\n\n".join(out)
