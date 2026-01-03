import threading
from typing import Optional

_context = threading.local()


def set_context(run_id: int, project_id: int, step_id: Optional[int] = None):
    _context.run_id = run_id
    _context.project_id = project_id
    _context.step_id = step_id


def update_step_id(step_id: int):
    _context.step_id = step_id


def get_context() -> dict:
    return {
        "run_id": getattr(_context, "run_id", None),
        "project_id": getattr(_context, "project_id", None),
        "step_id": getattr(_context, "step_id", None),
    }


def clear_context():
    _context.run_id = None
    _context.project_id = None
    _context.step_id = None
