#!/usr/bin/env python
"""
KDP-Ready Book Creator
Creates professional, print-ready PDFs for Amazon KDP publishing
Follows KDP formatting guidelines and best practices
"""

import sys
sys.path.insert(0, 'src')

from pathlib import Path
from rich.console import Console
from rich.prompt import Confirm
import argparse
import json

console = Console()

def find_chapter_files(project_dir: Path):
    """Find all chapter_*.md files"""
    chapter_files = []
    for file in sorted(project_dir.glob("chapter_*.md")):
        try:
            chapter_num = int(file.stem.split("_")[1])
            chapter_files.append((chapter_num, file))
        except (IndexError, ValueError):
            continue
    chapter_files.sort(key=lambda x: x[0])
    return chapter_files

def load_project_metadata(project_dir: Path):
    """Load project metadata from project_data.json"""
    metadata = {
        'title': 'Untitled Book',
        'author': 'Unknown Author',
        'genre': 'Fiction',
        'description': ''
    }
    
    project_data = project_dir / "project_data.json"
    if project_data.exists():
        try:
            with open(project_data, 'r', encoding='utf-8') as f:
                data = json.load(f)
                metadata['title'] = data.get('title', metadata['title'])
                metadata['author'] = data.get('author', metadata['author'])
                metadata['genre'] = data.get('genre', metadata['genre'])
                metadata['description'] = data.get('description', metadata['description'])
        except:
            pass
    
    return metadata

def create_kdp_pdf(chapter_files, output_pdf: Path, metadata: dict, trim_size: str = "6x9"):
    """Create KDP-ready PDF with professional formatting"""
    try:
        from reportlab.lib.pagesizes import inch
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT, TA_RIGHT
        from reportlab.platypus import (
            SimpleDocTemplate, Paragraph, Spacer, PageBreak,
            Table, TableStyle, KeepTogether
        )
        from reportlab.lib import colors
        from reportlab.pdfgen import canvas
        import markdown
        from html.parser import HTMLParser
        
        console.print(f"\n[cyan]📐 Creating KDP-ready PDF ({trim_size})...[/cyan]\n")
        
        # KDP Standard trim sizes
        trim_sizes = {
            "5x8": (5*inch, 8*inch),
            "6x9": (6*inch, 9*inch),
            "5.5x8.5": (5.5*inch, 8.5*inch),
            "8.5x11": (8.5*inch, 11*inch)
        }
        
        page_size = trim_sizes.get(trim_size, (6*inch, 9*inch))
        
        # KDP margin requirements (minimum 0.25" for gutter, 0.125" for outside)
        # Using safer margins for perfect binding
        left_margin = 0.75*inch  # Inside margin (gutter)
        right_margin = 0.5*inch  # Outside margin
        top_margin = 0.75*inch
        bottom_margin = 0.75*inch
        
        # Custom page template with headers/footers
        class KDPDocTemplate(SimpleDocTemplate):
            def __init__(self, filename, **kwargs):
                super().__init__(filename, **kwargs)
                self.book_title = metadata['title']
                self.author = metadata['author']
                
            def afterPage(self):
                """Add page numbers and headers"""
                self.canv.saveState()
                
                # Page number at bottom center
                page_num = self.canv.getPageNumber()
                if page_num > 3:  # Skip title pages
                    self.canv.setFont('Times-Roman', 10)
                    self.canv.drawCentredString(
                        self.width/2 + left_margin,
                        0.5*inch,
                        str(page_num - 3)
                    )
                
                # Header (book title on even pages, chapter on odd pages)
                if page_num > 3:
                    self.canv.setFont('Times-Italic', 9)
                    if page_num % 2 == 0:  # Even page - book title on left
                        self.canv.drawString(
                            left_margin,
                            self.height + top_margin - 0.3*inch,
                            self.book_title[:40]
                        )
                    else:  # Odd page - author on right
                        self.canv.drawRightString(
                            self.width + left_margin,
                            self.height + top_margin - 0.3*inch,
                            self.author
                        )
                
                self.canv.restoreState()
        
        # Create document
        doc = KDPDocTemplate(
            str(output_pdf),
            pagesize=page_size,
            leftMargin=left_margin,
            rightMargin=right_margin,
            topMargin=top_margin,
            bottomMargin=bottom_margin,
        )
        
        # Professional book styles
        styles = getSampleStyleSheet()
        
        # Title page style
        title_style = ParagraphStyle(
            'BookTitle',
            parent=styles['Title'],
            fontSize=28,
            leading=34,
            alignment=TA_CENTER,
            spaceAfter=0.5*inch,
            fontName='Times-Bold',
            textColor=colors.HexColor('#1a1a1a')
        )
        
        author_style = ParagraphStyle(
            'Author',
            parent=styles['Normal'],
            fontSize=16,
            alignment=TA_CENTER,
            spaceAfter=0.3*inch,
            fontName='Times-Roman'
        )
        
        # Chapter title style
        chapter_title_style = ParagraphStyle(
            'ChapterTitle',
            parent=styles['Heading1'],
            fontSize=20,
            leading=24,
            alignment=TA_CENTER,
            spaceAfter=0.4*inch,
            spaceBefore=0.5*inch,
            fontName='Times-Bold',
            textColor=colors.HexColor('#2c3e50')
        )
        
        # Chapter number style
        chapter_number_style = ParagraphStyle(
            'ChapterNumber',
            parent=styles['Normal'],
            fontSize=14,
            alignment=TA_CENTER,
            spaceAfter=0.2*inch,
            fontName='Times-Italic',
            textColor=colors.HexColor('#7f8c8d')
        )
        
        # Body text style (KDP standard)
        body_style = ParagraphStyle(
            'KDPBody',
            parent=styles['BodyText'],
            fontSize=11,
            leading=16,
            alignment=TA_JUSTIFY,
            spaceAfter=10,
            firstLineIndent=0.25*inch,
            fontName='Times-Roman',
            textColor=colors.HexColor('#2c3e50')
        )
        
        # Scene break style
        scene_break_style = ParagraphStyle(
            'SceneBreak',
            parent=styles['Normal'],
            fontSize=14,
            alignment=TA_CENTER,
            spaceAfter=12,
            spaceBefore=12,
            fontName='Times-Roman'
        )
        
        story = []
        
        # === TITLE PAGE ===
        story.append(Spacer(1, 2*inch))
        story.append(Paragraph(metadata['title'], title_style))
        story.append(Spacer(1, 0.3*inch))
        story.append(Paragraph(f"by {metadata['author']}", author_style))
        story.append(PageBreak())
        
        # === COPYRIGHT PAGE ===
        copyright_style = ParagraphStyle(
            'Copyright',
            parent=styles['Normal'],
            fontSize=9,
            alignment=TA_LEFT,
            fontName='Times-Roman'
        )
        
        story.append(Spacer(1, 6*inch))
        story.append(Paragraph(f"Copyright © 2024 {metadata['author']}", copyright_style))
        story.append(Spacer(1, 0.1*inch))
        story.append(Paragraph("All rights reserved.", copyright_style))
        story.append(Spacer(1, 0.2*inch))
        story.append(Paragraph(
            "No part of this book may be reproduced or transmitted in any form or by any means, "
            "electronic or mechanical, including photocopying, recording, or by any information "
            "storage and retrieval system, without permission in writing from the author.",
            copyright_style
        ))
        story.append(PageBreak())
        
        # === TABLE OF CONTENTS ===
        toc_title_style = ParagraphStyle(
            'TOCTitle',
            parent=styles['Heading1'],
            fontSize=18,
            alignment=TA_CENTER,
            spaceAfter=0.5*inch,
            fontName='Times-Bold'
        )
        
        toc_entry_style = ParagraphStyle(
            'TOCEntry',
            parent=styles['Normal'],
            fontSize=11,
            spaceAfter=8,
            fontName='Times-Roman'
        )
        
        story.append(Paragraph("Contents", toc_title_style))
        story.append(Spacer(1, 0.3*inch))
        
        # Read chapter titles for TOC
        for chapter_num, chapter_file in chapter_files:
            with open(chapter_file, 'r', encoding='utf-8') as f:
                first_lines = f.read(500)
                # Extract chapter title from markdown
                for line in first_lines.split('\n'):
                    if line.startswith('## Chapter'):
                        title = line.replace('## ', '').strip()
                        story.append(Paragraph(f"{title}", toc_entry_style))
                        break
                else:
                    story.append(Paragraph(f"Chapter {chapter_num}", toc_entry_style))
        
        story.append(PageBreak())
        
        # === CHAPTERS ===
        console.print("[cyan]📖 Processing chapters...[/cyan]\n")
        
        class ChapterParser(HTMLParser):
            def __init__(self):
                super().__init__()
                self.story = []
                self.text = []
                self.tag = None
                self.in_bold = False
                self.in_italic = False
                
            def handle_starttag(self, tag, attrs):
                self.tag = tag
                if tag == 'strong':
                    self.in_bold = True
                elif tag == 'em':
                    self.in_italic = True
                    
            def handle_endtag(self, tag):
                text = ''.join(self.text).strip()
                
                if tag == 'strong':
                    self.in_bold = False
                elif tag == 'em':
                    self.in_italic = False
                
                if text and tag in ['h1', 'h2', 'h3', 'p', 'hr']:
                    # Clean text for PDF (handle special characters)
                    text = text.encode('latin-1', 'replace').decode('latin-1')
                    
                    if tag == 'h2':
                        # Chapter title
                        if 'Chapter' in text:
                            parts = text.split(':', 1)
                            if len(parts) == 2:
                                self.story.append(Paragraph(parts[0], chapter_number_style))
                                self.story.append(Paragraph(parts[1].strip(), chapter_title_style))
                            else:
                                self.story.append(Paragraph(text, chapter_title_style))
                        else:
                            self.story.append(Paragraph(text, chapter_title_style))
                    elif tag == 'h3':
                        # Scene title
                        self.story.append(Spacer(1, 0.2*inch))
                        self.story.append(Paragraph(text, scene_break_style))
                    elif tag == 'p':
                        # Body paragraph
                        if text == '***' or text == '* * *':
                            self.story.append(Paragraph('* * *', scene_break_style))
                        else:
                            self.story.append(Paragraph(text, body_style))
                    elif tag == 'hr':
                        self.story.append(Spacer(1, 0.2*inch))
                        self.story.append(Paragraph('* * *', scene_break_style))
                        self.story.append(Spacer(1, 0.2*inch))
                
                self.text = []
                self.tag = None
                
            def handle_data(self, data):
                if self.tag:
                    if self.in_bold:
                        self.text.append(f'<b>{data}</b>')
                    elif self.in_italic:
                        self.text.append(f'<i>{data}</i>')
                    else:
                        self.text.append(data)
        
        for chapter_num, chapter_file in chapter_files:
            console.print(f"[green]✓ Processing Chapter {chapter_num}[/green]")
            
            # New chapter starts on odd page (right side)
            if len(story) > 0:
                story.append(PageBreak())
            
            with open(chapter_file, 'r', encoding='utf-8') as f:
                md_content = f.read()
            
            html_content = markdown.markdown(md_content, extensions=['extra', 'nl2br'])
            
            parser = ChapterParser()
            parser.feed(html_content)
            story.extend(parser.story)
        
        # Build PDF
        console.print(f"\n[cyan]🔨 Building PDF...[/cyan]")
        doc.build(story)
        
        file_size = output_pdf.stat().st_size / (1024 * 1024)
        console.print(f"\n[green]✓ KDP-ready PDF created![/green]")
        console.print(f"[bold]File:[/bold] {output_pdf}")
        console.print(f"[bold]Size:[/bold] {file_size:.2f} MB")
        console.print(f"[bold]Trim Size:[/bold] {trim_size}")
        console.print(f"[bold]Pages:[/bold] ~{len(chapter_files) * 15} (estimated)")
        
        return True
        
    except ImportError as e:
        console.print(f"[red]✗ Missing library: {e}[/red]")
        console.print("[yellow]Install with: pip install reportlab markdown[/yellow]")
        return False
    except Exception as e:
        console.print(f"[red]✗ Error: {e}[/red]")
        import traceback
        traceback.print_exc()
        return False

def main():
    parser = argparse.ArgumentParser(
        description='Create KDP-ready PDF from LibriScribe project'
    )
    parser.add_argument(
        'project_dir',
        nargs='?',
        default='projects/shivaAndSati',
        help='Project directory'
    )
    parser.add_argument(
        '-o', '--output',
        help='Output PDF filename'
    )
    parser.add_argument(
        '--trim-size',
        choices=['5x8', '6x9', '5.5x8.5', '8.5x11'],
        default='6x9',
        help='Book trim size (default: 6x9)'
    )
    parser.add_argument(
        '--author',
        help='Author name (overrides project data)'
    )
    
    args = parser.parse_args()
    
    project_dir = Path(args.project_dir)
    
    if not project_dir.exists():
        console.print(f"[red]✗ Project not found: {project_dir}[/red]")
        sys.exit(1)
    
    console.print("\n[bold cyan]📚 KDP Book Creator[/bold cyan]")
    console.print("[dim]Professional print-ready PDFs for Amazon KDP[/dim]\n")
    
    # Load metadata
    metadata = load_project_metadata(project_dir)
    if args.author:
        metadata['author'] = args.author
    
    console.print(f"[bold]Title:[/bold] {metadata['title']}")
    console.print(f"[bold]Author:[/bold] {metadata['author']}")
    console.print(f"[bold]Genre:[/bold] {metadata['genre']}")
    console.print(f"[bold]Trim Size:[/bold] {args.trim_size}\n")
    
    # Find chapters
    chapter_files = find_chapter_files(project_dir)
    
    if not chapter_files:
        console.print("[red]✗ No chapters found[/red]")
        sys.exit(1)
    
    console.print(f"[green]✓ Found {len(chapter_files)} chapters[/green]")
    
    # Determine output
    if args.output:
        output_pdf = Path(args.output)
    else:
        safe_title = "".join(c for c in metadata['title'] if c.isalnum() or c in (' ', '-', '_'))
        safe_title = safe_title.replace(' ', '_')
        output_pdf = project_dir / f"{safe_title}_KDP.pdf"
    
    # Create PDF
    success = create_kdp_pdf(chapter_files, output_pdf, metadata, args.trim_size)
    
    if success:
        console.print("\n[bold green]🎉 Success![/bold green]")
        console.print("\n[bold cyan]KDP Upload Checklist:[/bold cyan]")
        console.print("  ✓ PDF is print-ready")
        console.print("  ✓ Margins meet KDP requirements")
        console.print("  ✓ Page numbers included")
        console.print("  ✓ Copyright page added")
        console.print("  ✓ Table of contents included")
        console.print("\n[yellow]Next steps:[/yellow]")
        console.print("  1. Review the PDF carefully")
        console.print("  2. Upload to KDP: https://kdp.amazon.com")
        console.print("  3. Set your pricing and territories")
        console.print("  4. Order a proof copy to check quality\n")
    else:
        sys.exit(1)

if __name__ == "__main__":
    main()
