# Manuscript Lifecycle Management

This directory manages the double-blind review and camera-ready submission lifecycle.

---

## Directory Structure

```
manuscript/
├── initial-submission/          # Anonymous files for double-blind review
│   ├── ANONYMOUS_v1.0.pdf      # Submission PDF (no author info)
│   ├── figures/                # Embedded figures
│   └── checklist_artifact.pdf  # Supplementary material (if permitted)
│
└── camera-ready-submission/     # Identified files for post-acceptance
    ├── CAMERA_READY_v1.0.docx  # Editable source with author info
    ├── CAMERA_READY_v1.0.pdf   # Final PDF matching DOCX
    ├── copyright_form.pdf      # Springer copyright
    └── declarations/           # Author declarations
```

---

## Do-Not-Mix Rule

⚠️ **CRITICAL**: These two directories serve different stages and must never be confused.

### Initial Submission (Anonymous)
**When**: Before acceptance decision  
**Purpose**: Double-blind peer review  
**Requirements**:
- ❌ No author names
- ❌ No affiliations
- ❌ No acknowledgments
- ❌ No self-identifying references
- ✅ Anonymous PDF only

**Upload**: Only through official submission portal

---

### Camera-Ready Submission (Identified)
**When**: After acceptance notification  
**Purpose**: Final publication  
**Requirements**:
- ✅ Full author names and affiliations
- ✅ Acknowledgments
- ✅ Funding information
- ✅ AI assistance disclosure
- ✅ Copyright form

**Upload**: Only after acceptance email received

---

## Workflow

### Stage 1: Initial Submission (Now - 25 August 2026)
1. Generate anonymous PDF from paper draft
2. Remove all identifying information
3. Embed figures at 300 DPI
4. Verify page limit (≤6 pages)
5. Submit through portal
6. **Do not touch camera-ready directory**

### Stage 2: Under Review (26 Aug - 26 Nov 2026)
1. Keep repository private
2. Do not post to arXiv
3. Do not share on social media
4. Monitor email for review feedback
5. **Do not modify submitted files**

### Stage 3: Camera-Ready (If Accepted, 27 Nov - 01 Dec 2026)
1. Add author information to DOCX
2. Address reviewer feedback
3. Generate final PDF
4. Complete copyright form
5. Submit camera-ready package
6. **Now safe to reference repository**

---

## File Naming Convention

### Initial Submission
`BenchmarkDeploymentGates_ThinkAI2026_ANONYMOUS_v1.0.pdf`

### Camera-Ready
`BenchmarkDeploymentGates_ThinkAI2026_CAMERA_READY_v1.0.pdf`  
`BenchmarkDeploymentGates_ThinkAI2026_CAMERA_READY_v1.0.docx`

---

## Anonymization Checklist

Before uploading initial submission:

- [ ] Author names removed from PDF
- [ ] Affiliations removed
- [ ] Acknowledgments removed
- [ ] Funding statements removed
- [ ] Self-citations rephrased (e.g., "Prior work [X]" not "Our prior work [X]")
- [ ] Repository URLs removed
- [ ] Email addresses removed
- [ ] PDF metadata cleaned (no author in properties)

---

## Camera-Ready Checklist

After acceptance notification:

- [ ] Author names and affiliations added
- [ ] Acknowledgments added
- [ ] Funding information added
- [ ] AI assistance disclosure added
- [ ] Reviewer feedback addressed
- [ ] Copyright form completed
- [ ] Final PDF matches DOCX exactly
- [ ] Page limit verified (≤6 pages)
- [ ] Figures at 300 DPI
- [ ] References complete

---

## Confidentiality

**During Review**:
- Keep repository **private**
- Share only anonymous PDF through official portal
- Do not discuss on social media
- Do not post preprint

**After Acceptance**:
- May post to arXiv
- May share on social media
- May make repository public
- May present at conference

---

## Version Control

| Version | Date | Stage | Status |
|---------|------|-------|--------|
| v1.0 | 2026-08-24 | Initial submission | Pending |
| v1.1 | TBD | Revision (if requested) | - |
| v2.0 | TBD | Camera-ready | - |

---

## Emergency Contacts

**If submission issues arise**:
- Conference email: thinkai@klh.edu.in
- Check submission portal FAQ
- Contact technical support

**If acceptance questions arise**:
- Wait for official acceptance email
- Do not assume acceptance from informal communication
- Verify camera-ready deadline in acceptance letter
