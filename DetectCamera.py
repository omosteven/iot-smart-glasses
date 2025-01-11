import pixy
from pixy import BlockArray, Pixy2

# Initialize Pixy
pixy.init()

# Get Pixy version
version = pixy.get_version()

# Print Pixy firmware version
if version is not None:
    print("Pixy firmware version:", version)
else:
    print("Failed to get Pixy firmware version.")

# Set up blocks for detecting objects
blocks = BlockArray(100)

print("Detecting objects...")
while True:
    count = pixy.ccc_get_blocks(100, blocks)
    if count > 0:
        print(f"Detected {count} blocks:")
        for i in range(count):
            print(f"  Block {i}: Signature {blocks[i].signature}, X {blocks[i].x}, Y {blocks[i].y}")
    else:
        print("No objects detected.")
