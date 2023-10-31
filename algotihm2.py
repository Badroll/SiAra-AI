def char_height(filename, black_pixel_threshold = 1000):
    import cv2
    import numpy as np

    image = cv2.imread(f"{filename}", cv2.IMREAD_GRAYSCALE)
    inverted_image = image

    black_pixel_counts = [np.sum(inverted_image[y, :] == 0) for y in range(inverted_image.shape[0])]
    blackH = []
    for y, count in enumerate(black_pixel_counts):
        if count > black_pixel_threshold:
            blackH.append(y)

    height = blackH[-1] - blackH[0]
    print(f"tinggi karakter utama : {height}")

    print("============ char_height =========================")
    print(height)
    print("==============================================\n\n")
    return height


def resize_uniform(filename, char_height, maximum_char_height = 500):
    from PIL import Image

    try:
        maximum_char_height = 500
        overheight = char_height - maximum_char_height
        ratioW = 4
        ratioH = 3
        aug_name = "MC"

        input_image = Image.open(f"{filename}")
        hmax = overheight * 5
        vmax = hmax * ratioH / ratioW
        if "L" in aug_name:
            margin_left = 0
            margin_right = hmax
        if "M" in aug_name:
            margin_left = hmax / 2
            margin_right = hmax / 2
        if "R" in aug_name:
            margin_left = hmax
            margin_right = 0
        if "T" in aug_name:
            margin_top = 0
            margin_bottom = vmax
        if "C" in aug_name:
            margin_top = vmax / 2
            margin_bottom = vmax / 2
        if "B" in aug_name:
            margin_top = vmax
            margin_bottom = 0

        original_width, original_height = input_image.size

        new_width = 4000
        oversize = True
        while (oversize):
            new_height = int(new_width * (vmax / hmax))
            output_width = new_width + margin_left + margin_right
            output_height = new_height + margin_top + margin_bottom
            
            if output_width > 4000:
                new_width -= 100
            else:
                oversize = False

        resized_image = input_image.resize((new_width, new_height))

        output_shape = (int(output_width), int(output_height))
        output_image = Image.new("RGB", output_shape, "white")

        left = margin_left
        top = margin_top
        output_image.paste(resized_image, (int(left), int(top)))

        output_image.save(f"{filename}")

        input_image.close()
        resized_image.close()
        output_image.close()

        r = {
            "shape" : output_shape[::-1],
            "overheight" : overheight,
            "margin L T R B" : (margin_left, margin_top, margin_right, margin_bottom),
        }
        print("============ resize_uniform =========================")
        print(r)
        return r
    except Exception as e:
        print("============ resize_uniform =========================")
        print(e)
        return e