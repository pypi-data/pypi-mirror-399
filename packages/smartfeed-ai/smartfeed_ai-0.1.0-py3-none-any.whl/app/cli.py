from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt, Confirm
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich import box
from . import extraction, prompting

console = Console()

def get_input_source():
    console.print("\n[bold yellow]Step 1:[/bold yellow] Choose Input Source", style="bold")

    table = Table(show_header=True, header_style="bold magenta", box=box.ROUNDED)
    table.add_column("Option", style="cyan", width=10)
    table.add_column("Description", style="white")

    table.add_row("1", "📄 Document (PDF, DOCX, XLS, XLSX)")
    table.add_row("2", "🌐 Web Page URL")

    console.print(table)

    choice = Prompt.ask(
        "[bold green]Select input source[/bold green]",
        choices=["1", "2"],
        default="1"
    )

    return "document" if choice == "1" else "url"

def get_final_output(user_prompt, output_fields, data, links=None):
    with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=console
        ) as progress:
            progress.add_task(description="Preparing output...", total=None)

            if links: 
                return prompting.get_output_data(user_prompt, output_fields,
                                                                  data, links)
            else:
                 return prompting.get_output_data(user_prompt, output_fields,
                                                                  data)

def get_input_converted_files():
    console.print("\n[bold yellow]Step 3:[/bold yellow] Provide Input", style="bold")

    converted_files = {}

    while True:
        # Ask for multiple file names (not full paths)
        file_names = Prompt.ask("[bold green]Enter document file names (comma-separated)[/bold green]")
        file_names = [fn.strip() for fn in file_names.split(",") if fn.strip()]

        if not file_names:
            console.print("[red]No files provided. Please enter at least one file.[/red]")
            continue

        try:
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=console
            ) as progress:
                progress.add_task(description="📖 Loading documents...", total=len(file_names))
                converted_files = extraction.convert_files_to_text(file_names, converted_files)

            console.print("✓ All documents loaded successfully!", style="bold green")
            return converted_files

        except FileNotFoundError as e:
            console.print(f"[red]Error: {e}[/red]")
            retry = Prompt.ask("One or more files were not found. Do you want to retry? (yes/no)", default="yes")
            if retry.lower() not in {"yes", "y"}:
                console.print("[yellow]Skipping file input.[/yellow]")
                return converted_files

def get_crawled_links(web_url):
    with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=console
        ) as progress:
            progress.add_task(description="🔍 Crawling web page...", total=None)
            feeds = extraction.extract_links(web_url)
            console.print("✓ Web page crawled successfully!", style="bold green")

    return feeds
    
def get_input_url():
    console.print("\n[bold yellow]Step 3:[/bold yellow] Provide Input", style="bold")
    return Prompt.ask("[bold green]Enter the web page URL[/bold green]")

def get_extraction_prompt():
    console.print("\n[bold yellow]Step 4:[/bold yellow] Define Extraction Task", style="bold")

    prompt = Prompt.ask(
        "[bold green]What data do you want to extract?[/bold green]\n"
        "[dim](or type 'exit' to quit)[/dim]"
    )
    return prompt

def display_suggested_fields(fields):
    console.print("\n[bold cyan]💡 AI-Suggested Fields:[/bold cyan]")

    lines = []
    for item in fields:
        name = item.get("field") or ""
        desc = item.get("description") or ""
        if name:
            lines.append(f"{name} — {desc}" if desc else name)

    fields_text = "\n".join(lines)
    panel = Panel(fields_text, title="Recommended Fields", border_style="cyan", box=box.ROUNDED)
    console.print(panel)

def get_extraction_fields():
    console.print("\n[bold green]Enter fields to extract[/bold green] [dim](comma-separated)[/dim]")
    field_input = Prompt.ask("Fields", default="name, price, description")

    field_names = [f.strip() for f in field_input.split(",") if f.strip()]

    fields = []
    for field in field_names:
        fields.append({"name": field})

    return fields

def get_anonymization_choice():
    return Confirm.ask(
        "\n[bold yellow]🔒 Anonymize output?[/bold yellow]",
        default=False
    )

def display_cost(completion_tokens, prompt_tokens):
    console.print(
        f"📝 Prompt Tokens: [cyan]{prompt_tokens}[/cyan]\n"
        f"✍️ Completion Tokens: [green]{completion_tokens}[/green]",
        style="bold"
    )

def display_goodbye():
    console.print("[dim]Session ended.[/dim]\n")