from pathlib import Path
from PIL import Image
import qrcode
from qrcode.constants import ERROR_CORRECT_H
import streamlit as st
import tempfile


# =========================
# QR GENERATION FUNCTION
# =========================
def generate_ultra_qr_png(
    link: str,
    logo_path: str,
    out_path: str = "qr_ultra.png",
    box_size: int = 100,
    border: int = 4,
    logo_scale: float = 0.22,
):
    if not link.strip():
        raise ValueError("Please enter a valid URL.")

    logo_path = Path(logo_path)
    if not logo_path.exists():
        raise FileNotFoundError(f"Logo not found: {logo_path}")

    qr = qrcode.QRCode(
        version=None,
        error_correction=ERROR_CORRECT_H,
        box_size=box_size,
        border=border,
    )
    qr.add_data(link)
    qr.make(fit=True)

    qr_img = qr.make_image(
        fill_color="black",
        back_color="white",
    ).convert("RGBA")

    qr_w, qr_h = qr_img.size

    logo = Image.open(logo_path).convert("RGBA")

    logo_w = int(qr_w * logo_scale)
    w, h = logo.size
    logo_h = int((logo_w / w) * h)
    logo = logo.resize((logo_w, logo_h), Image.Resampling.LANCZOS)

    pad = max(40, int(qr_w * 0.015))
    bg = Image.new(
        "RGBA",
        (logo_w + pad * 2, logo_h + pad * 2),
        (255, 255, 255, 255),
    )
    bg.paste(logo, (pad, pad), logo)

    pos = ((qr_w - bg.width) // 2, (qr_h - bg.height) // 2)
    qr_img.paste(bg, pos, bg)

    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    qr_img.save(out_path, format="PNG", optimize=False)

    return out_path


# =========================
# PAGE CONFIG
# =========================
transparent_icon = Image.new("RGBA", (32, 32), (255, 255, 255, 0))

st.set_page_config(
    page_title="QR Generator",
    page_icon=transparent_icon,
    layout="centered",
)


# =========================
# CSS — force light theme + replace all orange/red with #006C35
# =========================
st.markdown(
    """
    <style>
        /* ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
           1. OVERRIDE STREAMLIT CSS VARIABLES
              These drive slider thumbs, focus rings,
              active states across ALL components.
        ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ */
        :root {
            --primary-color: #006C35 !important;
            --primary-hue: 145 !important;
            --background-color: #f7f9f7 !important;
            --secondary-background-color: #ffffff !important;
            --text-color: #1a1a1a !important;
            color-scheme: light !important;
        }

        /* ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
           2. FORCE LIGHT BACKGROUNDS ON ALL WRAPPERS
        ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ */
        html, body,
        .stApp,
        [data-testid="stApp"],
        [data-testid="stAppViewContainer"],
        [data-testid="stAppViewBlockContainer"],
        [data-testid="stVerticalBlock"],
        [data-testid="stMainBlockContainer"],
        [data-testid="block-container"],
        .block-container,
        .main,
        section[data-testid="stSidebar"],
        .stChatFloatingInputContainer {
            background-color: #f7f9f7 !important;
            color: #1a1a1a !important;
        }

        /* ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
           3. ALL TEXT ELEMENTS
        ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ */
        h1, h2, h3, h4, h5, h6, p, span, label,
        div, li, a, small, strong, em,
        [data-testid="stMarkdownContainer"] * {
            color: #1a1a1a !important;
        }

        .header-box h1 { font-size: 30px; font-weight: 700; margin: 0; }
        .header-box p  { font-size: 15px; margin-top: 8px; color: #3a3a3a !important; }
        .header-box    { padding: 28px; border-radius: 18px; margin-bottom: 24px; text-align: center; }

        /* ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
           4. TEXT INPUT
        ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ */
        input[type="text"],
        input[type="url"],
        input[type="email"],
        input[type="number"],
        input[type="search"],
        .stTextInput input {
            background-color: #ffffff !important;
            color: #1a1a1a !important;
            border: 1.5px solid #b7c9bf !important;
            border-radius: 10px !important;
            box-shadow: none !important;
            outline: none !important;
        }

        input[type="text"]:focus,
        input[type="url"]:focus,
        .stTextInput input:focus {
            border-color: #006C35 !important;
            box-shadow: 0 0 0 2px rgba(0,108,53,0.20) !important;
            outline: none !important;
        }

        /* ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
           5. FILE UPLOADER  (dark bg fix)
        ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ */
        [data-testid="stFileUploader"],
        [data-testid="stFileUploader"] > div,
        [data-testid="stFileUploader"] section,
        [data-testid="stFileUploadDropzone"],
        [data-testid="stFileUploadDropzone"] > div {
            background-color: #ffffff !important;
            color: #1a1a1a !important;
            border-color: #b7c9bf !important;
            border-radius: 10px !important;
        }

        [data-testid="stFileUploadDropzone"] {
            border: 1.5px dashed #b7c9bf !important;
        }

        /* "Browse files" button inside uploader */
        [data-testid="stFileUploadDropzone"] button,
        [data-testid="stFileUploader"] button {
            background-color: #ffffff !important;
            color: #006C35 !important;
            border: 1.5px solid #006C35 !important;
            border-radius: 8px !important;
        }

        /* ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
           6. EXPANDER  (dark header fix + green text)
        ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ */
        [data-testid="stExpander"],
        [data-testid="stExpander"] details,
        [data-testid="stExpander"] > div,
        [data-testid="stExpander"] > div > div {
            background-color: #ffffff !important;
            border: 1px solid #d9e4dc !important;
            border-radius: 10px !important;
        }

        /* The clickable header row */
        [data-testid="stExpander"] details > summary,
        [data-testid="stExpander"] details > summary * {
            background-color: #ffffff !important;
            color: #006C35 !important;
            font-weight: 600 !important;
        }

        [data-testid="stExpander"] details > summary svg path {
            stroke: #006C35 !important;
            fill: #006C35 !important;
        }

        /* ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
           7. SLIDERS  (thumb + active track = green)
        ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ */
        /* Webkit thumb */
        input[type="range"]::-webkit-slider-thumb {
            background: #006C35 !important;
            border: none !important;
            -webkit-appearance: none !important;
        }
        /* Firefox thumb */
        input[type="range"]::-moz-range-thumb {
            background: #006C35 !important;
            border: none !important;
        }
        /* Active filled portion of track (Streamlit div overlay) */
        [data-testid="stSlider"] [class*="track"] > div,
        [data-testid="stSlider"] div[style*="width"] {
            background-color: #006C35 !important;
        }
        /* Tooltip bubble above thumb */
        [data-testid="stSlider"] div[data-testid="stThumbValue"],
        [data-testid="stTickBar"] + div {
            color: #006C35 !important;
        }

        /* ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
           8. BUTTONS
        ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ */
        /* BUTTONS */
        .stButton > button,
        .stDownloadButton > button {
        width: 100% !important;
        background-color: #006C35 !important;
        color: #ffffff !important;
        border: none !important;
        border-radius: 10px !important;
        padding: 12px 18px !important;
        font-size: 16px !important;
        font-weight: 600 !important;
        transition: all 0.2s ease-in-out !important;
        }

        .stButton > button *,
        .stDownloadButton > button * {
        color: #ffffff !important;
        }

        .stButton > button:hover,
        .stDownloadButton > button:hover {
        color: #ffffff !important;
        }

        .stButton > button:active,
        .stDownloadButton > button:active {
        background-color: #004D26 !important;
        transform: translateY(0);
        box-shadow: none !important;}

        /* ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
           9. ALERTS
        ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ */
        [data-testid="stAlert"],
        [data-testid="stAlert"] * {
            background-color: #edf7f0 !important;
            color: #1a1a1a !important;
        }

        /* ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
           10. MISC
        ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ */
        .small-note { color: #5f6f67 !important; font-size: 13px; margin-top: 8px; }

        /* Hide the Streamlit top-bar menu in production if desired */
        /* [data-testid="stToolbar"] { display: none; } */
    </style>
    """,
    unsafe_allow_html=True,
)


# =========================
# UI
# =========================
st.markdown(
    """
    <div class="header-box">
        <h1>QR Code Generator</h1>
        <p>Generate a high-resolution QR code with logo in the center</p>
    </div>
    """,
    unsafe_allow_html=True,
)


url = st.text_input(
    "Website URL",
    placeholder="https://investsaudi.sa",
)

uploaded_logo = st.file_uploader(
    "Upload Logo Image",
    type=["png", "jpg", "jpeg", "webp"],
)

with st.expander("Advanced settings", expanded=False):
    box_size = st.slider("QR resolution / box size", 40, 150, 100)
    logo_scale = st.slider("Logo size", 0.10, 0.30, 0.22)
    border = st.slider("QR border", 2, 8, 4)

st.markdown('<p class="small-note">Recommended logo format: PNG with transparent background.</p>', unsafe_allow_html=True)

if st.button("Generate QR Code"):
    if not url.strip():
        st.error("Please enter the URL.")
    elif uploaded_logo is None:
        st.error("Please upload the logo image.")
    else:
        try:
            with tempfile.TemporaryDirectory() as temp_dir:
                temp_dir = Path(temp_dir)

                logo_path = temp_dir / uploaded_logo.name
                logo_path.write_bytes(uploaded_logo.getbuffer())

                output_path = temp_dir / "qr_code_with_logo.png"

                generate_ultra_qr_png(
                    link=url,
                    logo_path=str(logo_path),
                    out_path=str(output_path),
                    box_size=box_size,
                    border=border,
                    logo_scale=logo_scale,
                )

                st.success("QR code generated successfully.")

                st.subheader("Preview")
                st.image(str(output_path), caption="Generated QR Code", use_container_width=True)

                qr_bytes = output_path.read_bytes()
                st.download_button(
                    label="Download QR Code",
                    data=qr_bytes,
                    file_name="qr_code_with_logo.png",
                    mime="image/png",
                )

        except Exception as e:
            st.error(f"Error: {e}")

st.markdown("</div>", unsafe_allow_html=True)