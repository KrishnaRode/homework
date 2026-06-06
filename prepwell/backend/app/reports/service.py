"""Student reports: JSON data + a parent-friendly standalone HTML page."""
from __future__ import annotations

import html
from typing import Any

from ..mental_model import service as mm
from ..storage import db


def build_report(student_id: str) -> dict[str, Any]:
    student = db.get_student(student_id)
    summary = mm.summary(student_id)
    sessions = db.recent_sessions(student_id, limit=10)
    subject_scores: dict[str, dict[str, int]] = {}
    for key, tm in summary.get("topic_mastery", {}).items():
        subj = key.split(".", 1)[0].title()
        bucket = subject_scores.setdefault(subj, {"sum": 0, "n": 0})
        bucket["sum"] += tm.get("mastery", 0)
        bucket["n"] += 1
    subject_summary = {s: round(v["sum"] / v["n"]) for s, v in subject_scores.items() if v["n"]}

    return {
        "student": {"id": student_id, "name": student["name"] if student else student_id,
                    "class": student["class"] if student else summary.get("class")},
        "overall_index": summary["overall_index"],
        "indices": {
            "accuracy": summary["accuracy_index"],
            "confidence": summary["confidence_index"],
            "speed": summary["speed_index"],
            "reasoning": summary["reasoning_index"],
        },
        "subject_scores": subject_summary,
        "topic_mastery": summary["topic_mastery"],
        "strengths": summary["strengths"],
        "weak_areas": summary["weak_areas"],
        "mistake_patterns": summary["recent_mistakes"],
        "recommended_next": summary["recommended_next_topics"],
        "recent_sessions": [
            {"subject": s["subject"], "total": s["total"], "correct": s["correct"],
             "started_at": s["started_at"]}
            for s in sessions
        ],
        "parent_summary": _parent_summary(summary, subject_summary),
    }


def _parent_summary(summary: dict[str, Any], subject_summary: dict[str, int]) -> str:
    name = summary.get("name") or "Your child"
    idx = summary.get("overall_index", 50)
    level = "doing wonderfully" if idx >= 75 else "making steady progress" if idx >= 55 else "building their foundations"
    strong = ", ".join(summary.get("strengths", [])[:3]) or "a few core topics"
    weak = ", ".join(summary.get("weak_areas", [])[:3]) or "a couple of areas"
    return (
        f"{name} is {level} (overall learning index {idx}/100). "
        f"They are strongest in {strong}. With a little more practice on {weak}, "
        f"they'll keep growing. PrepWell adapts every question to how {name} learns."
    )


def render_html(report: dict[str, Any]) -> str:
    s = report["student"]
    def bar(label: str, val: int) -> str:
        return (
            f'<div class="row"><span>{html.escape(label)}</span>'
            f'<div class="track"><div class="fill" style="width:{val}%"></div></div>'
            f'<b>{val}</b></div>'
        )
    indices = "".join(bar(k.title(), v) for k, v in report["indices"].items())
    subjects = "".join(bar(k, v) for k, v in report["subject_scores"].items()) or "<p>No subject data yet.</p>"
    strengths = "".join(f"<li>{html.escape(x)}</li>" for x in report["strengths"]) or "<li>Building up…</li>"
    weak = "".join(f"<li>{html.escape(x)}</li>" for x in report["weak_areas"]) or "<li>None yet 🎉</li>"
    return f"""<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>PrepWell Report — {html.escape(s['name'])}</title>
<style>
  :root {{ color-scheme: light; }}
  body {{ font-family: system-ui, -apple-system, Segoe UI, Roboto, sans-serif;
    margin: 0; background: #f5f6fb; color: #1a1d29; }}
  .wrap {{ max-width: 820px; margin: 0 auto; padding: 40px 24px; }}
  h1 {{ margin: 0 0 4px; font-size: 28px; }}
  .muted {{ color: #5d6678; }}
  .card {{ background: #fff; border: 1px solid #e6e8f0; border-radius: 16px;
    padding: 24px; margin: 18px 0; box-shadow: 0 1px 2px rgba(0,0,0,.03); }}
  .big {{ font-size: 48px; font-weight: 800; color: #3d57c9; }}
  .row {{ display: flex; align-items: center; gap: 12px; margin: 10px 0; }}
  .row span {{ width: 110px; font-size: 14px; }}
  .track {{ flex: 1; height: 10px; background: #eef0f7; border-radius: 99px; overflow: hidden; }}
  .fill {{ height: 100%; background: linear-gradient(90deg,#6d8bff,#3d57c9); }}
  ul {{ margin: 8px 0; padding-left: 20px; }}
  .parent {{ font-size: 16px; line-height: 1.6; }}
  .grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 18px; }}
  @media (max-width: 600px) {{ .grid {{ grid-template-columns: 1fr; }} }}
</style></head><body><div class="wrap">
  <h1>PrepWell Learning Report</h1>
  <p class="muted">{html.escape(s['name'])} · Class {html.escape(str(s['class']))}</p>
  <div class="card"><div class="muted">Overall learning index</div>
    <div class="big">{report['overall_index']}<span style="font-size:20px;color:#9aa3b5">/100</span></div>
    <p class="parent">{html.escape(report['parent_summary'])}</p></div>
  <div class="grid">
    <div class="card"><h3>Learning indices</h3>{indices}</div>
    <div class="card"><h3>Subjects</h3>{subjects}</div>
  </div>
  <div class="grid">
    <div class="card"><h3>Strengths 💪</h3><ul>{strengths}</ul></div>
    <div class="card"><h3>Focus next 🎯</h3><ul>{weak}</ul></div>
  </div>
  <p class="muted" style="text-align:center;margin-top:24px">Generated locally by PrepWell · No data left this device.</p>
</div></body></html>"""
