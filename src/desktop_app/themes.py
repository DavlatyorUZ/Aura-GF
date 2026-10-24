"""
🎨 Jarvis UI Themes

Shared stylesheets for Qt interfaces, matching the Memory Viewer's
deep space theme with amber accents.
"""

from __future__ import annotations

import os
import tempfile

# Color palette
COLORS = {
    "bg_primary": "#0a0b0f",
    "bg_secondary": "#12141a",
    "bg_tertiary": "#1a1d26",
    "bg_card": "#161920",
    "bg_hover": "#1e222c",
    
    "accent_primary": "#f59e0b",
    "accent_secondary": "#fbbf24",
    "accent_glow": "rgba(245, 158, 11, 0.15)",
    "accent_muted": "#92400e",
    
    "text_primary": "#f4f4f5",
    "text_secondary": "#a1a1aa",
    "text_muted": "#71717a",
    
    "border": "#27272a",
    "border_glow": "rgba(245, 158, 11, 0.3)",
    
    "success": "#22c55e",
    "success_light": "#4ade80",
    "warning": "#f59e0b",
    "warning_light": "#fbbf24",
    "error": "#ef4444",
    "error_light": "#f87171",
}

# The procedural companion uses a compact pixel-art palette.
COMPANION_COLORS = {
    'ink': '#17294f', 'outline': '#243d70', 'blue_dark': '#2651ad',
    'blue': '#407bea', 'blue_light': '#77b2ff', 'ice': '#b9daff',
    'white': '#f5fcff', 'snow_shadow': '#d6e8ff', 'cyan': '#72eeff',
    'hair_shadow': '#648bd5', 'hair': '#9bc8ff', 'hair_light': '#c6e7ff',
    'skin_shadow': '#e6b5ac', 'skin': '#ffe4d3', 'skin_light': '#fff0e0',
    'blush': '#f3b1c0', 'mouth': '#ba5878', 'tongue': '#ff96af',
    'shadow': '#bec1e6',
}

CHAT_THEME_STYLESHEET = f"""
    QMainWindow#chatWindow, QWidget#phoneShell {{ background: transparent; }}
    QWidget#chatSurface {{
        background: {COLORS['bg_primary']}; border: 1px solid {COLORS['border']};
        border-radius: 28px;
    }}
    QWidget#chatSurface QWidget {{ background: transparent; }}
    QLabel#chatEyebrow {{ color: {COLORS['text_muted']}; font-size: 10px; letter-spacing: 2px; }}
    QLabel#chatName {{ color: {COLORS['text_primary']}; font-size: 24px; font-weight: 600; }}
    QLabel#chatCapsule {{
        color: {COLORS['accent_secondary']}; background: {COLORS['bg_secondary']};
        border: 1px solid {COLORS['border_glow']}; border-radius: 12px;
        padding: 5px 12px; font-size: 10px; letter-spacing: 2px;
    }}
    QPushButton#chatWindowControl {{
        color: {COLORS['text_secondary']}; background: transparent; border: none;
        border-radius: 18px; padding: 0; font-size: 19px; min-width: 36px;
    }}
    QPushButton#chatWindowControl:hover {{ background: {COLORS['bg_hover']}; color: {COLORS['text_primary']}; }}
    QPushButton#chatWindowControl:focus {{ border: 1px solid {COLORS['accent_primary']}; }}
    QLabel#chatEmptyTitle {{ font-size: 24px; font-weight: 600; color: {COLORS['text_primary']}; }}
    QLabel#chatEmptyDetail {{ font-size: 13px; color: {COLORS['text_secondary']}; }}
    QWidget#chatSurface QWidget#chatComposer {{ background: {COLORS['bg_secondary']}; border: 1px solid {COLORS['border']}; border-radius: 22px; }}
    QWidget#chatSurface QLabel#chatHomeIndicator {{ background: {COLORS['text_muted']}; border-radius: 2px; }}
    QScrollBar:vertical {{ background: transparent; width: 5px; margin: 0; }}
    QScrollBar::handle:vertical {{ background: {COLORS['border']}; border-radius: 2px; min-height: 28px; }}
"""


# Comprehensive Qt stylesheet matching the Memory Viewer's design
JARVIS_THEME_STYLESHEET = """
    QWidget#download_card {
        background-color: #161920;
        border: 1px solid #27272a;
        border-radius: 12px;
    }
    QMainWindow, QDialog, QWizard, QWizardPage {
        background-color: #0a0b0f;
    }
    
    QWidget {
        background-color: #0a0b0f;
        color: #f4f4f5;
        font-family: '.AppleSystemUIFont', 'Segoe UI', sans-serif;
    }
    
    QLabel {
        color: #f4f4f5;
        background: transparent;
    }
    
    QLabel#title {
        font-size: 18px;
        font-weight: 600;
        color: #f4f4f5;
    }
    
    QLabel#subtitle {
        font-size: 12px;
        color: #71717a;
    }
    
    QLabel#section_title {
        font-size: 16px;
        font-weight: bold;
        color: #fbbf24;
    }
    
    QTextEdit, QPlainTextEdit {
        background-color: #12141a;
        color: #f4f4f5;
        border: 1px solid #27272a;
        border-radius: 10px;
        padding: 12px;
        selection-background-color: rgba(245, 158, 11, 0.3);
        selection-color: #fbbf24;
    }
    
    QTextEdit:focus, QPlainTextEdit:focus {
        border-color: #f59e0b;
    }
    
    QLineEdit {
        background-color: #12141a;
        color: #f4f4f5;
        border: 1px solid #27272a;
        border-radius: 8px;
        padding: 8px 12px;
        selection-background-color: rgba(245, 158, 11, 0.3);
    }
    
    QLineEdit:focus {
        border-color: #f59e0b;
    }
    
    QLineEdit::placeholder {
        color: #71717a;
    }
    
    QPushButton {
        background-color: #1a1d26;
        color: #f4f4f5;
        border: 1px solid #27272a;
        border-radius: 8px;
        padding: 10px 20px;
        font-weight: 500;
    }
    
    QPushButton:hover {
        background-color: #1e222c;
        border-color: #f59e0b;
        color: #fbbf24;
    }
    
    QPushButton:pressed {
        background-color: rgba(245, 158, 11, 0.15);
    }
    
    QPushButton:disabled {
        background-color: #12141a;
        color: #71717a;
        border-color: #1a1d26;
    }
    
    QPushButton#primary {
        background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
            stop:0 #f59e0b, stop:1 #d97706);
        color: #0a0b0f;
        border: none;
        font-weight: 600;
    }
    
    QPushButton#primary:hover {
        background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
            stop:0 #fbbf24, stop:1 #f59e0b);
    }
    
    QPushButton#primary:disabled {
        background: #27272a;
        color: #71717a;
    }
    
    QPushButton#danger {
        background-color: #1a1d26;
        border-color: #ef4444;
        color: #ef4444;
    }
    
    QPushButton#danger:hover {
        background-color: rgba(239, 68, 68, 0.15);
        border-color: #f87171;
        color: #f87171;
    }
    
    QComboBox {
        background-color: #12141a;
        color: #f4f4f5;
        border: 1px solid #27272a;
        border-radius: 8px;
        padding: 8px 12px;
        min-width: 120px;
    }
    
    QComboBox:hover {
        border-color: #f59e0b;
    }
    
    QComboBox::drop-down {
        border: none;
        width: 24px;
    }
    
    QComboBox::down-arrow {
        image: none;
        border-left: 5px solid transparent;
        border-right: 5px solid transparent;
        border-top: 6px solid #71717a;
        margin-right: 8px;
    }
    
    QComboBox QAbstractItemView {
        background-color: #161920;
        color: #f4f4f5;
        border: 1px solid #27272a;
        border-radius: 8px;
        selection-background-color: rgba(245, 158, 11, 0.15);
        selection-color: #fbbf24;
    }
    
    QCheckBox {
        color: #f4f4f5;
        spacing: 8px;
        background: transparent;
    }
    
    QCheckBox::indicator {
        width: 18px;
        height: 18px;
        border: 1px solid #27272a;
        border-radius: 4px;
        background-color: transparent;
    }
    
    QCheckBox::indicator:hover {
        border-color: #f59e0b;
    }
    
    QCheckBox::indicator:checked {
        background-color: #f59e0b;
        border-color: #f59e0b;
    }
    
    QRadioButton {
        color: #f4f4f5;
        spacing: 8px;
        background: transparent;
    }
    
    QRadioButton::indicator {
        width: 18px;
        height: 18px;
        border: 1px solid #27272a;
        border-radius: 9px;
        background-color: #12141a;
    }
    
    QRadioButton::indicator:hover {
        border-color: #f59e0b;
    }
    
    QRadioButton::indicator:checked {
        background-color: #f59e0b;
        border-color: #f59e0b;
    }
    
    QProgressBar {
        background-color: #12141a;
        border: 1px solid #27272a;
        border-radius: 6px;
        height: 8px;
        text-align: center;
    }
    
    QProgressBar::chunk {
        background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
            stop:0 #f59e0b, stop:1 #fbbf24);
        border-radius: 5px;
    }
    
    QScrollArea {
        background: transparent;
        border: none;
    }
    
    QScrollBar:vertical {
        background-color: #12141a;
        width: 10px;
        border-radius: 5px;
        margin: 0;
    }
    
    QScrollBar::handle:vertical {
        background-color: #27272a;
        border-radius: 5px;
        min-height: 30px;
    }
    
    QScrollBar::handle:vertical:hover {
        background-color: #f59e0b;
    }
    
    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
        height: 0;
    }
    
    QScrollBar:horizontal {
        background-color: #12141a;
        height: 10px;
        border-radius: 5px;
    }
    
    QScrollBar::handle:horizontal {
        background-color: #27272a;
        border-radius: 5px;
        min-width: 30px;
    }
    
    QScrollBar::handle:horizontal:hover {
        background-color: #f59e0b;
    }
    
    QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
        width: 0;
    }
    
    QGroupBox {
        background-color: #161920;
        border: 1px solid #27272a;
        border-radius: 12px;
        margin-top: 12px;
        padding: 16px;
        padding-top: 24px;
        font-weight: 500;
    }
    
    QGroupBox::title {
        subcontrol-origin: margin;
        left: 16px;
        padding: 0 8px;
        color: #a1a1aa;
        font-size: 11px;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    
    QTabWidget::pane {
        background-color: #161920;
        border: 1px solid #27272a;
        border-radius: 12px;
        top: -1px;
    }
    
    QTabBar::tab {
        background-color: #12141a;
        color: #a1a1aa;
        border: 1px solid #27272a;
        border-bottom: none;
        border-top-left-radius: 8px;
        border-top-right-radius: 8px;
        padding: 10px 20px;
        margin-right: 2px;
    }
    
    QTabBar::tab:selected {
        background-color: #161920;
        color: #fbbf24;
        border-color: #27272a;
        border-bottom-color: #161920;
    }
    
    QTabBar::tab:hover:!selected {
        background-color: #1a1d26;
        color: #f4f4f5;
    }
    
    QSpinBox, QDoubleSpinBox {
        background-color: #12141a;
        color: #f4f4f5;
        border: 1px solid #27272a;
        border-radius: 8px;
        padding: 8px 12px;
    }
    
    QSpinBox:focus, QDoubleSpinBox:focus {
        border-color: #f59e0b;
    }
    
    QSpinBox::up-button, QDoubleSpinBox::up-button,
    QSpinBox::down-button, QDoubleSpinBox::down-button {
        background-color: #1a1d26;
        border: none;
        width: 20px;
    }

    QSpinBox::up-button:hover, QDoubleSpinBox::up-button:hover,
    QSpinBox::down-button:hover, QDoubleSpinBox::down-button:hover {
        background-color: #f59e0b;
    }

    
    QListWidget {
        background-color: #12141a;
        color: #f4f4f5;
        border: 1px solid #27272a;
        border-radius: 10px;
        padding: 8px;
    }
    
    QListWidget::item {
        padding: 8px 12px;
        border-radius: 6px;
    }
    
    QListWidget::item:selected {
        background-color: rgba(245, 158, 11, 0.15);
        color: #fbbf24;
    }
    
    QListWidget::item:hover:!selected {
        background-color: #1e222c;
    }
    
    QMessageBox {
        background-color: #0a0b0f;
    }
    
    QMessageBox QLabel {
        color: #f4f4f5;
    }
    
    QToolTip {
        background-color: #161920;
        color: #f4f4f5;
        border: 1px solid #27272a;
        border-radius: 6px;
        padding: 6px 10px;
    }
    
    QMenu {
        menu-scrollable: 1;
        background-color: #161920;
        color: #f4f4f5;
        border: 1px solid #27272a;
        border-radius: 8px;
        padding: 4px;
    }
    
    QMenu::item {
        padding: 8px 24px;
        border-radius: 4px;
    }
    
    QMenu::item:selected {
        background-color: rgba(245, 158, 11, 0.15);
        color: #fbbf24;
    }
    
    QMenu::item:disabled {
        color: #71717a;
    }

    QMenu::separator {
        height: 1px;
        background-color: #27272a;
        margin: 4px 8px;
    }
    
    /* Wizard-specific styles */
    QWizard QPushButton {
        min-width: 100px;
    }
    
    QWizard QLabel#qt_watermark_label {
        background: transparent;
    }
    
    /* Card-style container */
    QFrame#card {
        background-color: #161920;
        border: 1px solid #27272a;
        border-radius: 12px;
        padding: 16px;
    }
"""


WIZARD_STYLESHEET = f"""
    QWizard {{ background: {COLORS['bg_primary']}; }}
    QWizard QFrame#card {{
        background: {COLORS['bg_secondary']};
        border: 1px solid {COLORS['border']}; border-radius: 14px; padding: 0;
    }}
    QWizard QLabel#title {{
        color: {COLORS['text_primary']}; font-size: 28px; font-weight: 700;
    }}
    QWizard QLabel#subtitle {{
        color: {COLORS['text_secondary']}; font-size: 14px;
    }}
    QWizard QLabel#setupBrand {{
        color: {COLORS['accent_primary']}; font-size: 11px; font-weight: 700;
    }}
    QWizard QFrame#card[selected="true"] {{
        border-color: {COLORS['accent_primary']};
        background: {COLORS['bg_tertiary']};
    }}
    QWizard QLabel#setupStage {{
        color: {COLORS['text_muted']}; font-size: 11px; padding: 6px 10px;
        border-bottom: 2px solid {COLORS['border']};
    }}
    QWizard QLabel#setupStage[active="true"] {{
        color: {COLORS['text_primary']}; border-color: {COLORS['accent_primary']};
    }}
    QWizard QLabel#section_title {{
        color: {COLORS['text_primary']}; font-size: 15px; font-weight: 600;
    }}
    QWizard QPushButton {{ padding: 9px 16px; min-width: 80px; }}
    QWizard QPushButton#setupNext {{
        background: {COLORS['accent_primary']}; color: {COLORS['bg_primary']};
        border: none; font-weight: 600;
    }}
    QWizard QPushButton#setupNext:disabled {{
        background: {COLORS['bg_tertiary']}; color: {COLORS['text_muted']};
    }}
    QWizard QComboBox QLineEdit {{ padding: 0; border: none; background: transparent; }}
    QWizard QScrollArea {{ border: none; background: transparent; }}
"""


_CHECKMARK_SVG = (
    '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 18 18">'
    '<path d="M4 9l3.5 3.5L14 5" stroke="#0a0b0f" stroke-width="2.5" '
    'stroke-linecap="round" stroke-linejoin="round" fill="none"/></svg>'
)

_RADIO_DOT_SVG = (
    '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 18 18">'
    '<circle cx="9" cy="9" r="4" fill="#0a0b0f"/></svg>'
)

_ARROW_UP_SVG = (
    '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 12 12">'
    '<path d="M2.5 7.5L6 4l3.5 3.5" stroke="#a1a1aa" stroke-width="1.5" '
    'stroke-linecap="round" stroke-linejoin="round" fill="none"/></svg>'
)

_ARROW_DOWN_SVG = (
    '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 12 12">'
    '<path d="M2.5 4.5L6 8l3.5-3.5" stroke="#a1a1aa" stroke-width="1.5" '
    'stroke-linecap="round" stroke-linejoin="round" fill="none"/></svg>'
)

# Cached icon paths (created once per process)
_icon_dir: str | None = None


_ICON_STYLESHEET_TEMPLATE = """
    QCheckBox::indicator:checked {{
        image: url({check});
    }}
    QRadioButton::indicator:checked {{
        image: url({radio});
    }}
    QSpinBox::up-arrow, QDoubleSpinBox::up-arrow {{
        image: url({arrow_up});
        width: 10px;
        height: 10px;
    }}
    QSpinBox::down-arrow, QDoubleSpinBox::down-arrow {{
        image: url({arrow_down});
        width: 10px;
        height: 10px;
    }}
"""


def _ensure_icons() -> dict[str, str]:
    """Write indicator SVGs to a temp directory, return {name: path} mapping."""
    global _icon_dir
    if _icon_dir is None:
        _icon_dir = tempfile.mkdtemp(prefix="jarvis_theme_")

    icons = {
        "check": _CHECKMARK_SVG,
        "radio": _RADIO_DOT_SVG,
        "arrow_up": _ARROW_UP_SVG,
        "arrow_down": _ARROW_DOWN_SVG,
    }
    paths: dict[str, str] = {}
    for name, svg in icons.items():
        path = os.path.join(_icon_dir, f"{name}.svg")
        if not os.path.exists(path):
            with open(path, "w") as f:
                f.write(svg)
        paths[name] = path.replace("\\", "/")
    return paths


def apply_theme(widget) -> None:
    """Apply the Jarvis theme to a Qt widget, including SVG-based indicator icons."""
    icons = _ensure_icons()
    icon_css = _ICON_STYLESHEET_TEMPLATE.format(**icons)
    widget.setStyleSheet(JARVIS_THEME_STYLESHEET + icon_css)
COMPANION_REFERENCE_COLOURS = ('#1066a9fc', '#2066a9fc', '#3066a9fc', '#4066a9fc', '#5066a9fc', '#6066a9fc', '#7066a9fc', '#8066a9fc', '#9066a9fc', '#a066a9fc', '#ffffff', '#fffefc', '#fefdfd', '#fdfefe', '#fdfdfe', '#fdfcfd', '#fcfcfb', '#fafffe', '#fbfcfe', '#fbfcfd', '#fbfcfb', '#f9fcfe', '#fcfbfc', '#fafbfe', '#fafbfc', '#fafafb', '#f9fafe', '#f9fafc', '#f9fafb', '#faf9fb', '#f8f9fe', '#f8f9fc', '#f8f9fb', '#fbf9f8', '#f7fbfd', '#f7f9fe', '#f7f9fc', '#f7f8fa', '#f7f8f9', '#f4f9fd', '#e3fafe', '#f9f7f9', '#f6f7fc', '#f6f7fa', '#f6f7f9', '#f5f7fb', '#f4f5f9', '#f5f5f6', '#f2f6fc', '#f2f5f8', '#f1f3f7', '#eef4fb', '#e9f4fd', '#fdefec', '#feede7', '#edf0f7', '#f0eff2', '#e7effe', '#eaeff7', '#e6edfb', '#fee9e3', '#eee9ef', '#f8e0e0', '#f6ced2', '#e2eefd', '#daedfd', '#d9e8fd', '#dde7fc', '#a0d5e6fd', '#c0d5e6fd', '#d5e6fd', '#d9e4fb', '#a0d1e3fc', '#c0d1e3fc', '#e0d1e3fc', '#d1e3fc', '#d2e0f9', '#d2d5e9', '#bfe4fd', '#80c0dbfc', '#a0c0dbfc', '#c0dbfc', '#60bcd6fb', '#80bcd6fb', '#bcd6fb', '#bbd1f6', '#60afd0fc', '#80afd0fc', '#c0afd0fc', '#afd0fc', '#b5c8ed', '#a8d3fd', '#40a7cafc', '#60a7cafc', '#80a7cafc', '#a0a7cafc', '#c0a7cafc', '#a7cafc', '#40a6c5f9', '#60a6c5f9', '#80a6c5f9', '#a0a6c5f9', '#c0a6c5f9', '#a6c5f9', '#9dc9fb', '#c5b3c9', '#a0b3df', '#92b7f8', '#90abe6', '#7eb2fa', '#7ca9f9', '#79a4f8', '#bb8fac', '#8c92bc', '#789ef2', '#407b88b6', '#7b88b6', '#709efb', '#6f91e2', '#66a9fc', '#659cfa', '#6593f5', '#589ffb', '#4c8ef9', '#5087f7', '#4b7ef6', '#5a7ac5', '#3e7df9', '#7c668e', '#4d64a6', '#3468ee', '#3c60b7', '#7c4b74', '#403b4983', '#3b4983', '#304488', '#2449ad', '#233d8f', '#253a7c', '#1f357e', '#21336d', '#1f285e', '#142c78', '#0f2577', '#12235b', '#0a1a63', '#200d1847', '#0d1847', '#80061151', '#061151', '#02094e', '#20040a3c', '#40040a3c', '#60040a3c', '#a0040a3c', '#040a3c', '#2005082a', '#4005082a', '#6005082a', '#8005082a', '#c005082a', '#05082a', '#2000001e', '#4000001e', '#6000001e', '#8000001e', '#a000001e', '#c000001e', '#00001e', '#f5f6f9', '#fbf4f2', '#e2eafd', '#e0e9fd', '#81cffc', '#41a1fc', '#605a7ac5', '#3279f9', '#e04d64a6', '#203c60b7', '#603c60b7', '#803c60b7', '#245eed', '#402449ad', '#602449ad', '#801f357e', '#a01f357e', '#133ca8', '#40142c78', '#60142c78', '#400f2577', '#600f2577', '#c00f2577', '#4012235b', '#e012235b', '#200a1a63', '#400a1a63', '#c00a1a63', '#400d1847', '#600d1847', '#800d1847', '#20061151', '#40061151', '#60061151', '#a0061151', '#e0061151', '#2002094e', '#4002094e', '#6002094e', '#8002094e', '#a002094e', '#c002094e', '#e002094e', '#80040a3c', '#c0040a3c', '#e0040a3c', '#a005082a', '#e000001e', '#c0a8d3fd', '#409dc9fb', '#609dc9fb', '#809dc9fb', '#a09dc9fb', '#c09dc9fb', '#e09dc9fb', '#a081cffc', '#6092b7f8', '#8092b7f8', '#c092b7f8', '#e092b7f8', '#207eb2fa', '#407eb2fa', '#607eb2fa', '#807eb2fa', '#a07eb2fa', '#c07eb2fa', '#c066a9fc', '#e066a9fc', '#20589ffb', '#2041a1fc', '#4041a1fc', '#8041a1fc', '#a041a1fc', '#c041a1fc', '#204c8ef9', '#404c8ef9', '#604c8ef9', '#804c8ef9', '#a04c8ef9', '#c04c8ef9', '#e04c8ef9', '#404b7ef6', '#604b7ef6', '#203e7df9', '#403e7df9', '#603e7df9', '#803e7df9', '#203279f9', '#403279f9', '#603279f9', '#803279f9', '#a03279f9', '#c03279f9', '#203468ee', '#403468ee', '#603468ee', '#803468ee', '#a03468ee', '#c03468ee', '#20245eed', '#40245eed', '#60245eed', '#80245eed', '#a0245eed', '#c0245eed', '#e0245eed', '#f6f5f9', '#80d1e3fc', '#c0c0dbfc', '#40afd0fc', '#a0afd0fc', '#8090abe6', '#406f91e2', '#20253a7c', '#403c60b7', '#c03c60b7', '#202449ad', '#60233d8f', '#80233d8f', '#c0142c78', '#600a1a63', '#a00a1a63', '#e07eb2fa', '#20659cfa', '#40659cfa', '#60659cfa', '#a0659cfa', '#40589ffb', '#60589ffb', '#80589ffb', '#a0589ffb', '#c0589ffb', '#e0589ffb', '#6041a1fc', '#a03e7df9', '#c03e7df9', '#e03279f9', '#a0bcd6fb', '#60a8d3fd', '#4092b7f8', '#a092b7f8', '#204d64a6', '#a0daedfd', '#c0daedfd', '#e0daedfd', '#60bfe4fd', '#80bfe4fd', '#40a8d3fd', '#80a8d3fd', '#2081cffc', '#4081cffc', '#8081cffc', '#c081cffc', '#208c92bc', '#207b88b6', '#e03c60b7', '#203b4983', '#2021336d', '#20142c78', '#80142c78', '#800f2577', '#800a1a63', '#e005082a', '#40233d8f', '#a0233d8f', '#401f285e', '#200f2577', '#2012235b', '#e00a1a63', '#c0061151', '#207ca9f9', '#c07ca9f9', '#80709efb', '#80659cfa', '#e0c0dbfc', '#a0a8d3fd', '#405a7ac5', '#e0a8d3fd', '#209dc9fb', '#6081cffc', '#a090abe6', '#206f91e2', '#e06f91e2', '#206593f5', '#204b7ef6', '#a05a7ac5', '#802449ad', '#a02449ad', '#c02449ad', '#20233d8f', '#c0233d8f', '#401f357e', '#20133ca8', '#40133ca8', '#60133ca8', '#a0133ca8', '#a00f2577', '#c0d9e4fb', '#e041a1fc', '#e03e7df9', '#80bbd1f6', '#407ca9f9', '#e0d5e6fd', '#40bcd6fb', '#404d64a6', '#e01f285e', '#c00d1847', '#20bb8fac', '#40bb8fac', '#60bb8fac', '#80bb8fac', '#a0bb8fac', '#c0bb8fac', '#e0bb8fac', '#207c4b74', '#407c4b74', '#607c4b74', '#807c4b74', '#a07c4b74', '#c07c4b74', '#e07c4b74', '#a0a0b3df', '#60789ef2', '#201f285e', '#40bfe4fd', '#a0bfe4fd', '#c0bfe4fd', '#e0bfe4fd', '#20c5b3c9', '#40a0b3df', '#2090abe6', '#4090abe6', '#6012235b', '#c012235b', '#a00d1847')
