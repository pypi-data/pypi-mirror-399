import math

class Shape:
    def __init__(self, size, chars):
        self.size = size
        self.chars = chars
        self.points = [] # list of (x, y, z, char_index)
        self.generate_points()

    def generate_points(self):
        raise NotImplementedError

    def add_point(self, x, y, z, char_idx):
        self.points.append((x, y, z, char_idx))

class Cube(Shape):
    def generate_points(self):
        half = self.size / 2
        step = 0.6 # Adjust density
        
        # Ranges
        rng = []
        val = -half
        while val <= half:
            rng.append(val)
            val += step
            
        for i in rng:
            for j in rng:
                # Front, Back
                self.add_point(i, j, -half, 0)
                self.add_point(half, j, i, 1) # Rot 90
                self.add_point(-half, j, -i, 2)
                self.add_point(-i, -half, -j, 3)
                self.add_point(i, half, j, 4)
                self.add_point(i, j, half, 5)

class Line(Shape):
    def generate_points(self):
        # Cylindrical representation of a line
        # Height from -size to size
        # Radius is small relative to size
        
        radius = max(1, self.size / 8.0)
        height_half = self.size
        step = 0.5
        
        # Sides
        # Iterate circumference
        circumference = 2 * math.pi * radius
        # Number of points along circumference
        radial_steps = int(circumference / step * 1.5) 
        if radial_steps < 8: radial_steps = 8
        
        angle_step = 2 * math.pi / radial_steps
        
        # Vertical strip
        z = -height_half
        while z <= height_half:
            for i in range(radial_steps):
                theta = i * angle_step
                x = radius * math.cos(theta)
                y = radius * math.sin(theta)
                self.add_point(x, y, z, i % len(self.chars))
            z += step
            
        # Caps (Top and Bottom filled circles)
        r = 0
        while r <= radius:
            radial_sub_steps = int(2 * math.pi * r / step * 1.5)
            if radial_sub_steps < 1: radial_sub_steps = 1
            sub_angle_step = 2 * math.pi / radial_sub_steps
            
            for i in range(radial_sub_steps):
                theta = i * sub_angle_step
                x = r * math.cos(theta)
                y = r * math.sin(theta)
                self.add_point(x, y, -height_half, 0)
                self.add_point(x, y, height_half, 1)
            r += step

class Pyramid(Shape):
    def generate_points(self):
        # Square Base
        half = self.size / 2
        height = self.size 
        step = 0.6
        
        # Base
        rng = []
        val = -half
        while val <= half:
            rng.append(val)
            val += step
            
        for i in rng:
            for j in rng:
                self.add_point(i, j, -height/2, 0) # Base at z = -height/2
        
        # Faces
        apex_z = height/2
        base_z = -height/2
        
        # Iterate z from base to apex
        z_step = step
        z = base_z
        while z <= apex_z:
            progress = (z - base_z) / height # 0 to 1
            if progress >= 1: break 
            
            current_half = half * (1 - progress)
            
            w_start = -current_half
            w_end = current_half
            w = w_start
            while w <= w_end:
                # 4 sides
                self.add_point(w, w_start, z, 1)
                self.add_point(w, w_end, z, 2)
                self.add_point(w_start, w, z, 3)
                self.add_point(w_end, w, z, 4)
                w += step
            z += z_step

class Prism(Shape):
    def __init__(self, size, chars, sides):
        self.sides = sides
        super().__init__(size, chars)

    def generate_points(self):
        radius = self.size / 1.5 
        half_height = self.size / 2
        step = 0.5
        
        # Generate vertices of N-gon
        angles = []
        for i in range(self.sides):
            angles.append(2 * math.pi * i / self.sides)
        angles.append(0) # Wrap around for iteration
        
        # Draw Sides
        for i in range(self.sides):
            theta1 = angles[i]
            theta2 = angles[i+1]
            
            x1 = radius * math.cos(theta1)
            y1 = radius * math.sin(theta1)
            x2 = radius * math.cos(theta2)
            y2 = radius * math.sin(theta2)
            
            dist = math.sqrt((x2-x1)**2 + (y2-y1)**2)
            steps_h = int(dist / step) + 1
            
            for k in range(steps_h + 1):
                t = k / steps_h if steps_h > 0 else 0
                cx = x1 + (x2 - x1) * t
                cy = y1 + (y2 - y1) * t
                
                # Vertical strip
                z = -half_height
                while z <= half_height:
                    self.add_point(cx, cy, z, i % len(self.chars))
                    z += step
                    
        # Caps
        r = 0
        while r <= radius:
            for i in range(self.sides):
                theta1 = angles[i]
                theta2 = angles[i+1]
                x1 = r * math.cos(theta1)
                y1 = r * math.sin(theta1)
                x2 = r * math.cos(theta2)
                y2 = r * math.sin(theta2)
                
                dist = math.sqrt((x2-x1)**2 + (y2-y1)**2)
                steps_edge = int(dist / step) + 1
                for k in range(steps_edge + 1):
                     t = k / steps_edge if steps_edge > 0 else 0
                     px = x1 + (x2 - x1) * t
                     py = y1 + (y2 - y1) * t
                     self.add_point(px, py, -half_height, (self.sides) % len(self.chars))
                     self.add_point(px, py, half_height, (self.sides + 1) % len(self.chars))
            r += step
