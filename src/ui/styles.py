"""src/ui/styles.py - White / light theme Qt Style Sheet for BLE Monitor."""

# ── Light Color Palette ──
BG_PRIMARY = "#f5f6fa"
BG_SECONDARY = "#e8eaef"
BG_SURFACE = "#ffffff"
BG_HOVER = "#dde0e8"
BG_INPUT = "#ffffff"

TEXT_PRIMARY = "#2c3e50"
TEXT_SECONDARY = "#7f8c9b"
TEXT_ACCENT = "#0099ff"

BLUE_PRIMARY = "#0099ff"
BLUE_DARK = "#0077cc"
BLUE_LIGHT = "#33bbff"

GREEN = "#00c853"
ORANGE = "#ff9100"
RED = "#e53935"

BORDER = "#d0d4dc"
BORDER_FOCUS = "#0099ff"
RADIUS = "8px"
RADIUS_SM = "6px"


def main_window() -> str:
    return f"QMainWindow {{ background-color: {BG_PRIMARY}; }}"


def status_bar() -> str:
    return f"""
QStatusBar {{
    background-color: {BG_SECONDARY};
    color: {TEXT_SECONDARY};
    border-top: 1px solid {BORDER};
    padding: 4px 12px;
    font-size: 12px;
}}
QStatusBar::item {{ border: none; }}
"""


def tab_widget() -> str:
    return f"""
QTabWidget::pane {{
    background-color: {BG_SURFACE};
    border: 1px solid {BORDER};
    border-radius: {RADIUS};
    padding: 4px;
    top: -1px;
}}
QTabBar::tab {{
    background-color: #dde1e8;
    color: {TEXT_SECONDARY};
    border: 1px solid {BORDER};
    border-bottom: none;
    border-top-left-radius: {RADIUS_SM};
    border-top-right-radius: {RADIUS_SM};
    padding: 8px 18px;
    margin-right: 2px;
    font-size: 13px;
    font-weight: 500;
}}
QTabBar::tab:hover {{
    background-color: #eef1f6;
    color: {TEXT_PRIMARY};
}}
QTabBar::tab:selected {{
    background-color: {BG_SURFACE};
    color: {TEXT_ACCENT};
    border-bottom: 2px solid {BLUE_PRIMARY};
}}
"""


def button_base() -> str:
    return f"""
QPushButton {{
    background-color: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 #ffffff, stop:1 #f0f1f5);
    color: {TEXT_PRIMARY};
    border: 1px solid {BORDER};
    border-radius: {RADIUS_SM};
    padding: 8px 16px;
    font-size: 13px;
    font-weight: 500;
    min-height: 20px;
}}
QPushButton:hover {{
    background-color: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 #f5f7ff, stop:1 {BG_HOVER});
    border: 1px solid {BLUE_DARK};
}}
QPushButton:pressed {{
    background-color: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 #e0e2e8, stop:1 #d5d7de);
}}
QPushButton:disabled {{
    background-color: {BG_SECONDARY};
    color: #bbbbbb;
    border: 1px solid #e0e0e0;
}}
"""


def button_primary() -> str:
    return f"""
QPushButton[type="primary"] {{
    background-color: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 {BLUE_LIGHT}, stop:1 {BLUE_PRIMARY});
    color: #ffffff;
    border: none;
    border-radius: {RADIUS_SM};
    padding: 8px 20px;
    font-size: 13px;
    font-weight: 600;
    min-height: 20px;
}}
QPushButton[type="primary"]:hover {{
    background-color: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 #55ccff, stop:1 {BLUE_LIGHT});
}}
QPushButton[type="primary"]:pressed {{
    background-color: {BLUE_DARK};
}}
QPushButton[type="primary"]:disabled {{
    background-color: {BG_SECONDARY};
    color: #bbbbbb;
}}
"""


def button_danger() -> str:
    return f"""
QPushButton[type="danger"] {{
    background-color: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 #ff5252, stop:1 {RED});
    color: #ffffff;
    border: none;
    border-radius: {RADIUS_SM};
    padding: 8px 20px;
    font-size: 13px;
    font-weight: 600;
}}
QPushButton[type="danger"]:hover {{
    background-color: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 #ff7171, stop:1 #ff5252);
}}
QPushButton[type="danger"]:disabled {{
    background-color: {BG_SECONDARY};
    color: #bbbbbb;
}}
"""


def list_widget() -> str:
    return f"""
QListWidget {{
    background-color: {BG_INPUT};
    border: 1px solid {BORDER};
    border-radius: {RADIUS_SM};
    padding: 4px;
    outline: none;
    font-size: 12px;
    color: {TEXT_PRIMARY};
}}
QListWidget::item {{
    padding: 8px 12px;
    border-radius: 4px;
    margin: 2px 0px;
}}
QListWidget::item:hover {{
    background-color: #eef1f8;
}}
QListWidget::item:selected {{
    background-color: rgba(0, 153, 255, 0.12);
    color: {TEXT_ACCENT};
    border: 1px solid rgba(0, 153, 255, 0.3);
}}
"""


def table_widget() -> str:
    return f"""
QTableWidget {{
    background-color: {BG_INPUT};
    border: 1px solid {BORDER};
    border-radius: {RADIUS_SM};
    gridline-color: {BORDER};
    font-size: 12px;
    color: {TEXT_PRIMARY};
}}
QTableWidget::item {{
    padding: 6px 10px;
    border-bottom: 1px solid #e8eaef;
}}
QTableWidget::item:selected {{
    background-color: rgba(0, 153, 255, 0.12);
    color: {TEXT_ACCENT};
}}
QHeaderView::section {{
    background-color: {BG_SECONDARY};
    color: {TEXT_PRIMARY};
    padding: 8px 10px;
    border: none;
    border-bottom: 2px solid {BLUE_PRIMARY};
    font-weight: 600;
    font-size: 12px;
}}
"""


def combo_box() -> str:
    return f"""
QComboBox {{
    background-color: {BG_INPUT};
    color: {TEXT_PRIMARY};
    border: 1px solid {BORDER};
    border-radius: {RADIUS_SM};
    padding: 6px 12px;
    font-size: 13px;
    min-height: 20px;
}}
QComboBox:hover {{ border: 1px solid {BLUE_DARK}; }}
QComboBox::drop-down {{ border: none; width: 24px; }}
QComboBox::down-arrow {{
    image: none;
    border-left: 5px solid transparent;
    border-right: 5px solid transparent;
    border-top: 6px solid {TEXT_SECONDARY};
    margin-right: 6px;
}}
QComboBox QAbstractItemView {{
    background-color: {BG_INPUT};
    border: 1px solid {BORDER};
    border-radius: 4px;
    color: {TEXT_PRIMARY};
    selection-background-color: #eef1f8;
    selection-color: {TEXT_ACCENT};
    padding: 4px;
}}
"""


def progress_bar() -> str:
    return f"""
QProgressBar {{
    background-color: {BG_SECONDARY};
    border: 1px solid {BORDER};
    border-radius: 4px;
    text-align: center;
    color: {TEXT_PRIMARY};
    font-size: 12px;
    height: 20px;
}}
QProgressBar::chunk {{
    background-color: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 {BLUE_PRIMARY}, stop:1 {GREEN});
    border-radius: 3px;
}}
"""


def text_edit() -> str:
    return f"""
QTextEdit, QPlainTextEdit {{
    background-color: {BG_INPUT};
    color: {TEXT_PRIMARY};
    border: 1px solid {BORDER};
    border-radius: {RADIUS_SM};
    padding: 8px;
    font-size: 13px;
    font-family: "Consolas", "Courier New", monospace;
}}
QTextEdit:focus, QPlainTextEdit:focus {{ border: 1px solid {BORDER_FOCUS}; }}
"""


def scroll_bar() -> str:
    return f"""
QScrollBar:vertical {{ background: {BG_SECONDARY}; width: 10px; border-radius: 5px; }}
QScrollBar::handle:vertical {{ background: #c0c4cc; border-radius: 5px; min-height: 30px; }}
QScrollBar::handle:vertical:hover {{ background: {BLUE_DARK}; }}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{ height: 0; }}
QScrollBar:horizontal {{ background: {BG_SECONDARY}; height: 10px; border-radius: 5px; }}
QScrollBar::handle:horizontal {{ background: #c0c4cc; border-radius: 5px; min-width: 30px; }}
QScrollBar::handle:horizontal:hover {{ background: {BLUE_DARK}; }}
QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{ width: 0; }}
"""


def tool_tip() -> str:
    return f"""
QToolTip {{
    background-color: {BG_SURFACE};
    color: {TEXT_PRIMARY};
    border: 1px solid {BLUE_DARK};
    border-radius: 4px;
    padding: 6px 10px;
    font-size: 12px;
}}
"""


def group_box() -> str:
    return f"""
QGroupBox {{
    background-color: {BG_SURFACE};
    border: 1px solid {BORDER};
    border-radius: {RADIUS};
    margin-top: 12px;
    padding: 16px 12px 12px 12px;
    font-weight: 600;
    color: {TEXT_PRIMARY};
}}
QGroupBox::title {{
    subcontrol-origin: margin;
    subcontrol-position: top left;
    padding: 2px 10px;
    color: {TEXT_ACCENT};
}}
"""


def get_full_stylesheet() -> str:
    return "\n".join([
        main_window(), status_bar(), tab_widget(), button_base(),
        list_widget(), table_widget(), combo_box(), progress_bar(),
        text_edit(), scroll_bar(), tool_tip(), group_box(),
    ])