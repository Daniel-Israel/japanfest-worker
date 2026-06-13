from PIL import Image, ImageDraw, ImageFont


def _create_img(order_id):
    width = 576
    height = 180
    order_id = "#" + str(order_id) + "\n"

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
            order["total_price"]
        )
        printer.text(txt)
        printer.ln()
        for item in order["items"]:
            txt = "{}x - {} R$ {}\n".format(
                item["quantity"], item["product_name"], item["unit_price"]
            )
            printer.text(txt)
            for customization in item["customizations"]:
                txt = "----{}".format(customization)
                printer.text(txt)
        printer.cut()

    else:
        for item in order["items"]:
            txt = "{}x - {}".format(
                item["quantity"], item["product_name"]
            )
            printer.text(txt)
            for customization in item["customizations"]:
                txt = "----{}".format(customization)
                printer.text(txt)
        printer.cut()
    return "Via {} do pedido {} impresso".format(
        receipt_type,
        order["order_id"]
    )