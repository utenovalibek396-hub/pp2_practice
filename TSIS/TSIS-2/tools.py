"""
tools.py — Drawing tools for the Paint application (TSIS 2)
Implements: Pencil, Line, Rectangle, Circle, Eraser, Flood-Fill, Text,
            Square, Right Triangle, Equilateral Triangle, Rhombus
"""

import pygame  # Import the main Pygame library for graphics and input handling
import math  # Import the math module for geometric and trigonometric calculations
from collections import deque  # Import deque for an efficient queue in the flood-fill algorithm


# ---------------------------------------------
#  Base class
# ---------------------------------------------
class Tool:  # Define the abstract base class that all drawing tools will inherit from
    """Abstract base for every drawing tool."""

    name = "base"  # Default name identifier for the tool

    def on_mouse_down(self, canvas, pos, color, size):  # Method called when the mouse button is first pressed
        pass

    def on_mouse_drag(self, canvas, pos, color, size):  # Method called when the mouse is moved while held down
        pass

    def on_mouse_up(self, canvas, pos, color, size):  # Method called when the mouse button is released
        pass

    def draw_preview(self, surface, color, size):  # Method to draw temporary graphics on a preview overlay
        """Draw a live preview overlay (called every frame while dragging)."""
        pass


# ---------------------------------------------
#  Pencil (freehand)
# ---------------------------------------------
class PencilTool(Tool):  # Define a tool for freehand drawing
    name = "pencil"

    def __init__(self):  # Initialize the pencil tool
        self._last_pos = None  # Variable to store the previous mouse position to connect lines

    def on_mouse_down(self, canvas, pos, color, size):  # Start drawing when the mouse is clicked
        self._last_pos = pos  # Set the initial position
        pygame.draw.circle(canvas, color, pos, size // 2)  # Draw a single dot at the starting point

    def on_mouse_drag(self, canvas, pos, color, size):  # Continue drawing as the mouse moves
        if self._last_pos:  # If there was a previous position recorded
            pygame.draw.line(canvas, color, self._last_pos, pos, size)  # Draw a line from the last point to current
        self._last_pos = pos  # Update the last position to the current mouse location

    def on_mouse_up(self, canvas, pos, color, size):  # Stop drawing when the mouse is released
        self._last_pos = None  # Reset the last position


# ---------------------------------------------
#  Eraser
# ---------------------------------------------
class EraserTool(Tool):  # Define a tool to remove content by painting with the background color
    name = "eraser"

    def __init__(self):  # Initialize the eraser tool
        self._last_pos = None  # Store the last position to ensure continuous erasing lines

    def on_mouse_down(self, canvas, pos, color, size):  # Start erasing on mouse click
        self._last_pos = pos  # Set the starting eraser position
        pygame.draw.circle(canvas, (255, 255, 255), pos, size * 2)  # Draw a large white circle at the start

    def on_mouse_drag(self, canvas, pos, color, size):  # Continue erasing as mouse moves
        if self._last_pos:  # If dragging has started
            pygame.draw.line(canvas, (255, 255, 255), self._last_pos, pos, size * 4)  # Draw thick white lines
        self._last_pos = pos  # Update position for the next frame

    def on_mouse_up(self, canvas, pos, color, size):  # Stop erasing on mouse release
        self._last_pos = None  # Reset tracking


# ---------------------------------------------
#  Straight Line
# ---------------------------------------------
class LineTool(Tool):  # Define a tool to draw straight lines between two points
    name = "line"

    def __init__(self):  # Initialize line tool state
        self._start = None  # Starting point of the line
        self._current = None  # Current (end) point for previewing

    def on_mouse_down(self, canvas, pos, color, size):  # Set the start of the line
        self._start = pos  # Fix the origin point
        self._current = pos  # Set current position to origin initially

    def on_mouse_drag(self, canvas, pos, color, size):  # Update end point during drag
        self._current = pos  # Continuously update current position for preview

    def on_mouse_up(self, canvas, pos, color, size):  # Permanently draw the line on release
        if self._start:  # If a start point exists
            pygame.draw.line(canvas, color, self._start, pos, size)  # Commit the line to the canvas
        self._start = None  # Reset state
        self._current = None

    def draw_preview(self, surface, color, size):  # Show the line while the user is still dragging
        if self._start and self._current:  # If active
            pygame.draw.line(surface, color, self._start, self._current, size)  # Draw to the preview surface


# ---------------------------------------------
#  Rectangle
# ---------------------------------------------
class RectangleTool(Tool):  # Define a tool to draw rectangles
    name = "rectangle"

    def __init__(self):  # Initialize rectangle states
        self._start = None  # Top-left or initial corner
        self._current = None  # Opposite corner during drag

    def on_mouse_down(self, canvas, pos, color, size):  # Start rectangle at mouse click
        self._start = pos
        self._current = pos

    def on_mouse_drag(self, canvas, pos, color, size):  # Update rectangle size during drag
        self._current = pos

    def on_mouse_up(self, canvas, pos, color, size):  # Draw the final rectangle
        if self._start:  # Ensure a starting point was set
            rect = pygame.Rect(  # Calculate the standard rectangle area using min/abs
                min(self._start[0], pos[0]),
                min(self._start[1], pos[1]),
                abs(pos[0] - self._start[0]),
                abs(pos[1] - self._start[1]),
            )
            pygame.draw.rect(canvas, color, rect, size)  # Draw final rect with chosen thickness
        self._start = None
        self._current = None

    def draw_preview(self, surface, color, size):  # Show rectangle outline during drag
        if self._start and self._current:
            rect = pygame.Rect(  # Dynamically calculate rect for preview
                min(self._start[0], self._current[0]),
                min(self._start[1], self._current[1]),
                abs(self._current[0] - self._start[0]),
                abs(self._current[1] - self._start[1]),
            )
            pygame.draw.rect(surface, color, rect, size)  # Draw on the transparent preview surface


# ---------------------------------------------
#  Square
# ---------------------------------------------
class SquareTool(Tool):  # Define a tool to draw equilateral rectangles (squares)
    name = "square"

    def __init__(self):  # Initialize square states
        self._start = None
        self._current = None

    def on_mouse_down(self, canvas, pos, color, size):  # Start square
        self._start = pos
        self._current = pos

    def on_mouse_drag(self, canvas, pos, color, size):  # Update square size
        self._current = pos

    def _make_rect(self, end):  # Internal logic to force equal width and height
        dx = end[0] - self._start[0]  # Difference in X
        dy = end[1] - self._start[1]  # Difference in Y
        side = min(abs(dx), abs(dy))  # Use the smaller delta to maintain square proportions
        x = self._start[0] if dx >= 0 else self._start[0] - side  # Calculate X based on direction
        y = self._start[1] if dy >= 0 else self._start[1] - side  # Calculate Y based on direction
        return pygame.Rect(x, y, side, side)  # Return the square-constrained Rect

    def on_mouse_up(self, canvas, pos, color, size):  # Commit square to canvas
        if self._start:
            pygame.draw.rect(canvas, color, self._make_rect(pos), size)
        self._start = None
        self._current = None

    def draw_preview(self, surface, color, size):  # Show square during drag
        if self._start and self._current:
            pygame.draw.rect(surface, color, self._make_rect(self._current), size)


# ---------------------------------------------
#  Circle
# ---------------------------------------------
class CircleTool(Tool):  # Define a tool to draw circles from center to radius
    name = "circle"

    def __init__(self):  # Initialize circle states
        self._start = None
        self._current = None

    def on_mouse_down(self, canvas, pos, color, size):  # Fix center point
        self._start = pos
        self._current = pos

    def on_mouse_drag(self, canvas, pos, color, size):  # Update radius
        self._current = pos

    def _radius(self, end):  # Calculate distance between start and end using hypotenuse
        dx = end[0] - self._start[0]
        dy = end[1] - self._start[1]
        return max(1, int(math.hypot(dx, dy)))  # Ensure radius is at least 1 pixel

    def on_mouse_up(self, canvas, pos, color, size):  # Draw final circle
        if self._start:
            pygame.draw.circle(canvas, color, self._start, self._radius(pos), size)
        self._start = None
        self._current = None

    def draw_preview(self, surface, color, size):  # Preview circle outline
        if self._start and self._current:
            pygame.draw.circle(surface, color, self._start, self._radius(self._current), size)


# ---------------------------------------------
#  Right Triangle
# ---------------------------------------------
class RightTriangleTool(Tool):  # Define a tool for right-angled triangles
    name = "right_triangle"

    def __init__(self):  # Initialize states
        self._start = None
        self._current = None

    def on_mouse_down(self, canvas, pos, color, size):  # Fix the origin corner
        self._start = pos
        self._current = pos

    def on_mouse_drag(self, canvas, pos, color, size):  # Update size
        self._current = pos

    def _points(self, end):  # Define the three vertices of the right triangle
        x0, y0 = self._start
        x1, y1 = end
        return [(x0, y0), (x0, y1), (x1, y1)]  # Corner, vertical leg, horizontal leg

    def on_mouse_up(self, canvas, pos, color, size):  # Draw the triangle on release
        if self._start:
            pygame.draw.polygon(canvas, color, self._points(pos), size)
        self._start = None
        self._current = None

    def draw_preview(self, surface, color, size):  # Live preview of the triangle shape
        if self._start and self._current:
            pygame.draw.polygon(surface, color, self._points(self._current), size)


# ---------------------------------------------
#  Equilateral Triangle
# ---------------------------------------------
class EquilateralTriangleTool(Tool):  # Define a tool for equal-sided triangles
    name = "equilateral_triangle"

    def __init__(self):  # Initialize states
        self._start = None
        self._current = None

    def on_mouse_down(self, canvas, pos, color, size):  # Fix the base starting point
        self._start = pos
        self._current = pos

    def on_mouse_drag(self, canvas, pos, color, size):  # Update base length and apex
        self._current = pos

    def _points(self, end):  # Calculate vertices using geometry
        x0, y0 = self._start
        x1, y1 = end
        base = math.hypot(x1 - x0, y1 - y0)  # Length of the base side
        h = base * math.sqrt(3) / 2  # Height calculation for equilateral triangle
        mid_x = (x0 + x1) / 2  # Midpoint of the base (X)
        mid_y = (y0 + y1) / 2  # Midpoint of the base (Y)
        dx = x1 - x0  # Change in X
        dy = y1 - y0  # Change in Y
        length = math.hypot(dx, dy) or 1  # Base vector length
        nx = -dy / length  # Normal vector X (90 degree rotation)
        ny = dx / length  # Normal vector Y (90 degree rotation)
        apex = (mid_x + nx * h, mid_y + ny * h)  # Apex point shifted from midpoint by height
        return [(x0, y0), (x1, y1), apex]

    def on_mouse_up(self, canvas, pos, color, size):  # Commit equilateral triangle
        if self._start:
            pygame.draw.polygon(canvas, color, self._points(pos), size)
        self._start = None
        self._current = None

    def draw_preview(self, surface, color, size):  # Preview triangle during drag
        if self._start and self._current:
            pygame.draw.polygon(surface, color, self._points(self._current), size)


# ---------------------------------------------
#  Rhombus
# ---------------------------------------------
class RhombusTool(Tool):  # Define a tool to draw diamond shapes
    name = "rhombus"

    def __init__(self):  # Initialize states
        self._start = None
        self._current = None

    def on_mouse_down(self, canvas, pos, color, size):  # Start rhombus bounding box
        self._start = pos
        self._current = pos

    def on_mouse_drag(self, canvas, pos, color, size):  # Update box
        self._current = pos

    def _points(self, end):  # Calculate the four diamond tips based on the mouse box
        x0, y0 = self._start
        x1, y1 = end
        cx = (x0 + x1) / 2  # Horizontal center
        cy = (y0 + y1) / 2  # Vertical center
        return [(cx, y0), (x1, cy), (cx, y1), (x0, cy)]  # Top, right, bottom, left tips

    def on_mouse_up(self, canvas, pos, color, size):  # Draw final rhombus
        if self._start:
            pygame.draw.polygon(canvas, color, self._points(pos), size)
        self._start = None
        self._current = None

    def draw_preview(self, surface, color, size):  # Preview rhombus during drag
        if self._start and self._current:
            pygame.draw.polygon(surface, color, self._points(self._current), size)


# ---------------------------------------------
#  Flood-Fill
# ---------------------------------------------
class FillTool(Tool):  # Define a tool to fill enclosed areas with color
    name = "fill"

    def on_mouse_down(self, canvas, pos, color, size):  # Start fill algorithm on click
        target_color = canvas.get_at(pos)[:3]  # Detect color of the pixel clicked
        fill_color = color[:3] if len(color) > 3 else color  # Ensure fill color format is correct
        if target_color == fill_color:  # Do nothing if colors are already identical
            return

        w, h = canvas.get_size()  # Get canvas dimensions
        visited = set()  # Track processed pixels to avoid infinite loops
        queue = deque([pos])  # Use a queue for Breadth-First Search (BFS)

        while queue:  # Process pixels while queue is not empty
            cx, cy = queue.popleft()  # Get the next coordinate to check
            if (cx, cy) in visited:  # Skip if already handled
                continue
            if cx < 0 or cx >= w or cy < 0 or cy >= h:  # Skip if outside canvas bounds
                continue
            if canvas.get_at((cx, cy))[:3] != target_color:  # Skip if pixel color doesn't match target
                continue
            canvas.set_at((cx, cy), fill_color)  # Change pixel to the new color
            visited.add((cx, cy))  # Mark as visited
            queue.extend([(cx + 1, cy), (cx - 1, cy), (cx, cy + 1), (cx, cy - 1)])  # Add neighbors


# ---------------------------------------------
#  Text Tool
# ---------------------------------------------
class TextTool(Tool):  # Define a tool to type text onto the canvas
    name = "text"

    def __init__(self):  # Initialize text tool variables
        self._pos = None  # Text insertion point
        self._text = ""  # String being typed
        self._active = False  # Is the tool currently in "typing mode"
        self._font = None  # Cached font object

    def _get_font(self, size):  # Determine font size based on the brush size setting
        font_size = {2: 16, 5: 24, 10: 36}.get(size, 20)  # Map brush widths to font points
        if self._font is None or self._font.size("A")[1] != font_size:  # Rebuild font if size changed
            self._font = pygame.font.SysFont("monospace", font_size)  # Use monospace system font
        return self._font

    def on_mouse_down(self, canvas, pos, color, size):  # Set position and activate typing
        self._pos = pos
        self._text = ""
        self._active = True

    def handle_key(self, event, canvas, color, size):  # Capture keyboard input
        """Call from main loop with pygame.KEYDOWN events."""
        if not self._active:  # Only handle keys if active
            return
        if event.key == pygame.K_RETURN:  # Commit text to canvas on Enter
            self._commit(canvas, color, size)
        elif event.key == pygame.K_ESCAPE:  # Cancel typing on Escape
            self._active = False
            self._text = ""
        elif event.key == pygame.K_BACKSPACE:  # Remove last character
            self._text = self._text[:-1]
        else:  # Append printable characters to the string
            if event.unicode and event.unicode.isprintable():
                self._text += event.unicode

    def _commit(self, canvas, color, size):  # Permanently render text onto the canvas
        if self._pos and self._text:
            font = self._get_font(size)
            surf = font.render(self._text, True, color)  # Create a surface from the text
            canvas.blit(surf, self._pos)  # Stamp the text surface onto the main canvas
        self._active = False
        self._text = ""

    def draw_preview(self, surface, color, size):  # Show the text + cursor before committing
        if self._active and self._pos:
            font = self._get_font(size)
            preview = self._text + "|"  # Add a visual cursor
            surf = font.render(preview, True, color)
            surface.blit(surf, self._pos)  # Draw to preview overlay

    @property
    def is_active(self):  # Read-only access to activation state
        return self._active