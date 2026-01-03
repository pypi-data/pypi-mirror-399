import re
from typing import Any, Dict, List, Optional, Sequence, Tuple, Union
from .compare import Compare


class CompareWithDiffTable(Compare):
    """
    Extends Compare to extract and print only differing entries in a console-friendly table.
    """

    def __init__(self, base, test, method, tolerance, rows=None, cols=None):
        super().__init__(base, test, method, tolerance, rows=rows, cols=cols)
        self._diff_entries: List[Dict[str, Any]] = []

    def compare(self):
        # Keep original behavior
        res = super().compare()

        # If files differ and method is numeric, compute detailed diff entries
        if res.get("status") is False and self._method in ["absolute", "relative", "power"]:
            # If read failed, there is nothing to detail reliably
            if self._baseContent and self._testContent and self._rows is not None and self._cols is not None:
                self._collect_diff_entries()

        return res

    def _collect_diff_entries(self):
        """
        Collect only the entries that fail the comparison, along with useful metrics.
        """
        self._diff_entries = []

        for i in self._rows:
            for j in self._cols[i]:
                v1 = self._baseContent[i][j]
                v2 = self._testContent[i][j]

                # Compute metrics for this pair
                self._computeCurrentAndMaxValues(v1, v2)

                passed = True
                if self._method == "absolute":
                    passed = (self._currentAbs <= self._tolerance)
                elif self._method == "relative":
                    passed = (self._currentRel <= self._tolerance)
                elif self._method == "power":
                    if self._currentPower == 0:
                        passed = True
                    elif self._tolerance == 0:
                        passed = False
                    else:
                        passed = (self._currentPower >= self._tolerance)

                if not passed:
                    self._diff_entries.append({
                        "row": int(i),
                        "col": int(j),
                        "base": v1,
                        "test": v2,
                        "abs": self._currentAbs,
                        "rel": self._currentRel,
                        "power": self._currentPower,
                    })

    def get_diff_entries(self) -> List[Dict[str, Any]]:
        return list(self._diff_entries)


def _ascii_table(title: str, headers: List[str], rows: List[List[str]]) -> str:
    # Compute widths
    widths = [len(h) for h in headers]
    for r in rows:
        for i, cell in enumerate(r):
            widths[i] = max(widths[i], len(cell))

    def sep() -> str:
        return "+-" + "-+-".join("-" * w for w in widths) + "-+"

    def fmt(r: List[str]) -> str:
        return "| " + " | ".join(r[i].ljust(widths[i]) for i in range(len(headers))) + " |"

    out = []
    out.append(title)
    out.append("=" * len(title))
    out.append(sep())
    out.append(fmt(headers))
    out.append(sep())
    for r in rows:
        out.append(fmt(r))
    out.append(sep())
    return "\n".join(out)


def _safe_float_str(x: Any) -> str:
    # Nicely format floats in scientific-ish style without going crazy
    try:
        xf = float(x)
        # Use compact repr
        return f"{xf:.6g}"
    except Exception:
        return str(x)


def print_diff_table_for_file(
    base_path: str,
    test_path: str,
    method: str,
    tolerance: Union[str, float, int],
    rows: Optional[Sequence[int]] = None,
    cols: Optional[Sequence[int]] = None,
    max_rows: int = 200,
) -> str:
    """
    Returns a console-friendly table.
    - If comparison passes: returns a short OK message.
    - If FAIL:
        * method in absolute/relative/power: show only failing (row,col) entries
        * method == diff: show a compact "diff-like" line list (best-effort)
    """
    cmp = CompareWithDiffTable(base_path, test_path, method, tolerance, rows=rows, cols=cols)
    res = cmp.compare()

    title = f"{test_path}  (method={method}, tol={tolerance})"

    if res.get("status", True):
        return _ascii_table(
            title,
            ["status", "error", "differences", "total", "maxAbs", "maxRel", "maxPower"],
            [[
                "OK",
                str(res.get("error", "OK")),
                str(res.get("differences", 0)),
                str(res.get("total", 0)),
                _safe_float_str(res.get("maxAbs", 0)),
                _safe_float_str(res.get("maxRel", 0)),
                str(res.get("maxPower", 0)),
            ]]
        )

    # FAIL cases
    if method in ["absolute", "relative", "power"]:
        entries = cmp.get_diff_entries()

        if not entries:
            # Failure happened but we couldn't compute per-entry diffs (read/shape issue)
            return _ascii_table(
                title,
                ["status", "error", "differences", "total", "maxAbs", "maxRel", "maxPower"],
                [[
                    "FAIL",
                    str(res.get("error", "")),
                    str(res.get("differences", "")),
                    str(res.get("total", "")),
                    _safe_float_str(res.get("maxAbs", "")),
                    _safe_float_str(res.get("maxRel", "")),
                    str(res.get("maxPower", "")),
                ]]
            )

        # Build rows for table (limit size for CI logs)
        headers = ["row", "col", "base", "test", "abs", "rel", "power"]
        table_rows = []
        for e in entries[:max_rows]:
            table_rows.append([
                str(e["row"]),
                str(e["col"]),
                str(e["base"]),
                str(e["test"]),
                _safe_float_str(e["abs"]),
                _safe_float_str(e["rel"]),
                str(e["power"]),
            ])

        if len(entries) > max_rows:
            table_rows.append([
                "...", "...", "...", "...", "...", "...",
                f"+{len(entries) - max_rows} more"
            ])

        return _ascii_table(
            f"{title}  => FAIL: showing only failing entries",
            headers,
            table_rows
        )

    if method == "diff":
        # Best effort: show unified-ish "changed lines" without external deps.
        # (Your original code used command("diff ...") which doesn't capture output.)
        # Here we do a minimal in-Python line compare.
        try:
            with open(base_path, "r", encoding="utf-8", errors="replace") as fb:
                base_lines = fb.readlines()
            with open(test_path, "r", encoding="utf-8", errors="replace") as ft:
                test_lines = ft.readlines()
        except Exception as e:
            return _ascii_table(
                title,
                ["status", "error"],
                [["FAIL", f"diff-read: {e}"]]
            )

        # Find differing line numbers (simple positional comparison)
        maxlen = max(len(base_lines), len(test_lines))
        diff_rows = []
        for i in range(maxlen):
            b = base_lines[i].rstrip("\n") if i < len(base_lines) else "<NO LINE>"
            t = test_lines[i].rstrip("\n") if i < len(test_lines) else "<NO LINE>"
            if b != t:
                diff_rows.append([str(i), b[:120], t[:120]])  # trim to keep logs sane
                if len(diff_rows) >= max_rows:
                    break

        if len(diff_rows) == max_rows and maxlen > max_rows:
            diff_rows.append(["...", "...", "..."])

        return _ascii_table(
            f"{title}  => FAIL: showing differing lines (simple diff)",
            ["line", "base", "test"],
            diff_rows if diff_rows else [["-", "-", "-"]]
        )

    # Unknown method fallback
    return _ascii_table(
        title,
        ["status", "error"],
        [["FAIL", f"unknown method: {method}"]]
    )
