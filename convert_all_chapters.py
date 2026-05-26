#!/usr/bin/env python
"""
Convert all chapter MD files in a project folder to a single PDF
"""

import sys
sys.path.insert(0, 'src')

from pathlib import Path
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn
import argparse

console = Console()

def find_chapter_files(project_dir: Path):
    """Find all chapter_*.md files in the project directory"""
    chapter_files = []
    
    for file in sorted(project_dir.glob("chapter_*.md")):
        # Extract chapter number from filename
        try:
            chapter_num = int(file.stem.split("_")[1])
            chapter_files.append((chapter_num, file))
        except (IndexError, ValueError):
            continue
    
    # Sort by chapter number
    chapter_files.sort(key=lambda x: x[0])
    return chapter_files

def combine_chapters(chapter_files, output_md: Path, project_name: str = "Book"):
    """Combine all chapter files into one markdown file"""
    console.print(f"\n[cyan]📚 Combining {len(chapter_files)} chapters...[/cyan]\n")
    
    combined_content = []
    
    # Add title page
    combined_content.append(f"# {project_name}\n\n")
    combined_content.append("---\n\n")
    
    # Add each chapter
    for chapter_num, chapter_file in chapter_files:
        console.print(f"[green]✓ Adding Chapter {chapter_num}[/green]")
        
        try:
            with open(chapter_file, 'r', encoding='utf-8') as f:
                content = f.read()
                combined_content.append(content)
                combined_content.append("\n\n---\n\n")  # Chapter separator
        except Exception as e:
            console.print(f"[red]✗ Error reading Chapter {chapter_num}: {e}[/red]")
    
    # Write combined file
    console.print(f"\n[cyan]💾 Saving combined markdown...[/cyan]")
    with open(output_md, 'w', encoding='utf-8') as f:
        f.write('\n'.join(combined_content))
    
    console.print(f"[green]✓ Combined markdown saved: {output_md}[/green]")
    return output_md

def convert_to_pdf_weasyprint(md_file: Path, output_pdf: Path):
    """Convert markdown to PDF using WeasyPrint"""
    try:
        import markdown
        from weasyprint import HTML
        
        console.print("\n[cyan]🔄 Converting to PDF with WeasyPrint...[/cyan]")
        
        with open(md_file, 'r', encoding='utf-8') as f:
            md_content = f.read()
        
        html_content = markdown.markdown(
            md_content,
            extensions=['extra', 'nl2br', 'tables', 'toc']
        )
        
        css_style = """
        @page {
            size: letter;
            margin: 1in;
            @bottom-center {
                content: counter(page);
                font-size: 10pt;
            }
        }
        body {
            font-family: 'Georgia', 'Times New Roman', serif;
            font-size: 12pt;
            line-height: 1.8;
            color: #2c3e50;
            text-align: justify;
        }
        h1 {
            font-size: 28pt;
            text-align: center;
            margin: 40pt 0 30pt 0;
            color: #1a1a1a;
            page-break-before: always;
            page-break-after: avoid;
        }
        h2 {
            font-size: 20pt;
            margin: 30pt 0 15pt 0;
            color: #34495e;
            page-break-after: avoid;
        }
        h3 {
            font-size: 16pt;
            margin: 20pt 0 10pt 0;
            color: #34495e;
        }
        p {
            margin-bottom: 12pt;
            text-indent: 2em;
        }
        hr {
            border: none;
            border-top: 2px solid #bdc3c7;
            margin: 30pt 0;
        }
        strong {
            font-weight: bold;
            color: #2c3e50;
        }
        em {
            font-style: italic;
        }
        """
        
        full_html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <style>{css_style}</style>
        </head>
        <body>
            {html_content}
        </body>
        </html>
        """
        
        HTML(string=full_html).write_pdf(output_pdf)
        console.print(f"[green]✓ PDF created: {output_pdf}[/green]")
        return True
        
    except ImportError:
        console.print("[yellow]⚠ WeasyPrint not installed[/yellow]")
        return False
    except Exception as e:
        console.print(f"[red]✗ Error: {e}[/red]")
        return False

def convert_to_pdf_reportlab(md_file: Path, output_pdf: Path):
    """Convert markdown to PDF using ReportLab"""
    try:
        import markdown
        from reportlab.lib.pagesizes import letter
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.units import inch
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
        from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY
        from html.parser import HTMLParser
        
        console.print("\n[cyan]🔄 Converting to PDF with ReportLab...[/cyan]")
        
        with open(md_file, 'r', encoding='utf-8') as f:
            md_content = f.read()
        
        html_content = markdown.markdown(md_content, extensions=['extra'])
        
        doc = SimpleDocTemplate(
            str(output_pdf),
            pagesize=letter,
            rightMargin=72,
            leftMargin=72,
            topMargin=72,
            bottomMargin=36,
        )
        
        styles = getSampleStyleSheet()
        
        title_style = ParagraphStyle(
            'Title',
            parent=styles['Heading1'],
            fontSize=24,
            alignment=TA_CENTER,
            spaceAfter=30,
            fontName='Helvetica-Bold'
        )
        
        heading_style = ParagraphStyle(
            'Heading',
            parent=styles['Heading2'],
            fontSize=16,
            spaceAfter=12,
            spaceBefore=20,
            fontName='Helvetica-Bold'
        )
        
        body_style = ParagraphStyle(
            'Body',
            parent=styles['BodyText'],
            fontSize=12,
            alignment=TA_JUSTIFY,
            spaceAfter=12,
            leading=18
        )
        
        story = []
        
        class PDFParser(HTMLParser):
            def __init__(self):
                super().__init__()
                self.story = []
                self.text = []
                self.tag = None
                
            def handle_starttag(self, tag, attrs):
                self.tag = tag
                
            def handle_endtag(self, tag):
                text = ''.join(self.text).strip()
                if text:
                    if tag == 'h1':
                        self.story.append(PageBreak())
                        self.story.append(Paragraph(text, title_style))
                        self.story.append(Spacer(1, 0.3*inch))
                    elif tag == 'h2':
                        self.story.append(Spacer(1, 0.2*inch))
                        self.story.append(Paragraph(text, heading_style))
                    elif tag == 'p':
                        self.story.append(Paragraph(text, body_style))
                    elif tag == 'hr':
                        self.story.append(Spacer(1, 0.3*inch))
                self.text = []
                self.tag = None
                
            def handle_data(self, data):
                if self.tag:
                    self.text.append(data)
        
        parser = PDFParser()
        parser.feed(html_content)
        
        doc.build(parser.story)
        console.print(f"[green]✓ PDF created: {output_pdf}[/green]")
        return True
        
    except ImportError:
        console.print("[yellow]⚠ ReportLab not installed[/yellow]")
        return False
    except Exception as e:
        console.print(f"[red]✗ Error: {e}[/red]")
        return False

def main():
    parser = argparse.ArgumentParser(
        description='Convert all chapter MD files to a single PDF'
    )
    parser.add_argument(
        'project_dir',
        nargs='?',
        default='projects/shivaAndSati',
        help='Project directory (default: projects/shivaAndSati)'
    )
    parser.add_argument(
        '-o', '--output',
        help='Output PDF filename (default: book.pdf in project dir)'
    )
    parser.add_argument(
        '--name',
        help='Book title for the cover page'
    )
    
    args = parser.parse_args()
    
    project_dir = Path(args.project_dir)
    
    if not project_dir.exists():
        console.print(f"[red]✗ Project directory not found: {project_dir}[/red]")
        sys.exit(1)
    
    console.print("\n[bold cyan]📚 Chapter to PDF Converter[/bold cyan]")
    console.print(f"[bold]Project:[/bold] {project_dir}\n")
    
    # Find chapter files
    console.print("[cyan]🔍 Scanning for chapter files...[/cyan]")
    chapter_files = find_chapter_files(project_dir)
    
    if not chapter_files:
        console.print("[red]✗ No chapter files found (chapter_*.md)[/red]")
        sys.exit(1)
    
    console.print(f"[green]✓ Found {len(chapter_files)} chapters[/green]")
    
    # Get book name
    book_name = args.name
    if not book_name:
        try:
            import json
            project_data = project_dir / "project_data.json"
            if project_data.exists():
                with open(project_data, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    book_name = data.get('title', project_dir.name)
            else:
                book_name = project_dir.name
        except:
            book_name = project_dir.name
    
    console.print(f"[bold]Book Title:[/bold] {book_name}\n")
    
    # Combine chapters
    combined_md = project_dir / "combined_manuscript.md"
    combine_chapters(chapter_files, combined_md, book_name)
    
    # Determine output PDF
    if args.output:
        output_pdf = Path(args.output)
    else:
        output_pdf = project_dir / "book.pdf"
    
    # Convert to PDF
    success = convert_to_pdf_weasyprint(combined_md, output_pdf)
    
    if not success:
        success = convert_to_pdf_reportlab(combined_md, output_pdf)
    
    if not success:
        console.print("\n[red]❌ PDF conversion failed[/red]")
        console.print("[yellow]Install required libraries:[/yellow]")
        console.print("  pip install weasyprint markdown reportlab")
        console.print(f"\n[cyan]Combined markdown saved at:[/cyan] {combined_md}")
        console.print("[cyan]You can convert it manually using online tools[/cyan]")
        sys.exit(1)
    
    # Show results
    file_size = output_pdf.stat().st_size / (1024 * 1024)
    console.print(f"\n[bold green]🎉 Success![/bold green]")
    console.print(f"[bold]PDF:[/bold] {output_pdf}")
    console.print(f"[bold]Size:[/bold] {file_size:.2f} MB")
    console.print(f"[bold]Chapters:[/bold] {len(chapter_files)}\n")

if __name__ == "__main__":
    main()
