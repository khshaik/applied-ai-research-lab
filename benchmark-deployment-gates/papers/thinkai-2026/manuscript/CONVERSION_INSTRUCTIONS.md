# Manuscript Conversion Instructions

**Purpose**: Convert `DRAFT_MANUSCRIPT.md` to Springer LNCS format (DOCX and PDF)

---

## Option 1: Using Pandoc (Recommended)

### Prerequisites
```bash
# Install Pandoc
brew install pandoc  # macOS
# or
sudo apt-get install pandoc  # Linux

# Install LaTeX (for PDF generation)
brew install --cask mactex  # macOS
# or
sudo apt-get install texlive-full  # Linux
```

### Step 1: Download Springer LNCS Template
1. Visit: https://www.springer.com/gp/computer-science/lncs/conference-proceedings-guidelines
2. Download: "LaTeX2e Proceedings Templates (zip)"
3. Extract to: `papers/thinkai-2026/manuscript/templates/springer-lncs/`

### Step 2: Convert Markdown to LaTeX
```bash
cd papers/thinkai-2026/manuscript

# Convert to LaTeX using Springer template
pandoc DRAFT_MANUSCRIPT.md \
  -o initial-submission/BenchmarkDeploymentGates_ThinkAI2026_ANONYMOUS_v1.0.tex \
  --template=templates/springer-lncs/llncs.cls \
  --bibliography=references.bib \
  --citeproc
```

### Step 3: Manually Adjust LaTeX
Open the `.tex` file and:
- [ ] Remove author names (for anonymous submission)
- [ ] Remove affiliations
- [ ] Embed figures using `\includegraphics`
- [ ] Format tables using `\begin{table}`
- [ ] Verify section numbering

### Step 4: Generate PDF from LaTeX
```bash
cd initial-submission

# Compile LaTeX to PDF
pdflatex BenchmarkDeploymentGates_ThinkAI2026_ANONYMOUS_v1.0.tex
bibtex BenchmarkDeploymentGates_ThinkAI2026_ANONYMOUS_v1.0
pdflatex BenchmarkDeploymentGates_ThinkAI2026_ANONYMOUS_v1.0.tex
pdflatex BenchmarkDeploymentGates_ThinkAI2026_ANONYMOUS_v1.0.tex
```

### Step 5: Clean PDF Metadata
```bash
# Install exiftool
brew install exiftool  # macOS

# Remove author metadata
exiftool -Author="" \
  -Creator="" \
  -Producer="LaTeX" \
  BenchmarkDeploymentGates_ThinkAI2026_ANONYMOUS_v1.0.pdf
```

---

## Option 2: Using Microsoft Word (Manual)

### Step 1: Download Springer LNCS Word Template
1. Visit: https://www.springer.com/gp/computer-science/lncs/conference-proceedings-guidelines
2. Download: "MS Word 2007, 2010, 2013, 2016 Template (zip)"
3. Extract: `splnproc1703.dotx`

### Step 2: Create New Document from Template
1. Open Microsoft Word
2. File → New from Template
3. Select `splnproc1703.dotx`
4. Save as: `BenchmarkDeploymentGates_ThinkAI2026_ANONYMOUS_v1.0.docx`

### Step 3: Copy Content from DRAFT_MANUSCRIPT.md
1. Open `DRAFT_MANUSCRIPT.md` in text editor
2. Copy section by section into Word document
3. Apply Springer LNCS styles:
   - **Title**: Use "Title" style
   - **Headings**: Use "Heading 1", "Heading 2" styles
   - **Body**: Use "Normal" style
   - **Abstract**: Use "Abstract" style

### Step 4: Insert Figures
```
Insert → Pictures → From File
Select: papers/thinkai-2026/figures/rank_reversal_heatmap.png
Caption: "Figure 1. Rank reversals across studies..."
```

Repeat for all 3-4 figures.

### Step 5: Insert Tables
Create tables manually:
- Table 1: Data Sources (4 columns × 4 rows)
- Table 2: Hypothesis Outcomes (4 columns × 4 rows)

### Step 6: Format References
Use Springer LNCS reference style:
```
[1] Author, A., Author, B.: Title. Journal Name, Volume(Issue), Pages (Year)
```

### Step 7: Remove Author Information (Anonymous)
- Delete author names
- Delete affiliations
- Delete email addresses
- Delete acknowledgments

### Step 8: Generate PDF from Word
1. File → Save As → PDF
2. Options → PDF/A compliant
3. Save as: `BenchmarkDeploymentGates_ThinkAI2026_ANONYMOUS_v1.0.pdf`

### Step 9: Clean PDF Metadata
1. File → Properties (in Adobe Acrobat or Preview)
2. Remove author name
3. Remove company/organization
4. Keep title only

---

## Option 3: Using Overleaf (Online LaTeX)

### Step 1: Create Overleaf Account
1. Visit: https://www.overleaf.com
2. Sign up for free account

### Step 2: Create New Project
1. New Project → Upload Project
2. Upload Springer LNCS template (zip file)
3. Project name: "Benchmark Deployment Gates - ThinkAI 2026"

### Step 3: Copy Content
1. Open `main.tex` in Overleaf
2. Copy content from `DRAFT_MANUSCRIPT.md`
3. Convert markdown to LaTeX syntax

### Step 4: Upload Figures
1. Upload → Select files
2. Upload all 4 figures from `papers/thinkai-2026/figures/`

### Step 5: Compile
1. Click "Recompile" button
2. Verify PDF output
3. Fix any errors

### Step 6: Download PDF
1. Download → PDF
2. Save as: `BenchmarkDeploymentGates_ThinkAI2026_ANONYMOUS_v1.0.pdf`

### Step 7: Clean Metadata
Use exiftool (see Option 1, Step 5)

---

## Verification Checklist

After generating PDF, verify:

### Content
- [ ] Abstract present (150-200 words)
- [ ] All sections present (Introduction through Conclusion)
- [ ] All figures embedded and visible
- [ ] All tables formatted correctly
- [ ] All references listed

### Formatting
- [ ] Page limit: ≤6 pages (excluding references)
- [ ] Font: Times New Roman or similar
- [ ] Font size: 10pt body
- [ ] Margins: Per Springer LNCS
- [ ] Section numbering: 1, 2, 3, etc.

### Anonymization (Initial Submission)
- [ ] NO author names
- [ ] NO affiliations
- [ ] NO acknowledgments
- [ ] NO funding statements
- [ ] PDF metadata clean

### Quality
- [ ] Figures clear at 100% zoom
- [ ] Tables readable
- [ ] No typos in abstract
- [ ] No broken references
- [ ] File size <10 MB

---

## Quick Commands Reference

### Pandoc Conversion
```bash
# Markdown → LaTeX
pandoc DRAFT_MANUSCRIPT.md -o output.tex --template=springer-lncs

# Markdown → DOCX
pandoc DRAFT_MANUSCRIPT.md -o output.docx --reference-doc=springer-template.docx

# Markdown → PDF (direct)
pandoc DRAFT_MANUSCRIPT.md -o output.pdf --pdf-engine=xelatex
```

### LaTeX Compilation
```bash
# Compile LaTeX
pdflatex manuscript.tex
bibtex manuscript
pdflatex manuscript.tex
pdflatex manuscript.tex
```

### Metadata Cleaning
```bash
# View metadata
exiftool manuscript.pdf

# Remove author
exiftool -Author="" manuscript.pdf

# Remove all metadata except title
exiftool -all= -Title="Paper Title" manuscript.pdf
```

---

## Troubleshooting

### Issue: PDF too large (>10 MB)
**Solution**: Compress images
```bash
# Using ImageMagick
convert input.png -quality 85 -resize 2000x output.png

# Using Python
python3 scripts/compress_images.py
```

### Issue: Fonts not embedded
**Solution**: Use PDF/A format
```
In Word: File → Save As → PDF → Options → PDF/A compliant
In LaTeX: Add \usepackage{pdf14} to preamble
```

### Issue: Figures not displaying
**Solution**: Check file paths
```latex
% Use relative paths
\includegraphics[width=0.8\textwidth]{../figures/rank_reversal_heatmap.png}
```

### Issue: References not formatting correctly
**Solution**: Use BibTeX
```latex
\bibliographystyle{splncs04}
\bibliography{references}
```

---

## Final Steps

### For Initial Submission (Anonymous)
1. Generate PDF using one of the options above
2. Verify anonymization
3. Clean metadata
4. Save as: `initial-submission/BenchmarkDeploymentGates_ThinkAI2026_ANONYMOUS_v1.0.pdf`
5. Complete `PRE_SUBMISSION_CHECKLIST.md`
6. Complete `QA_RECORD.md`
7. Submit through ThinkAI 2026 portal

### For Camera-Ready (After Acceptance)
1. Add author information
2. Add acknowledgments
3. Add declarations
4. Address reviewer feedback
5. Generate DOCX and PDF
6. Save as: `camera-ready-submission/BenchmarkDeploymentGates_ThinkAI2026_CAMERA_READY_v1.0.*`
7. Complete `CAMERA_READY_CHECKLIST.md`
8. Submit through camera-ready portal

---

## Resources

**Springer LNCS Guidelines**: https://www.springer.com/gp/computer-science/lncs/conference-proceedings-guidelines

**Pandoc Manual**: https://pandoc.org/MANUAL.html

**Overleaf Documentation**: https://www.overleaf.com/learn

**LaTeX Wikibook**: https://en.wikibooks.org/wiki/LaTeX

---

**Recommended Approach**: Option 2 (Microsoft Word) for easiest manual control, or Option 3 (Overleaf) for collaborative editing.
