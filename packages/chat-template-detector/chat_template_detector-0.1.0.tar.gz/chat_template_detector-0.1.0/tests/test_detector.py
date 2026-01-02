"""Tests for template detector."""

import pytest
from chat_template_detector.detector import TemplateDetector, TemplateMismatch
from chat_template_detector.templates import detect_template_from_text


def test_detect_chatml():
    text = "<|im_start|>user\nHello<|im_end|>\n<|im_start|>assistant\nHi<|im_end|>"
    assert detect_template_from_text(text) == "chatml"


def test_detect_llama2():
    text = "<s>[INST] Hello [/INST] Hi</s>"
    assert detect_template_from_text(text) == "llama-2"


def test_template_mismatch():
    detector = TemplateDetector()
    mismatches = detector.compare_templates("chatml", "llama-2")
    
    assert len(mismatches) == 1
    assert mismatches[0].severity == "error"
    assert "mismatch" in mismatches[0].message.lower()


def test_template_match():
    detector = TemplateDetector()
    mismatches = detector.compare_templates("chatml", "chatml")
    
    assert len(mismatches) == 1
    assert mismatches[0].severity == "info"


def test_analyze_formatted_text_missing_tokens():
    detector = TemplateDetector()
    text = "Hello world"
    mismatches = detector.analyze_formatted_text(text, "chatml")
    
    assert len(mismatches) > 0
    assert any(m.field == "user_prefix" for m in mismatches)
