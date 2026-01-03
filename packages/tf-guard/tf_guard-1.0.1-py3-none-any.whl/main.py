# main.py
import os
import json
import click
import subprocess
import glob
from pathlib import Path
from rich.console import Console
from rich.table import Table

from parser import parse_tf_plan
from analyzer import analyze_plan
from naming import check_resource_group_naming

console = Console()

CONFIG_DIR = Path.home() / ".ftltf"
CONFIG_FILE = CONFIG_DIR / "config.json"


def save_config(api_key):
    CONFIG_DIR.mkdir(exist_ok=True)
    with open(CONFIG_FILE, "w") as f:
        json.dump({"api_key": api_key}, f)


def load_config():
    if CONFIG_FILE.exists():
        with open(CONFIG_FILE, "r") as f:
            return json.load(f).get("api_key")
    return os.environ.get("OPENAI_API_KEY")


@click.group()
def cli():
    pass


@cli.command()
@click.argument("api_key")
def config(api_key):
    save_config(api_key)
    console.print(f"API key saved to {CONFIG_FILE}", style="green")


def render_risk_table(risks):
    table = Table(title="Risk Assessment")

    table.add_column("Resource", style="cyan", overflow="fold")
    table.add_column("Action", justify="center")
    table.add_column("What is being created", overflow="fold")
    table.add_column("Risk Description", overflow="fold")
    table.add_column("Severity", justify="center")

    for r in risks:
        action_color = {
            "create": "green",
            "update": "yellow",
            "modify": "yellow",
            "delete": "red",
            "destroy": "red",
        }.get(r["action"].lower(), "white")

        severity_color = {
            "none": "green",
            "low": "green",
            "medium": "yellow",
            "high": "red",
            "critical": "bold red",
        }.get(r["severity"].lower(), "white")

        table.add_row(
            r["resource"],
            f"[{action_color}]{r['action']}[/{action_color}]",
            r["what"],
            r["description"],
            f"[{severity_color}]{r['severity']}[/{severity_color}]",
        )

    console.print(table)


@cli.command()
@click.argument("env", required=False)
@click.option("--path", "-p", default=".")
def plan(env, path):
    api_key = load_config()
    if not api_key:
        console.print("No API key found", style="red")
        return

    target_dir = os.path.abspath(path)
    plan_file = "tfplan"

    selected_var_file = None
    if env:
        matches = glob.glob(
            os.path.join(target_dir, "**", f"{env}.tfvars"),
            recursive=True,
        )
        if matches:
            selected_var_file = os.path.relpath(matches[0], target_dir)
            console.print(f"Found variables: {selected_var_file}", style="blue")

    with console.status("Running Terraform plan"):
        cmd = ["terraform", f"-chdir={target_dir}", "plan", "-out", plan_file]
        if selected_var_file:
            cmd.append(f"-var-file={selected_var_file}")

        plan_proc = subprocess.run(cmd, capture_output=True, text=True)
        if plan_proc.returncode != 0:
            console.print(plan_proc.stderr, style="red")
            return

        show_proc = subprocess.run(
            ["terraform", f"-chdir={target_dir}", "show", "-json", plan_file],
            capture_output=True,
            text=True,
        )
        if show_proc.returncode != 0:
            console.print(show_proc.stderr, style="red")
            return

    changes = parse_tf_plan(show_proc.stdout)
    if not changes:
        console.print("No changes detected", style="yellow")
        return

    rg_naming_issues = check_resource_group_naming(changes)

    with console.status("Security audit in progress"):
        analysis = json.loads(analyze_plan(changes, api_key))

    console.print("\nEXECUTIVE SUMMARY\n", style="bold")
    console.print(analysis["summary"])

    render_risk_table(analysis["risks"])

    console.print("\nFINAL VERDICT\n", style="bold")
    console.print(f"Rating: {analysis['rating']}")
    console.print(f"Recommendation: {analysis['recommendation']}")

    if rg_naming_issues:
        console.print(
            "\nNaming Convention Issues (Resource Groups)",
            style="bold #ff9f1c",
        )
        for issue in rg_naming_issues:
            console.print(
                f"- {issue['resource']} → '{issue['name']}': {issue['issue']}"
            )

    plan_path = os.path.join(target_dir, plan_file)
    if os.path.exists(plan_path):
        os.remove(plan_path)


if __name__ == "__main__":
    cli()
