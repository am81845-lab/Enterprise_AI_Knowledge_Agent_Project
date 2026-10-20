"""Lightweight smoke tests for document filename handling and configuration defaults."""
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from src.ingestion import _safe_name


def test_safe_name_removes_path_components():
    assert _safe_name("../../my report.pdf") == "my report.pdf"


def test_safe_name_falls_back_for_empty_name():
    assert _safe_name("...   ") == "uploaded_document"
