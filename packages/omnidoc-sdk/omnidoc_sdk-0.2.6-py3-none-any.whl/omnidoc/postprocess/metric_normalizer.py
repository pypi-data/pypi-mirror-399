import re
from typing import Dict, List

METRIC_PATTERN = re.compile(
    r"(?P<label>[A-Za-z ].+?)\s+(?P<min>\d+)[–-](?P<max>\d+)%\s+(?P<impact>.+)"
)

def extract_metrics(text: str) -> List[Dict]:
    metrics = []

    for line in text.splitlines():
        match = METRIC_PATTERN.search(line)
        if match:
            metrics.append({
                "metric": match.group("label").strip(),
                "min": int(match.group("min")),
                "max": int(match.group("max")),
                "unit": "%",
                "impact": match.group("impact").strip()
            })

    return metrics
