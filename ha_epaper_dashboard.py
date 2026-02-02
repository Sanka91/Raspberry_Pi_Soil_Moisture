import io
import random
import pandas as pd
from PIL import Image, ImageDraw, ImageFont
from datetime import datetime

# @service
def df_to_image_pyscript(df, title, filename="WaterMonitoring.png"):

    # 1. Setup dimensions and styling
    img_width = 800
    img_height = 600
    cell_width_regular = 50
    cell_height = 30
    padding = 10
    y_start_header = 45
    y_start_table = 45

    font_semibold = ImageFont.truetype('fonts/Quicksand/static/Quicksand-SemiBold.ttf', size=10)
    font_bold = ImageFont.truetype('fonts/Quicksand/static/Quicksand-Bold.ttf', size=15)

    # 2. Create a white background (Mode 'L' is 8-bit Black and White)
    img = Image.new('L', (img_width, img_height), color=255)
    draw = ImageDraw.Draw(img)

    # 3. Draw general header
    draw.text((180, 0), title, font=font_bold, fill=0)

    x_trailing_headers = 0
    # 4. Draw Header of dataframe
    for i, col in enumerate(df.columns):
        # First 6 columns are regular width
        if i == 0:
            draw.text((padding + i * cell_width_regular, y_start_header),
                      str(col),
                      font=font_semibold, fill=0)
            x_trailing_headers += padding + i * cell_width_regular
        if i == 1:
            x_trailing_headers += padding + cell_width_regular + 80
            draw.text((x_trailing_headers, y_start_header), str(col),font=font_semibold, fill=0)
        if 2 <= i <= 6:
            x_trailing_headers += padding + cell_width_regular
            draw.text((x_trailing_headers, y_start_header), str(col), font=font_semibold, fill=0)
        if i == 7:
            x_trailing_headers += padding + cell_width_regular + 150
            draw.text((x_trailing_headers, y_start_header),
                                    str(col),
                                    font=font_semibold, fill=0)

        # Draw a horizontal line under header row
        draw.line([(padding, y_start_header + padding * 2),
                   (img_width - padding, y_start_header + padding * 2)],
                  fill=0, width=3)

    # 5. Draw Rows
    for row_idx, row in enumerate(df.values):
        x_trailing_rows = 0
        for col_idx, value in enumerate(row):
            y = y_start_table + padding + (row_idx + 1) * cell_height
            # First 6 columns are regular width
            if col_idx == 0:
                x_trailing_rows += padding + col_idx * cell_width_regular
            if col_idx == 1:
                x_trailing_rows += padding + cell_width_regular + 80
            if 2 <= col_idx <= 6:
                x_trailing_rows += padding + cell_width_regular
            if col_idx == 7:
                x_trailing_rows += padding + cell_width_regular + 150

            draw.text((x_trailing_rows, y), str(value), font=font_semibold, fill=0)

    # 6. Save the image
    img.save(filename)


def helloworld():


    plant_names = ["{}".format(random.choice(["Sauerkirsche","Basilikum", "Ananasminze", "Aronia", "Stachelbeere"])) for i in range(16)]
    starts_ts = pd.Timestamp("2026-02-01 08:30:00")
    example_dates = pd.date_range(start=starts_ts, periods=16, freq="h")
    example_people = ["Philipp", "Little P", "Grossvater", "Mama"]

    example_data = ["{} %".format(i*random.choice([8,23,5,6])) for i in range(16)]

    data = {
        "M T-24": example_data,
        "M T-8": example_data,
        "M T-4": example_data,
        "M T-2": example_data,
        "M T0": example_data,
        "Last watered": ["{}: {} @ {}".format(random.choice(example_people),
                                              random.choice(example_dates.strftime("%d.%m.%Y")),
                                             random.choice(example_dates.strftime("%H:%M")) ) for i in range(16)],
        "Last watered autom.": ["{} @ {}".format(random.choice(example_dates.strftime("%d.%m.%Y")),
                                             random.choice(example_dates.strftime("%H:%M")) ) for i in range(16)],

    }
    pd.set_option("display.max_columns", None)
    pd.set_option('display.expand_frame_repr', False)
    pd.set_option('display.width', 1000)
    df = pd.DataFrame(data, index=plant_names)
    df.index.name = "Plant Name"
    df.reset_index(inplace=True)

    df_title = "Plant Monitoring - Area 1, Last updated: {} @ {}".format(datetime.now().strftime("%d.%m.%Y"),
                      datetime.now().strftime("%H:%M"))

    df_to_image_pyscript(df, df_title, filename="Plant_Monitoring_Area1.png")


if __name__ == "__main__":
    helloworld()
