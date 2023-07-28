from PIL import Image
import glob
import os

# Function to merge and save images as layers in a TIFF file
def merge_and_save_as_layers(base_name):
    o_file = f"{base_name}_o.tif"
    r_file = f"{base_name}_r.tif"
    le_file = f"{base_name}_le.tif"
    be_file = f"{base_name}_be.tif"
    te_file = f"{base_name}_te.tif"
    re_file = f"{base_name}_re.tif"

    try:
        # Check if all necessary files exist
        required_files = [o_file, r_file, le_file, be_file, te_file, re_file]
        if all(os.path.isfile(file) and Image.open(file).mode == 'RGB' for file in required_files):
          # Open all images and convert to RGB mode if needed
            te_img = Image.open(te_file).convert('RGBA')
            le_img = Image.open(le_file).convert('RGBA')
            o_img = Image.open(o_file).convert('RGBA')
            re_img = Image.open(re_file).convert('RGBA')
            be_img = Image.open(be_file).convert('RGBA')
            r_img = Image.open(r_file).convert('RGBA')

            # Extract DPI metadata from one of the original images
            dpi = o_img.info.get('dpi', (72, 72))

            # Calculate the canvas size to fit the fat cross motif
            canvas_width = max([img.width for img in [le_img, o_img, re_img]])
            canvas_height = max([img.height for img in [te_img, o_img, be_img, r_img]])

            # Create a blank canvas with an alpha channel (RGBA mode)
            canvas = Image.new('RGBA', (canvas_width * 3, canvas_height * 3), (0, 0, 0, 0))

            # Calculate the positioning based on the schema
            o_x, o_y = canvas_width, canvas_height // 2
            te_x, te_y = (canvas_width - te_img.width) // 2 + o_x, o_y - te_img.height
            le_x, le_y = o_x - le_img.width, o_y + o_img.height // 2 - le_img.height // 2
            re_x, re_y = o_x + o_img.width, o_y + o_img.height // 2 - re_img.height // 2
            be_x, be_y = (canvas_width - be_img.width) // 2 + o_x, o_y + o_img.height
            r_x, r_y = (canvas_width - r_img.width) // 2 + o_x, o_y + o_img.height + be_img.height

            # Position the images on the canvas
            canvas.paste(te_img, (te_x, te_y), mask=te_img)
            canvas.paste(le_img, (le_x, le_y), mask=le_img)
            canvas.paste(o_img, (o_x, o_y), mask=o_img)
            canvas.paste(re_img, (re_x, re_y), mask=re_img)
            canvas.paste(be_img, (be_x, be_y), mask=be_img)
            canvas.paste(r_img, (r_x, r_y), mask=r_img)

            # Add a black background layer at the back
            background = Image.new('RGBA', canvas.size, (0, 0, 0, 255))
            canvas = Image.alpha_composite(background, canvas)

            # Create the output folder if it doesn't exist
            output_folder = "merged_images"
            os.makedirs(output_folder, exist_ok=True)

            # Save the merged canvas as a multi-layered TIFF file with DPI metadata
            output_file = f"{output_folder}/{base_name}.tif"
            canvas.save(output_file, format="TIFF", dpi=dpi, compression="tiff_deflate", save_all=True, append_images=[te_img, le_img, o_img, re_img, be_img, r_img])

        else:
            print(f"Skipping {base_name} - Incomplete set of images or non-RGB format.")

    except Exception as e:
        print(f"Error processing {base_name}: {e}")

# Process each image object
for o_file in glob.glob("*_o.tif"):
    base_name = o_file[:-6]
    merge_and_save_as_layers(base_name)
