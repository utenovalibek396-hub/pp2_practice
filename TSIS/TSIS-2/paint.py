import sys
import datetime
import pygame

from tools import (
    PencilTool, LineTool, RectangleTool, CircleTool, EraserTool,
    FillTool, TextTool, SquareTool, RightTriangleTool,
    EquilateralTriangleTool, RhombusTool,
)

# ─────────────────────────────
# SCREEN
# ─────────────────────────────
SCREEN_W, SCREEN_H = 900, 600
TOOLBAR_H = 60
CANVAS_TOP = TOOLBAR_H
CANVAS_H = SCREEN_H - TOOLBAR_H

BG_COLOR      = (30, 30, 35)
TOOLBAR_COLOR = (22, 22, 28)
CANVAS_BG     = (255, 255, 255)
TEXT_COLOR    = (220, 220, 230)
HOVER_COLOR   = (55, 55, 65)
ACTIVE_COLOR  = (70, 110, 200)

BRUSH_SIZES = {1: 2, 2: 5, 3: 10}

PALETTE = [
    (0,0,0), (80,80,80), (160,160,160), (255,255,255),
    (220,50,50), (230,130,50), (230,210,50), (60,190,80),
    (50,160,230), (80,80,220), (160,60,200), (220,80,150),
    (100,50,20), (30,100,80), (0,60,120), (200,170,100),
]

TOOL_DEFS = [
    ("P", "Pencil", PencilTool()),
    ("L", "Line", LineTool()),
    ("R", "Rect", RectangleTool()),
    ("C", "Circle", CircleTool()),
    ("S", "Square", SquareTool()),
    ("G", "R.Tri", RightTriangleTool()),
    ("Q", "Eq.Tri", EquilateralTriangleTool()),
    ("H", "Rhombus", RhombusTool()),
    ("E", "Eraser", EraserTool()),
    ("F", "Fill", FillTool()),
    ("T", "Text", TextTool()),
]

KEY_MAP = {
    pygame.K_p: "Pencil",
    pygame.K_l: "Line",
    pygame.K_r: "Rect",
    pygame.K_c: "Circle",
    pygame.K_s: "Square",
    pygame.K_g: "R.Tri",
    pygame.K_q: "Eq.Tri",
    pygame.K_h: "Rhombus",
    pygame.K_e: "Eraser",
    pygame.K_f: "Fill",
    pygame.K_t: "Text",
}

def draw_rounded_rect(surface, color, rect, radius=6):
    pygame.draw.rect(surface, color, rect, border_radius=radius)


# ─────────────────────────────
# TOOLBAR
# ─────────────────────────────
class Toolbar:
    BTN_W, BTN_H = 44, 34
    BTN_GAP = 3
    SIDE_PAD = 6

    def __init__(self, font_small, font_key):
        self.font_small = font_small
        self.font_key = font_key
        self._build()

    def _build(self):
        self.tool_rects = {}
        self.size_rects = {}
        self.palette_rects = {}

        x = self.SIDE_PAD
        cy = TOOLBAR_H // 2

        for shortcut, name, _ in TOOL_DEFS:
            rect = pygame.Rect(x, cy - self.BTN_H // 2, self.BTN_W, self.BTN_H)
            self.tool_rects[name] = (rect, shortcut)
            x += self.BTN_W + self.BTN_GAP

        x += 10

        for k in (1,2,3):
            rect = pygame.Rect(x, cy - 14, 28, 28)
            self.size_rects[k] = rect
            x += 32

        x += 10

        sw = 18
        gap = 2
        per_row = 10

        for i, color in enumerate(PALETTE):
            r = i // per_row
            c = i % per_row
            self.palette_rects[color] = pygame.Rect(
                x + c*(sw+gap),
                cy - 18 + r*(sw+gap),
                sw, sw
            )

    def draw(self, surface, active_tool, active_size, active_color):
        pygame.draw.rect(surface, TOOLBAR_COLOR, (0,0,SCREEN_W,TOOLBAR_H))

        for name,(rect,short) in self.tool_rects.items():
            col = ACTIVE_COLOR if name == active_tool else HOVER_COLOR
            draw_rounded_rect(surface, col, rect)
            surface.blit(self.font_small.render(name, True, TEXT_COLOR),
                         self.font_small.render(name, True, TEXT_COLOR).get_rect(center=rect.center))
            surface.blit(self.font_key.render(short, True, (150,200,255)),
                         self.font_key.render(short, True, (150,200,255)).get_rect(center=(rect.centerx, rect.centery-10)))

        for k,rect in self.size_rects.items():
            col = ACTIVE_COLOR if k == active_size else HOVER_COLOR
            draw_rounded_rect(surface, col, rect)
            pygame.draw.circle(surface, TEXT_COLOR, rect.center, k*2)

        for col,rect in self.palette_rects.items():
            draw_rounded_rect(surface, col, rect, 3)
            if col == active_color:
                pygame.draw.rect(surface, (255,255,255), rect, 1)


# ─────────────────────────────
# MAIN
# ─────────────────────────────
def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))
    clock = pygame.time.Clock()

    font_ui = pygame.font.SysFont("arial", 11, bold=True)
    font_key = pygame.font.SysFont("consolas", 10, bold=True)

    canvas = pygame.Surface((SCREEN_W, CANVAS_H))
    canvas.fill(CANVAS_BG)

    preview = pygame.Surface((SCREEN_W, CANVAS_H), pygame.SRCALPHA)

    toolbar = Toolbar(font_ui, font_key)

    tool_map = {n:t for _,n,t in TOOL_DEFS}
    active = "Pencil"
    tool = tool_map[active]

    size = 2
    color = (0,0,0)
    drawing = False

    def pos(p): return (p[0], p[1]-CANVAS_TOP)

    while True:
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            elif e.type == pygame.MOUSEBUTTONDOWN:
                p = e.pos

                if p[1] < TOOLBAR_H:
                    for n,(r,_) in toolbar.tool_rects.items():
                        if r.collidepoint(p):
                            active = n
                            tool = tool_map[n]

                    for k,r in toolbar.size_rects.items():
                        if r.collidepoint(p):
                            size = k

                    for c,r in toolbar.palette_rects.items():
                        if r.collidepoint(p):
                            color = c

                else:
                    drawing = True
                    tool.on_mouse_down(canvas, pos(p), color, BRUSH_SIZES[size])

            elif e.type == pygame.MOUSEMOTION:
                if drawing:
                    tool.on_mouse_drag(canvas, pos(e.pos), color, BRUSH_SIZES[size])

            elif e.type == pygame.MOUSEBUTTONUP:
                drawing = False
                tool.on_mouse_up(canvas, pos(e.pos), color, BRUSH_SIZES[size])

        screen.fill(BG_COLOR)
        screen.blit(canvas, (0, TOOLBAR_H))

        preview.fill((0,0,0,0))
        tool.draw_preview(preview, color, BRUSH_SIZES[size])
        screen.blit(preview, (0, TOOLBAR_H))

        toolbar.draw(screen, active, size, color)

        pygame.display.flip()
        clock.tick(60)


if __name__ == "__main__":
    main()