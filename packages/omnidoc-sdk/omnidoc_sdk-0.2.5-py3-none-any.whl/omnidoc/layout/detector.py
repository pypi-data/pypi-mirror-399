from functools import lru_cache


@lru_cache(maxsize=1)
def _load_layout_model():
    """
    Load Detectron2-based layout model if available.

    Returns
    -------
    model | None
        Layout model or None if backend is unavailable.
    """
    try:
        import layoutparser as lp
    except ImportError:
        return None

    # Detectron2 backend is NOT available on most macOS systems
    if not hasattr(lp, "Detectron2LayoutModel"):
        return None

    try:
        return lp.Detectron2LayoutModel(
            "lp://PubLayNet/faster_rcnn_R_50_FPN_3x/config",
            extra_config=["MODEL.ROI_HEADS.SCORE_THRESH_TEST", 0.5],
            label_map={
                0: "Text",
                1: "Title",
                2: "List",
                3: "Table",
                4: "Figure",
            },
        )
    except Exception:
        # Any failure here should NOT crash the pipeline
        return None


def detect_layout(image):
    """
    Detect document layout blocks.

    Gracefully degrades when layout ML backend is unavailable.

    Parameters
    ----------
    image : PIL.Image | numpy.ndarray

    Returns
    -------
    list
        Detected layout blocks, or empty list if unavailable
    """
    model = _load_layout_model()
    if model is None:
        return []

    try:
        return model.detect(image)
    except Exception:
        return []
