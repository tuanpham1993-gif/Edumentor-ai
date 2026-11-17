"""Runner pipeline kiểu n8n — chuỗi khối, mỗi khối một việc, có nhánh, thử lại, nhật ký từng khối
(module 09 · Tuấn · B6, 14/11/2026 — docs/Review-AI-Grading.md mục 2).

    Node(name, run, retries, on_error)   một khối; run(ctx) -> Step | None
    run_pipeline(nodes, ctx)             gọi lần lượt; ghi ctx.trace = [{node, status, ms, attempts, output, error}]

Quy tắc chạy (giống n8n):
  - Khối trả Step(goto="tên khối") → nhảy tới khối đó (nhánh); không trả gì → sang khối kế tiếp.
  - Khối đặt ctx.done = True → dừng sớm (vd bài trống: không cần gọi AI).
  - Khối raise NodeFailed → thử lại tối đa `retries` lần (trừ khi retryable=False) → vẫn lỗi: đi nhánh `on_error`
    (nếu có), không có thì raise lên trên. Trace của khối lỗi giữ `output` gắn trong NodeFailed. Lỗi lạ (không phải NodeFailed) KHÔNG nuốt — để lộ bug.
  - Khối không chạy tới (bị nhánh bỏ qua) không có trong trace — như node xám trong n8n.
  - Giới hạn số bước (MAX_STEPS) để nhánh vòng (6 → 4 ở B8) không lặp vô hạn.
Runner không biết gì về chấm bài — khối cụ thể nằm ở essay.py.
"""

import time
from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Any

MAX_STEPS = 20


class NodeFailed(Exception):
    """Khối thất bại có thể xử lý (AI lỗi, JSON sai…) → thử lại / đi nhánh on_error.

    output:    dữ liệu ghi vào trace dù khối lỗi (vd AI chạy bao lâu mới lỗi — phân biệt quá giờ với lỗi ngay)
    retryable: False → không thử lại dù khối có `retries` (vd kết quả lấy sẵn từ luồng song song đã quá giờ:
               thử lại cũng ra đúng kết quả đó, còn gọi AI lại thì giữ người học chờ thêm)."""

    def __init__(self, message: str, *, output: dict | None = None, retryable: bool = True):
        super().__init__(message)
        self.output = output or {}
        self.retryable = retryable


class PipelineError(Exception):
    """Lỗi cấu hình pipeline (tên khối sai, lặp quá MAX_STEPS)."""


@dataclass
class Step:
    """Kết quả một khối: goto = tên khối nhảy tới (None → khối kế tiếp); output = dữ liệu ghi vào trace."""

    goto: str | None = None
    output: dict[str, Any] = field(default_factory=dict)


@dataclass
class Node:
    name: str
    run: Callable[[Any], Step | None]
    retries: int = 0
    on_error: str | None = None


def run_pipeline(nodes: list[Node], ctx: Any) -> Any:
    """Chạy pipeline trên ctx (object bất kỳ có thuộc tính `trace: list` và `done: bool`). Trả ctx."""
    index = {n.name: i for i, n in enumerate(nodes)}
    if len(index) != len(nodes):
        raise PipelineError("Tên khối bị trùng")
    for n in nodes:
        if n.on_error is not None and n.on_error not in index:
            raise PipelineError(f"Khối {n.name}: on_error '{n.on_error}' không tồn tại")

    i, steps = 0, 0
    while i < len(nodes) and not ctx.done:
        steps += 1
        if steps > MAX_STEPS:
            raise PipelineError(f"Pipeline chạy quá {MAX_STEPS} bước (nhánh vòng?)")
        node = nodes[i]
        start = time.perf_counter()
        attempts, error, step, failed_output = 0, None, None, {}
        while True:
            attempts += 1
            try:
                step = node.run(ctx) or Step()
                error = None
                break
            except NodeFailed as e:
                error, failed_output = str(e), e.output
                if attempts > node.retries or not e.retryable:
                    break
        ctx.trace.append(
            {
                "node": node.name,
                "status": "ok" if error is None else "error",
                "ms": round((time.perf_counter() - start) * 1000, 1),
                "attempts": attempts,
                "output": step.output if error is None else failed_output,
                "error": error,
            }
        )
        if error is not None:
            if node.on_error is None:
                raise NodeFailed(f"{node.name}: {error}")
            i = index[node.on_error]
            continue
        if step.goto is not None:
            if step.goto not in index:
                raise PipelineError(f"Khối {node.name}: goto '{step.goto}' không tồn tại")
            i = index[step.goto]
        else:
            i += 1
    return ctx
