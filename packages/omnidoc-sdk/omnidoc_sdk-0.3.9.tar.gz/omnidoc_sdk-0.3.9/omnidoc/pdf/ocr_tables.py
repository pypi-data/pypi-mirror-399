import cv2
import numpy as np
import pytesseract

def extract_ocr_tables(image):
    gray = cv2.cvtColor(np.array(image), cv2.COLOR_BGR2GRAY)
    thresh = cv2.adaptiveThreshold(
        gray, 255, cv2.ADAPTIVE_THRESH_MEAN_C,
        cv2.THRESH_BINARY_INV, 15, 10
    )

    horizontal = thresh.copy()
    vertical = thresh.copy()

    cols = cv2.getStructuringElement(cv2.MORPH_RECT, (40, 1))
    rows = cv2.getStructuringElement(cv2.MORPH_RECT, (1, 40))

    horizontal = cv2.morphologyEx(horizontal, cv2.MORPH_OPEN, cols)
    vertical = cv2.morphologyEx(vertical, cv2.MORPH_OPEN, rows)

    table_mask = cv2.add(horizontal, vertical)
    contours, _ = cv2.findContours(
        table_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
    )

    tables = []
    for cnt in contours:
        x, y, w, h = cv2.boundingRect(cnt)
        roi = image.crop((x, y, x + w, y + h))
        text = pytesseract.image_to_string(roi)
        tables.append(text.splitlines())

    return tables
