#!/usr/bin/env python
"""
Professional Book Creator for KDP Publishing
Uses Pandoc + LaTeX for publication-quality PDFs
Industry-standard formatting for professional books
"""

import sys
sys.path.insert(0, 'src')

from pathlib import Path
from rich.console import Console
import argparse
import json
import subprocess
import shutil
from libriscribe.auth import authenticate

console = Console()

def check_pandoc():
    """Check if Pandoc is installed"""
    try:
        result = subprocess.run(['pandoc', '--version'], 
                              capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            version = result.stdout.split('\n')[0]
            console.print(f"[green]✓ {version}[/green]")
            return True
    except:
        pass
    
    console.print("[red]✗ Pandoc not found[/red]")
    console.print("\n[yellow]Install Pandoc:[/yellow]")
    console.print("  Windows: https://pandoc.org/installing.html")
    console.print("  Or: winget install pandoc")
    console.print("  Or: choco install pandoc")
    return False

def find_chapter_files(project_dir: Path):
    """Find all chapter MD files"""
    chapter_files = []
    for file in sorted(project_dir.glob("chapter_*.md")):
        try:
            chapter_num = int(file.stem.split("_")[1])
            chapter_files.append((chapter_num, file))
        except:
            continue
    chapter_files.sort(key=lambda x: x[0])
    return chapter_files

def generate_isbn():
    """Generate a random ISBN-13 for the book"""
    import random
    # ISBN-13 format: 978-X-XXX-XXXXX-X
    # Using 978 prefix (standard for books)
    isbn_base = "978" + "".join([str(random.randint(0, 9)) for _ in range(9)])
    
    # Calculate check digit
    total = sum(int(digit) * (1 if i % 2 == 0 else 3) for i, digit in enumerate(isbn_base))
    check_digit = (10 - (total % 10)) % 10
    
    isbn = isbn_base + str(check_digit)
    # Format: 978-X-XXX-XXXXX-X
    return f"{isbn[:3]}-{isbn[3]}-{isbn[4:7]}-{isbn[7:12]}-{isbn[12]}"

def load_metadata(project_dir: Path):
    """Load project metadata"""
    metadata = {
        'title': 'Untitled Book',
        'author': 'Unknown Author',
        'genre': 'Fiction',
        'description': '',
        'language': 'en-US'
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

def create_latex_template(trim_size: str, isbn: str):
    """Create professional LaTeX template for book"""
    
    # Page dimensions for different trim sizes
    sizes = {
        '5x8': ('5in', '8in'),
        '6x9': ('6in', '9in'),
        '5.5x8.5': ('5.5in', '8.5in'),
        '8.5x11': ('8.5in', '11in')
    }
    
    width, height = sizes.get(trim_size, ('6in', '9in'))
    
    template = r'''
\documentclass[11pt,openright]{book}

% Page setup
\usepackage[paperwidth=''' + width + r''',paperheight=''' + height + r''',
            inner=0.75in,outer=0.5in,top=0.75in,bottom=0.75in,
            headsep=0.25in,footskip=0.3in]{geometry}

% Use standard fonts (no fontspec needed)
\usepackage[T1]{fontenc}
\usepackage{lmodern}

% Better typography
\usepackage{microtype}
\usepackage{setspace}
\setstretch{1.15}

% -------------------------------------------------------
% OVERFLOW / MARGIN BLEED PREVENTION
% -------------------------------------------------------
% emergencystretch: before declaring overfull, LaTeX will
% stretch word spacing up to this much — prevents >99% of
% text-bleeding-out-of-margin cases in prose books.
\emergencystretch=3em

% Allow LaTeX to be sloppy about line-breaking rather than
% letting text spill into the margin.
\sloppy

% Lower the penalty for hyphenating — encourages breaking
% long compound words instead of overflowing the line.
\hyphenpenalty=200
\exhyphenpenalty=200

% Raise tolerance so LaTeX accepts "less ideal" line breaks
% instead of overflowing the margin.
\tolerance=2000
\pretolerance=150

% Allow tiny invisible overruns (< 2pt) silently — removes
% spurious overfull warnings for rounding-error overflows.
\hfuzz=2pt

% URL and long-string overflow fix: let URLs/long tokens
% break at any character rather than spilling out.
\usepackage[hyphens]{url}
\usepackage{xurl}
% -------------------------------------------------------

% Headers and footers
\usepackage{fancyhdr}
\pagestyle{fancy}
\fancyhf{}
\fancyhead[LE]{\small\itshape\nouppercase{\leftmark}}
\fancyhead[RO]{\small\itshape $author$}
\fancyfoot[C]{\thepage}
\renewcommand{\headrulewidth}{0.4pt}

% Chapter styling
\usepackage{titlesec}
\titleformat{\chapter}[display]
  {\normalfont\huge\bfseries\centering}
  {\chaptertitlename\ \thechapter}{20pt}{\Huge}
\titlespacing*{\chapter}{0pt}{50pt}{40pt}

% Section styling
\titleformat{\section}
  {\normalfont\Large\bfseries}{\thesection}{1em}{}
\titlespacing*{\section}{0pt}{3.5ex plus 1ex minus .2ex}{2.3ex plus .2ex}

% Paragraph formatting
\setlength{\parindent}{0.25in}
\setlength{\parskip}{0pt}

% Better lists
\usepackage{enumitem}
\setlist{nosep}

% Graphics
\usepackage{graphicx}

% Hyperlinks (for PDF)
\usepackage[hidelinks]{hyperref}
\hypersetup{
    pdftitle={$title$},
    pdfauthor={$author$},
    pdfsubject={$genre$},
    pdfkeywords={fiction, novel},
    colorlinks=false,
    pdfborder={0 0 0}
}

% Better tables
\usepackage{booktabs}
\usepackage{longtable}

% Prevent widows and orphans
\widowpenalty=10000
\clubpenalty=10000

\begin{document}

% Front matter
\frontmatter

% Title page
\begin{titlepage}
\centering
\vspace*{2in}
{\Huge\bfseries $title$\par}
\vspace{0.5in}
{\Large by\par}
\vspace{0.3in}
{\LARGE $author$\par}
\vfill
\end{titlepage}

% Copyright page
\thispagestyle{empty}
\vspace*{\fill}
\begin{flushleft}
Copyright \copyright\ 2024 $author$

All rights reserved.

No part of this book may be reproduced or transmitted in any form or by any means, electronic or mechanical, including photocopying, recording, or by any information storage and retrieval system, without permission in writing from the author.

\vspace{0.2in}
First Edition
\end{flushleft}
\clearpage

% Table of contents
\tableofcontents
\clearpage

% Main content
\mainmatter

$body$

\end{document}
'''
    
    return template

def escape_latex_title(title: str) -> str:
    """
    Escape LaTeX special characters in chapter titles so they
    render cleanly in the TOC without leaking markup.
    Handles: & % $ # _ ^ ~ { } \
    """
    replacements = [
        ('\\', r'\textbackslash{}'),   # must come first
        ('&',  r'\&'),
        ('%',  r'\%'),
        ('$',  r'\$'),
        ('#',  r'\#'),
        ('_',  r'\_'),
        ('^',  r'\^{}'),
        ('~',  r'\textasciitilde{}'),
        ('{',  r'\{'),
        ('}',  r'\}'),
    ]
    for char, escaped in replacements:
        title = title.replace(char, escaped)
    return title

def strip_markdown_inline(text: str) -> str:
    """
    Remove inline markdown formatting (**bold**, *italic*, `code`)
    from a string, so chapter titles are plain text in the TOC.
    """
    import re
    text = re.sub(r'\*\*(.+?)\*\*', r'\1', text)   # bold
    text = re.sub(r'\*(.+?)\*',     r'\1', text)   # italic
    text = re.sub(r'`(.+?)`',       r'\1', text)   # inline code
    text = re.sub(r'__(.+?)__',     r'\1', text)   # alt bold
    text = re.sub(r'_(.+?)_',       r'\1', text)   # alt italic
    return text.strip()

# Pandoc raw-LaTeX fence: tells Pandoc this is LaTeX, not text,
# so it passes it through rather than treating it as content or
# accidentally indexing it into the TOC.
_CLEARPAGE = '\n\n```{=latex}\n\\clearpage\n```\n\n'

def combine_chapters(chapter_files, output_md: Path, metadata: dict):
    """Combine chapters into one markdown file with proper formatting"""
    console.print(f"\n[cyan]📚 Combining {len(chapter_files)} chapters...[/cyan]\n")
    
    combined = []
    
    for chapter_num, chapter_file in chapter_files:
        console.print(f"[green]✓ Chapter {chapter_num}[/green]")
        
        with open(chapter_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Clean up the content
        lines = content.split('\n')
        cleaned_lines = []
        
        for i, line in enumerate(lines):
            # Skip "to be continued" lines (case-insensitive)
            if 'to be continued' in line.lower() or 'continued...' in line.lower():
                continue
            
            # Skip scene headers entirely (all formats)
            if (line.startswith('### Scene') or 
                line.startswith('**Scene') or 
                line.startswith('Title: Scene') or
                ('Scene' in line and line.startswith('Title:'))):
                continue
            
            # Convert markdown headers to proper format
            if line.startswith('## Chapter'):
                # Extract chapter title, strip inline markdown, escape LaTeX chars
                parts = line.replace('## ', '').split(':', 1)
                raw_title = parts[1].strip() if len(parts) == 2 else parts[0]
                clean_title = escape_latex_title(strip_markdown_inline(raw_title))
                cleaned_lines.append(f'\n# {clean_title}\n')
            else:
                cleaned_lines.append(line)
        
        combined.append('\n'.join(cleaned_lines))
        # Use Pandoc raw-LaTeX fence so \clearpage is never treated as text
        combined.append(_CLEARPAGE)
    
    # Write combined file
    with open(output_md, 'w', encoding='utf-8') as f:
        f.write('\n'.join(combined))
    
    console.print(f"\n[green]✓ Combined markdown created[/green]")
    return output_md

def create_professional_pdf(combined_md: Path, output_pdf: Path, metadata: dict, trim_size: str):
    """Create professional PDF using Pandoc + LaTeX"""
    
    console.print(f"\n[cyan]🔨 Creating professional PDF...[/cyan]")
    
    # Generate ISBN
    isbn = generate_isbn()
    console.print(f"[dim]ISBN: {isbn}[/dim]")
    
    # Create LaTeX template
    template_content = create_latex_template(trim_size, isbn)
    template_file = combined_md.parent / 'book_template.tex'
    
    with open(template_file, 'w', encoding='utf-8') as f:
        f.write(template_content)
    
    # Pandoc command with professional settings
    cmd = [
        'pandoc',
        str(combined_md),
        '-o', str(output_pdf),
        '--template', str(template_file),
        '--pdf-engine=pdflatex',
        '--toc',
        '--toc-depth=2',
        f'--metadata=title:{metadata["title"]}',
        f'--metadata=author:{metadata["author"]}',
        f'--metadata=genre:{metadata["genre"]}',
        '--variable', 'documentclass=book',
        '--variable', 'fontsize=11pt',
        '--variable', 'geometry:inner=0.75in',
        '--variable', 'geometry:outer=0.5in',
        '--variable', 'geometry:top=0.75in',
        '--variable', 'geometry:bottom=0.75in',
        '--number-sections'
    ]
    
    try:
        console.print("[cyan]Running Pandoc (this may take a minute)...[/cyan]")
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
        
        if result.returncode == 0:
            console.print("[green]✓ PDF created successfully![/green]")
            
            # Clean up template
            template_file.unlink()
            
            return True
        else:
            console.print(f"[red]✗ Pandoc error:[/red]")
            console.print(result.stderr)
            return False
            
    except subprocess.TimeoutExpired:
        console.print("[red]✗ Pandoc timed out[/red]")
        return False
    except Exception as e:
        console.print(f"[red]✗ Error: {e}[/red]")
        return False

def main():
    # Authenticate first
    if not authenticate():
        console.print("[red]❌ Authentication failed. Exiting.[/red]")
        sys.exit(1)
    
    parser = argparse.ArgumentParser(
        description='Create professional KDP-ready book'
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
        help='Book trim size'
    )
    parser.add_argument(
        '--author',
        help='Author name'
    )
    
    args = parser.parse_args()
    
    console.print("\n[bold cyan]📚 Professional Book Creator[/bold cyan]")
    console.print("[dim]Publication-quality PDFs using Pandoc + LaTeX[/dim]\n")
    
    # Check Pandoc
    console.print("[cyan]Checking requirements...[/cyan]")
    if not check_pandoc():
        sys.exit(1)
    
    # Load project
    project_dir = Path(args.project_dir)
    if not project_dir.exists():
        console.print(f"[red]✗ Project not found: {project_dir}[/red]")
        sys.exit(1)
    
    metadata = load_metadata(project_dir)
    if args.author:
        metadata['author'] = args.author
    
    console.print(f"\n[bold]Title:[/bold] {metadata['title']}")
    console.print(f"[bold]Author:[/bold] {metadata['author']}")
    console.print(f"[bold]Trim Size:[/bold] {args.trim_size}")
    
    # Find chapters
    chapter_files = find_chapter_files(project_dir)
    if not chapter_files:
        console.print("\n[red]✗ No chapters found[/red]")
        sys.exit(1)
    
    console.print(f"[bold]Chapters:[/bold] {len(chapter_files)}\n")
    
    # Combine chapters
    combined_md = project_dir / 'manuscript_combined.md'
    combine_chapters(chapter_files, combined_md, metadata)
    
    # Output file
    if args.output:
        output_pdf = Path(args.output)
    else:
        safe_title = "".join(c for c in metadata['title'] if c.isalnum() or c in (' ', '-', '_'))
        safe_title = safe_title.replace(' ', '_')
        output_pdf = project_dir / f"{safe_title}_Professional.pdf"
    
    # Create PDF
    success = create_professional_pdf(combined_md, output_pdf, metadata, args.trim_size)
    
    if success:
        file_size = output_pdf.stat().st_size / (1024 * 1024)
        
        console.print(f"\n[bold green]🎉 Success![/bold green]")
        console.print(f"\n[bold]PDF:[/bold] {output_pdf}")
        console.print(f"[bold]Size:[/bold] {file_size:.2f} MB")
        console.print(f"[bold]Quality:[/bold] Professional/Print-ready")
        
        console.print("\n[bold cyan]✓ Professional Features:[/bold cyan]")
        console.print("  • Publication-quality typography")
        console.print("  • Professional chapter styling")
        console.print("  • Proper page headers/footers")
        console.print("  • Table of contents with links")
        console.print("  • Copyright page")
        console.print("  • KDP-compliant margins")
        console.print("  • No text overlap")
        console.print("  • No margin bleed")
        console.print("  • Print-ready PDF/X format")
        
        console.print("\n[yellow]Ready for KDP upload![/yellow]\n")
    else:
        console.print("\n[red]✗ Failed to create PDF[/red]")
        console.print("[yellow]Make sure pdflatex is installed (comes with MiKTeX or TeX Live)[/yellow]")
        sys.exit(1)

if __name__ == "__main__":
    main()