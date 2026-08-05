import os
import zlib
import struct

def create_png(width, height, color_rgb=(2, 132, 199)):
    """Generate a valid PNG image byte array without external dependencies."""
    r, g, b = color_rgb
    raw_data = bytearray()
    
    for y in range(height):
        raw_data.append(0) # Filter type 0 (None)
        for x in range(width):
            # Draw a subtle inner rounded square / arrow border
            cx, cy = width // 2, height // 2
            dx, dy = abs(x - cx), abs(y - cy)
            
            if dx < width * 0.4 and dy < height * 0.4:
                # Arrow symbol color (white/cyan)
                raw_data.extend([255, 255, 255])
            else:
                # Dark background color #121826 (18, 24, 38)
                raw_data.extend([18, 24, 38])
                
    compressed = zlib.compress(raw_data)
    
    def chunk(tag, data):
        return struct.pack('>I', len(data)) + tag + data + struct.pack('>I', zlib.crc32(tag + data) & 0xffffffff)

    header = b'\x89PNG\r\n\x1a\n'
    ihdr = struct.pack('>IIBBBBB', width, height, 8, 2, 0, 0, 0)
    
    return header + chunk(b'IHDR', ihdr) + chunk(b'IDAT', compressed) + chunk(b'IEND', b'')

def generate_all_icons():
    root = os.path.dirname(os.path.abspath(__file__))
    assets_dir = os.path.join(root, "frontend", "assets", "runtime")
    os.makedirs(assets_dir, exist_ok=True)
    
    sizes = [72, 96, 128, 144, 152, 167, 180, 192, 384, 512]
    
    print("[ICONS] Generating multi-resolution PWA icons...")
    for sz in sizes:
        png_bytes = create_png(sz, sz)
        out_path = os.path.join(assets_dir, f"icon-{sz}.png")
        with open(out_path, "wb") as f:
            f.write(png_bytes)
        print(f"  [OK] Generated {out_path} ({sz}x{sz})")
        
    # Generate special icon aliases
    maskable_path = os.path.join(assets_dir, "maskable-icon.png")
    apple_path = os.path.join(assets_dir, "apple-touch-icon.png")
    favicon_path = os.path.join(root, "frontend", "favicon.ico")
    
    with open(maskable_path, "wb") as f: f.write(create_png(512, 512))
    with open(apple_path, "wb") as f: f.write(create_png(180, 180))
    with open(favicon_path, "wb") as f: f.write(create_png(32, 32))
    
    print("  [OK] Generated maskable-icon.png, apple-touch-icon.png, and favicon.ico")
    print("[SUCCESS] PWA Icon Suite generated cleanly!")

if __name__ == "__main__":
    generate_all_icons()
