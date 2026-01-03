import math
import sys
import time

class Renderer:
    def __init__(self, width=80, height=24):
        self.width = width
        self.height = height
        self.rotation_speed_a = 0.02
        self.rotation_speed_b = 0.02
        self.rotation_speed_c = 0.01

    def render_loop(self, shape):
        chars = shape.chars
        points = shape.points
        
        A, B, C = 0.0, 0.0, 0.0
        
        try:
            while True:
                z_buffer = [-float('inf')] * (self.width * self.height)
                buffer = [' '] * (self.width * self.height)
                
                cosA, sinA = math.cos(A), math.sin(A)
                cosB, sinB = math.cos(B), math.sin(B)
                cosC, sinC = math.cos(C), math.sin(C)
                
                for (px, py, pz, char_idx) in points:
                    # Rotate X
                    y = py * cosA - pz * sinA
                    z = py * sinA + pz * cosA
                    x = px
                    
                    # Rotate Y
                    xx = x * cosB + z * sinB
                    zz = -x * sinB + z * cosB
                    yy = y
                    
                    # Rotate Z
                    xxx = xx * cosC - yy * sinC
                    yyy = xx * sinC + yy * cosC
                    zzz = zz
                    
                    distance = 60 + shape.size * 1.5
                    if zzz + distance == 0: continue
                    ooz = 1 / (zzz + distance)
                    
                    xp = int(self.width / 2 + 2 * self.width * ooz * xxx)
                    yp = int(self.height / 2 + self.width * ooz * yyy)
                    
                    idx = xp + yp * self.width
                    if 0 <= idx < self.width * self.height:
                        if ooz > z_buffer[idx]:
                            z_buffer[idx] = ooz
                            buffer[idx] = chars[char_idx % len(chars)]
                
                # Print
                sys.stdout.write("\x1b[H")
                for k in range(self.width * self.height):
                    if k % self.width == 0 and k != 0:
                        sys.stdout.write("\n")
                    sys.stdout.write(buffer[k])
                sys.stdout.flush()
                
                A += self.rotation_speed_a
                B += self.rotation_speed_b
                C += self.rotation_speed_c
                
                time.sleep(0.01) # Small sleep to prevent 100% CPU usage
                
        except KeyboardInterrupt:
            print("\nExiting animation...")
