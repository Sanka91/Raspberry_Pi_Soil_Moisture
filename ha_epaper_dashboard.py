import io
import random
import matplotlib.pyplot as plt
import pandas as pd
from PIL import Image
from plottable import Table, ColumnDefinition

@service
def helloworld():

    plant_names = ["Plant: {}".format(i) for i in range(2)]
    starts_ts = pd.Timestamp("2026-02-01 08:30:00")
    example_dates = pd.date_range(start=starts_ts, periods=2, freq="h")
    formatted_ts = example_dates.strftime("%d.%m.%Y %H:%M")
    example_people = ["Philipp", "Little P", "Grossvater", "Mama"]

    data = {
        "M T-24": [sensor.moisture_sensor, 4],
        "M T-8": [i*random.choice([1,5,6,2]) for i in range(2)],
        "M T-4": [i*random.choice([1,5,6,2]) for i in range(2)],
        "M T-2": [i*random.choice([1,5,6,2]) for i in range(2)],
        "M T0": [i*2 for i in range(2)],
        "Last watered": ["{} @ {}".format(random.choice(example_people),
                                             random.choice(formatted_ts) ) for i in range(2)],
        "Last watered automatically": [random.choice(formatted_ts) for i in range(2)],

    }
    pd.set_option("display.max_columns", None)
    pd.set_option('display.expand_frame_repr', False)
    pd.set_option('display.width', 1000)
    df = pd.DataFrame(data, index=plant_names)
    df.index.name = "Plant Name"

    col_defs = [
        ColumnDefinition(name="Plant Name", width=0.25, textprops={'ha': 'center'}),
        ColumnDefinition(name="M T-24", width=0.25, textprops={'ha': 'center'}),
        ColumnDefinition(name="M T-8", width=0.25, textprops={'ha': 'center'}),
        ColumnDefinition(name="M T-4", width=0.25, textprops={'ha': 'center'}),
        ColumnDefinition(name="M T-2", width=0.25, textprops={'ha': 'center'}),
        ColumnDefinition(name="M T0", width=0.25, textprops={'ha': 'center'}),
        ColumnDefinition(name="Last watered", width=0.5, textprops={'ha': 'center'}),
        ColumnDefinition(name="Last watered automatically", width=0.5, textprops={'ha': 'center'}),
    ]

    fig, ax = plt.subplots(figsize=(16, 4))

    # 3. Create the table
    tab = Table(df,
                column_definitions=col_defs,
                 )

    log.info(tab)
    # 2. Save the plot to a "virtual file" (memory) instead of the disk
    # This is faster on a Raspberry Pi
    buf = io.BytesIO()
    plt.savefig(buf, format='png', bbox_inches='tight', dpi=300)
    buf.seek(0)

    # 3. Open with Pillow and convert
    img = Image.open(buf)

    # "L" = Grayscale (256 shades of gray)
    # "1" = Pure Black and White (Dithered, high contrast)
    bw_img = img.convert("1")

    # 4. Save the final B&W file
    bw_img.save("table_bw.png")

    plt.close(fig) # Always close fig to save RAM on your Pi!


if __name__ == "__main__":
    helloworld()