"""
Helper script for creating new templates for create-ragbits-app.
"""
import os
import pathlib
import shutil
from typing import Dict, List

from inquirer.shortcuts import list_input, text, confirm

TEMPLATES_DIR = pathlib.Path(__file__).parent.parent.parent / "templates"

def create_template():
    """Create a new template for create-ragbits-app."""
    print("Creating a new template for create-ragbits-app")
    
    # Get template name
    template_name = text("Template name:")
    template_path = TEMPLATES_DIR / template_name
    
    if template_path.exists():
        overwrite = confirm(
            f"Template '{template_name}' already exists. Overwrite?",
            default=False
        )
        if not overwrite:
            print("Template creation cancelled.")
            return
        shutil.rmtree(template_path)
    
    # Create template directory
    os.makedirs(template_path, exist_ok=True)
    
    # Create template_config.py
    template_description = text("Template description:")
    
    # Define questions for the template
    questions = []
    while True:
        add_question = confirm("Add a question?", default=True)
        if not add_question:
            break
        
        q_name = text("Question name (variable name):")
        q_message = text("Question message:", default=q_name)
        q_type = list_input(
            "Question type:",
            choices=["text", "list", "confirm"],
            default="text"
        )
        
        question = {
            "type": q_type,
            "name": q_name,
            "message": q_message,
        }
        
        if q_type == "text":
            q_default = text("Default value (optional):")
            if q_default:
                question["default"] = q_default
        elif q_type == "list":
            choices = []
            while True:
                choice = text("Add choice (empty to finish):")
                if not choice:
                    break
                choices.append(choice)
            question["choices"] = choices
            
            if choices:
                default_idx = list_input(
                    "Default choice:",
                    choices=choices,
                    default=choices[0]
                )
                question["default"] = default_idx
        elif q_type == "confirm":
            q_default = confirm("Default value:", default=True)
            question["default"] = q_default
        
        questions.append(question)
    
    # Write template_config.py
    with open(template_path / "template_config.py", "w") as f:
        f.write(f'"""\nConfiguration for the {template_name} template.\n"""\n\n')
        f.write(f'# Template metadata\n')
        f.write(f'name = "{template_name}"\n')
        f.write(f'description = "{template_description}"\n\n')
        f.write('# Questions to ask when creating a project\n')
        f.write('questions = [\n')
        for q in questions:
            f.write('    {\n')
            for k, v in q.items():
                if isinstance(v, str):
                    f.write(f'        "{k}": "{v}",\n')
                else:
                    f.write(f'        "{k}": {v},\n')
            f.write('    },\n')
        f.write(']\n')
    
    print(f"Template '{template_name}' created at {template_path}")
    print("Add your template files to this directory.")
    print("Use .j2 extension for files that should be processed as Jinja2 templates.")
    print("You can use Jinja2 variables in directory names with {{variable_name}} syntax.")
    print("Available variables in templates:")
    print("  - project_name: Name of the project")
    print("  - ragbits_version: Latest version of ragbits")
    for q in questions:
        print(f"  - {q['name']}: Answer to '{q['message']}'")

if __name__ == "__main__":
    create_template()
