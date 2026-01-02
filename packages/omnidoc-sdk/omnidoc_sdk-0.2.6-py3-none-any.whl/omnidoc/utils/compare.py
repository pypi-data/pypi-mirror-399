def compare_outputs(raw, improved):
    return {
        "before": raw[:1500],
        "after": improved[:1500],
        "improvement_ratio": len(improved) / max(len(raw), 1)
    }
