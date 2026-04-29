import math
import sys

import pygame


WIDTH = 900
HEIGHT = 640
TOOLBAR_HEIGHT = 82
CANVAS_TOP = TOOLBAR_HEIGHT
FPS = 60

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (210, 214, 220)
DARK_GRAY = (69, 75, 85)
BLUE = (45, 113, 235)

COLORS = [
    ("Black", (0, 0, 0)),
    ("Red", (229, 57, 53)),
    ("Green", (67, 160, 71)),
    ("Blue", (30, 136, 229)),
    ("Yellow", (251, 192, 45)),
    ("Purple", (142, 68, 173)),
    ("Orange", (245, 124, 0)),
]

TOOLS = [
    ("brush", "Brush"),
    ("rectangle", "Rectangle"),
    ("circle", "Circle"),
    ("eraser", "Eraser"),
]


def main():
    pygame.init()
    pygame.display.set_caption("Paint")
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    clock = pygame.time.Clock()
    font = pygame.font.SysFont(None, 24)
    small_font = pygame.font.SysFont(None, 20)

    canvas = pygame.Surface((WIDTH, HEIGHT - CANVAS_TOP))
    canvas.fill(WHITE)

    tool = "brush"
    color = BLACK
    brush_size = 5
    eraser_size = 24
    drawing = False
    start_pos = None
    last_pos = None
    preview_pos = None

    toolbar_items = layout_toolbar()

    while True:
        pressed = pygame.key.get_pressed()
        alt_held = pressed[pygame.K_LALT] or pressed[pygame.K_RALT]
        ctrl_held = pressed[pygame.K_LCTRL] or pressed[pygame.K_RCTRL]

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return
                if event.key == pygame.K_w and ctrl_held:
                    return
                if event.key == pygame.K_F4 and alt_held:
                    return
                if event.key == pygame.K_c and ctrl_held:
                    canvas.fill(WHITE)
                if event.key == pygame.K_LEFTBRACKET:
                    brush_size = max(1, brush_size - 1)
                    eraser_size = max(4, eraser_size - 2)
                if event.key == pygame.K_RIGHTBRACKET:
                    brush_size = min(80, brush_size + 1)
                    eraser_size = min(120, eraser_size + 2)
                if event.key == pygame.K_b:
                    tool = "brush"
                elif event.key == pygame.K_r:
                    tool = "rectangle"
                elif event.key == pygame.K_o:
                    tool = "circle"
                elif event.key == pygame.K_e:
                    tool = "eraser"
                elif event.key == pygame.K_1:
                    color = COLORS[0][1]
                    tool = "brush"
                elif event.key == pygame.K_2:
                    color = COLORS[1][1]
                    tool = "brush"
                elif event.key == pygame.K_3:
                    color = COLORS[2][1]
                    tool = "brush"
                elif event.key == pygame.K_4:
                    color = COLORS[3][1]
                    tool = "brush"
                elif event.key == pygame.K_5:
                    color = COLORS[4][1]
                    tool = "brush"
                elif event.key == pygame.K_6:
                    color = COLORS[5][1]
                    tool = "brush"
                elif event.key == pygame.K_7:
                    color = COLORS[6][1]
                    tool = "brush"

            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    pos = event.pos
                    clicked = toolbar_hit_test(pos, toolbar_items)
                    if clicked:
                        kind, value = clicked
                        if kind == "tool":
                            tool = value
                        elif kind == "color":
                            color = value
                            if tool == "eraser":
                                tool = "brush"
                        elif kind == "clear":
                            canvas.fill(WHITE)
                        continue

                    if is_on_canvas(pos):
                        drawing = True
                        start_pos = to_canvas_pos(pos)
                        last_pos = start_pos
                        preview_pos = start_pos
                        if tool == "brush":
                            pygame.draw.circle(canvas, color, start_pos, brush_size)
                        elif tool == "eraser":
                            pygame.draw.circle(canvas, WHITE, start_pos, eraser_size)

                elif event.button == 4:
                    brush_size = min(80, brush_size + 1)
                    eraser_size = min(120, eraser_size + 2)
                elif event.button == 5:
                    brush_size = max(1, brush_size - 1)
                    eraser_size = max(4, eraser_size - 2)

            if event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1 and drawing:
                    end_pos = clamp_canvas_pos(event.pos)
                    if tool == "rectangle":
                        draw_rectangle(canvas, start_pos, end_pos, color, brush_size)
                    elif tool == "circle":
                        draw_circle(canvas, start_pos, end_pos, color, brush_size)
                    drawing = False
                    start_pos = None
                    last_pos = None
                    preview_pos = None

            if event.type == pygame.MOUSEMOTION:
                if drawing:
                    current_pos = clamp_canvas_pos(event.pos)
                    preview_pos = current_pos
                    if tool == "brush":
                        draw_line_between(canvas, last_pos, current_pos, brush_size, color)
                        last_pos = current_pos
                    elif tool == "eraser":
                        draw_line_between(canvas, last_pos, current_pos, eraser_size, WHITE)
                        last_pos = current_pos

        screen.fill(GRAY)
        draw_toolbar(
            screen,
            toolbar_items,
            font,
            small_font,
            tool,
            color,
            brush_size,
            eraser_size,
        )
        screen.blit(canvas, (0, CANVAS_TOP))

        if drawing and tool in ("rectangle", "circle"):
            draw_preview(screen, tool, start_pos, preview_pos, color, brush_size)

        pygame.display.flip()
        clock.tick(FPS)


def layout_toolbar():
    items = []
    x = 12
    y = 14

    for tool_id, label in TOOLS:
        rect = pygame.Rect(x, y, 104, 38)
        items.append(("tool", tool_id, label, rect))
        x += rect.width + 8

    x += 10
    for label, color in COLORS:
        rect = pygame.Rect(x, y, 30, 30)
        items.append(("color", color, label, rect))
        x += rect.width + 7

    clear_rect = pygame.Rect(WIDTH - 112, y, 94, 38)
    items.append(("clear", "clear", "Clear", clear_rect))
    return items


def toolbar_hit_test(pos, toolbar_items):
    if pos[1] >= TOOLBAR_HEIGHT:
        return None

    for kind, value, _label, rect in toolbar_items:
        if rect.collidepoint(pos):
            return kind, value
    return None


def draw_toolbar(
    screen,
    toolbar_items,
    font,
    small_font,
    selected_tool,
    selected_color,
    brush_size,
    eraser_size,
):
    pygame.draw.rect(screen, (244, 246, 248), (0, 0, WIDTH, TOOLBAR_HEIGHT))
    pygame.draw.line(screen, (172, 178, 187), (0, TOOLBAR_HEIGHT - 1), (WIDTH, TOOLBAR_HEIGHT - 1), 2)

    for kind, value, label, rect in toolbar_items:
        if kind == "tool":
            active = value == selected_tool
            button_color = (226, 235, 255) if active else WHITE
            border_color = BLUE if active else (152, 158, 168)
            pygame.draw.rect(screen, button_color, rect, border_radius=6)
            pygame.draw.rect(screen, border_color, rect, width=2, border_radius=6)
            draw_centered_text(screen, font, label, DARK_GRAY, rect)
        elif kind == "color":
            pygame.draw.rect(screen, value, rect, border_radius=4)
            border_width = 4 if value == selected_color else 2
            border_color = BLUE if value == selected_color else DARK_GRAY
            pygame.draw.rect(screen, border_color, rect, width=border_width, border_radius=4)
        elif kind == "clear":
            pygame.draw.rect(screen, WHITE, rect, border_radius=6)
            pygame.draw.rect(screen, (152, 158, 168), rect, width=2, border_radius=6)
            draw_centered_text(screen, font, label, DARK_GRAY, rect)

    hint = "Keys: B brush, R rectangle, O circle, E eraser, 1-7 colors, [/] size, Ctrl+C clear"
    size_label = f"Brush {brush_size}px  Eraser {eraser_size}px"
    hint_surface = small_font.render(hint, True, DARK_GRAY)
    size_surface = small_font.render(size_label, True, DARK_GRAY)
    screen.blit(hint_surface, (14, 58))
    screen.blit(size_surface, (WIDTH - size_surface.get_width() - 18, 58))


def draw_centered_text(screen, font, text, color, rect):
    surface = font.render(text, True, color)
    screen.blit(surface, surface.get_rect(center=rect.center))


def draw_line_between(surface, start, end, width, color):
    dx = start[0] - end[0]
    dy = start[1] - end[1]
    iterations = max(abs(dx), abs(dy))

    if iterations == 0:
        pygame.draw.circle(surface, color, start, width)
        return

    for i in range(iterations + 1):
        progress = i / iterations
        aprogress = 1 - progress
        x = int(aprogress * start[0] + progress * end[0])
        y = int(aprogress * start[1] + progress * end[1])
        pygame.draw.circle(surface, color, (x, y), width)


def draw_rectangle(surface, start, end, color, width):
    rect = rect_from_points(start, end)
    pygame.draw.rect(surface, color, rect, width=max(1, width))


def draw_circle(surface, start, end, color, width):
    rect = rect_from_points(start, end)

    radius = min(rect.width, rect.height) // 2
    center = (rect.left + rect.width // 2, rect.top + rect.height // 2)

    if radius > 0:
        pygame.draw.circle(surface, color, center, radius, width=max(1, width))

def draw_preview(screen, tool, start, end, color, width):
    if start is None or end is None:
        return

    preview_start = from_canvas_pos(start)
    preview_end = from_canvas_pos(end)

    if tool == "rectangle":
        pygame.draw.rect(screen, color, rect_from_points(preview_start, preview_end), width=max(1, width))
    elif tool == "circle":
        rect = rect_from_points(preview_start, preview_end)
        radius = min(rect.width, rect.height) // 2
        center = (rect.left + rect.width // 2, rect.top + rect.height // 2)

        if radius > 0:
            pygame.draw.circle(screen, color, center, radius, width=max(1, width))

def rect_from_points(start, end):
    left = min(start[0], end[0])
    top = min(start[1], end[1])
    width = abs(start[0] - end[0])
    height = abs(start[1] - end[1])
    return pygame.Rect(left, top, width, height)


def is_on_canvas(pos):
    return pos[1] >= CANVAS_TOP


def to_canvas_pos(pos):
    return pos[0], pos[1] - CANVAS_TOP


def from_canvas_pos(pos):
    return pos[0], pos[1] + CANVAS_TOP


def clamp_canvas_pos(pos):
    x = max(0, min(WIDTH - 1, pos[0]))
    y = max(CANVAS_TOP, min(HEIGHT - 1, pos[1]))
    return x, y - CANVAS_TOP


if __name__ == "__main__":
    try:
        main()
    finally:
        pygame.quit()
        sys.exit()