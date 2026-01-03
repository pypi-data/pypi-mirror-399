import sys
from .utils import get_valid_input, clear_screen
from .factory import ShapeFactory
from .renderer import Renderer

def main():
    print("Welcome to Terminal Shape Creator 3000")
    print("Select a shape:")
    print("1. Cube")
    print("2. Pyramid (Square Base)")
    print("3. Line")
    print("4. Pentagon Prism")
    print("5. Hexagon Prism")
    print("6. Heptagon Prism")
    print("7. Octagon Prism")
    print("8. Nonagon Prism")
    
    choice = get_valid_input("Enter choice (1-8): ", 1, 8)
    size = get_valid_input("Enter size (4-50): ", 4, 50)
    
    special_chars = ['@', '#', '$', '%', '&', '*', '+', '=', '-', ':']
    
    # Use Factory to create shape
    shape = ShapeFactory.create_shape(choice, size, special_chars)
    
    if shape:
        clear_screen()
        renderer = Renderer()
        renderer.render_loop(shape)
    else:
        print("Error creating shape.")

if __name__ == "__main__":
    main()
