from llama_index.core import Document

def to_llamaindex(doc):
    return [
        Document(
            text=section.text,
            metadata={"page": section.page}
        )
        for section in doc.sections
    ]
