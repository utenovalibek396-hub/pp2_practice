import sys  # Import the system-specific parameters and functions module
import datetime  # Import the module for manipulating dates and times
import pygame  # Import the Pygame library for game development and graphics

from tools import (  # Import specific tool classes from a local tools module
    PencilTool, LineTool, RectangleTool, CircleTool, EraserTool,
    FillTool, TextTool, SquareTool, RightTriangleTool,
    EquilateralTriangleTool, RhombusTool,
)

# -----------------------------
# SCREEN
# -----------------------------
SCREEN_W, SCREEN_H = 900, 600  # Define the width and height of the main window
TOOLBAR_H = 60  # Define the height of the toolbar area at the top
CANVAS_TOP = TOOLBAR_H  # Set the starting Y-coordinate for the drawing canvas
CANVAS_H = SCREEN_H - TOOLBAR_H  # Calculate the remaining height for the canvas

BG_COLOR      = (30, 30, 35)  # Define the background color for the application
TOOLBAR_COLOR = (22, 22, 28)  # Define the background color for the toolbar
CANVAS_BG     = (255, 255, 255)  # Define the background color for the drawing canvas (white)
TEXT_COLOR    = (220, 220, 230)  # Define the primary color for UI text elements
HOVER_COLOR   = (55, 55, 65)  # Define the color for buttons when the mouse hovers over them
ACTIVE_COLOR  = (70, 110, 200)  # Define the color for the currently selected tool or size

BRUSH_SIZES = {1: 2, 2: 5, 3: 10}  # Map UI size levels (1, 2, 3) to actual pixel widths

PALETTE = [  # Define a list of RGB tuples representing the available color palette
    (0,0,0), (80,80,80), (160,160,160), (255,255,255),
    (220,50,50), (230,130,50), (230,210,50), (60,190,80),
    (50,160,230), (80,80,220), (160,60,200), (220,80,150),
    (100,50,20), (30,100,80), (0,60,120), (200,170,100),
]

TOOL_DEFS = [  # Define a list of tuples containing tool shortcuts, names, and class instances
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

KEY_MAP = {  # Map keyboard keys to the corresponding tool names for quick switching
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

def draw_rounded_rect(surface, color, rect, radius=6):  # Helper function to draw a rectangle with rounded corners
    pygame.draw.rect(surface, color, rect, border_radius=radius)


# -----------------------------
# TOOLBAR
# -----------------------------
class Toolbar:  # Class to manage the creation and rendering of the UI toolbar
    BTN_W, BTN_H = 44, 34  # Set standard width and height for tool buttons
    BTN_GAP = 3  # Set the horizontal gap between adjacent buttons
    SIDE_PAD = 6  # Set the padding from the left edge of the screen

    def __init__(self, font_small, font_key):  # Initialize the toolbar with fonts and build layouts
        self.font_small = font_small  # Store font for tool names
        self.font_key = font_key  # Store font for shortcut keys
        self._build()  # Call the build method to define UI regions

    def _build(self):  # Define hitboxes for buttons, sizes, and colors
        self.tool_rects = {}  # Dictionary to store rectangles and shortcuts for tools
        self.size_rects = {}  # Dictionary to store rectangles for brush size selectors
        self.palette_rects = {}  # Dictionary to store rectangles for the color palette

        x = self.SIDE_PAD  # Set the initial X position starting with padding
        cy = TOOLBAR_H // 2  # Calculate the vertical center of the toolbar

        for shortcut, name, _ in TOOL_DEFS:  # Iterate through tool definitions to create button rects
            rect = pygame.Rect(x, cy - self.BTN_H // 2, self.BTN_W, self.BTN_H)  # Create a centered Rect
            self.tool_rects[name] = (rect, shortcut)  # Store the Rect and shortcut string
            x += self.BTN_W + self.BTN_GAP  # Advance the X position for the next button

        x += 10  # Add extra spacing before the brush size section

        for k in (1,2,3):  # Create hitboxes for the three brush size options
            rect = pygame.Rect(x, cy - 14, 28, 28)  # Define a square hitbox for the size selector
            self.size_rects[k] = rect  # Store the Rect with its corresponding size key
            x += 32  # Advance X for the next size selector

        x += 10  # Add extra spacing before the color palette section

        sw = 18  # Set the width of each individual color swatch
        gap = 2  # Set the gap between color swatches
        per_row = 10  # Define how many color swatches to display per row

        for i, color in enumerate(PALETTE):  # Iterate through the PALETTE to create swatch hitboxes
            r = i // per_row  # Calculate the row index based on the current swatch index
            c = i % per_row  # Calculate the column index based on the current swatch index
            self.palette_rects[color] = pygame.Rect(  # Define and store the swatch Rect
                x + c*(sw+gap),
                cy - 18 + r*(sw+gap),
                sw, sw
            )

    def draw(self, surface, active_tool, active_size, active_color):  # Render the entire toolbar onto the screen
        pygame.draw.rect(surface, TOOLBAR_COLOR, (0,0,SCREEN_W,TOOLBAR_H))  # Draw the toolbar background

        for name,(rect,short) in self.tool_rects.items():  # Render each tool button
            col = ACTIVE_COLOR if name == active_tool else HOVER_COLOR  # Highlight the active tool
            draw_rounded_rect(surface, col, rect)  # Draw the button background
            surface.blit(self.font_small.render(name, True, TEXT_COLOR),  # Render and draw the tool name text
                         self.font_small.render(name, True, TEXT_COLOR).get_rect(center=rect.center))
            surface.blit(self.font_key.render(short, True, (150,200,255)),  # Render and draw the shortcut key text
                         self.font_key.render(short, True, (150,200,255)).get_rect(center=(rect.centerx, rect.centery-10)))

        for k,rect in self.size_rects.items():  # Render each brush size selector
            col = ACTIVE_COLOR if k == active_size else HOVER_COLOR  # Highlight the active size
            draw_rounded_rect(surface, col, rect)  # Draw the size button background
            pygame.draw.circle(surface, TEXT_COLOR, rect.center, k*2)  # Draw a circle representing the brush size

        for col,rect in self.palette_rects.items():  # Render each color swatch
            draw_rounded_rect(surface, col, rect, 3)  # Draw the colored swatch rectangle
            if col == active_color:  # If the color is active, draw a white border around it
                pygame.draw.rect(surface, (255,255,255), rect, 1)


# -----------------------------
# MAIN
# -----------------------------
def main():  # Main execution function for the drawing application
    pygame.init()  # Initialize all imported pygame modules
    screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))  # Create the main application window
    clock = pygame.time.Clock()  # Create a clock object to manage the frame rate

    font_ui = pygame.font.SysFont("arial", 11, bold=True)  # Load the primary font for UI text
    font_key = pygame.font.SysFont("consolas", 10, bold=True)  # Load a monospaced font for shortcut labels

    canvas = pygame.Surface((SCREEN_W, CANVAS_H))  # Create a separate surface for the drawing area
    canvas.fill(CANVAS_BG)  # Initialize the canvas with the background color (white)

    preview = pygame.Surface((SCREEN_W, CANVAS_H), pygame.SRCALPHA)  # Create a transparent surface for tool previews

    toolbar = Toolbar(font_ui, font_key)  # Instantiate the Toolbar object

    tool_map = {n:t for _,n,t in TOOL_DEFS}  # Create a lookup dictionary mapping names to tool instances
    active = "Pencil"  # Set the default active tool name
    tool = tool_map[active]  # Get the default tool instance

    size = 2  # Set the default brush size level
    color = (0,0,0)  # Set the default drawing color (black)
    drawing = False  # Boolean flag to track if the user is currently drawing on the canvas

    def pos(p): return (p[0], p[1]-CANVAS_TOP)  # Helper to convert screen coordinates to canvas-local coordinates

    while True:  # Main application loop
        for e in pygame.event.get():  # Iterate through all pending events in the queue
            if e.type == pygame.QUIT:  # Check if the user closed the window
                pygame.quit()  # Uninitialize pygame
                sys.exit()  # Exit the script

            elif e.type == pygame.MOUSEBUTTONDOWN:  # Check for mouse click events
                p = e.pos  # Get the global position of the mouse click

                if p[1] < TOOLBAR_H:  # Logic for handling clicks inside the toolbar region
                    for n,(r,_) in toolbar.tool_rects.items():  # Check for collisions with tool buttons
                        if r.collidepoint(p):  # If a tool button is clicked
                            active = n  # Update the active tool name
                            tool = tool_map[n]  # Update the active tool instance

                    for k,r in toolbar.size_rects.items():  # Check for collisions with brush size selectors
                        if r.collidepoint(p):  # If a size selector is clicked
                            size = k  # Update the active size level

                    for c,r in toolbar.palette_rects.items():  # Check for collisions with color swatches
                        if r.collidepoint(p):  # If a color swatch is clicked
                            color = c  # Update the active drawing color

                else:  # Logic for handling clicks inside the drawing canvas region
                    drawing = True  # Set the drawing flag to True
                    tool.on_mouse_down(canvas, pos(p), color, BRUSH_SIZES[size])  # Trigger the tool's click logic

            elif e.type == pygame.MOUSEMOTION:  # Check for mouse movement events
                if drawing:  # Only trigger tool logic if the user is currently drawing
                    tool.on_mouse_drag(canvas, pos(e.pos), color, BRUSH_SIZES[size])  # Trigger the tool's drag logic

            elif e.type == pygame.MOUSEBUTTONUP:  # Check for mouse release events
                drawing = False  # Set the drawing flag to False
                tool.on_mouse_up(canvas, pos(e.pos), color, BRUSH_SIZES[size])  # Trigger the tool's release logic

        screen.fill(BG_COLOR)  # Clear the screen with the application background color
        screen.blit(canvas, (0, TOOLBAR_H))  # Draw the persistent drawing canvas onto the screen

        preview.fill((0,0,0,0))  # Clear the preview surface with transparency
        tool.draw_preview(preview, color, BRUSH_SIZES[size])  # Let the tool draw a temporary preview (like a line hint)
        screen.blit(preview, (0, TOOLBAR_H))  # Overlay the preview surface onto the screen

        toolbar.draw(screen, active, size, color)  # Render the UI toolbar on top of everything

        pygame.display.flip()  # Update the full display surface to the screen
        clock.tick(60)  # Maintain a consistent frame rate of 60 frames per second


if __name__ == "__main__":  # Entry point check
    main()  # Run the main function