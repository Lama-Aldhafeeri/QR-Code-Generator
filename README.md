# QR Code Generator

A Streamlit web app for generating high-resolution QR codes with a custom logo in the center.

## Features

- Generate QR codes from any website URL
- Upload a logo image to place in the center of the QR code
- Preview the generated QR code inside the app
- Download the final QR code as a PNG file
- Advanced settings for QR resolution, logo size, and border size


## Requirements

Before running the project, make sure you have:

- Python 3.10 or newer
- pip installed

Python packages are listed in `requirements.txt`:

```txt
streamlit
pillow
qrcode[pil]
```

## Installation

1. Create a project folder and place the Python file inside it.

Example:

```bash
mkdir qr-generator
cd qr-generator
```

2. Create a virtual environment:

```bash
python3 -m venv .venv
```

3. Activate the virtual environment:

On macOS/Linux:

```bash
source .venv/bin/activate
```

On Windows:

```bash
.venv\Scripts\activate
```

4. Install the required packages:

```bash
pip install -r requirements.txt
```

## How to Run

Run the Streamlit app using:

```bash
streamlit run app.py
```

Replace `app.py` with the actual name of your Python file if it is different.

## How to Use

1. Open the app in your browser.
2. Enter the website URL.
3. Upload a logo image.
4. Adjust advanced settings if needed.
5. Click **Generate QR Code**.
6. Preview the generated QR code.
7. Click **Download QR Code** to save the PNG file.

## Supported Logo Formats

The app supports the following logo image formats:

- PNG
- JPG
- JPEG
- WEBP

For best results, use a PNG logo with a transparent background.

## Project Structure

```txt
qr-generator/
│
├── app.py
├── requirements.txt
└── README.md
```

## Notes

- The QR code uses high error correction to support placing a logo in the center.
- Make sure the uploaded logo is clear and not too large.
- If the QR code is hard to scan, reduce the logo size from the advanced settings.
