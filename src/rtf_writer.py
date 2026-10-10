"""A minimal, real RTF table writer -- produces valid .rtf files (openable
in Word) using plain-text RTF table markup, mirroring what SAS's ODS RTF
destination would produce from a PROC REPORT table. No SAS is used; this
is a genuine from-scratch RTF generator, not a placeholder text file with
an .rtf extension.
"""
from __future__ import annotations


def _escape(text: str) -> str:
    return str(text).replace("\\", r"\\").replace("{", r"\{").replace("}", r"\}")


def write_rtf_table(path: str, titles: list[str], col_headers: list[str],
                     rows: list[list[str]], footnotes: list[str]) -> None:
    col_width = 2000
    n_cols = len(col_headers)
    cellx = "".join(f"\\cellx{col_width * (i + 1)}" for i in range(n_cols))

    def _row(cells: list[str], bold: bool = False) -> str:
        b_on, b_off = (r"\b", r"\b0") if bold else ("", "")
        cell_text = "".join(f"{b_on}{_escape(c)}{b_off}\\cell " for c in cells)
        return f"\\trowd\\trgaph80{cellx}{cell_text}\\row\n"

    body = []
    body.append(_row(col_headers, bold=True))
    for row in rows:
        body.append(_row([str(c) for c in row]))

    title_block = "".join(f"{{\\pard\\qc\\b {_escape(t)}\\par}}\n" for t in titles)
    footnote_block = "".join(f"{{\\pard\\fs16 {_escape(f)}\\par}}\n" for f in footnotes)

    rtf = (
        "{\\rtf1\\ansi\\deff0\n"
        "{\\fonttbl{\\f0 Times New Roman;}}\n"
        "\\f0\\fs20\n"
        f"{title_block}"
        "\\par\n"
        f"{''.join(body)}"
        "\\par\n"
        f"{footnote_block}"
        "}"
    )
    with open(path, "w") as f:
        f.write(rtf)
