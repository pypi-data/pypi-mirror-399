"""Known chat template definitions for popular models."""

from dataclasses import dataclass
from typing import Dict, List, Optional


@dataclass
class ChatTemplate:
    """Represents a chat template format."""
    
    name: str
    bos_token: Optional[str]
    eos_token: Optional[str]
    user_prefix: str
    user_suffix: str
    assistant_prefix: str
    assistant_suffix: str
    system_prefix: Optional[str] = None
    system_suffix: Optional[str] = None


KNOWN_TEMPLATES: Dict[str, ChatTemplate] = {
    "llama-2": ChatTemplate(
        name="Llama-2",
        bos_token="<s>",
        eos_token="</s>",
        user_prefix="[INST] ",
        user_suffix=" [/INST]",
        assistant_prefix="",
        assistant_suffix="</s>",
        system_prefix="<<SYS>>\n",
        system_suffix="\n<</SYS>>\n\n",
    ),
    "chatml": ChatTemplate(
        name="ChatML",
        bos_token=None,
        eos_token="<|im_end|>",
        user_prefix="<|im_start|>user\n",
        user_suffix="<|im_end|>\n",
        assistant_prefix="<|im_start|>assistant\n",
        assistant_suffix="<|im_end|>\n",
        system_prefix="<|im_start|>system\n",
        system_suffix="<|im_end|>\n",
    ),
    "mistral": ChatTemplate(
        name="Mistral",
        bos_token="<s>",
        eos_token="</s>",
        user_prefix="[INST] ",
        user_suffix=" [/INST]",
        assistant_prefix="",
        assistant_suffix="</s>",
    ),
    "alpaca": ChatTemplate(
        name="Alpaca",
        bos_token=None,
        eos_token="</s>",
        user_prefix="### Instruction:\n",
        user_suffix="\n\n",
        assistant_prefix="### Response:\n",
        assistant_suffix="</s>",
        system_prefix="### System:\n",
        system_suffix="\n\n",
    ),
    "vicuna": ChatTemplate(
        name="Vicuna",
        bos_token=None,
        eos_token="</s>",
        user_prefix="USER: ",
        user_suffix="\n",
        assistant_prefix="ASSISTANT: ",
        assistant_suffix="</s>",
        system_prefix="SYSTEM: ",
        system_suffix="\n",
    ),
}


MODEL_TEMPLATE_MAPPING = {
    "meta-llama/Llama-2": "llama-2",
    "mistralai/Mistral": "mistral",
    "mistralai/Mixtral": "mistral",
    "unsloth/mistral": "mistral",
    "lmsys/vicuna": "vicuna",
    "tatsu-lab/alpaca": "alpaca",
}


def detect_template_from_model_name(model_name: str) -> Optional[str]:
    """Detect template type from model name."""
    for pattern, template_name in MODEL_TEMPLATE_MAPPING.items():
        if pattern.lower() in model_name.lower():
            return template_name
    return None


def detect_template_from_text(text: str) -> Optional[str]:
    """Detect template type from formatted text."""
    template_indicators = {
        "chatml": ["<|im_start|>", "<|im_end|>"],
        "llama-2": ["[INST]", "[/INST]", "<<SYS>>"],
        "mistral": ["[INST]", "[/INST]"],
        "alpaca": ["### Instruction:", "### Response:"],
        "vicuna": ["USER:", "ASSISTANT:"],
    }
    
    for template_name, indicators in template_indicators.items():
        if any(indicator in text for indicator in indicators):
            return template_name
    
    return None
