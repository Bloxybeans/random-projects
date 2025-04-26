import tkinter as tk

# Game class for handling game logic
class Game:
    def __init__(self, root):
        self.root = root
        self.canvas = tk.Canvas(root, width=800, height=600, bg="white")
        self.canvas.pack()
        
        # Game state
        self.game_objects = []
        self.keys = set()
        self.running = False

        # Button to start the game
        self.run_button = tk.Button(root, text="Run", command=self.start_game)
        self.run_button.pack()

        # Draggable object (player)
        self.player = GameObject(self.canvas, 100, 100, 50, 50, "blue")
        self.game_objects.append(self.player)

        # Mouse drag functionality
        self.dragging = None
        self.canvas.bind("<ButtonPress-1>", self.on_drag_start)
        self.canvas.bind("<B1-Motion>", self.on_drag_motion)
        self.canvas.bind("<ButtonRelease-1>", self.on_drag_end)
        
        self.setup()

    def setup(self):
        """Set up the initial game environment."""
        self.canvas.create_rectangle(100, 100, 200, 200, fill="blue")  # Debugging static rectangle
        self.canvas.create_rectangle(300, 300, 400, 400, fill="green")  # Another static rectangle

    def on_drag_start(self, event):
        """Start dragging the object when clicked."""
        for obj in self.game_objects:
            if obj.is_hit(event.x, event.y):
                self.dragging = obj
                break

    def on_drag_motion(self, event):
        """Move the object while dragging."""
        if self.dragging:
            self.dragging.move_to(event.x, event.y)
            self.render()

    def on_drag_end(self, event):
        """End the dragging."""
        self.dragging = None

    def start_game(self):
        """Start the game when the Run button is clicked."""
        self.running = True
        self.run_button.config(state=tk.DISABLED)  # Disable the button once the game is running
        self.game_loop()

    def game_loop(self):
        """The main game loop."""
        if self.running:
            self.update()
            self.render()
            self.root.after(16, self.game_loop)  # ~60 FPS

    def update(self):
        """Update game logic, such as player movement."""
        pass  # We will keep this empty for now as we are focusing on dragging

    def render(self):
        """Render all game objects to the canvas."""
        self.canvas.delete("all")  # Clear the canvas
        for obj in self.game_objects:
            obj.draw()

# GameObject class for representing objects in the game
class GameObject:
    def __init__(self, canvas, x, y, width, height, color):
        self.canvas = canvas
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.color = color
        self.id = None

    def is_hit(self, x, y):
        """Check if the mouse click is inside the object."""
        return self.x <= x <= self.x + self.width and self.y <= y <= self.y + self.height

    def move_to(self, x, y):
        """Move the object to a new position."""
        self.x = x - self.width // 2  # Center the object on the mouse
        self.y = y - self.height // 2

    def draw(self):
        """Draw the object on the canvas."""
        if not self.id:
            self.id = self.canvas.create_rectangle(self.x, self.y, self.x + self.width, self.y + self.height, fill=self.color)
        else:
            self.canvas.coords(self.id, self.x, self.y, self.x + self.width, self.y + self.height)

# Main function to set up the game window
def main():
    root = tk.Tk()
    root.title("2D Game Engine with Draggable Assets")
    game = Game(root)
    root.mainloop()

if __name__ == "__main__":
    main()
