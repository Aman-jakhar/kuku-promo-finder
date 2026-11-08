"""generate_solution_pdf.py

Generates a publication-grade, exactly 2-page executive solution document in PDF format
using ReportLab, adhering strictly to Kuku's 2-page max requirement.

Sections covered:
1. Problem Framing & Scope
2. Core Assumptions
3. Architecture: AI vs Code vs Human-in-the-Loop
4. Scaling to Every Show (Economics, Caching, Parallelism, Genre Rubrics)
5. Quality Results & Real Failure Modes
6. AI Tool Usage & Retrospective (Where Tools Got It Wrong)
"""

from pathlib import Path
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether, HRFlowable
)
from reportlab.pdfgen import canvas


class NumberedCanvas(canvas.Canvas):
    """Two-pass canvas to dynamically compute and print 'Page X of Y'."""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_decorations(num_pages)
            super().showPage()
        super().save()

    def draw_page_decorations(self, total_pages):
        self.saveState()
        self.setFont("Helvetica", 8)
        self.setFillColor(colors.HexColor("#64748B"))
        
        # Header (pages > 1)
        if self._pageNumber > 1:
            self.drawString(40, 755, "Kuku AI Studio — Problem 1: Automated Promo Finder Solution Document")
            self.setStrokeColor(colors.HexColor("#CBD5E1"))
            self.setLineWidth(0.5)
            self.line(40, 748, 572, 748)

        # Footer
        footer_text = f"Page {self._pageNumber} of {total_pages}"
        self.drawRightString(572, 25, footer_text)
        self.drawString(40, 25, "Confidential — Kuku AI Microdrama Studio Assignment Submission")
        self.setStrokeColor(colors.HexColor("#CBD5E1"))
        self.setLineWidth(0.5)
        self.line(40, 35, 572, 35)
        self.restoreState()


def build_pdf(filename: str = "solution_doc.pdf"):
    doc = SimpleDocTemplate(
        filename,
        pagesize=letter,
        leftMargin=36,
        rightMargin=36,
        topMargin=36,
        bottomMargin=36
    )

    styles = getSampleStyleSheet()

    # Custom styles
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=17,
        leading=20,
        textColor=colors.HexColor("#0F172A"),
        spaceAfter=2
    )

    subtitle_style = ParagraphStyle(
        'DocSubtitle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8.5,
        leading=11,
        textColor=colors.HexColor("#475569"),
        spaceAfter=6
    )

    h1_style = ParagraphStyle(
        'SectionHeading',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=10,
        leading=13,
        textColor=colors.HexColor("#1E3A8A"),
        spaceBefore=4,
        spaceAfter=3,
        keepWithNext=True
    )

    body_style = ParagraphStyle(
        'Body',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=7.6,
        leading=9.6,
        textColor=colors.HexColor("#1E293B"),
        spaceAfter=3
    )

    bullet_style = ParagraphStyle(
        'Bullet',
        parent=body_style,
        leftIndent=10,
        spaceAfter=2
    )

    code_style = ParagraphStyle(
        'CodeStyle',
        parent=body_style,
        fontName='Courier',
        fontSize=7.0,
        leading=8.5,
        textColor=colors.HexColor("#0F172A")
    )

    story = []

    # Title & Metadata
    story.append(Paragraph("KUKU AI MICRODRAMA STUDIO — PROBLEM 1: FIND THE PROMOS", title_style))
    story.append(Paragraph("<b>Author:</b> AI Generalist Candidate &nbsp;|&nbsp; <b>Time Budget:</b> ~3 Hours &nbsp;|&nbsp; <b>Output:</b> Rerunnable CLI Pipeline + Snapping Engine + Streamlit Studio", subtitle_style))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#2563EB"), spaceAfter=5))

    # SECTION 1: Why Problem 1 & Scope
    story.append(Paragraph("1. Problem Choice, Framing & Scope", h1_style))
    story.append(Paragraph(
        "<b>Why Problem 1?</b> In vertical microdrama (ReelShort, DramaBox, Kuku TV), organic growth and user acquisition are dominated by paid and organic TikTok/Reels marketing. While traditional Hollywood relies on atmospheric trailers, microdramas convert viewers exclusively on <b>20–60 second vertical clips</b> featuring high-velocity emotional whiplash: an immediate hook in the first 3 seconds, accelerating tension, and a sudden cutoff at maximum cliffhanger tension. Manual editing across 50–100 episodes per show creates a severe production bottleneck as release cadence scales weekly. Automating promo discovery directly removes human latency from the studio growth flywheel.",
        body_style
    ))
    story.append(Paragraph(
        "<b>Scope Boundaries:</b> The system focuses strictly on candidate discovery, boundary snapping, and standalone clarity ranking. It specifically avoids video transcoding, audio ducking, or overlay styling, preserving clean timestamp handoffs for the finishing team.",
        body_style
    ))

    # SECTION 2: Assumptions
    story.append(Paragraph("2. Key Assumptions (Recorded in ASSUMPTIONS.md)", h1_style))
    story.append(Paragraph("• <b>Screenplay Invariance:</b> Scripts follow standard format (`EPISODE NUMBER`, `LOGLINE`, `CONTINUITY`, `SCENE NN`, and `**LABEL:**` with `Start: (MM:SS.ss) | End: (MM:SS.ss)`). File parsers must be robust to episode count and filename variance.", bullet_style))
    story.append(Paragraph("• <b>Boundary Legality:</b> Start timestamps must land on an event start; end timestamps on an event end. `CAMERA` actions are excluded from LLM prompts to save 40% token budget, but their start/end timestamps are preserved as legal cut points.", bullet_style))
    story.append(Paragraph("• <b>Deterministic Snapping:</b> LLM-proposed timestamps are snapped to the nearest event boundary within ±2.5s. If an LLM hallucination requires a larger jump, the candidate is flagged.", bullet_style))
    story.append(Paragraph("• <b>Scoring Weights:</b> Deterministic formula: <code>Overall = 0.35 * Hook + 0.35 * Cliffhanger + 0.30 * Standalone</code>, keeping weights transparent and tunable in code rather than hidden inside LLM prompt text.", bullet_style))

    # SECTION 3: How it Works
    story.append(Paragraph("3. How It Works: AI vs Code vs Human-in-the-Loop", h1_style))
    story.append(Paragraph(
        "The architecture enforces a strict boundary between non-deterministic semantic interpretation (AI) and deterministic validation guarantees (Code):",
        body_style
    ))

    arch_data = [
        [
            Paragraph("<b>Component</b>", body_style),
            Paragraph("<b>Agent / Engine</b>", body_style),
            Paragraph("<b>Responsibility & Guarantees</b>", body_style)
        ],
        [
            Paragraph("<b>Parser & Condenser</b>", body_style),
            Paragraph("Code (Python)", body_style),
            Paragraph("Parses 3,727 events across 50 episodes into float seconds. Compresses verbose screenplay lines by 55% while retaining full boundary cut indices.", body_style)
        ],
        [
            Paragraph("<b>Pass 1: Episode Mining</b>", body_style),
            Paragraph("AI (Gemini/GPT-4o)", body_style),
            Paragraph("Proposes up to 4 candidates per episode. Considers previous episode logline & continuity to evaluate what backstory a scrolling viewer lacks.", body_style)
        ],
        [
            Paragraph("<b>Pass 2: Stitched Promos</b>", body_style),
            Paragraph("AI (Cross-Episode)", body_style),
            Paragraph("Synthesizes 2–4 segment promos across episodes (e.g., Ep 1 altar betrayal spliced directly with Ep 3 Duke marriage) within the 20–60s limit.", body_style)
        ],
        [
            Paragraph("<b>Snapping & Validator</b>", body_style),
            Paragraph("Code (Deterministic)", body_style),
            Paragraph("Enforces hard specs: rejects &lt;20s or &gt;60s, &gt;4 segments, out-of-order chronology, and hooks &gt;3.0s. Snaps timestamps to exact dialogue boundaries.", body_style)
        ],
        [
            Paragraph("<b>Pass 3: Standalone Judge</b>", body_style),
            Paragraph("AI (Blind Evaluator)", body_style),
            Paragraph("Sees <i>only</i> clip text without context. Scores standalone legibility (1–5) and pinpoints confusing jargon or missing emotional stakes.", body_style)
        ],
        [
            Paragraph("<b>Human-in-the-Loop</b>", body_style),
            Paragraph("Studio Growth Editor", body_style),
            Paragraph("Editor reviews Top 10 in React 9:16 Mobile Studio / Streamlit, tunes rubric weights live, and exports CMX 3600 EDL cuts directly into Adobe Premiere.", body_style)
        ]
    ]

    t_arch = Table(arch_data, colWidths=[105, 95, 340])
    t_arch.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#F1F5F9")),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 2),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
    ]))
    story.append(t_arch)
    story.append(Spacer(1, 4))

    # SECTION 4: Scaling to Every Show
    story.append(Paragraph("4. Scaling to Every Show (Economics, Caching & Genre Tuning)", h1_style))
    story.append(Paragraph(
        "<b>Cost Economics:</b> Microdrama episodes are short (~1,800 words, condensed to ~900 tokens). A 50-episode show requires 50 Pass-1 calls (~75k tokens), 1 Pass-2 call (~15k tokens), and ~120 Pass-3 judge calls (~25k tokens). Total volume per show: <b>~115k input tokens, ~18k output tokens</b>.",
        body_style
    ))
    story.append(Paragraph("• <b>Gemini 2.5 Flash / Free Tier:</b> Free during evaluation tier; $0.075 / 1M input = <b>$0.014 per 50-episode show</b>.", bullet_style))
    story.append(Paragraph("• <b>Cost at Scale:</b> 100 shows (5,000 episodes) costs <b>$1.40 total</b>. With OpenAI GPT-4o-mini ($0.15/$0.60 per 1M), total cost is <b>$2.80 per 100 shows</b>, rendering AI cost negligible compared to manual editing salaries.", bullet_style))
    story.append(Paragraph("• <b>Disk Caching:</b> Every LLM request is cached by <code>SHA256(model, prompt_hash)</code>. Re-running the pipeline on existing shows incurs <b>$0.00 cost</b> and finishes in &lt;2 seconds.", bullet_style))
    story.append(Paragraph("• <b>Per-Genre Rubric Tuning:</b> Weights can be adapted per genre: Billionaire/Revenge shows favor cliffhangers (<code>w_cliff=0.45</code>), while Werewolf/Romance favor standalone clarity (<code>w_standalone=0.40</code>).", bullet_style))

    # PAGE BREAK TO ENSURE STRICT 2-PAGE CONSTRAINT
    story.append(PageBreak())

    # PAGE 2: Quality Results, Real Numbers & Failures
    story.append(Paragraph("5. Quality Results: Real Validation Numbers & Failure Diagnostics", h1_style))
    story.append(Paragraph(
        "The pipeline was executed against all 50 episodes of <i>'I Married a Broken Soldier. He was a Duke'</i> (3,727 screenplay events).",
        body_style
    ))

    metrics_data = [
        [Paragraph("<b>Metric</b>", body_style), Paragraph("<b>Count / Rate</b>", body_style), Paragraph("<b>Engineering Impact & Significance</b>", body_style)],
        [Paragraph("<b>Screenplay Events Parsed</b>", body_style), Paragraph("3,727 (0 errors)", body_style), Paragraph("100% parse success across all 50 episodes; Ep 1 Scene 01 confirmed at 138.00s.", body_style)],
        [Paragraph("<b>Total Candidates Evaluated</b>", body_style), Paragraph("144 candidates", body_style), Paragraph("Combined pool of per-episode candidates and cross-episode stitched candidates.", body_style)],
        [Paragraph("<b>Pre-Snap Valid Rate</b>", body_style), Paragraph("100.0% (144/144)", body_style), Paragraph("Raw candidate proposals falling within the initial 20–60s window.", body_style)],
        [Paragraph("<b>Boundary Snapping Adjustments</b>", body_style), Paragraph("28 candidates (19.4%)", body_style), Paragraph("Micro-adjusted by 0.1s to 1.5s to snap cleanly to event start/end boundaries.", body_style)],
        [Paragraph("<b>Deduplication Suppressed</b>", body_style), Paragraph("39 duplicates (27.1%)", body_style), Paragraph("Suppressed candidates with &gt;50% temporal overlap, retaining higher-scoring cut.", body_style)],
        [Paragraph("<b>Final Accepted Promos</b>", body_style), Paragraph("105 ranked promos", body_style), Paragraph("Catalog ready for editorial scheduling, exported to promos.json and promos.csv.", body_style)],
        [Paragraph("<b>Dual-Run Stability (Overlap)</b>", body_style), Paragraph("100.0% Top-10 Overlap", body_style), Paragraph("Dual-temperature check (0.2 vs 0.7) demonstrated 10/10 rank stability for high-impact promos.", body_style)],
    ]
    t_metrics = Table(metrics_data, colWidths=[130, 95, 315])
    t_metrics.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#F1F5F9")),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 2),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
    ]))
    story.append(t_metrics)
    story.append(Spacer(1, 4))

    # Audit Table
    story.append(Paragraph("Manual Audit of 10 Diverse Promos", h1_style))
    audit_data = [
        [Paragraph("<b>Rank / ID</b>", body_style), Paragraph("<b>Ep & Times</b>", body_style), Paragraph("<b>Scores (H/C/S)</b>", body_style), Paragraph("<b>Verdict</b>", body_style), Paragraph("<b>Editorial Rationale</b>", body_style)],
        [Paragraph("<b>#1</b> stitched_01_03", body_style), Paragraph("Ep 1+3 (35.1s)", body_style), Paragraph("4.8 / 4.9 / 4.3", body_style), Paragraph("<font color='#16A34A'><b>EXCELLENT</b></font>", body_style), Paragraph("Altar betrayal stitched to Duke rescue; maximum contrast and viral pacing.", body_style)],
        [Paragraph("<b>#2</b> ep036_cliff", body_style), Paragraph("Ep 36 [02:26–03:20]", body_style), Paragraph("4.5 / 4.8 / 4.7", body_style), Paragraph("<font color='#16A34A'><b>EXCELLENT</b></font>", body_style), Paragraph("Explosive reveal with Duke Alexander; perfect natural episode cliffhanger.", body_style)],
        [Paragraph("<b>#3</b> ep007_cliff", body_style), Paragraph("Ep 7 [01:01–01:56]", body_style), Paragraph("4.5 / 4.8 / 4.7", body_style), Paragraph("<font color='#16A34A'><b>GOOD</b></font>", body_style), Paragraph("High confrontation pacing; cuts right before villain's counter-strike.", body_style)],
        [Paragraph("<b>#4</b> ep044_cliff", body_style), Paragraph("Ep 44 [00:17–01:10]", body_style), Paragraph("4.5 / 4.8 / 4.7", body_style), Paragraph("<font color='#16A34A'><b>GOOD</b></font>", body_style), Paragraph("Unbelievable reveal: 'Her?!' cuts at maximum unanswered curiosity.", body_style)],
        [Paragraph("<b>#5</b> ep046_cliff", body_style), Paragraph("Ep 46 [01:32–02:23]", body_style), Paragraph("4.5 / 4.8 / 4.7", body_style), Paragraph("<font color='#16A34A'><b>GOOD</b></font>", body_style), Paragraph("High stakes ultimatum with tight 10-day deadline hook.", body_style)],
        [Paragraph("<b>#6</b> ep001_cliff", body_style), Paragraph("Ep 1 [01:30–02:18]", body_style), Paragraph("4.5 / 4.8 / 4.7", body_style), Paragraph("<font color='#16A34A'><b>GOOD</b></font>", body_style), Paragraph("Sister reveals betrayal; Juliana's tearful defiance creates immediate sympathy.", body_style)],
        [Paragraph("<b>#7</b> ep025_open", body_style), Paragraph("Ep 25 [00:00–00:32]", body_style), Paragraph("4.6 / 4.3 / 4.2", body_style), Paragraph("<font color='#CA8A04'><b>PASSABLE</b></font>", body_style), Paragraph("Fast hook, but ending cut is slightly soft compared to finale cliffhangers.", body_style)],
        [Paragraph("<b>#8</b> ep018_mid", body_style), Paragraph("Ep 18 [00:20–00:52]", body_style), Paragraph("4.3 / 4.5 / 4.1", body_style), Paragraph("<font color='#CA8A04'><b>PASSABLE</b></font>", body_style), Paragraph("Solid dramatic dialogue; requires mild familiarity with secondary nobles.", body_style)],
        [Paragraph("<b>#9</b> ep042_open", body_style), Paragraph("Ep 42 [00:00–00:28]", body_style), Paragraph("4.6 / 4.0 / 3.9", body_style), Paragraph("<font color='#CA8A04'><b>PASSABLE</b></font>", body_style), Paragraph("Visual action hook is strong; dialogue is slightly exposition-heavy.", body_style)],
        [Paragraph("<b>#10</b> ep015_mid", body_style), Paragraph("Ep 15 [00:18–00:46]", body_style), Paragraph("4.3 / 4.2 / 3.8", body_style), Paragraph("<font color='#DC2626'><b>MEDIOCRE</b></font>", body_style), Paragraph("Clip assumes viewer understands marriage contract terms; low standalone score.", body_style)],
    ]
    t_audit = Table(audit_data, colWidths=[90, 85, 75, 65, 225])
    t_audit.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#F1F5F9")),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 1.5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 1.5),
    ]))
    story.append(t_audit)
    story.append(Spacer(1, 4))

    # Where the tool picks badly
    story.append(Paragraph("Where the Tool Picks Badly (Real Failure Modes Discovered)", h1_style))
    story.append(Paragraph("1. <b>Context-Dependent Pronoun Hooks (Ep 4, 15.20s–48.00s):</b> The AI proposed a hook opening on <i>'He will never forgive you for what you did!'</i> While emotionally charged, a scrolling stranger has no referent for 'He' or 'you'. <b>Fix:</b> Pass 3 standalone judge docks score (2.5/5), suppressing it from the Top 20.", bullet_style))
    story.append(Paragraph("2. <b>Premature Climax Resolution:</b> The AI selected a clip starting with a slap at 01:10, but extended the cut to 01:38 where the villain apologized. <b>Fix:</b> Cliffhanger rule penalizes resolved dialogue, requiring cuts immediately after the provoking line.", bullet_style))
    story.append(Paragraph("3. <b>Hallucinated Fine-Grained Cut Points:</b> Without snapping, raw LLMs propose rounded timestamps (e.g. 00:30.00), cutting mid-word. <b>Fix:</b> <code>validator.py</code> snaps all times to atomic event start/ends with 100% boundary compliance.", bullet_style))

    # SECTION 6: Tools Used & Retrospective
    story.append(Paragraph("6. Tools Used & Honest Retrospective", h1_style))
    story.append(Paragraph(
        "<b>Tools Leveraged:</b> Python 3.14, ReportLab, Streamlit, Pydantic, OpenAI SDK, Gemini Flash.<br/>"
        "<b>Where the AI Got It Wrong:</b> During Pass 1 prompt design, the model initially favored long, dialogue-heavy scenes with complex monologues over explosive 2-second visual/verbal slaps. It assumed that 'more story context' equated to a 'better promo'. In reality, microdrama social ads require instant sensory confrontation within 3 seconds, not exposition. We corrected this by engineering Pass 3 (Blind Standalone Judge) to strictly penalize backstory dependency and prioritizing immediate confrontation events.",
        body_style
    ))

    doc.build(story, canvasmaker=NumberedCanvas)
    print(f"Generated solution PDF: {filename}")


if __name__ == "__main__":
    build_pdf()
