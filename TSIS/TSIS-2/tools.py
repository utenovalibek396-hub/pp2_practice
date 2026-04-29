"""
tools.py — Drawing tools for the Paint application (TSIS 2)
Implements: Pencil, Line, Rectangle, Circle, Eraser, Flood-Fill, Text,
            Square, Right Triangle, Equilateral Triangle, Rhombus
"""

import pygame
import math
from collections import deque


# ─────────────────────────────────────────────
#  Base class
# ─────────────────────────────────────────────
class Tool:
    """Abstract base for every drawing tool."""

    name = "base"

    def on_mouse_down(self, canvas, pos, color, size):
        pass

    def on_mouse_drag(self, canvas, pos, color, size):
        pass

    def on_mouse_up(self, canvas, pos, color, size):
        pass

    def draw_preview(self, surface, color, size):
        """Draw a live preview overlay (called every frame while dragging)."""
        pass


# ─────────────────────────────────────────────
#  Pencil (freehand)
# ─────────────────────────────────────────────
class PencilTool(Tool):
    name = "pencil"

    def __init__(self):
        self._last_pos = None

    def on_mouse_down(self, canvas, pos, color, size):
        self._last_pos = pos
        pygame.draw.circle(canvas, color, pos, size // 2)

    def on_mouse_drag(self, canvas, pos, color, size):
        if self._last_pos:
            pygame.draw.line(canvas, color, self._last_pos, pos, size)
        self._last_pos = pos

    def on_mouse_up(self, canvas, pos, color, size):
        self._last_pos = None


# ─────────────────────────────────────────────
#  Eraser
# ─────────────────────────────────────────────
class EraserTool(Tool):
    name = "eraser"

    def __init__(self):
        self._last_pos = None

    def on_mouse_down(self, canvas, pos, color, size):
        self._last_pos = pos
        pygame.draw.circle(canvas, (255, 255, 255), pos, size * 2)

    def on_mouse_drag(self, canvas, pos, color, size):
        if self._last_pos:
            pygame.draw.line(canvas, (255, 255, 255), self._last_pos, pos, size * 4)
        self._last_pos = pos

    def on_mouse_up(self, canvas, pos, color, size):
        self._last_pos = None


# ─────────────────────────────────────────────
#  Straight Line
# ─────────────────────────────────────────────
class LineTool(Tool):
    name = "line"

    def __init__(self):
        self._start = None
        self._current = None

    def on_mouse_down(self, canvas, pos, color, size):
        self._start = pos
        self._current = pos

    def on_mouse_drag(self, canvas, pos, color, size):
        self._current = pos

    def on_mouse_up(self, canvas, pos, color, size):
        if self._start:
            pygame.draw.line(canvas, color, self._start, pos, size)
        self._start = None
        self._current = None

    def draw_preview(self, surface, color, size):
        if self._start and self._current:
            pygame.draw.line(surface, color, self._start, self._current, size)


# ─────────────────────────────────────────────
#  Rectangle
# ─────────────────────────────────────────────
class RectangleTool(Tool):
    name = "rectangle"

    def __init__(self):
        self._start = None
        self._current = None

    def on_mouse_down(self, canvas, pos, color, size):
        self._start = pos
        self._current = pos

    def on_mouse_drag(self, canvas, pos, color, size):
        self._current = pos

    def on_mouse_up(self, canvas, pos, color, size):
        if self._start:
            rect = pygame.Rect(
                min(self._start[0], pos[0]),
                min(self._start[1], pos[1]),
                abs(pos[0] - self._start[0]),
                abs(pos[1] - self._start[1]),
            )
            pygame.draw.rect(canvas, color, rect, size)
        self._start = None
        self._current = None

    def draw_preview(self, surface, color, size):
        if self._start and self._current:
            rect = pygame.Rect(
                min(self._start[0], self._current[0]),
                min(self._start[1], self._current[1]),
                abs(self._current[0] - self._start[0]),
                abs(self._current[1] - self._start[1]),
            )
            pygame.draw.rect(surface, color, rect, size)


# ─────────────────────────────────────────────
#  Square
# ─────────────────────────────────────────────
class SquareTool(Tool):
    name = "square"

    def __init__(self):
        self._start = None
        self._current = None

    def on_mouse_down(self, canvas, pos, color, size):
        self._start = pos
        self._current = pos

    def on_mouse_drag(self, canvas, pos, color, size):
        self._current = pos

    def _make_rect(self, end):
        dx = end[0] - self._start[0]
        dy = end[1] - self._start[1]
        side = min(abs(dx), abs(dy))
        x = self._start[0] if dx >= 0 else self._start[0] - side
        y = self._start[1] if dy >= 0 else self._start[1] - side
        return pygame.Rect(x, y, side, side)

    def on_mouse_up(self, canvas, pos, color, size):
        if self._start:
            pygame.draw.rect(canvas, color, self._make_rect(pos), size)
        self._start = None
        self._current = None

    def draw_preview(self, surface, color, size):
        if self._start and self._current:
            pygame.draw.rect(surface, color, self._make_rect(self._current), size)


# ─────────────────────────────────────────────
#  Circle
# ─────────────────────────────────────────────
class CircleTool(Tool):
    name = "circle"

    def __init__(self):
        self._start = None
        self._current = None

    def on_mouse_down(self, canvas, pos, color, size):
        self._start = pos
        self._current = pos

    def on_mouse_drag(self, canvas, pos, color, size):
        self._current = pos

    def _radius(self, end):
        dx = end[0] - self._start[0]
        dy = end[1] - self._start[1]
        return max(1, int(math.hypot(dx, dy)))

    def on_mouse_up(self, canvas, pos, color, size):
        if self._start:
            pygame.draw.circle(canvas, color, self._start, self._radius(pos), size)
        self._start = None
        self._current = None

    def draw_preview(self, surface, color, size):
        if self._start and self._current:
            pygame.draw.circle(surface, color, self._start, self._radius(self._current), size)


# ─────────────────────────────────────────────
#  Right Triangle
# ─────────────────────────────────────────────
class RightTriangleTool(Tool):
    name = "right_triangle"

    def __init__(self):
        self._start = None
        self._current = None

    def on_mouse_down(self, canvas, pos, color, size):
        self._start = pos
        self._current = pos

    def on_mouse_drag(self, canvas, pos, color, size):
        self._current = pos

    def _points(self, end):
        x0, y0 = self._start
        x1, y1 = end
        return [(x0, y0), (x0, y1), (x1, y1)]

    def on_mouse_up(self, canvas, pos, color, size):
        if self._start:
            pygame.draw.polygon(canvas, color, self._points(pos), size)
        self._start = None
        self._current = None

    def draw_preview(self, surface, color, size):
        if self._start and self._current:
            pygame.draw.polygon(surface, color, self._points(self._current), size)


# ─────────────────────────────────────────────
#  Equilateral Triangle
# ─────────────────────────────────────────────
class EquilateralTriangleTool(Tool):
    name = "equilateral_triangle"

    def __init__(self):
        self._start = None
        self._current = None

    def on_mouse_down(self, canvas, pos, color, size):
        self._start = pos
        self._current = pos

    def on_mouse_drag(self, canvas, pos, color, size):
        self._current = pos

    def _points(self, end):
        x0, y0 = self._start
        x1, y1 = end
        base = math.hypot(x1 - x0, y1 - y0)
        h = base * math.sqrt(3) / 2
        mid_x = (x0 + x1) / 2
        mid_y = (y0 + y1) / 2
        dx = x1 - x0
        dy = y1 - y0
        length = math.hypot(dx, dy) or 1
        nx = -dy / length
        ny = dx / length
        apex = (mid_x + nx * h, mid_y + ny * h)
        return [(x0, y0), (x1, y1), apex]

    def on_mouse_up(self, canvas, pos, color, size):
        if self._start:
            pygame.draw.polygon(canvas, color, self._points(pos), size)
        self._start = None
        self._current = None

    def draw_preview(self, surface, color, size):
        if self._start and self._current:
            pygame.draw.polygon(surface, color, self._points(self._current), size)


# ─────────────────────────────────────────────
#  Rhombus
# ─────────────────────────────────────────────
class RhombusTool(Tool):
    name = "rhombus"

    def __init__(self):
        self._start = None
        self._current = None

    def on_mouse_down(self, canvas, pos, color, size):
        self._start = pos
        self._current = pos

    def on_mouse_drag(self, canvas, pos, color, size):
        self._current = pos

    def _points(self, end):
        x0, y0 = self._start
        x1, y1 = end
        cx = (x0 + x1) / 2
        cy = (y0 + y1) / 2
        return [(cx, y0), (x1, cy), (cx, y1), (x0, cy)]

    def on_mouse_up(self, canvas, pos, color, size):
        if self._start:
            pygame.draw.polygon(canvas, color, self._points(pos), size)
        self._start = None
        self._current = None

    def draw_preview(self, surface, color, size):
        if self._start and self._current:
            pygame.draw.polygon(surface, color, self._points(self._current), size)


# ─────────────────────────────────────────────
#  Flood-Fill
# ─────────────────────────────────────────────
class FillTool(Tool):
    name = "fill"

    def on_mouse_down(self, canvas, pos, color, size):
        target_color = canvas.get_at(pos)[:3]
        fill_color = color[:3] if len(color) > 3 else color
        if target_color == fill_color:
            return

        w, h = canvas.get_size()
        visited = set()
        queue = deque([pos])

        while queue:
            cx, cy = queue.popleft()
            if (cx, cy) in visited:
                continue
            if cx < 0 or cx >= w or cy < 0 or cy >= h:
                continue
            if canvas.get_at((cx, cy))[:3] != target_color:
                continue
            canvas.set_at((cx, cy), fill_color)
            visited.add((cx, cy))
            queue.extend([(cx + 1, cy), (cx - 1, cy), (cx, cy + 1), (cx, cy - 1)])


# ─────────────────────────────────────────────
#  Text Tool
# ─────────────────────────────────────────────
class TextTool(Tool):
    name = "text"

    def __init__(self):
        self._pos = None
        self._text = ""
        self._active = False
        self._font = None

    def _get_font(self, size):
        font_size = {2: 16, 5: 24, 10: 36}.get(size, 20)
        if self._font is None or self._font.size("A")[1] != font_size:
            self._font = pygame.font.SysFont("monospace", font_size)
        return self._font

    def on_mouse_down(self, canvas, pos, color, size):
        self._pos = pos
        self._text = ""
        self._active = True

    def handle_key(self, event, canvas, color, size):
        """Call from main loop with pygame.KEYDOWN events."""
        if not self._active:
            return
        if event.key == pygame.K_RETURN:
            self._commit(canvas, color, size)
        elif event.key == pygame.K_ESCAPE:
            self._active = False
            self._text = ""
        elif event.key == pygame.K_BACKSPACE:
            self._text = self._text[:-1]
        else:
            if event.unicode and event.unicode.isprintable():
                self._text += event.unicode

    def _commit(self, canvas, color, size):
        if self._pos and self._text:
            font = self._get_font(size)
            surf = font.render(self._text, True, color)
            canvas.blit(surf, self._pos)
        self._active = False
        self._text = ""

    def draw_preview(self, surface, color, size):
        if self._active and self._pos:
            font = self._get_font(size)
            preview = self._text + "|"
            surf = font.render(preview, True, color)
            surface.blit(surf, self._pos)

    @property
    def is_active(self):
        return self._active