#!/usr/bin/env python3
"""
Generate rich end-to-end workflow diagram for benchmark deployment gates analysis.
Styled similar to draw.io with detailed boxes, connections, and annotations.
"""

from pathlib import Path

try:
    from PIL import Image, ImageDraw, ImageFont
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False
    print("Warning: PIL not available. Install with: pip install Pillow")

OUTPUT_DIR = Path(__file__).parent.parent / "papers" / "thinkai-2026" / "figures"

def draw_box(draw, x, y, w, h, fill, outline, text, font, text_color='white'):
    """Draw a rounded rectangle box with text."""
    radius = 10
    draw.rounded_rectangle([x, y, x+w, y+h], radius=radius, fill=fill, outline=outline, width=3)
    bbox = draw.textbbox((0, 0), text, font=font)
    text_w = bbox[2] - bbox[0]
    text_h = bbox[3] - bbox[1]
    draw.text((x + w//2 - text_w//2, y + h//2 - text_h//2), text, fill=text_color, font=font)

def draw_arrow(draw, x1, y1, x2, y2, color, width=3):
    """Draw an arrow from (x1,y1) to (x2,y2)."""
    draw.line([(x1, y1), (x2, y2)], fill=color, width=width)
    # Arrow head
    arrow_size = 12
    draw.polygon([(x2, y2), (x2-arrow_size//2, y2-arrow_size), (x2+arrow_size//2, y2-arrow_size)], fill=color)

def draw_side_box(draw, x, y, w, h, text, font, color):
    """Draw a side annotation box."""
    draw.rectangle([x, y, x+w, y+h], fill='#F8F9FA', outline=color, width=2)
    lines = text.split('\n')
    line_height = 18
    for i, line in enumerate(lines):
        draw.text((x+10, y+10+i*line_height), line, fill='#2C3E50', font=font)

def create_workflow_diagram():
    """Create rich workflow diagram showing the analysis pipeline."""
    
    if not PIL_AVAILABLE:
        print("Skipping workflow diagram - PIL not available")
        return
    
    # Image dimensions
    width = 1600
    height = 2000
    
    # Create image with light background
    img = Image.new('RGB', (width, height), color='#FAFBFC')
    draw = ImageDraw.Draw(img)
    
    # Colors - professional palette
    color_data = '#3498DB'      # Blue - data sources
    color_process = '#9B59B6'   # Purple - processing
    color_analysis = '#E74C3C'  # Red - analysis
    color_output = '#27AE60'    # Green - outputs
    color_arrow = '#34495E'     # Dark gray - arrows
    color_text = '#2C3E50'      # Text
    
    # Try to load fonts
    try:
        font_title = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 28)
        font_heading = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 20)
        font_text = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 16)
        font_small = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 13)
    except:
        font_title = ImageFont.load_default()
        font_heading = ImageFont.load_default()
        font_text = ImageFont.load_default()
        font_small = ImageFont.load_default()
    
    # Title
    title = "Benchmark Deployment Gates: End-to-End Analysis Pipeline"
    bbox = draw.textbbox((0, 0), title, font=font_title)
    title_w = bbox[2] - bbox[0]
    draw.text((width//2 - title_w//2, 30), title, fill=color_text, font=font_title)
    draw.text((width//2 - 200, 65), "Cross-Study Multi-Criteria Evaluation Framework", fill='#7F8C8D', font=font_text)
    
    y_offset = 120
    
    # ===== PHASE 1: IMMUTABLE DATA SOURCES =====
    draw.text((50, y_offset), "PHASE 1: Immutable Data Sources", fill=color_data, font=font_heading)
    y_offset += 40
    
    # Three study boxes side by side
    box_w = 380
    box_h = 140
    spacing = 50
    start_x = (width - 3*box_w - 2*spacing) // 2
    
    # RAER box
    draw_box(draw, start_x, y_offset, box_w, box_h, color_data, color_data, "", font_text)
    draw.text((start_x+20, y_offset+15), "RAER v2", fill='white', font=font_heading)
    draw.text((start_x+20, y_offset+50), "• 9 policies", fill='white', font=font_text)
    draw.text((start_x+20, y_offset+75), "• 72 design cases", fill='white', font=font_text)
    draw.text((start_x+20, y_offset+100), "• 8 criteria", fill='white', font=font_text)
    draw.rectangle([start_x+250, y_offset+50, start_x+360, y_offset+110], fill='#2980B9', outline='white', width=2)
    draw.text((start_x+260, y_offset+60), "Safe", fill='white', font=font_small)
    draw.text((start_x+260, y_offset+80), "Completion", fill='white', font=font_small)
    
    # OVAR box
    draw_box(draw, start_x+box_w+spacing, y_offset, box_w, box_h, color_data, color_data, "", font_text)
    draw.text((start_x+box_w+spacing+20, y_offset+15), "OVAR v1.0", fill='white', font=font_heading)
    draw.text((start_x+box_w+spacing+20, y_offset+50), "• 5 policies", fill='white', font=font_text)
    draw.text((start_x+box_w+spacing+20, y_offset+75), "• 48 calibration cases", fill='white', font=font_text)
    draw.text((start_x+box_w+spacing+20, y_offset+100), "• 9 criteria", fill='white', font=font_text)
    draw.rectangle([start_x+box_w+spacing+250, y_offset+50, start_x+box_w+spacing+360, y_offset+110], fill='#2980B9', outline='white', width=2)
    draw.text((start_x+box_w+spacing+260, y_offset+60), "ROI", fill='white', font=font_small)
    draw.text((start_x+box_w+spacing+260, y_offset+80), "Reduction", fill='white', font=font_small)
    
    # VDCM box
    draw_box(draw, start_x+2*(box_w+spacing), y_offset, box_w, box_h, color_data, color_data, "", font_text)
    draw.text((start_x+2*(box_w+spacing)+20, y_offset+15), "VDCM", fill='white', font=font_heading)
    draw.text((start_x+2*(box_w+spacing)+20, y_offset+50), "• 5 comparators", fill='white', font=font_text)
    draw.text((start_x+2*(box_w+spacing)+20, y_offset+75), "• 11 scenarios × 24 reps", fill='white', font=font_text)
    draw.text((start_x+2*(box_w+spacing)+20, y_offset+100), "• 2 criteria", fill='white', font=font_text)
    draw.rectangle([start_x+2*(box_w+spacing)+250, y_offset+50, start_x+2*(box_w+spacing)+360, y_offset+110], fill='#2980B9', outline='white', width=2)
    draw.text((start_x+2*(box_w+spacing)+260, y_offset+60), "Brier", fill='white', font=font_small)
    draw.text((start_x+2*(box_w+spacing)+260, y_offset+80), "Score", fill='white', font=font_small)
    
    y_offset += box_h + 30
    
    # Side annotation
    draw_side_box(draw, width-350, y_offset-140, 330, 110, 
                  "Total Dataset:\n• 19 methods\n• 165 evaluation instances\n• Prospective evaluation\n• Immutable & versioned", 
                  font_small, color_data)
    
    # Arrow down
    draw_arrow(draw, width//2, y_offset, width//2, y_offset+50, color_arrow)
    y_offset += 60
    
    # ===== PHASE 2: DATA EXTRACTION =====
    draw.text((50, y_offset), "PHASE 2: Data Extraction & Normalization", fill=color_process, font=font_heading)
    y_offset += 40
    
    # Extraction box
    box_w = 1200
    box_h = 180
    start_x = (width - box_w) // 2
    draw_box(draw, start_x, y_offset, box_w, box_h, color_process, color_process, "", font_text)
    
    # Three extraction scripts
    script_w = 350
    script_x = start_x + 50
    draw.rectangle([script_x, y_offset+20, script_x+script_w, y_offset+150], fill='#8E44AD', outline='white', width=2)
    draw.text((script_x+10, y_offset+30), "extract_raer_results.py", fill='white', font=font_text)
    draw.text((script_x+10, y_offset+60), "→ Single-metric rankings", fill='white', font=font_small)
    draw.text((script_x+10, y_offset+80), "→ Multi-criteria outcomes", fill='white', font=font_small)
    draw.text((script_x+10, y_offset+100), "→ Failed criteria list", fill='white', font=font_small)
    draw.text((script_x+10, y_offset+120), "→ Gate decisions", fill='white', font=font_small)
    
    script_x += script_w + 30
    draw.rectangle([script_x, y_offset+20, script_x+script_w, y_offset+150], fill='#8E44AD', outline='white', width=2)
    draw.text((script_x+10, y_offset+30), "extract_ovar_results.py", fill='white', font=font_text)
    draw.text((script_x+10, y_offset+60), "→ Policy summaries", fill='white', font=font_small)
    draw.text((script_x+10, y_offset+80), "→ Authorization checks", fill='white', font=font_small)
    draw.text((script_x+10, y_offset+100), "→ ROI metrics", fill='white', font=font_small)
    draw.text((script_x+10, y_offset+120), "→ Criteria passed/failed", fill='white', font=font_small)
    
    script_x += script_w + 30
    draw.rectangle([script_x, y_offset+20, script_x+script_w, y_offset+150], fill='#8E44AD', outline='white', width=2)
    draw.text((script_x+10, y_offset+30), "extract_vdcm_results.py", fill='white', font=font_text)
    draw.text((script_x+10, y_offset+60), "→ Scenario summaries", fill='white', font=font_small)
    draw.text((script_x+10, y_offset+80), "→ Brier scores", fill='white', font=font_small)
    draw.text((script_x+10, y_offset+100), "→ Scenario wins", fill='white', font=font_small)
    draw.text((script_x+10, y_offset+120), "→ Deployment criteria", fill='white', font=font_small)
    
    y_offset += box_h + 30
    
    # Side annotation
    draw_side_box(draw, width-350, y_offset-180, 330, 150, 
                  "Extraction Protocol:\n• Deterministic scripts\n• SHA-256 verification\n• No retrospective edits\n• Normalized schema\n• JSON output format\n• Version controlled", 
                  font_small, color_process)
    
    # Arrow down
    draw_arrow(draw, width//2, y_offset, width//2, y_offset+50, color_arrow)
    y_offset += 60
    
    # ===== PHASE 3: CROSS-STUDY ANALYSIS =====
    draw.text((50, y_offset), "PHASE 3: Cross-Study Analysis", fill=color_analysis, font=font_heading)
    y_offset += 40
    
    # Analysis boxes - two rows
    box_w = 550
    box_h = 120
    start_x = (width - 2*box_w - 100) // 2
    
    # Rank Reversal Analysis
    draw_box(draw, start_x, y_offset, box_w, box_h, color_analysis, color_analysis, "", font_text)
    draw.text((start_x+20, y_offset+15), "Rank Reversal Analysis", fill='white', font=font_heading)
    draw.text((start_x+20, y_offset+50), "• Compare single-metric vs multi-criteria ranks", fill='white', font=font_small)
    draw.text((start_x+20, y_offset+70), "• Detect reversals ≥2 positions", fill='white', font=font_small)
    draw.text((start_x+20, y_offset+90), "• Test H1: ≥20% reversal rate", fill='white', font=font_small)
    
    # Multi-Criteria Failure Detection
    draw_box(draw, start_x+box_w+100, y_offset, box_w, box_h, color_analysis, color_analysis, "", font_text)
    draw.text((start_x+box_w+120, y_offset+15), "Multi-Criteria Failure Detection", fill='white', font=font_heading)
    draw.text((start_x+box_w+120, y_offset+50), "• Identify single-metric success cases", fill='white', font=font_small)
    draw.text((start_x+box_w+120, y_offset+70), "• Check deployment criteria failures", fill='white', font=font_small)
    draw.text((start_x+box_w+120, y_offset+90), "• Test H2: ≥1 method with hidden failures", fill='white', font=font_small)
    
    y_offset += box_h + 30
    
    # Threshold Sensitivity
    draw_box(draw, start_x, y_offset, box_w, box_h, color_analysis, color_analysis, "", font_text)
    draw.text((start_x+20, y_offset+15), "Threshold Sensitivity Testing", fill='white', font=font_heading)
    draw.text((start_x+20, y_offset+50), "• Perturb thresholds ±10%, ±20%", fill='white', font=font_small)
    draw.text((start_x+20, y_offset+70), "• Track decision changes (pass ↔ fail)", fill='white', font=font_small)
    draw.text((start_x+20, y_offset+90), "• Test H3: ≥15% instability rate", fill='white', font=font_small)
    
    # Hypothesis Testing
    draw_box(draw, start_x+box_w+100, y_offset, box_w, box_h, color_analysis, color_analysis, "", font_text)
    draw.text((start_x+box_w+120, y_offset+15), "Hypothesis Testing", fill='white', font=font_heading)
    draw.text((start_x+box_w+120, y_offset+50), "• Pre-registered thresholds", fill='white', font=font_small)
    draw.text((start_x+box_w+120, y_offset+70), "• No post-hoc adjustments", fill='white', font=font_small)
    draw.text((start_x+box_w+120, y_offset+90), "• Transparent negative results", fill='white', font=font_small)
    
    y_offset += box_h + 30
    
    # Side annotation - Key Finding
    draw.rectangle([width-350, y_offset-270, width-20, y_offset-30], fill='#FFF3CD', outline='#F39C12', width=3)
    draw.text((width-340, y_offset-260), "🔒 CRITICAL FINDING", fill='#856404', font=font_heading)
    draw.text((width-340, y_offset-230), "Authorization Failures:", fill='#856404', font=font_text)
    draw.text((width-340, y_offset-205), "• 94.3% ROI reduction", fill='#856404', font=font_small)
    draw.text((width-340, y_offset-185), "• Failed authorization", fill='#856404', font=font_small)
    draw.text((width-340, y_offset-165), "• 100% replication", fill='#856404', font=font_small)
    draw.text((width-340, y_offset-145), "• Deployment blocker", fill='#856404', font=font_small)
    draw.text((width-340, y_offset-120), "Single metrics can mask", fill='#856404', font=font_small)
    draw.text((width-340, y_offset-100), "critical failures!", fill='#856404', font=font_small)
    
    # Arrow down
    draw_arrow(draw, width//2, y_offset, width//2, y_offset+50, color_arrow)
    y_offset += 60
    
    # ===== PHASE 4: OUTPUTS & DELIVERABLES =====
    draw.text((50, y_offset), "PHASE 4: Outputs & Deliverables", fill=color_output, font=font_heading)
    y_offset += 40
    
    # Output boxes
    box_w = 350
    box_h = 100
    spacing = 50
    start_x = (width - 3*box_w - 2*spacing) // 2
    
    # Figures
    draw_box(draw, start_x, y_offset, box_w, box_h, color_output, color_output, "", font_text)
    draw.text((start_x+20, y_offset+15), "📊 Visualizations", fill='white', font=font_heading)
    draw.text((start_x+20, y_offset+50), "• 4 figures (300 DPI)", fill='white', font=font_small)
    draw.text((start_x+20, y_offset+70), "• Heatmaps & charts", fill='white', font=font_small)
    
    # Analysis Results
    draw_box(draw, start_x+box_w+spacing, y_offset, box_w, box_h, color_output, color_output, "", font_text)
    draw.text((start_x+box_w+spacing+20, y_offset+15), "📈 Analysis Results", fill='white', font=font_heading)
    draw.text((start_x+box_w+spacing+20, y_offset+50), "• H1: FAIL (10.5%)", fill='white', font=font_small)
    draw.text((start_x+box_w+spacing+20, y_offset+70), "• H2: PASS (3 methods)", fill='white', font=font_small)
    
    # Checklist
    draw_box(draw, start_x+2*(box_w+spacing), y_offset, box_w, box_h, color_output, color_output, "", font_text)
    draw.text((start_x+2*(box_w+spacing)+20, y_offset+15), "✅ Checklist Artifact", fill='white', font=font_heading)
    draw.text((start_x+2*(box_w+spacing)+20, y_offset+50), "• NIST AI 800-2 aligned", fill='white', font=font_small)
    draw.text((start_x+2*(box_w+spacing)+20, y_offset+70), "• Community reusable", fill='white', font=font_small)
    
    y_offset += box_h + 30
    
    # Paper
    box_w = 1200
    box_h = 80
    start_x = (width - box_w) // 2
    draw_box(draw, start_x, y_offset, box_w, box_h, color_output, color_output, "", font_text)
    draw.text((start_x+20, y_offset+15), "📄 6-Page ThinkAI 2026 Paper", fill='white', font=font_heading)
    draw.text((start_x+20, y_offset+50), "Multi-Criteria Deployment Gates Reveal Hidden Failures in AI Evaluation: A Cross-Study Analysis", fill='white', font=font_text)
    
    y_offset += box_h + 40
    
    # Footer - Reproducibility
    draw.rectangle([100, y_offset, width-100, y_offset+80], fill='#ECF0F1', outline='#95A5A6', width=2)
    draw.text((width//2-200, y_offset+15), "🔄 Fully Reproducible Pipeline", fill=color_text, font=font_heading)
    draw.text((width//2-300, y_offset+45), "make extract → make analyze → make verify → python3 scripts/generate_visualizations.py", fill='#7F8C8D', font=font_text)
    
    # Save
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    output_file = OUTPUT_DIR / "workflow_diagram.png"
    img.save(output_file, dpi=(300, 300))
    print(f"Saved: {output_file}")

def main():
    """Generate workflow diagram."""
    print("Generating rich workflow diagram...")
    
    if not PIL_AVAILABLE:
        print("\nTo generate workflow diagram, install Pillow:")
        print("  python3 -m pip install Pillow")
        return
    
    create_workflow_diagram()
    print("\nRich workflow diagram generated successfully!")

if __name__ == "__main__":
    main()
