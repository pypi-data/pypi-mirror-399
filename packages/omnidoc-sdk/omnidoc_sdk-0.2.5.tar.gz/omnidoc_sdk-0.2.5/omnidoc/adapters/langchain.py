from langchain.schema import Document as LCDocument

def to_langchain(doc):
    return [
        LCDocument(
            page_content=section.text,
            metadata={"page": section.page}
        )
        for section in doc.sections
    ]
