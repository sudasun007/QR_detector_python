# QR/Barcode Scanner Application

This is a Python-based QR/Barcode scanner with a GUI built using `Tkinter`. The application supports scanning QR/Barcodes either from an image file or using a webcam in real-time. It provides options to open URLs in the browser, copy the result to the clipboard, and automatically detect QR/Barcodes.

## Features
- **Select Image**: Browse and load an image to decode the QR/Barcode.
- **Scan from Webcam**: Use the webcam to scan QR/Barcodes in real-time.
- **Stop Scanning**: Stop the ongoing webcam scanning.
- **Copy to Clipboard**: Copy the decoded QR/Barcode data to clipboard.
- **Open in Browser**: Open URLs encoded in QR/Barcodes directly in the browser.

## Requirements
- Python 3.x
- Tkinter (usually pre-installed with Python)
- PyZbar: For decoding QR/Barcode
- OpenCV: For webcam functionality
- Pillow: For image handling

### Install Dependencies
To install the required dependencies, use the following command:

```bash
pip install pyzbar opencv-python pillow
```

## Usage

1. Run the `QR/Barcode Scanner` application.
2. You can either:
    - **Select Image**: Browse an image containing a QR/Barcode.
    - **Scan from Webcam**: Use the webcam to scan a QR/Barcode in real-time.
3. If a URL is detected in the QR/Barcode, you can open it directly in the browser or copy it to the clipboard.

## How It Works
- **Browse Image**: Select an image file using the file dialog. The image is decoded for QR/Barcode, and the result is displayed in a textbox.
- **Scan from Webcam**: The webcam captures video frames, and QR/Barcodes are decoded in real-time. Once a code is detected, the app will display the result and stop scanning.
- **Hyperlink Detection**: If the decoded data is a URL, it will appear as a clickable link in the result box.
- **Clipboard**: Copy the decoded result to the clipboard for easy use.
- **Browser**: Open detected URLs directly in the default web browser.

## Credits

- **Tkinter** for GUI development
- **PyZbar** for QR/Barcode decoding
- **OpenCV** for webcam integration
- **Pillow** for image handling
