"""Chat Template Detector - Detect chat template mismatches in LLM fine-tuning."""

__version__ = "0.1.0"

from .detector import TemplateDetector, TemplateMismatch

__all__ = ["TemplateDetector", "TemplateMismatch"]
