"""
Make a printable A4 sheet of QR tags for Tag-to-Wear.

Usage:
    pip install "qrcode[pil]"
    python make_qr.py https://YOUR-USERNAME.github.io/tag-to-wear/

Output:
    qr-sheet.png   (A4 at 200 dpi, 3 x 3 grid: tags 1-8 and the practice tag 0)
    qr-links.txt   (the 9 links, in case you would rather use an online QR generator)

Print at 100% scale (no "fit to page"). Each QR code prints about 4 cm wide.
Cut the tags out and tape or string one to each prop garment.
"""
import sys
import qrcode
from PIL import Image, ImageDraw, ImageFont

# Keep these in step with ITEMS in index.html.
ITEMS = [
    (0, "Practice tag", None),
    (1, "Black hoodie", 80),
    (2, "Denim jacket", 120),
    (3, "White tee", 25),
    (4, "Jeans", 90),
    (5, "Flannel shirt", 60),
    (6, "Sneakers", 110),
    (7, "Beanie", 20),
    (8, "Raincoat", 150),
]

DPI = 200
A4 = (int(8.27 * DPI), int(11.69 * DPI))
COLS, ROWS = 3, 3
QR_PX = int(4.0 / 2.54 * DPI)  # 4 cm


def font(size):
    for name in ("DejaVuSans-Bold.ttf", "Arial Bold.ttf", "Arial.ttf", "Helvetica.ttc"):
        try:
            return ImageFont.truetype(name, size)
        except OSError:
            continue
    return ImageFont.load_default()


def main():
    if len(sys.argv) != 2 or not sys.argv[1].startswith("http"):
        sys.exit("Usage: python make_qr.py https://YOUR-USERNAME.github.io/tag-to-wear/")
    base = sys.argv[1].split("?")[0]
    if not base.endswith("/") and not base.endswith(".html"):
        base += "/"

    sheet = Image.new("RGB", A4, "white")
    draw = ImageDraw.Draw(sheet)
    cell_w, cell_h = A4[0] // COLS, A4[1] // ROWS
    f_name, f_small = font(34), font(26)

    links = []
    for n, (item_id, name, price) in enumerate(ITEMS):
        url = f"{base}?item={item_id}"
        links.append(f"{item_id}\t{name}\t{url}")
        qr = qrcode.QRCode(error_correction=qrcode.constants.ERROR_CORRECT_M, box_size=10, border=2)
        qr.add_data(url)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white").convert("RGB").resize((QR_PX, QR_PX), Image.NEAREST)

        col, row = n % COLS, n // COLS
        x0, y0 = col * cell_w, row * cell_h
        # cut line around each tag
        draw.rectangle([x0 + 12, y0 + 12, x0 + cell_w - 12, y0 + cell_h - 12], outline="#999999", width=2)
        sheet.paste(img, (x0 + (cell_w - QR_PX) // 2, y0 + 40))
        label = f"{item_id}  {name}" if item_id else name
        draw.text((x0 + cell_w // 2, y0 + 40 + QR_PX + 30), label, fill="black", font=f_name, anchor="mm")
        if price is not None:
            draw.text((x0 + cell_w // 2, y0 + 40 + QR_PX + 75), f"${price}", fill="#444444", font=f_small, anchor="mm")

    sheet.save("qr-sheet.png", dpi=(DPI, DPI))
    with open("qr-links.txt", "w") as fh:
        fh.write("\n".join(links) + "\n")
    print("Wrote qr-sheet.png and qr-links.txt")
    print("First link:", links[1].split("\t")[2])


if __name__ == "__main__":
    main()
