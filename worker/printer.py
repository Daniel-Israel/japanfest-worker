import time
from os import getenv

from PIL import Image, ImageDraw, ImageFont


def _format_num(num):
    return f"{num:.2f}".replace('.', ',')


def _create_img(order_id):
    width = 576
    height = 180
    order_id = "#" + str(order_id)

    img = Image.new("RGB", (width, height), "black")
    draw = ImageDraw.Draw(img)

    font = ImageFont.truetype(
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        140
    )

    bbox = draw.textbbox((0, 0), order_id, font=font)

    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]

    x = (width - text_width) // 2
    y = (height - text_height) // 2

    draw.text(
        (x, y),
        order_id,
        fill="white",
        font=font
    )
    return img


def print_receipt(printer, order):
    order_id = _create_img(order["order_id"])
    receipt_type = order["receipt_type"]

    printer.set(
        align="center",
        double_width=True,
        double_height=True,
        bold=True,
        density=8,
        font='a'
    )

    if receipt_type != "client":
        time.sleep(int(getenv("SLEEP", 5)))
        printer.text("\n\n\n\n\n")
        printer.ln(2)

    printer.text("Festival do Japão")
    printer.ln()
    printer.text("Barraquinha de Fukushima\n")
    printer.ln()
    printer.image(order_id)
    printer.ln()

    printer.set(
        align="left",
        double_width=False,
        double_height=False,
        bold=False,
        density=4,
        font='b'
    )

    if receipt_type == "client":
        txt = "Pagamento via {}: R$ {}".format(
            order["payment_method"],
            _format_num(order["total_price"])
        )
        printer.text(txt)
        printer.ln()
        for item in order["items"]:
            txt = "{}x - {} R$ {}\n".format(
                item["quantity"],
                item["product_name"],
                _format_num(item["unit_price"])
            )
            printer.text(txt)
            for customization in item["customizations"]:
                txt = "   ----{}\n".format(customization)
                printer.text(txt)
        printer.ln()
        printer.cut()

    else:
        for item in order["items"]:
            txt = "{}x - {}\n".format(
                item["quantity"], item["product_name"]
            )
            printer.text(txt)
            for customization in item["customizations"]:
                txt = "   ----{}\n".format(customization)
                printer.text(txt)
        printer.text("\n")
        printer.ln()
        
        printer.cut()
    return "Via {} do pedido {} impresso".format(
        receipt_type,
        order["order_id"]
    )
