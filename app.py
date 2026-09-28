"""Streamlit QR generator for one URL or an Excel sheet (Name, Link)."""
from pathlib import Path
import io
import re
import tempfile
import zipfile

import qrcode
from qrcode.constants import ERROR_CORRECT_H
from qrcode.image.styledpil import StyledPilImage
from qrcode.image.styles.colormasks import SolidFillColorMask
from qrcode.image.styles.moduledrawers.pil import (
    CircleModuleDrawer,
    GappedSquareModuleDrawer,
    RoundedModuleDrawer,
    SquareModuleDrawer,
)
from PIL import Image
from openpyxl import load_workbook
import streamlit as st

SHAPES = {
    "Squares": SquareModuleDrawer,
    "Rounded": RoundedModuleDrawer,
    "Circles": CircleModuleDrawer,
    "Gapped squares": GappedSquareModuleDrawer,
}


def generate_ultra_qr_png(
    link: str,
    logo_path: str | Path | None = None,
    out_path: str | Path = "qr_code.png",
    box_size: int = 100,
    border: int = 4,
    logo_scale: float = 0.22,
    color: str = "#000000",
    shape: str = "Squares",
) -> Path:
    if not link.strip():
        raise ValueError("Please enter a valid URL.")
    if shape not in SHAPES:
        raise ValueError(f"Unsupported QR shape: {shape}")
    if not re.fullmatch(r"#[0-9A-Fa-f]{6}", color):
        raise ValueError("QR color must be a six-digit hex color.")
    if not 0 < logo_scale <= 0.30:
        raise ValueError("Logo size must be between 0 and 30% of QR width.")

    qr = qrcode.QRCode(
        version=None, error_correction=ERROR_CORRECT_H,
        box_size=box_size, border=border,
    )
    qr.add_data(link)
    qr.make(fit=True)
    rgb = tuple(bytes.fromhex(color[1:]))
    # Styled drawers apply only to the data modules; finder patterns stay square.
    qr_img = qr.make_image(
        image_factory=StyledPilImage,
        module_drawer=SHAPES[shape](),
        color_mask=SolidFillColorMask(back_color=(255, 255, 255), front_color=rgb),
    ).convert("RGBA")

    if logo_path is not None:
        logo_path = Path(logo_path)
        if not logo_path.exists():
            raise FileNotFoundError(f"Logo not found: {logo_path}")
        with Image.open(logo_path) as source:
            logo = source.convert("RGBA")
        if not logo.width or not logo.height:
            raise ValueError("Logo image has invalid dimensions.")
        qr_w, qr_h = qr_img.size
        # Bound both dimensions, including wide or tall uploaded logos.
        max_side = int(qr_w * logo_scale)
        logo.thumbnail((max_side, max_side), Image.Resampling.LANCZOS)
        pad = max(2 * box_size, int(qr_w * 0.015))
        bg = Image.new("RGBA", (logo.width + 2 * pad, logo.height + 2 * pad), "white")
        bg.alpha_composite(logo, (pad, pad))
        qr_img.alpha_composite(bg, ((qr_w - bg.width) // 2, (qr_h - bg.height) // 2))

    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    qr_img.convert("RGB").save(out_path, format="PNG", optimize=False)
    return out_path


def safe_file_name(value: str) -> str:
    name = re.sub(r'[<>:"/\\|?*\x00-\x1f]', "_", str(value)).strip(" .")
    return name or "Unnamed"


def generate_batch_zip(excel_file, logo_file, box_size, border, logo_scale, color, shape):
    with tempfile.TemporaryDirectory() as directory:
        temp_dir = Path(directory)
        logo_path = None
        if logo_file is not None:
            logo_path = temp_dir / ("uploaded_logo" + (Path(logo_file.name).suffix or ".png"))
            logo_path.write_bytes(logo_file.getbuffer())
        workbook = load_workbook(io.BytesIO(excel_file.getbuffer()))
        sheet = workbook.active
        if (str(sheet.cell(1, 1).value or "").strip().lower() != "name"
                or str(sheet.cell(1, 2).value or "").strip().lower() != "link"):
            raise ValueError('The Excel file must have "Name" in column A and "Link" in column B.')
        sheet.cell(1, 3, "QR Image Link")
        files, used_names, skipped_rows = [], set(), []
        for row_number in range(2, sheet.max_row + 1):
            name = str(sheet.cell(row_number, 1).value or "").strip()
            link = str(sheet.cell(row_number, 2).value or "").strip()
            if not name and not link:
                continue
            if not name or not link:
                skipped_rows.append(row_number)
                sheet.cell(row_number, 3, "Skipped: missing Name or Link")
                continue
            base = f"{safe_file_name(name)} BC QR"
            filename, copy_number = f"{base}.png", 2
            while filename.casefold() in used_names:
                filename = f"{base} ({copy_number}).png"
                copy_number += 1
            used_names.add(filename.casefold())
            path = generate_ultra_qr_png(
                link, logo_path, temp_dir / filename, box_size, border,
                logo_scale, color, shape,
            )
            relative_path = f"QR Codes/{filename}"
            cell = sheet.cell(row_number, 3, relative_path)
            cell.hyperlink = relative_path
            cell.style = "Hyperlink"
            files.append((relative_path, path.read_bytes()))
        if not files:
            raise ValueError("No valid rows were found in the Excel file.")
        sheet.column_dimensions["C"].width = 55
        updated_excel = io.BytesIO()
        workbook.save(updated_excel)
        output = io.BytesIO()
        with zipfile.ZipFile(output, "w", zipfile.ZIP_DEFLATED) as archive:
            for name, image_bytes in files:
                archive.writestr(name, image_bytes)
            archive.writestr("updated_qr_links.xlsx", updated_excel.getvalue())
        return output.getvalue(), len(files), skipped_rows


st.set_page_config(page_title="QR Generator", layout="centered")
st.title("QR Code Generator")
st.write("Generate a QR code for one link or multiple links from Excel.")

with st.expander("Customize QR code"):
    custom_color = st.checkbox("Choose a QR color", value=False)
    color = st.color_picker("QR color", "#000000", disabled=not custom_color) if custom_color else "#000000"
    custom_shape = st.checkbox("Choose a QR shape", value=False)
    shape = st.selectbox("QR shape", list(SHAPES), disabled=not custom_shape) if custom_shape else "Squares"
    box_size = st.slider("QR resolution / box size", 40, 150, 100)
    border = st.slider("QR border", 4, 8, 4)
    logo_scale = st.slider("Logo size (when a logo is uploaded)", 0.10, 0.25, 0.18)

single_tab, batch_tab = st.tabs(["Single QR Code", "Batch from Excel"])
with single_tab:
    url = st.text_input("Website URL", placeholder="https://example.com")
    uploaded_logo = st.file_uploader("Upload logo (optional)", type=["png", "jpg", "jpeg", "webp"], key="single_logo")
    if st.button("Generate QR Code", key="single_generate"):
        if not url.strip():
            st.error("Please enter the URL.")
        else:
            try:
                with tempfile.TemporaryDirectory() as directory:
                    temp_dir = Path(directory)
                    logo_path = None
                    if uploaded_logo is not None:
                        logo_path = temp_dir / ("uploaded_logo" + (Path(uploaded_logo.name).suffix or ".png"))
                        logo_path.write_bytes(uploaded_logo.getbuffer())
                    output_path = generate_ultra_qr_png(
                        url, logo_path, temp_dir / "qr_code.png",
                        box_size, border, logo_scale, color, shape,
                    )
                    st.session_state["single_png"] = output_path.read_bytes()
            except Exception as error:
                st.error(f"Error: {error}")
    if "single_png" in st.session_state:
        st.image(st.session_state["single_png"], caption="Generated QR Code", use_container_width=True)
        st.download_button("Download QR Code", st.session_state["single_png"], "qr_code.png", "image/png")

with batch_tab:
    st.write("Upload an Excel file with **Name** in column A and **Link** in column B.")
    uploaded_excel = st.file_uploader("Upload Excel File", type=["xlsx"], key="batch_excel")
    batch_logo = st.file_uploader("Upload logo (optional)", type=["png", "jpg", "jpeg", "webp"], key="batch_logo")
    if st.button("Generate All QR Codes", key="batch_generate"):
        if uploaded_excel is None:
            st.error("Please upload the Excel file.")
        else:
            try:
                with st.spinner("Generating QR codes..."):
                    data, count, skipped = generate_batch_zip(
                        uploaded_excel, batch_logo, box_size, border, logo_scale, color, shape,
                    )
                st.session_state["batch_zip"] = data
                st.session_state["batch_count"] = count
                st.session_state["batch_skipped"] = skipped
            except Exception as error:
                st.error(f"Error: {error}")
    if "batch_zip" in st.session_state:
        st.success(f'{st.session_state["batch_count"]} QR code(s) generated successfully.')
        if st.session_state.get("batch_skipped"):
            st.warning("Skipped incomplete Excel row(s): " + ", ".join(map(str, st.session_state["batch_skipped"])))
        st.download_button(
            "Download All QR Codes + Updated Excel", st.session_state["batch_zip"],
            "qr_codes.zip", "application/zip",
        )
