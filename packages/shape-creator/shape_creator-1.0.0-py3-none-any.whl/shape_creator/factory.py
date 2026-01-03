from .shapes import Cube, Pyramid, Line, Prism

class ShapeFactory:
    @staticmethod
    def create_shape(shape_type, size, chars):
        """
        Creates a shape based on the type identifier.
        1: Cube
        2: Pyramid
        3: Line
        4-8: Prisms (Pentagon to Nonagon)
        """
        if shape_type == 1:
            return Cube(size, chars)
        elif shape_type == 2:
            return Pyramid(size, chars)
        elif shape_type == 3:
            return Line(size, chars)
        elif 4 <= shape_type <= 8:
            sides = shape_type + 1
            return Prism(size, chars, sides)
        else:
            return None
