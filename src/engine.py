from __future__ import annotations
import json
from pathlib import Path
import yaml

def load_playbook(path: Path) -> dict:
    return yaml.safe_load(path.read_text(encoding="utf-8"))

def execute_steps(playbook: dict, answers: dict | None = None) -> dict:
    answers = answers or {}
    results = []
    completed = 0
    for step in playbook.get("steps", []):
        sid = step["id"]
        required = bool(step.get("required", True))
        done = bool(answers.get(sid, step.get("default_done", False)))
        if done:
            completed += 1
        results.append({
            "id": sid,
            "title": step.get("title"),
            "owner": step.get("owner"),
            "required": required,
            "done": done,
            "sla_hours": step.get("sla_hours"),
        })
    total = len(results) or 1
    return {
        "playbook": playbook.get("name"),
        "completion_percent": round(100.0 * completed / total, 1),
        "completed": completed,
        "total": total,
        "open_required": [r["id"] for r in results if r["required"] and not r["done"]],
        "steps": results,
    }

def run(data_dir: Path, out_dir: Path) -> dict:
    playbook = load_playbook(data_dir / "playbook.yaml")
    answers_path = data_dir / "step_status.json"
    answers = json.loads(answers_path.read_text(encoding="utf-8")) if answers_path.exists() else {}
    summary = execute_steps(playbook, answers)
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "playbook_run.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    return summary
