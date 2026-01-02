"""Core template detection and validation logic."""

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Any

from .templates import KNOWN_TEMPLATES, detect_template_from_text, detect_template_from_model_name


@dataclass
class TemplateMismatch:
    """Represents a detected template mismatch."""
    
    severity: str  # "error", "warning", "info"
    field: str
    expected: str
    actual: str
    message: str
    
    def __str__(self) -> str:
        return f"[{self.severity.upper()}] {self.field}: {self.message}"


class TemplateDetector:
    """Detects and validates chat template consistency."""
    
    def __init__(self):
        self.mismatches: List[TemplateMismatch] = []
    
    def validate_training_file(self, file_path: str) -> Optional[str]:
        """Analyze training file and detect template format."""
        path = Path(file_path)
        
        if not path.exists():
            raise FileNotFoundError(f"Training file not found: {file_path}")
        
        if not path.is_file():
            raise ValueError(f"Path is not a file: {file_path}")
        
        # Read first few examples
        examples = []
        try:
            with open(path, 'r', encoding='utf-8') as f:
                for i, line in enumerate(f):
                    if i >= 10:  # Sample first 10
                        break
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        examples.append(json.loads(line))
                    except json.JSONDecodeError as e:
                        continue
        except UnicodeDecodeError:
            raise ValueError(f"File encoding not supported. Please use UTF-8: {file_path}")
        except PermissionError:
            raise PermissionError(f"Permission denied reading file: {file_path}")
        except Exception as e:
            raise IOError(f"Error reading file {file_path}: {str(e)}")
        
        if not examples:
            raise ValueError(f"No valid JSON examples found in training file. Expected JSONL format (one JSON object per line)")
        
        # Detect format
        detected_template = None
        for example in examples:
            # Check if it's raw formatted text
            if "text" in example:
                detected = detect_template_from_text(example["text"])
                if detected:
                    detected_template = detected
                    break
            
            # Check if it's messages format
            if "messages" in example:
                # Messages format detected - will be formatted at training time
                # Return "messages" as a special marker
                return "messages"
        
        return detected_template
    
    def validate_inference_config(self, config: Dict[str, Any]) -> Optional[str]:
        """Analyze inference config and detect template format."""
        if not isinstance(config, dict):
            raise ValueError("Config must be a dictionary")
        
        # Check for model name
        model_name = config.get("model", "")
        if model_name:
            if not isinstance(model_name, str):
                raise ValueError("Model name must be a string")
            detected = detect_template_from_model_name(model_name)
            if detected:
                return detected
        
        # Check for explicit chat template
        if "chat_template" in config:
            template_text = config["chat_template"]
            if not isinstance(template_text, str):
                raise ValueError("Chat template must be a string")
            return detect_template_from_text(template_text)
        
        return None
    
    def compare_templates(
        self,
        training_template: Optional[str],
        inference_template: Optional[str]
    ) -> List[TemplateMismatch]:
        """Compare training and inference templates."""
        self.mismatches = []
        
        if training_template is None and inference_template is None:
            self.mismatches.append(
                TemplateMismatch(
                    severity="warning",
                    field="template",
                    expected="Unknown",
                    actual="Unknown",
                    message="Could not detect template format in either training or inference config"
                )
            )
            return self.mismatches
        
        # Handle "messages" format - it will use model's default template
        if training_template == "messages":
            if inference_template:
                self.mismatches.append(
                    TemplateMismatch(
                        severity="info",
                        field="template",
                        expected=f"{inference_template} (via model default)",
                        actual=inference_template,
                        message=f"Training uses messages format. Model will apply {inference_template} template automatically."
                    )
                )
            else:
                self.mismatches.append(
                    TemplateMismatch(
                        severity="warning",
                        field="template",
                        expected="messages (model default)",
                        actual="Unknown",
                        message="Training uses messages format. Verify model applies correct template during training."
                    )
                )
            return self.mismatches
        
        if training_template != inference_template:
            self.mismatches.append(
                TemplateMismatch(
                    severity="error",
                    field="template",
                    expected=training_template or "Unknown",
                    actual=inference_template or "Unknown",
                    message=f"Template mismatch: training uses {training_template}, inference uses {inference_template}"
                )
            )
        
        # If both detected and same, validate details
        if training_template and inference_template and training_template == inference_template:
            template_def = KNOWN_TEMPLATES.get(training_template)
            if template_def:
                self.mismatches.append(
                    TemplateMismatch(
                        severity="info",
                        field="template",
                        expected=training_template,
                        actual=training_template,
                        message=f"Templates match: {template_def.name}"
                    )
                )
        
        return self.mismatches
    
    def analyze_formatted_text(self, text: str, expected_template: str) -> List[TemplateMismatch]:
        """Analyze a formatted text string for template compliance."""
        mismatches = []
        
        if expected_template not in KNOWN_TEMPLATES:
            return mismatches
        
        template = KNOWN_TEMPLATES[expected_template]
        
        # Check for required tokens
        if template.bos_token and template.bos_token not in text:
            mismatches.append(
                TemplateMismatch(
                    severity="warning",
                    field="bos_token",
                    expected=template.bos_token,
                    actual="missing",
                    message=f"Missing BOS token: {template.bos_token}"
                )
            )
        
        if template.eos_token and template.eos_token not in text:
            mismatches.append(
                TemplateMismatch(
                    severity="warning",
                    field="eos_token",
                    expected=template.eos_token,
                    actual="missing",
                    message=f"Missing EOS token: {template.eos_token}"
                )
            )
        
        # Check for role prefixes
        if template.user_prefix not in text:
            mismatches.append(
                TemplateMismatch(
                    severity="error",
                    field="user_prefix",
                    expected=template.user_prefix,
                    actual="missing",
                    message=f"Missing user prefix: {template.user_prefix}"
                )
            )
        
        if template.assistant_prefix not in text:
            mismatches.append(
                TemplateMismatch(
                    severity="error",
                    field="assistant_prefix",
                    expected=template.assistant_prefix,
                    actual="missing",
                    message=f"Missing assistant prefix: {template.assistant_prefix}"
                )
            )
        
        return mismatches
