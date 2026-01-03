# utils.py

def colorize_report(text: str) -> str:
    """
    Applies Rich color markup to actions and severity levels
    inside the AI-generated risk report.
    """
    replacements = {
        # Actions
        " create ": " [green]create[/green] ",
        " delete ": " [red]delete[/red] ",
        " destroy ": " [red]destroy[/red] ",
        " update ": " [yellow]update[/yellow] ",
        " modify ": " [yellow]modify[/yellow] ",

        # Severity
        " Low ": " [green]Low[/green] ",
        " Medium ": " [yellow]Medium[/yellow] ",
        " High ": " [red]High[/red] ",
        " Critical ": " [bold red]Critical[/bold red] ",
    }

    for k, v in replacements.items():
        text = text.replace(k, v)

    return text
