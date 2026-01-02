import camelot
from omnidoc.core.document import Table

def extract_tables(path: str) -> list[Table]:
    tables = camelot.read_pdf(path, pages="all", flavor="lattice")
    result = []

    for t in tables:
        df = t.df
        result.append(
            Table(
                page=t.page,
                headers=df.iloc[0].tolist(),
                rows=df.iloc[1:].values.tolist()
            )
        )
    return result
