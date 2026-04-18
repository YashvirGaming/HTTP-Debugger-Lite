from __future__ import annotations

from PySide6.QtCore import Qt
qcenter = Qt.AlignmentFlag.AlignCenter

from PySide6.QtGui import QColor
from PySide6.QtWidgets import QTableWidgetItem


def make_item(text: str, align=None) -> QTableWidgetItem:
    item = QTableWidgetItem(str(text))

    if align is not None:
        item.setTextAlignment(align)

    return item


def status_color(status_code: int) -> QColor:
    if 200 <= status_code <= 299:
        return QColor("#22c55e")
    if 300 <= status_code <= 399:
        return QColor("#eab308")
    if 400 <= status_code <= 499:
        return QColor("#f97316")
    if 500 <= status_code <= 599:
        return QColor("#ef4444")
    return QColor("#94a3b8")


def method_color(method: str) -> QColor:
    colors = {
        "GET": "#38bdf8",
        "POST": "#22c55e",
        "PUT": "#f59e0b",
        "PATCH": "#a855f7",
        "DELETE": "#ef4444",
        "OPTIONS": "#14b8a6",
        "HEAD": "#94a3b8",
        "TLS": "#f472b6",
    }
    return QColor(colors.get(method.upper(), "#cbd5e1"))


def qcenter():
    return Qt.AlignmentFlag.AlignCenter