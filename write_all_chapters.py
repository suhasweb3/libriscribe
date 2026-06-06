#!/usr/bin/env python
"""Dynamically write all chapters for any LibriScribe project"""

import sys
sys.path.insert(0, 'src')

from pathlib import Path
from libriscribe.agents.project_manager import ProjectManagerAgent
from libriscribe.settings import Settings
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TimeElapsedColumn
from rich.table import Table

console = Console()

def find_projects():
    """Find all available projects in the projects directory"""
    settings = Settings()
    projects_dir = Path(settings.projects_dir)
    
    if not projects_dir.exists():
        return []
    
    projects = []
    for project_path in projects_dir.iterdir():
        if project_path.is_dir():
            project_data_file = project_path / "project_data.json"
            if project_data_file.exists():
                projects.append(project_path.name)
    
    return projects

def select_project(projects):
    """Let user select a project"""
    if not projects:
        console.print("[red]❌ No projects found in the projects directory[/red]")
        return None
    
    if len(projects) == 1:
        console.print(f"[cyan]Found 1 project: {projects[0]}[/cyan]")
        return projects[0]
    
    console.print("\n[bold]📚 Available Projects:[/bold]\n")
    
    table = Table(show_header=True, header_style="bold cyan")
    table.add_column("#", style="cyan", width=6)
    table.add_column("Project Name", style="green")
    
    for idx, project in enumerate(projects, 1):
        table.add_row(str(idx), project)
    
    console.print(table)
    console.print()
    
    while True:
        try:
            choice = input("Select project number (or 'q' to quit): ").strip()
            if choice.lower() == 'q':
                return None
            
            choice_idx = int(choice) - 1
            if 0 <= choice_idx < len(projects):
                return projects[choice_idx]
            else:
                console.print("[red]Invalid choice. Please try again.[/red]")
        except ValueError:
            console.print("[red]Please enter a number.[/red]")

def check_existing_chapters(project_manager, num_chapters):
    """Check which chapters already exist"""
    existing = []
    missing = []
    
    for i in range(1, num_chapters + 1):
        chapter_file = project_manager.project_dir / f"chapter_{i}.md"
        if chapter_file.exists():
            existing.append(i)
        else:
            missing.append(i)
    
    return existing, missing

def main():
    console.print("\n[bold cyan]📚 LibriScribe - Dynamic Chapter Writer[/bold cyan]\n")
    
    # Find available projects
    console.print("🔍 Scanning for projects...")
    projects = find_projects()
    
    if not projects:
        console.print("[red]No projects found. Please create a project first.[/red]")
        return
    
    # Select project
    project_name = select_project(projects)
    if not project_name:
        console.print("\n👋 Cancelled.")
        return
    
    console.print(f"\n[green]✓ Selected project: {project_name}[/green]\n")
    
    # Initialize project manager
    project_manager = ProjectManagerAgent(llm_client=None)
    
    # Load project
    console.print("📂 Loading project data...")
    try:
        project_manager.load_project_data(project_name)
    except Exception as e:
        console.print(f"[red]❌ Failed to load project: {e}[/red]")
        return
    
    if not project_manager.project_knowledge_base:
        console.print("[red]❌ Project data is invalid[/red]")
        return
    
    kb = project_manager.project_knowledge_base
    
    # Display project info
    console.print("[green]✓ Project loaded successfully![/green]\n")
    console.print(f"[bold]Title:[/bold] {kb.title}")
    console.print(f"[bold]Genre:[/bold] {kb.genre}")
    console.print(f"[bold]Category:[/bold] {kb.category}")
    console.print(f"[bold]Language:[/bold] {kb.language}")
    
    # Get LLM provider
    llm_provider = kb.get("llm_provider", "ollama")
    console.print(f"[bold]LLM Provider:[/bold] {llm_provider}\n")
    
    # Initialize LLM
    console.print(f"🤖 Initializing {llm_provider}...")
    try:
        project_manager.initialize_llm_client(llm_provider)
        console.print(f"[green]✓ {llm_provider} connected[/green]\n")
    except Exception as e:
        console.print(f"[red]❌ Failed to initialize LLM: {e}[/red]")
        return
    
    # Get number of chapters
    num_chapters = len(kb.chapters)
    if num_chapters == 0:
        console.print("[red]❌ No chapters found in outline. Please generate an outline first.[/red]")
        return
    
    console.print(f"[bold]📖 Total chapters in outline: {num_chapters}[/bold]\n")
    
    # Check existing chapters
    existing, missing = check_existing_chapters(project_manager, num_chapters)
    
    if existing:
        console.print(f"[yellow]⚠️  Found {len(existing)} existing chapters: {existing}[/yellow]")
        overwrite = input("Do you want to overwrite existing chapters? (y/n): ").strip().lower()
        if overwrite != 'y':
            console.print("[cyan]Will only write missing chapters.[/cyan]")
            chapters_to_write = missing
        else:
            chapters_to_write = list(range(1, num_chapters + 1))
    else:
        chapters_to_write = list(range(1, num_chapters + 1))
    
    if not chapters_to_write:
        console.print("\n[green]✓ All chapters already exist![/green]")
        return
    
    console.print(f"\n[bold]📝 Chapters to write: {len(chapters_to_write)}[/bold]")
    console.print(f"[dim]Chapters: {chapters_to_write}[/dim]\n")
    
    # Confirm before starting
    response = input(f"Start writing {len(chapters_to_write)} chapters? (y/n): ")
    if response.lower() != 'y':
        console.print("\n👋 Cancelled.")
        return
    
    console.print("\n[cyan]Starting chapter generation...[/cyan]\n")
    
    # Write chapters with progress tracking
    success_count = 0
    error_count = 0
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
        TimeElapsedColumn(),
        console=console
    ) as progress:
        
        task = progress.add_task("[cyan]Writing chapters...", total=len(chapters_to_write))
        
        for chapter_num in chapters_to_write:
            chapter = kb.get_chapter(chapter_num)
            chapter_title = chapter.title if chapter else f"Chapter {chapter_num}"
            
            progress.update(task, description=f"[cyan]Ch {chapter_num}/{num_chapters}: {chapter_title[:40]}...")
            
            try:
                project_manager.write_and_review_chapter(chapter_num)
                project_manager.checkpoint()
                console.print(f"[green]✓ Chapter {chapter_num}: {chapter_title}[/green]")
                success_count += 1
            except Exception as e:
                console.print(f"[red]✗ Chapter {chapter_num} failed: {str(e)}[/red]")
                error_count += 1
                
                # Ask if user wants to continue after error
                if error_count >= 3:
                    cont = input("\nMultiple errors occurred. Continue? (y/n): ").strip().lower()
                    if cont != 'y':
                        console.print("\n[yellow]Stopping chapter generation.[/yellow]")
                        break
            
            progress.update(task, advance=1)
    
    # Summary
    console.print("\n" + "="*60)
    console.print("[bold green]📊 Generation Summary[/bold green]")
    console.print("="*60)
    console.print(f"[green]✓ Successfully written: {success_count} chapters[/green]")
    if error_count > 0:
        console.print(f"[red]✗ Failed: {error_count} chapters[/red]")
    console.print(f"\n📁 Location: {project_manager.project_dir}")
    
    console.print("\n[bold]Next steps:[/bold]")
    console.print("  • Review chapters in the project folder")
    console.print("  • Format book: [cyan]python -m libriscribe.main format[/cyan]")
    console.print("  • Edit chapter: [cyan]python -m libriscribe.main edit --chapter-number N[/cyan]")
    console.print("  • Resume project: [cyan]python -m libriscribe.main resume[/cyan]\n")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        console.print("\n\n[yellow]⚠️  Interrupted by user[/yellow]")
        console.print("Progress has been saved. Run the script again to continue.\n")
    except Exception as e:
        console.print(f"\n[red]❌ Unexpected error: {e}[/red]")
        import traceback
        traceback.print_exc()
