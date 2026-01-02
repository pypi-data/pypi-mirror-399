"""Command-line interface for chat template detection."""

import json
import sys
import time
from pathlib import Path
from typing import Optional

import click
import yaml

from .detector import TemplateDetector
from .templates import KNOWN_TEMPLATES


@click.group()
@click.version_option()
def main():
    """Detect chat template mismatches in LLM fine-tuning."""
    pass


@main.command()
@click.option(
    "--training-file",
    type=click.Path(exists=True),
    required=True,
    help="Path to training data file (JSONL format)"
)
@click.option(
    "--inference-config",
    type=click.Path(exists=True),
    help="Path to inference config file (YAML/JSON)"
)
@click.option(
    "--model",
    type=str,
    help="Model name to check against"
)
@click.option(
    "--format",
    type=click.Choice(["text", "json"]),
    default="text",
    help="Output format"
)
def validate(training_file: str, inference_config: Optional[str], model: Optional[str], format: str):
    """Validate training data against inference configuration."""
    detector = TemplateDetector()
    
    # Step 1: Analyze training file
    start_time = time.time()
    try:
        training_template = detector.validate_training_file(training_file)
        elapsed = time.time() - start_time
        if training_template:
            click.echo(f"1: [{elapsed:.1f}s] Analyzing training file, detected training template: {training_template}")
        else:
            click.echo(f"1: [{elapsed:.1f}s] Analyzing training file, could not detect template")
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)
    
    # Step 2: Check model or config
    inference_template = None
    start_time = time.time()
    
    if inference_config:
        try:
            with open(inference_config, 'r', encoding='utf-8') as f:
                if inference_config.endswith('.yaml') or inference_config.endswith('.yml'):
                    config = yaml.safe_load(f)
                else:
                    config = json.load(f)
            
            if config is None:
                click.echo("Error: Config file is empty", err=True)
                sys.exit(1)
            
            inference_template = detector.validate_inference_config(config)
            elapsed = time.time() - start_time
            if inference_template:
                click.echo(f"2: [{elapsed:.1f}s] Checking config: {inference_config}, validating template consistency...")
            else:
                click.echo(f"2: [{elapsed:.1f}s] Checking config: {inference_config}, could not detect template")
        except FileNotFoundError:
            click.echo(f"Error: Config file not found: {inference_config}", err=True)
            sys.exit(1)
        except yaml.YAMLError as e:
            click.echo(f"Error: Invalid YAML format: {e}", err=True)
            sys.exit(1)
        except json.JSONDecodeError as e:
            click.echo(f"Error: Invalid JSON format: {e}", err=True)
            sys.exit(1)
        except Exception as e:
            click.echo(f"Error: {e}", err=True)
            sys.exit(1)
    elif model:
        from .templates import detect_template_from_model_name
        inference_template = detect_template_from_model_name(model)
        elapsed = time.time() - start_time
        click.echo(f"2: [{elapsed:.1f}s] Checking model: {model}, validating template consistency...")
    
    # Compare templates
    mismatches = detector.compare_templates(training_template, inference_template)
    
    # Output results
    if format == "json":
        output = {
            "training_template": training_template,
            "inference_template": inference_template,
            "mismatches": [
                {
                    "severity": m.severity,
                    "field": m.field,
                    "expected": m.expected,
                    "actual": m.actual,
                    "message": m.message
                }
                for m in mismatches
            ]
        }
        click.echo(json.dumps(output, indent=2))
    else:
        # Step 3: Results
        has_errors = any(m.severity == "error" for m in mismatches)
        
        if has_errors:
            click.echo("3: Results: Validation FAILED")
        else:
            click.echo("3: Results: Validation PASSED")
        
        # Show errors
        errors = [m for m in mismatches if m.severity == "error"]
        if errors:
            for e in errors:
                click.echo(click.style(f"   Error: {e.message}", fg="red"))
        
        # Show warnings dimmed
        warnings = [m for m in mismatches if m.severity == "warning"]
        if warnings:
            for w in warnings:
                click.echo(click.style(f"   Warning: {w.message}", fg="white", dim=True))
                click.echo(click.style(f"   File: {training_file}", fg="white", dim=True))
        
        # Exit code
        if has_errors:
            sys.exit(1)
        else:
            sys.exit(0)


@main.command()
def list_templates():
    """List all known chat templates."""
    click.echo("Known chat templates:\n")
    for name, template in KNOWN_TEMPLATES.items():
        click.echo(f"{name}: {template.name}")
        click.echo(f"  BOS: {template.bos_token or 'None'}")
        click.echo(f"  EOS: {template.eos_token or 'None'}")
        click.echo(f"  User: {template.user_prefix}...{template.user_suffix}")
        click.echo(f"  Assistant: {template.assistant_prefix}...{template.assistant_suffix}")
        click.echo()


@main.command()
@click.argument("file_path", type=click.Path(exists=True))
@click.option(
    "--template",
    type=click.Choice(list(KNOWN_TEMPLATES.keys())),
    help="Expected template format"
)
def check(file_path: str, template: Optional[str]):
    """Check a single file for template issues."""
    detector = TemplateDetector()
    
    # Step 1: Read file
    start_time = time.time()
    path = Path(file_path)
    try:
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()
        elapsed = time.time() - start_time
    except UnicodeDecodeError:
        click.echo("Error: File encoding not supported. Please use UTF-8", err=True)
        sys.exit(1)
    except PermissionError:
        click.echo(f"Error: Permission denied reading file: {file_path}", err=True)
        sys.exit(1)
    except Exception as e:
        click.echo(f"Error reading file: {e}", err=True)
        sys.exit(1)
    
    # Step 2: Auto-detect template
    if not template:
        from .templates import detect_template_from_text
        template = detect_template_from_text(content)
        if template:
            click.echo(f"1: [{elapsed:.1f}s] Analyzing file, detected template: {template}")
        else:
            click.echo("Error: Could not auto-detect template. Please specify with --template")
            sys.exit(1)
    else:
        click.echo(f"1: [{elapsed:.1f}s] Analyzing file with template: {template}")
    
    # Step 3: Analyze
    start_time = time.time()
    mismatches = detector.analyze_formatted_text(content, template)
    elapsed = time.time() - start_time
    
    # Output
    has_errors = any(m.severity == "error" for m in mismatches)
    has_warnings = any(m.severity == "warning" for m in mismatches)
    
    if not mismatches:
        click.echo(f"2: [{elapsed:.1f}s] Checking template compliance")
        click.echo("3: Results: No issues found")
    else:
        click.echo(f"2: [{elapsed:.1f}s] Checking template compliance")
        if has_errors:
            click.echo("3: Results: Issues found")
        else:
            click.echo("3: Results: Warnings found")
        
        # Show errors
        errors = [m for m in mismatches if m.severity == "error"]
        if errors:
            for e in errors:
                click.echo(click.style(f"   Error: {e.message}", fg="red"))
        
        # Show warnings
        warnings = [m for m in mismatches if m.severity == "warning"]
        if warnings:
            for w in warnings:
                click.echo(click.style(f"   Warning: {w.message}", fg="white", dim=True))
    
    # Exit code
    if has_errors:
        sys.exit(1)
    else:
        sys.exit(0)


if __name__ == "__main__":
    main()
