"""
docling_extractor - Production-grade document extraction with intelligent fallback chains.

Main components:
- extract_single_document: Primary entry point for document processing
- DoclingExtractor: Handles digital PDF extraction with Docling
- is_scanned_pdf: Detects whether a PDF is scanned or digital

For full documentation, see: https://github.com/panwarnalini-hub/clinical-doc-pipelines
"""

__version__ = "1.0.0"
__author__ = "Nalini Panwar"

from .extractor import (
    extract_single_document,
    DoclingExtractor,
    is_scanned_pdf,
)

__all__ = [
    "extract_single_document",
    "DoclingExtractor", 
    "is_scanned_pdf",
]
