# main.py
import os
import json
import click
import subprocess
import glob
from pathlib import Path
from rich.console import Console
from rich.markdown import Markdown
from naming import check_resource_group_naming


# Local imports
from parser import parse_tf_plan
from analyzer import analyze_plan

console = Console()

# Configuration paths
CONFIG_DIR = Path.home() / ".ftltf"
CONFIG_FILE = CONFIG_DIR / "config.json"

def save_config(api_key):
    """Saves the API key to the user's home directory."""
    CONFIG_DIR.mkdir(exist_ok=True)
    with open(CONFIG_FILE, 'w') as f:
        json.dump({"api_key": api_key}, f)

def load_config():
    """Loads the API key from config file or environment variables."""
    if CONFIG_FILE.exists():
        with open(CONFIG_FILE, 'r') as f:
            return json.load(f).get("api_key")
    return os.environ.get("OPENAI_API_KEY")

@click.group()
def cli():
    """🛡️ FTL-TF: AI-Powered Terraform Guard"""
    pass

@cli.command()
@click.argument('api_key')
def config(api_key):
    """Setup your OpenAI API Key (Saved to ~/.ftltf/config.json)"""
    save_config(api_key)
    console.print(f"[bold green]✅ Success![/bold green] API key saved to {CONFIG_FILE}")

@cli.command()
@click.argument('env', required=False)
@click.option('--path', '-p', default='.', help='Path to Terraform files')

def plan(env, path):
    """Generate and AI-analyze a Terraform plan."""
    api_key = load_config()
    if not api_key:
        console.print("[bold red]Error:[/bold red] No API key found.")
        console.print("Run: [bold cyan]ftltf config YOUR_OPENAI_KEY[/bold cyan]")
        return

    target_dir = os.path.abspath(path)
    plan_file = "tfplan"
    
    # --- Smart Var-File Discovery ---
    selected_var_file = None
    if env:
        search_pattern = os.path.join(target_dir, "**", f"{env}.tfvars")
        found_files = glob.glob(search_pattern, recursive=True)
        if found_files:
            selected_var_file = os.path.relpath(found_files[0], target_dir)
            console.print(f"[bold blue]Found variables:[/bold blue] {selected_var_file}")
    
    # --- Execute Terraform ---
    with console.status("[bold green]Running Terraform Plan...") as status:
        plan_cmd = ["terraform", f"-chdir={target_dir}", "plan", f"-out={plan_file}"]
        if selected_var_file:
            plan_cmd.append(f"-var-file={selected_var_file}")
            
        plan_proc = subprocess.run(
            plan_cmd,
            capture_output=True,
            text=True
        )

        if plan_proc.returncode != 0:
            console.print("[bold red]Terraform plan failed[/bold red]")
            console.print(plan_proc.stderr)
            return

        show_proc = subprocess.run(
            ["terraform", f"-chdir={target_dir}", "show", "-json", plan_file],
            capture_output=True,
            text=True
        )

        if show_proc.returncode != 0:
            console.print("[bold red]Terraform show failed[/bold red]")
            console.print(show_proc.stderr)
            return


    # --- Parse & Analyze ---
    changes = parse_tf_plan(show_proc.stdout)
    if not changes:
        console.print("[yellow]No changes detected.[/yellow]")
        return
    rg_naming_issues = check_resource_group_naming(changes)
    if rg_naming_issues:
        console.print("[bold yellow]Naming Convention Issues (Resource Groups)[/bold yellow]")
        for issue in rg_naming_issues:
            console.print(
                f"- {issue['resource']} → '{issue['name']}': {issue['issue']}"
            )


    with console.status("[bold magenta]Security Audit in progress...") as status:
        try:
            analysis = analyze_plan(changes, api_key)
            console.print(Markdown(analysis))
        except Exception as e:
            console.print(f"[bold red]AI Error:[/bold red] {str(e)}")
    
    # Cleanup binary plan file
    if os.path.exists(os.path.join(target_dir, plan_file)):
        os.remove(os.path.join(target_dir, plan_file))

if __name__ == "__main__":
    cli()