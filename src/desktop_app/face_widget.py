"""A procedural pixel companion, animated from the daemon's activity."""

from __future__ import annotations

from enum import Enum
import math
import random
import time as _time

from PyQt6.QtCore import QPoint, QRectF, Qt, QTimer, pyqtSignal
from PyQt6.QtGui import QColor, QFont, QImage, QPainter, QPen, QPixmap, QRegion
from PyQt6.QtWidgets import QApplication, QMenu, QVBoxLayout, QWidget

from desktop_app.themes import COLORS, apply_theme
from desktop_app.companion_painter import CompanionPose, render_companion
from jarvis.activity import JarvisState, get_jarvis_state
from jarvis.debug import debug_log


class Expression(Enum):
    """Expressions accepted by the desktop's shared face interface."""

    NEUTRAL = 'neutral'
    HAPPY = 'happy'
    SAD = 'sad'
    THINKING = 'thinking'
    SURPRISED = 'surprised'
    CURIOUS = 'curious'
    EXCITED = 'excited'
    CONCERNED = 'concerned'


_STATUS = {
    JarvisState.ASLEEP: ('Standby', 'text_secondary'),
    JarvisState.IDLE: ('Ready', 'success_light'),
    JarvisState.LISTENING: ('Listening', 'accent_secondary'),
    JarvisState.THINKING: ('Thinking', 'accent_primary'),
    JarvisState.SPEAKING: ('Speaking', 'success_light'),
    JarvisState.DICTATING: ('Recording', 'error_light'),
    JarvisState.DICTATION_PROCESSING: ('Transcribing', 'warning_light'),
}


class FaceWidget(QWidget):
    """A bounded animation with separate blink, speech and activity cues."""

    state_observed = pyqtSignal(str)
    DESIGN_WIDTH = 240
    DESIGN_HEIGHT = 380

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self._state_manager = get_jarvis_state()
        self._jarvis_state = self._state_manager.state
        self._expression = Expression.NEUTRAL
        self._started_at = _time.monotonic()
        self._elapsed = 0.0
        self._next_blink_at = self._started_at + random.uniform(4.5, 7.5)
        self._blink_started_at = None
        self._blink_factor = 0.0
        self._mouth_open = 0.0
        self._wave_started_at = None
        self._pose = CompanionPose()
        self._animation_timer = QTimer(self)
        self._animation_timer.timeout.connect(self._animate)
        self._refresh_accessibility()

    @property
    def status_text(self) -> str:
        return _STATUS[self._jarvis_state][0]

    def _refresh_accessibility(self):
        self.setAccessibleName('Jarvis anime companion')
        self.setAccessibleDescription(f'{self.status_text}. Double-click to open chat.')

    def set_expression(self, expression: Expression):
        self._expression = expression
        self._animate()

    def wave(self):
        """Greet the user without moving the window or changing daemon state."""
        self._wave_started_at = _time.monotonic()
        debug_log('Companion greeting', 'face')
        self._animate()
        self.update()

    def showEvent(self, event):
        super().showEvent(event)
        self._blink_started_at = None
        self._next_blink_at = _time.monotonic() + random.uniform(4.5, 7.5)
        self._animate()
        self._animation_timer.start()

    def hideEvent(self, event):
        self._animation_timer.stop()
        super().hideEvent(event)

    def _animate(self):
        now = _time.monotonic()
        self._elapsed = max(0.0, now - self._started_at)
        state = self._state_manager.state
        if state != self._jarvis_state:
            if self._jarvis_state == JarvisState.ASLEEP and state == JarvisState.IDLE:
                self._wave_started_at = now
                debug_log('Companion greeting on voice readiness', 'face')
            self._jarvis_state = state
            self._refresh_accessibility()
            self.state_observed.emit(state.value)
            debug_log(f'Companion activity: {state.value}', 'face')
        awake = state != JarvisState.ASLEEP
        if state == JarvisState.SPEAKING:
            syllable = (math.sin(self._elapsed * 16.0) * 0.7 + math.sin(self._elapsed * 7.5) * 0.3 + 1.0) / 2.0
            phrase = max(0.0, math.sin(self._elapsed * 3.5))
            self._mouth_open = max(0.0, min(1.0, syllable * (0.4 + 0.6 * phrase)))
        else:
            self._mouth_open = 0.0
        self._blink_factor = 0.0
        if awake:
            if self._blink_started_at is None and now >= self._next_blink_at:
                self._blink_started_at = now
            if self._blink_started_at is not None:
                progress = (now - self._blink_started_at) / 0.16
                if progress >= 1:
                    self._blink_started_at = None
                    self._next_blink_at = now + random.uniform(4.5, 7.5)
                else:
                    self._blink_factor = math.sin(max(0, progress) * math.pi)
        else:
            self._blink_started_at = None
            self._next_blink_at = now + random.uniform(4.5, 7.5)
        wave = 0.0
        if self._wave_started_at is not None:
            progress = (now - self._wave_started_at) / 2.4
            if progress < 1:
                wave = max(0.001, progress)
            else:
                self._wave_started_at = None
        thinking = state in (JarvisState.THINKING, JarvisState.DICTATION_PROCESSING)
        effective_expression = self._expression.value
        if self._expression == Expression.NEUTRAL:
            if thinking:
                effective_expression = Expression.THINKING.value
            elif state == JarvisState.SPEAKING:
                effective_expression = Expression.HAPPY.value
            elif state in (JarvisState.LISTENING, JarvisState.DICTATING):
                effective_expression = Expression.CURIOUS.value
        self._pose = CompanionPose(
            breath=round((1 + math.sin(self._elapsed * 1.8)) / 2) if awake else 0,
            blink=self._blink_factor, mouth=self._mouth_open, wave=wave,
            hair=round(math.sin(self._elapsed * 1.4)) if awake else 0,
            gaze=round(math.sin(self._elapsed * 1.2)) if thinking else 0,
            expression=effective_expression,
            attentive=state in (JarvisState.LISTENING, JarvisState.DICTATING),
            thinking=thinking,
        )
        # Standby keeps open, welcoming eyes; it never impersonates a reply.
        self._animation_timer.setInterval(33 if wave else 250 if not awake else 66 if state == JarvisState.IDLE else 33)
        self.update()

    def _character_rect(self) -> QRectF:
        height = self.height() - 48.0
        width = height * 104 / 144
        if width > self.width() - 24:
            width = self.width() - 24.0
            height = width * 144 / 104
        return QRectF((self.width() - width) / 2, 8, width, height)

    def _badge_rect(self) -> QRectF:
        width = min(164.0, self.width() - 24.0)
        return QRectF((self.width() - width) / 2, self.height() - 32, width, 26)

    def input_region(self) -> QRegion:
        """Include painted pixels and motion padding, leaving empty desktop free."""
        image = QImage(self.size(), QImage.Format.Format_ARGB32_Premultiplied)
        image.fill(Qt.GlobalColor.transparent)
        painter = QPainter(image)
        # Sample the extremities of articulated poses to reserve a stable hit region.
        target = self._character_rect()
        for wave in (0, 0.1, 0.3, 0.5, 0.7, 0.9):
            for hair in (-1, 1):
                painter.drawImage(target, render_companion(CompanionPose(wave=wave, hair=hair, thinking=True)))
        painter.end()
        region = QRegion(QPixmap.fromImage(image).mask())
        padded = QRegion(region)
        padding = math.ceil(target.width() / 104 * 2)
        for x in range(-padding, padding + 1):
            for y in range(-padding, padding + 1):
                padded |= region.translated(x, y)
        return padded | QRegion(self._badge_rect().adjusted(-1, -1, 1, 1).toAlignedRect())

    def paintEvent(self, event):
        painter = QPainter(self)
        try:
            painter.setRenderHint(QPainter.RenderHint.Antialiasing)
            target = self._character_rect()
            painter.save()
            painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform, False)
            painter.drawImage(target, render_companion(self._pose))
            painter.restore()
            self._paint_status(painter)
        finally:
            painter.end()

    def _paint_status(self, painter):
        badge = self._badge_rect()
        colour = QColor(COLORS[_STATUS[self._jarvis_state][1]])
        painter.setPen(QPen(QColor(COLORS['border']), 1))
        painter.setBrush(QColor(COLORS['bg_card']))
        painter.drawRoundedRect(badge, 13, 13)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(colour)
        painter.drawEllipse(QRectF(badge.x() + 13, badge.y() + 10, 6, 6))
        painter.setPen(QColor(COLORS['text_primary']))
        painter.setFont(QFont('Segoe UI', 9))
        painter.drawText(badge.adjusted(24, 0, -26, 0), Qt.AlignmentFlag.AlignCenter, self.status_text)
        if self._jarvis_state in (JarvisState.THINKING, JarvisState.DICTATION_PROCESSING):
            painter.setPen(QPen(colour, 1.6))
            painter.drawArc(badge.adjusted(badge.width() - 22, 8, -12, -8),
                            int(-self._elapsed * 160 * 16), 250 * 16)
        elif self._jarvis_state in (JarvisState.SPEAKING, JarvisState.LISTENING, JarvisState.DICTATING):
            painter.setPen(QPen(colour, 1.6, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap))
            for index in range(3):
                x = badge.right() - 21 + index * 4
                amplitude = 2 + 3 * (1 + math.sin(self._elapsed * 6 + index)) / 2
                painter.drawLine(QPoint(round(x), round(badge.center().y() - amplitude)),
                                 QPoint(round(x), round(badge.center().y() + amplitude)))


class FaceWindow(QWidget):
    """A non-activating companion with deliberate access to the shared chat."""

    chat_requested = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle('Jarvis Companion')
        self.resize(FaceWidget.DESIGN_WIDTH, FaceWidget.DESIGN_HEIGHT)
        self.setWindowFlags(Qt.WindowType.Tool | Qt.WindowType.FramelessWindowHint
                            | Qt.WindowType.WindowStaysOnTopHint | Qt.WindowType.WindowDoesNotAcceptFocus)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating)
        self.setAttribute(Qt.WidgetAttribute.WA_MacAlwaysShowToolWindow)
        self.setStyleSheet('background: transparent;')
        self.setAccessibleName('Jarvis anime companion')
        self.setToolTip('Double-click to open chat. Drag to move. Right-click for controls.')
        self._tray_menu = None
        self._drag_offset = None
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        self.face = FaceWidget()
        layout.addWidget(self.face)
        self.face.state_observed.connect(self._update_presence)
        self._update_presence(self.face._jarvis_state.value)
        self._position_on_right()

    def _position_on_right(self):
        screen = QApplication.primaryScreen()
        if screen is not None:
            bounds = screen.availableGeometry()
            self.move(bounds.right() - self.width() - 20,
                      bounds.top() + (bounds.height() - self.height()) // 2)

    def set_expression(self, expression: Expression):
        self.face.set_expression(expression)

    def _update_presence(self, state_value: str):
        state = JarvisState(state_value)
        self.setWindowOpacity(0.9 if state == JarvisState.ASLEEP else 0.98 if state == JarvisState.IDLE else 1.0)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.layout().activate()
        self.setMask(self.face.input_region())

    def mouseDoubleClickEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self._drag_offset = None
            debug_log('Companion requested text chat', 'desktop')
            self.chat_requested.emit()
            event.accept()
        else:
            super().mouseDoubleClickEvent(event)

    def mousePressEvent(self, event):
        self._drag_offset = None
        if event.button() == Qt.MouseButton.LeftButton:
            handle = self.windowHandle()
            if handle is None or not handle.startSystemMove():
                self._drag_offset = event.globalPosition().toPoint() - self.pos()
            event.accept()

    def mouseMoveEvent(self, event):
        if self._drag_offset is not None and event.buttons() & Qt.MouseButton.LeftButton:
            self.move(event.globalPosition().toPoint() - self._drag_offset)
            event.accept()

    def mouseReleaseEvent(self, event):
        self._drag_offset = None
        super().mouseReleaseEvent(event)

    def set_tray_menu(self, menu: QMenu):
        self._tray_menu = menu

    def contextMenuEvent(self, event):
        menu = QMenu(self)
        menu.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)
        apply_theme(menu)
        menu.addAction('👋 Wave', self.face.wave)
        menu.addAction('👤 Hide Companion', self.hide)
        if self._tray_menu is not None:
            menu.addSeparator()
            menu.addActions(self._tray_menu.actions())
        debug_log('Companion context menu opened', 'desktop')
        menu.popup(event.globalPos())
        event.accept()
