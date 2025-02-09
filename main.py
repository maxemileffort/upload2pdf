import os
import math
from PIL import Image, ImageDraw, ImageFont

def find_images(directory=".", extensions=(".jpg", ".png", ".jpeg")):
    """Finds all images in the given directory matching the specified extensions."""
    return [os.path.join(directory, f) for f in os.listdir(directory) if f.lower().endswith(extensions)]

def gen_brand_label():
    # Create a blank image for the text
    text_img = Image.new("RGBA", (200, 50), (255, 255, 255, 0))  # Adjust size as needed
    text_draw = ImageDraw.Draw(text_img)

    # Define text and font
    brand_label = "storystills.com"
    font = ImageFont.truetype("arial.ttf", 30)  # Use your preferred font and size

    # Draw text onto the blank image
    text_draw.text((0, 0), brand_label, fill=(0, 0, 0), font=font)

    # Rotate the text image
    rotated_text = text_img.rotate(90, expand=True)

    # Open your template image
    template = Image.new("RGB", (45, 250), (255, 255, 255))

    # Define the position to paste the rotated text
    x, y = 5, 25  # Adjust coordinates as needed

    # Paste the rotated text onto the template
    template.paste(rotated_text, (x, y), rotated_text)

    # Save or show the result
    # template.show()  # Or 
    # template.save("brand_label.png")
    return template

def create_story_stills_template(image_paths, output_prefix="story_stills_page"):
    """Creates 8x10 templates with 2x3 images in octagonal frames, generating multiple pages if needed."""
    page_width, page_height = 2400, 3000  # Page dimensions (8x10 inches at 300 DPI)
    image_size = 600  # 2x2 inches at 300 DPI
    frame_size = image_size + 150  # 1/8 inch larger on all sides
    images_per_page = 6
    num_pages = math.ceil(len(image_paths) / images_per_page)
    positions = [(500, 450), (1900, 450), (500, 1350), (1900, 1350), (500, 2250), (1900, 2250)]
    output_files = []
    
    # Load a font (default PIL font or specify a ttf file)
    try:
        font = ImageFont.truetype("arial.ttf", 25)
    except IOError:
        font = ImageFont.load_default()

    for page in range(num_pages):
        template = Image.new("RGB", (page_width, page_height), (255, 255, 255))
        draw = ImageDraw.Draw(template)
        start_idx = page * images_per_page
        end_idx = min(start_idx + images_per_page, len(image_paths))
        page_images = image_paths[start_idx:end_idx]
        images = [Image.open(img).convert("RGB").resize((image_size, image_size), Image.Resampling.LANCZOS) for img in page_images]

        # Create a dictionary comprehension to associate img_order_nums with images
        img_dict = {pi: [img, pi.split('_')[0]] for pi, img in zip(page_images, images)}

        for pos in positions:
            try:
                order_num = list(img_dict.values())[positions.index(pos)][1]  # Accessing the order number
            except IndexError:
                continue
            img = img_dict[list(img_dict.keys())[positions.index(pos)]][0]  # Retrieve the image from the dictionary
            x, y = pos
            
            frame = Image.new("RGB", (frame_size, frame_size), (255, 255, 255))
            mask = Image.new("L", (frame_size, frame_size), 0)
            frame_draw = ImageDraw.Draw(mask)
            offset = 49
            points = [
                (offset, 0), (frame_size - offset, 0),
                (frame_size, offset), (frame_size, frame_size - offset),
                (frame_size - offset, frame_size), (offset, frame_size),
                (0, frame_size - offset), (0, offset)
            ]
            frame_draw.polygon(points, fill=255)
            template_points = [(x + px - frame_size // 2, y + py - frame_size // 2) for px, py in points]
            draw.polygon(template_points, outline=(0, 0, 0), width=2)

            # Paste the image onto the frame
            frame.paste(img, ((frame_size - image_size) // 2, (frame_size - image_size) // 2))
            template.paste(frame, (x - frame_size // 2, y - frame_size // 2), mask)

            # Draw the order number below the image inside the frame
            text_position = (x - frame_size // 2 + (frame_size - frame_size // 4) // 2, 
                             y - frame_size // 2 + image_size + 120)  # Adjust Y position for spacing
            draw.text(text_position, str(order_num), fill=(0, 0, 0), font=font)

            # Add brand_label
            brand_label = gen_brand_label()
            label_position = (x - frame_size // 2 + 20, 
                             y - frame_size // 5 )  # Adjust Y position for spacing
            template.paste(brand_label, label_position)

        output_file = f"{output_prefix}{page + 1}.png"
        template.save(output_file)
        output_files.append(output_file)
        print(f"Page {page + 1} saved as {output_file}")
    
    return output_files

def convert_to_pdf(image_files, output_pdf="story_stills.pdf"):
    """Converts a list of image files into a single PDF."""
    if not image_files:
        print("No images to convert to PDF.")
        return
    
    images = [Image.open(img).convert("RGB") for img in image_files]
    pdf_path = os.path.join(os.getcwd(), output_pdf)
    images[0].save(pdf_path, save_all=True, append_images=images[1:])
    print(f"PDF created: {pdf_path}")

if __name__ == "__main__":
    images = find_images()
    if images:
        generated_images = create_story_stills_template(images)
        convert_to_pdf(generated_images)
        print(f"Created {math.ceil(len(images) / 6)} pages with {len(images)} images and compiled them into a PDF.")
        [os.remove(f) for f in generated_images]
    else:
        print("No images found in the current directory.")
