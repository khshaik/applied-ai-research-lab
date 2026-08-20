# Pre-Submission Checklist

**Paper**: Multi-Criteria Deployment Gates Reveal Hidden Failures in AI Evaluation  
**Venue**: ThinkAI 2026  
**Deadline**: 25 August 2026  
**Submission Type**: Initial Submission (Anonymous, Double-Blind)

---

## ✅ Content Completeness

### Abstract
- [ ] Word count: 150-200 words (currently: 195 words) ✅
- [ ] Problem statement included
- [ ] Method overview included
- [ ] Key findings included (H2 supported)
- [ ] Contribution stated (Minimum Responsible Benchmark Checklist)

### Introduction
- [ ] Problem motivation clear
- [ ] NIST AI 800-2 context provided
- [ ] Research question stated
- [ ] Contributions listed (3 items)
- [ ] Length: ~1 page ✅

### Background
- [ ] RAER v2 summarized
- [ ] OVAR v1.0 summarized
- [ ] VDCM summarized
- [ ] All three studies' negative results mentioned
- [ ] Length: ~0.5 pages ✅

### Method
- [ ] Data sources table included
- [ ] Extraction protocol described
- [ ] Analysis procedures explained
- [ ] Hypothesis testing framework defined
- [ ] Length: ~1 page ✅

### Results
- [ ] H1 results reported (10.5%, FAIL)
- [ ] H2 results reported (3 methods, PASS) ⭐
- [ ] H3 results reported (0%, FAIL)
- [ ] Authorization failure pattern detailed
- [ ] Cross-study patterns analyzed
- [ ] All figures cited in text
- [ ] All tables cited in text
- [ ] Length: ~2 pages ✅

### Discussion
- [ ] Implications for AI evaluation stated
- [ ] Context-dependent alignment discussed
- [ ] Limitations acknowledged (small sample, constructed cases, 3 studies)
- [ ] Future work outlined
- [ ] Length: ~1 page ✅

### Checklist Section
- [ ] Minimum Responsible Benchmark Report Checklist presented
- [ ] Key requirements highlighted
- [ ] Usage guidance provided
- [ ] NIST AI 800-2 alignment stated
- [ ] Length: ~0.5 pages ✅

### Conclusion
- [ ] Key findings summarized
- [ ] Authorization failure emphasized
- [ ] Checklist contribution stated
- [ ] Length: ~0.25 pages ✅

### References
- [ ] NIST AI 800-2 cited
- [ ] RAER, OVAR, VDCM papers cited
- [ ] Responsible AI frameworks cited
- [ ] All in-text citations have references
- [ ] Springer LNCS format ✅

---

## ✅ Figures and Tables

### Figures (3-4 required)
- [ ] Figure 1: Rank reversal heatmap (300 DPI) ✅
- [ ] Figure 2: Criteria failure patterns (300 DPI) ✅
- [ ] Figure 3: Workflow diagram (300 DPI) ✅
- [ ] Optional: Threshold sensitivity (300 DPI) ✅
- [ ] All figures embedded in document
- [ ] All figures have captions
- [ ] All figures cited in text

### Tables (2 required)
- [ ] Table 1: Data sources (Study, Methods, Cases, Criteria) ✅
- [ ] Table 2: Hypothesis outcomes (H1, H2, H3 results) ✅
- [ ] All tables have captions
- [ ] All tables cited in text

---

## ✅ Formatting

### Springer LNCS Format
- [ ] Template downloaded from Springer website
- [ ] Page limit: ≤6 pages (excluding references) ✅
- [ ] Font: Times New Roman or similar
- [ ] Font size: 10pt body, 12pt headings
- [ ] Line spacing: Single
- [ ] Margins: Per LNCS template
- [ ] Section numbering: 1, 2, 3, etc.
- [ ] Subsection numbering: 1.1, 1.2, etc.

### References
- [ ] Springer LNCS citation style
- [ ] Numbered citations [1], [2], etc.
- [ ] All URLs accessible
- [ ] DOIs included where available

---

## ✅ Anonymization (CRITICAL)

### Author Information
- [ ] **NO author names** in PDF ✅
- [ ] **NO affiliations** in PDF ✅
- [ ] **NO acknowledgments** in PDF ✅
- [ ] **NO funding statements** in PDF ✅
- [ ] **NO email addresses** in PDF ✅

### Self-Citations
- [ ] Self-citations rephrased (e.g., "Prior work [3]" not "Our prior work [3]")
- [ ] Repository URLs removed
- [ ] GitHub links removed
- [ ] Personal website links removed

### PDF Metadata
- [ ] Author field: BLANK or "Anonymous"
- [ ] Title field: Paper title only
- [ ] Subject field: BLANK
- [ ] Keywords field: Research keywords only
- [ ] Creator/Producer: PDF software name only

### File Properties Check
```bash
# Verify PDF metadata is clean
exiftool BenchmarkDeploymentGates_ThinkAI2026_ANONYMOUS_v1.0.pdf
# Should show NO author information
```

---

## ✅ Quality Assurance

### Language and Grammar
- [ ] Spell-check completed (US English)
- [ ] Grammar check completed
- [ ] No typos in abstract
- [ ] No typos in introduction
- [ ] No typos in section headings
- [ ] Consistent terminology throughout

### Technical Accuracy
- [ ] All numbers verified against analysis results
- [ ] H1: 10.5% (2/19 methods) ✅
- [ ] H2: 3 methods identified ✅
- [ ] H3: 0.0% (0/19 methods) ✅
- [ ] Authorization failure: 94.3% ROI reduction ✅
- [ ] VDCM reversals: 40% (2/5 methods) ✅

### Consistency
- [ ] Hypothesis numbering consistent (H1, H2, H3)
- [ ] Study names consistent (RAER v2, OVAR v1.0, VDCM)
- [ ] Metric names consistent
- [ ] Terminology consistent (single-metric vs. multi-criteria)

### Visual Quality
- [ ] All figures clear and readable
- [ ] Figure resolution: 300 DPI minimum
- [ ] Figure labels legible
- [ ] Table formatting consistent
- [ ] No pixelated images

---

## ✅ File Preparation

### File Naming
- [ ] Filename: `BenchmarkDeploymentGates_ThinkAI2026_ANONYMOUS_v1.0.pdf`
- [ ] No spaces in filename
- [ ] Version number included
- [ ] ANONYMOUS clearly indicated

### File Size
- [ ] PDF size: <10 MB ✅
- [ ] If >10 MB, compress images
- [ ] Verify file opens correctly

### File Format
- [ ] PDF/A format (archival)
- [ ] Fonts embedded
- [ ] Images embedded (not linked)
- [ ] No external dependencies

---

## ✅ Submission Portal

### Portal Access
- [ ] Portal URL verified: https://thinkai2026.klh.edu.in/
- [ ] Account created (if required)
- [ ] Login credentials saved
- [ ] Submission deadline confirmed: 25 August 2026

### Submission Fields
- [ ] Paper title entered correctly
- [ ] Abstract pasted (plain text, no formatting)
- [ ] Keywords entered (4-6 keywords)
- [ ] Track selected: Research Track / Data Science & Analytics
- [ ] Conflicts of interest declared (if any)

### File Upload
- [ ] Anonymous PDF uploaded
- [ ] File size verified (<10 MB)
- [ ] Upload confirmation received
- [ ] Download uploaded file to verify

---

## ✅ Final Verification

### Pre-Upload Checklist
- [ ] Open PDF and visually inspect every page
- [ ] Verify NO author information anywhere
- [ ] Check all figures display correctly
- [ ] Check all tables display correctly
- [ ] Verify page count ≤6 pages (excluding references)
- [ ] Check references section complete

### Post-Upload Checklist
- [ ] Save submission confirmation email
- [ ] Note paper ID from portal
- [ ] Download submitted PDF from portal
- [ ] Verify downloaded PDF matches uploaded PDF
- [ ] Keep repository PRIVATE during review

---

## ✅ Backup and Archive

### Local Backup
- [ ] Anonymous PDF saved in multiple locations
- [ ] Source DOCX/LaTeX saved
- [ ] Figures saved separately (high-res)
- [ ] Submission confirmation email saved

### Repository Status
- [ ] Repository remains PRIVATE ✅
- [ ] No public links shared
- [ ] No social media posts
- [ ] No arXiv preprint (wait for acceptance)

---

## 🚨 Common Mistakes to Avoid

❌ **DO NOT**:
- Include author names anywhere
- Include affiliations
- Include acknowledgments
- Include funding statements
- Reference your own repository
- Post to arXiv before acceptance
- Share on social media
- Upload camera-ready file (that's for post-acceptance)

✅ **DO**:
- Keep repository private
- Share only anonymous PDF through official portal
- Monitor email for review feedback
- Prepare response to reviews (if needed)

---

## 📅 Timeline

**Target Submission**: 23-24 August 2026 (1-2 days before deadline)  
**Deadline**: 25 August 2026  
**Expected Notification**: 26 November 2026  
**Camera-Ready (if accepted)**: 01 December 2026

---

## ✅ Sign-Off

- [ ] All checklist items completed
- [ ] PDF anonymized and verified
- [ ] File size <10 MB
- [ ] Ready for submission

**Prepared by**: [Your Name]  
**Date**: [Date]  
**Status**: READY / NOT READY

---

**IMPORTANT**: This is for ANONYMOUS submission only. Do NOT upload camera-ready files during double-blind review.
