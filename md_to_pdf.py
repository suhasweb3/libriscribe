#!/usr/bin/env python
"""
Professional Markdown to PDF Converter
Converts Markdown files to beautifully formatted PDFs with Unicode support
"""

import sys
import argparse
from pathlib import Path
from rich.console import Console

console = Console()

def convert_with_markdown(md_file: str, output_pdf: str):
    """Convert using markdown library + reportlab (best quality)"""
    try:
        import markdown
        from reportlab.lib.pagesizes import letter, A4
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.units import inch
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
        from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY
        from reportlab.pdfbase import pdfmetrics
        from reportlab.pdfbase.ttfonts import TTFont
        
        console.print("[cyan]📄 Reading Markdown file...[/cyan]")
        with open(md_file, 'r', encoding='utf-8') as f:
            md_content = f.read()
        
        console.print("[cyan]🔄 Converting Markdown to HTML...[/cyan]")
        html_content = markdown.markdown(md_content, extensions=['extra', 'nl2br'])
        
        console.print("[cyan]📝 Creating PDF...[/cyan]")
        
        # Create PDF
        doc = SimpleDocTemplate(
            output_pdf,
            pagesize=letter,
            rightMargin=72,
            leftMargin=72,
            topMargin=72,
            bottomMargin=18,
        )
        
        # Styles
        styles = getSampleStyleSheet()
        
        # Custom styles
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            textColor='#1a1a1a',
            spaceAfter=30,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        )
        
        heading_style = ParagraphStyle(
            'CustomHeading',
            parent=styles['Heading2'],
            fontSize=16,
            textColor='#2c3e50',
            spaceAfter=12,
            spaceBefore=12,
            fontName='Helvetica-Bold'
        )
        
        body_style = ParagraphStyle(
            'CustomBody',
            parent=styles['BodyText'],
            fontSize=12,
            textColor='#333333',
            alignment=TA_JUSTIFY,
            spaceAfter=12,
            leading=16
        )
        
        # Build PDF content
        story = []
        
        # Parse HTML and create PDF elements
        from html.parser import HTMLParser
        
        class PDFHTMLParser(HTMLParser):
            def __init__(self):
                super().__init__()
                self.story = []
                self.current_text = []
                self.in_h1 = False
                self.in_h2 = False
                self.in_p = False
                
            def handle_starttag(self, tag, attrs):
                if tag == 'h1':
                    self.in_h1 = True
                elif tag == 'h2':
                    self.in_h2 = True
                elif tag == 'p':
                    self.in_p = True
                elif tag == 'br':
                    self.current_text.append('<br/>')
                    
            def handle_endtag(self, tag):
                text = ''.join(self.current_text).strip()
                
                if tag == 'h1' and self.in_h1:
                    if text:
                        self.story.append(Paragraph(text, title_style))
                        self.story.append(Spacer(1, 0.3*inch))
                    self.in_h1 = False
                    self.current_text = []
                    
                elif tag == 'h2' and self.in_h2:
                    if text:
                        self.story.append(Spacer(1, 0.2*inch))
                        self.story.append(Paragraph(text, heading_style))
                        self.story.append(Spacer(1, 0.1*inch))
                    self.in_h2 = False
                    self.current_text = []
                    
                elif tag == 'p' and self.in_p:
                    if text:
                        self.story.append(Paragraph(text, body_style))
                    self.in_p = False
                    self.current_text = []
                    
            def handle_data(self, data):
                self.current_text.append(data)
        
        parser = PDFHTMLParser()
        parser.feed(html_content)
        story = parser.story
        
        # Build PDF
        doc.build(story)
        
        console.print(f"[green]✓ PDF created successfully: {output_pdf}[/green]")
        return True
        
    except ImportError as e:
        console.print(f"[yellow]Missing library: {e}[/yellow]")
        console.print("[yellow]Install with: pip install markdown reportlab[/yellow]")
        return False
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        return False

def convert_with_weasyprint(md_file: str, output_pdf: str):
    """Convert using weasyprint (excellent quality, CSS support)"""
    try:
        import markdown
        from weasyprint import HTML, CSS
        
        console.print("[cyan]📄 Reading Markdown file...[/cyan]")
        with open(md_file, 'r', encoding='utf-8') as f:
            md_content = f.read()
        
        console.print("[cyan]🔄 Converting to HTML...[/cyan]")
        html_content = markdown.markdown(md_content, extensions=['extra', 'nl2br', 'tables'])
        
        # Add CSS styling
        css_style = """
        @page {
            size: letter;
            margin: 1in;
        }
        body {
            font-family: 'Georgia', serif;
            font-size: 12pt;
            line-height: 1.6;
            color: #333;
        }
        h1 {
            font-size: 24pt;
            text-align: center;
            margin-top: 0;
            margin-bottom: 30pt;
            color: #1a1a1a;
            page-break-after: avoid;
        }
        h2 {
            font-size: 18pt;
            margin-top: 20pt;
            margin-bottom: 10pt;
            color: #2c3e50;
            page-break-after: avoid;
        }
        h3 {
            font-size: 14pt;
            margin-top: 15pt;
            margin-bottom: 8pt;
            color: #34495e;
        }
        p {
            text-align: justify;
            margin-bottom: 12pt;
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
        
        console.print("[cyan]📝 Creating PDF...[/cyan]")
        HTML(string=full_html).write_pdf(output_pdf)
        
        console.print(f"[green]✓ PDF created successfully: {output_pdf}[/green]")
        return True
        
    except ImportError:
        console.print("[yellow]WeasyPrint not installed.[/yellow]")
        console.print("[yellow]Install with: pip install weasyprint[/yellow]")
        return False
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        return False

def convert_with_pypandoc(md_file: str, output_pdf: str):
    """Convert using pypandoc (requires pandoc installed)"""
    try:
        import pypandoc
        
        console.print("[cyan]📄 Converting with Pandoc...[/cyan]")
        
        pypandoc.convert_file(
            md_file,
            'pdf',
            outputfile=output_pdf,
            extra_args=[
                '--pdf-engine=xelatex',
                '-V', 'geometry:margin=1in',
                '-V', 'fontsize=12pt',
                '-V', 'linestretch=1.5'
            ]
        )
        
        console.print(f"[green]✓ PDF created successfully: {output_pdf}[/green]")
        return True
        
    except ImportError:
        console.print("[yellow]pypandoc not installed.[/yellow]")
        console.print("[yellow]Install with: pip install pypandoc[/yellow]")
        return False
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        return False

def main():
    parser = argparse.ArgumentParser(
        description='Convert Markdown to PDF with professional formatting'
    )
    parser.add_argument('input', help='Input Markdown file (.md)')
    parser.add_argument('-o', '--output', help='Output PDF file (optional)')
    parser.add_argument(
        '-m', '--method',
        choices=['auto', 'weasyprint', 'reportlab', 'pandoc'],
        default='auto',
        help='Conversion method (default: auto)'
    )
    
    args = parser.parse_args()
    
    # Validate input file
    input_file = Path(args.input)
    if not input_file.exists():
        console.print(f"[red]Error: File not found: {args.input}[/red]")
        sys.exit(1)
    
    # Determine output file
    if args.output:
        output_file = args.output
    else:
        output_file = str(input_file.with_suffix('.pdf'))
    
    console.print("\n[bold cyan]📚 Markdown to PDF Converter[/bold cyan]\n")
    console.print(f"[bold]Input:[/bold]  {input_file}")
    console.print(f"[bold]Output:[/bold] {output_file}\n")
    
    # Try conversion methods
    success = False
    
    if args.method == 'auto':
        # Try methods in order of quality
        console.print("[cyan]Trying WeasyPrint (best quality)...[/cyan]")
        success = convert_with_weasyprint(str(input_file), output_file)
        
        if not success:
            console.print("\n[cyan]Trying ReportLab...[/cyan]")
            success = convert_with_markdown(str(input_file), output_file)
        
        if not success:
            console.print("\n[cyan]Trying Pandoc...[/cyan]")
            success = convert_with_pypandoc(str(input_file), output_file)
            
    elif args.method == 'weasyprint':
        success = convert_with_weasyprint(str(input_file), output_file)
    elif args.method == 'reportlab':
        success = convert_with_markdown(str(input_file), output_file)
    elif args.method == 'pandoc':
        success = convert_with_pypandoc(str(input_file), output_file)
    
    if not success:
        console.print("\n[red]❌ All conversion methods failed.[/red]")
        console.print("\n[yellow]Install required libraries:[/yellow]")
        console.print("  pip install weasyprint markdown reportlab pypandoc")
        console.print("\n[yellow]Or install Pandoc:[/yellow]")
        console.print("  https://pandoc.org/installing.html")
        sys.exit(1)
    
    console.print(f"\n[bold green]🎉 Conversion complete![/bold green]")
    console.print(f"[dim]File size: {Path(output_file).stat().st_size / 1024:.1f} KB[/dim]\n")

if __name__ == "__main__":
    main()
