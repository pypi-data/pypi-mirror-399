# OmniDoc PDF Intelligence SDK

**Enterprise-grade PDF understanding for Agentic AI, RAG, and automation systems**

---

## 🚀 Overview

**OmniDoc** is a production-ready PDF intelligence SDK designed to convert **raw PDFs (documents, slides, brochures, scanned files)** into **clean, structured, agent-ready outputs**.

It goes beyond OCR by applying **layout intelligence, semantic normalization, metric extraction, and agent-native serialization**.

Built for:
- Agentic AI systems
- RAG (Retrieval-Augmented Generation)
- Knowledge Bases
- Autonomous remediation & workflows
- Enterprise document automation

---

## 🧠 Core Capabilities

### Supported PDF Types
- Digital PDFs
- Slide decks & brochures
- Scanned PDFs
- Mixed-content PDFs

### Intelligence Layers
- PDF type detection (digital vs scanned)
- OCR (Tesseract / AWS Textract)
- Layout-aware block ordering
- Vision-Language Models (Donut – optional)
- Slide → report restructuring
- Heading detection & paragraph merging
- Bullet normalization
- Table → metric extraction
- Noise & artifact removal
- RAG-ready chunking

### Output Formats
- Python-native `Document`
- **Enterprise JSON**
- **Agent-native TOON**

---

## 📦 Installation

```bash
pip install omnidoc
```

### System Dependencies (macOS / Linux)

```bash
brew install poppler tesseract
```

Optional:

```bash
pip install pdf2image pytesseract
```

---

## 🏗️ Architecture

```
PDF
 │
 ├─ Detection (Digital / Scanned)
 │
 ├─ Extraction
 │   ├─ Text
 │   ├─ OCR
 │   └─ Layout ML
 │
 ├─ Cleaning & Normalization
 │
 ├─ Slide → Report Structuring
 │
 ├─ Table & Metric Processing
 │
 └─ Output
     ├─ Document
     ├─ JSON
     └─ TOON
```

---

## 🔧 Core API

### extract_pdf()

```python
extract_pdf(
    path: str,
    enable_layout: bool = True,
    enable_cloud_ocr: bool = False,
    enable_vlm: bool = False,
    enable_pii_masking: bool = False,
    output_format: str = "document"  # document | json | toon
)
```

---

## 📄 Example — Plain Text

```python
from omnidoc.pdf.pipeline import extract_pdf

doc = extract_pdf("sample.pdf", enable_layout=True)
print(doc.raw_text)
```

---

## 📄 Example — JSON (RAG Ready)

```python
from omnidoc.pdf.pipeline import extract_pdf
import json

result = extract_pdf(
    "sample.pdf",
    enable_layout=True,
    enable_cloud_ocr=True,
    output_format="json"
)

print(json.dumps(result, indent=2))
```

---

## 🤖 Example — TOON (Agent Output)

```python
toon = extract_pdf(
    "sample.pdf",
    enable_layout=True,
    output_format="toon"
)

print(toon)
```

---

## 🧪 Real Use Case — RAG Pipeline

```python
doc = extract_pdf("strategy.pdf", output_format="json")

for chunk in doc["chunks"]:
    vector_db.add(chunk["text"], metadata=chunk)
```

---

## 🔐 Enterprise Design

- Deterministic output
- No stdout hijacking
- No numeric loss
- Agent-safe serialization
- Optional PII masking
- Cloud OCR fallback

---

## 📜 License

© 2025 OmniDoc — Internal / Enterprise SDK
