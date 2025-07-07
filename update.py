# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "cookiecutter",
#     "typer",
# ]
# ///
from __future__ import annotations
import contextlib
import json
import os
import shutil
import tempfile
from typing import TYPE_CHECKING
import typer
from rich import print_json

if TYPE_CHECKING:
    from typing import TypedDict
    class CookieCutterConfig(TypedDict):
        """
        Configuration for the Cookiecutter template.
        """
        project_name: str
        project_slug: str
        project_short_description: str
        minimum_python_version: str
        full_name: str
        email: str
        github_username: str

TEMPLATE_DIR = os.path.dirname(os.path.abspath(__file__))

SAMPLE_CONFIG = os.path.join(TEMPLATE_DIR, "cookiecutter.json")

def update_config(project_dir: str) -> CookieCutterConfig:
    with open(SAMPLE_CONFIG, "r") as f:
        sample_config = json.load(f)

    project_cookiecutter_config = os.path.join(project_dir, "cookiecutter.json")
    if os.path.exists(project_cookiecutter_config):
        with open(project_cookiecutter_config, "r") as f:
            for k,v in json.load(f).items():
                sample_config[k] = v
    import tomllib
    with open(os.path.join(project_dir, "pyproject.toml"), "rb") as f:
        pyproject = tomllib.load(f)

    slug = os.listdir(os.path.join(project_dir, "src"))[0]

    sample_config["project_name"] = os.path.basename(project_dir)
    sample_config["package_name"] = pyproject["project"]["name"]
    sample_config["module_name"] = slug
    sample_config["project_short_description"] = pyproject["project"]["description"]
    sample_config["minimum_python_version"] = pyproject["project"]["requires-python"].split("=")[-1].strip()
    sample_config["full_name"] = pyproject["project"]["authors"][0]["name"]
    sample_config["email"] = pyproject["project"]["authors"][0]["email"]

    with open(project_cookiecutter_config, "w") as f:
        json.dump(sample_config, f, indent=2)
        f.write("\n")  # Ensure the file ends with a newline

    return sample_config


@contextlib.contextmanager
def in_temporary_directory():
    original_dir = os.getcwd()
    with tempfile.TemporaryDirectory() as temp_dir:
        os.chdir(temp_dir)
        try:
            yield temp_dir
        finally:
            os.chdir(original_dir)


app = typer.Typer()


def list_files_recursively(directory: str) -> list[str]:
    """
    List all files in a directory and its subdirectories recursively.

    Args:
        directory (str): Path to the directory to search

    Returns:
        list: List of file paths relative to the given directory
    """
    file_list = []
    for root, dirs, files in os.walk(directory):
        for file in files:
            # Get path relative to the directory argument
            full_path = os.path.join(root, file)
            rel_path = os.path.relpath(full_path, directory)
            file_list.append(rel_path)
    return file_list

@app.command()
def update_cookies(project_dir: str):
    project_dir = os.path.abspath(project_dir)

    config = update_config(project_dir)
    with in_temporary_directory() as temp_dir:
        # Create a temporary directory to run the cookiecutter command
        import cookiecutter.main
        cookiecutter.main.cookiecutter(
            TEMPLATE_DIR,
            no_input=True,
            extra_context=config,
            output_dir=os.getcwd(),
            overwrite_if_exists=True,
        )

        p_dir = os.path.join(temp_dir, os.listdir(temp_dir)[0])

        for file in list_files_recursively(p_dir):
            file_path = os.path.join(p_dir, file)
            target_path = os.path.join(project_dir, file)
            if not os.path.exists(target_path):
                os.makedirs(os.path.dirname(target_path), exist_ok=True)
                shutil.move(file_path, target_path)
                continue
            if "tests" in file or file.endswith(".py") or "LICENSE" in file or "README" in file:
                continue

            shutil.move(file_path, target_path)


    # Use the config to update the cookies
    # print_json(data=config, indent=2)

if __name__ == "__main__":
    app()
