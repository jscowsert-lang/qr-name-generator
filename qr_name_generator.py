import streamlit as st
import pandas as pd
import qrcode
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont
from reportlab.lib.pagesizes import letter, inch
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
import tempfile
import zipfile

# --- Page setup ---
st.set_page_config(page_title="QR Code Name Generator", page_icon="🔳", layout="centered")

st.title("🔳 QR Code Name Generator (One per Page + Bulk Download)")
st.write("Upload a CSV or Excel file with first and last names. The app will generate a large QR code for each name and let you download them all at once as PNGs or a printable PDF.")

# --- File uploader ---
uploaded_file = st.file_uploader("Upload your file", type=["csv", "xlsx"])

if uploaded_file:
    # Load data
    if uploaded_file.name.endswith(".csv"):
        df = pd.read_csv(uploaded_file)
    else:
        df = pd.read_excel(uploaded_file)

    # Validate columns
    if not {"first_name", "last_name"}.issubset(df.columns):
        st.error("Your file must include columns: first_name and last_name")
    else:
        st.success(f"✅ Loaded {len(df)} names.")
        qr_images = []

        # --- Generate all QR codes ---
        for _, row in df.iterrows():
            full_name = f"{row['first_name']} {row['last_name']}"

            # Generate QR code
            qr = qrcode.QRCode(box_size=20, border=4)
            qr.add_data(full_name)
            qr.make(fit=True)
            qr_img = qr.make_image(fill_color="black", back_color="white").convert("RGB")

            # Add name above QR
            font = ImageFont.load_default()
            draw = ImageDraw.Draw(qr_img)
            bbox = draw.textbbox((0, 0), full_name, font=font)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]

            new_img = Image.new(
                "RGB",
                (max(qr_img.width, text_width + 100), qr_img.height + text_height + 100),
                "white",
            )
            new_draw = ImageDraw.Draw(new_img)
            new_draw.text(
                ((new_img.width - text_width) / 2, 20),
                full_name,
                fill="black",
                font=font,
            )
            new_img.paste(qr_img, ((new_img.width - qr_img.width) // 2, text_height + 40))

            # Resize for high-res printing (6" wide at 300 dpi)
            new_img = new_img.resize((1800, int(1800 * new_img.height / new_img.width)), Image.LANCZOS)
            qr_images.append((full_name, new_img))

        st.success("✅ All QR codes generated successfully!")

        # --- Create ZIP of all PNGs ---
        with tempfile.NamedTemporaryFile(delete=False, suffix=".zip") as tmpzip:
            with zipfile.ZipFile(tmpzip.name, "w") as zf:
                for full_name, img in qr_images:
                    buffer = BytesIO()
                    img.save(buffer, format="PNG")
                    buffer.seek(0)
                    filename = f"{full_name.replace(' ', '_')}.png"
                    zf.writestr(filename, buffer.read())
            zip_path = tmpzip.name

        # --- Create a PDF (one per 8.5x11 page) ---
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmpfile:
            c = canvas.Canvas(tmpfile.name, pagesize=letter)
            page_width, page_height = letter

            for full_name, img in qr_images:
                img_io = BytesIO()
                img.save(img_io, format="PNG")
                img_io.seek(0)

                # Use ImageReader to avoid TypeError
                image_reader = ImageReader(img_io)

                # Scale and position image
                img_width = 6 * inch
                aspect_ratio = img.height / img.width
                img_height = img_width * aspect_ratio
                x_pos = (page_width - img_width) / 2
                y_pos = (page_height - img_height) / 2 - 0.5 * inch

                c.drawImage(
                    image_reader,
                    x_pos,
                    y_pos,
                    width=img_width,
                    height=img_height,
                    preserveAspectRatio=True,
                )

                # Add name text above QR
                c.setFont("Helvetica-Bold", 24)
                c.drawCentredString(page_width / 2, y_pos + img_height + 0.75 * inch, full_name)

                c.showPage()

            c.save()
            pdf_path = tmpfile.name

        # --- Download buttons ---
        with open(zip_path, "rb") as zf:
            st.download_button(
                label="📦 Download All QR Codes (ZIP of PNGs)",
                data=zf,
                file_name="qr_codes_all.zip",
                mime="application/zip",
            )

        with open(pdf_path, "rb") as pf:
            st.download_button(
                label="📄 Download Printable PDF (One per Page)",
                data=pf,
                file_name="qr_codes_fullpage.pdf",
                mime="application/pdf",
            )

        st.info("All QR codes are ready. Choose ZIP for individual files or PDF for printing.")
else:
    st.info("👆 Upload a CSV or Excel file to begin.")

