import base64
import os

def save_image(image_data, filename):
    """Save base64 image data to a file."""
    if not os.path.exists('images'):
        os.makedirs('images')
    
    filepath = os.path.join('images', filename)
    with open(filepath, 'wb') as f:
        f.write(base64.b64decode(image_data))

# Save the images from the conversation
# The base64 data for each image would go here
print("Please save the following images to the images directory:")
print("1. images/fighter.webp - Human fighter with shield and sword")
print("2. images/rogue.webp - Elven rogue/fighter with multiple weapons")
print("3. images/wizard.webp - White-haired wizard in blue and gold robes with medallions")
print("4. images/goblin.webp - Goblin warrior with curved blade")
print("5. images/ogre.webp - Large ogre with crude weapon")
print("6. images/wyvern.webp - Blue dragon/wyvern")

# Note: All images must be in .webp format
# The game will automatically scale them to the appropriate size (100x100 pixels)
# Ensure Pygame is installed with extended image support for .webp format
# If you have issues loading .webp images, you may need to install additional system libraries

# Note: Save the wizard image as wizard.png in the images directory
# The image should be saved at a reasonable resolution (recommended 256x256 or larger)
# The game will automatically scale it to the appropriate size (100x100 pixels) 