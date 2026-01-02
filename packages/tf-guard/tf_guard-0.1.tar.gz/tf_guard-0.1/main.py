import os
import click
import subprocess
import glob
from rich.console import Console
from rich.markdown import Markdown
from dotenv import load_dotenv

from parser import parse_tf_plan
from analyzer import analyze_plan

console = Console()

script_dir = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(script_dir, '.env'))

@click.group()
def cli():
    """FTL-TF: AI-Powered Terraform Guard"""
    pass

@cli.command()
@click.argument('env', required=False) # Allows 'ftltf plan sbx'
@click.option('--path', '-p', default='.', help='Path to TF files')
def plan(env, path):
    """Generate and Analyze a Terraform Plan for a specific environment."""
    
    target_dir = os.path.abspath(path)
    plan_file = "tfplan"
    
    if not os.path.exists(target_dir):
        console.print(f"[bold red]Error:[/bold red] Directory '{target_dir}' not found.")
        return

    # --- INTELLIGENT VAR-FILE DISCOVERY ---
    selected_var_file = None
    
    if env:
        # Search recursively for any file named 'env.tfvars' or 'env' starting with env
        # This handles: ./sbx.tfvars, ./vars/sbx.tfvars, ./environments/sbx.tfvars, etc.
        search_pattern = os.path.join(target_dir, "**", f"{env}.tfvars")
        found_files = glob.glob(search_pattern, recursive=True)
        
        if found_files:
            # Get the path relative to the target_dir for Terraform -chdir compatibility
            selected_var_file = os.path.relpath(found_files[0], target_dir)
            console.print(f"[bold blue]🔍🔍🔍Found variables at:[/bold blue] {selected_var_file}")
        else:
            console.print(f"[bold yellow]⚠️  Warning:[/bold yellow] No var-file found matching '{env}'.")
    
    # Fallback to defaults if no env provided or found
    if not selected_var_file and not env:
        for default in ["value.tfvars", "variables.tfvars"]:
            if os.path.exists(os.path.join(target_dir, default)):
                selected_var_file = default
                break

    # --- CONSTRUCT COMMAND ---
    plan_cmd = ["terraform", f"-chdir={target_dir}", "plan", f"-out={plan_file}"]
    if selected_var_file:
        plan_cmd.append(f"-var-file={selected_var_file}")

    # --- EXECUTION ---
    with console.status(f"[bold green]Running Plan for {env if env else 'default'}...") as status:
        plan_proc = subprocess.run(plan_cmd, capture_output=True, text=True)
        
        if plan_proc.returncode != 0:
            console.print("[bold red]❌ Terraform Plan Failed:[/bold red]")
            console.print(plan_proc.stderr)
            return

        show_proc = subprocess.run(
            ["terraform", f"-chdir={target_dir}", "show", "-json", plan_file],
            capture_output=True, text=True
        )

    # --- ANALYSIS ---
    changes = parse_tf_plan(show_proc.stdout)
    
    if not changes:
        console.print("[yellow]✨ No changes detected.[/yellow]")
        return

    with console.status("[bold magenta]🧠 AI Security Audit in progress...") as status:
        try:
            analysis_markdown = analyze_plan(changes)
            console.print(Markdown(analysis_markdown))
        except Exception as e:
            console.print(f"[bold red]AI Error:[/bold red] {str(e)}")
    
    # Cleanup
    if os.path.exists(os.path.join(target_dir, plan_file)):
        os.remove(os.path.join(target_dir, plan_file))

if __name__ == "__main__":
    cli()