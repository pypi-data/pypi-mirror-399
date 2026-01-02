import re

def normalize_metrics(table):
    """
    Converts tables into structured metrics.
    """
    metrics = []

    for row in table.rows:
        text = " ".join(row)

        m = re.search(r"(\d+)\s*[–\-]\s*(\d+)\s*%", text)
        if m:
            metrics.append({
                "label": row[0],
                "min": int(m.group(1)),
                "max": int(m.group(2)),
                "unit": "%"
            })

    return metrics
