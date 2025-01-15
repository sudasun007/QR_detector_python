import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from pyzbar.pyzbar import decode
from PIL import Image, ImageTk
import cv2
import webbrowser
import threading

class QRBarcodeScanner:
    def __init__(self, root):
        self.root = root
        self.root.title("QR/Barcode Scanner")
        self.root.geometry("600x700")
        self.root.resizable(False, False)

        self.is_scanning = False
        self.webcam_thread = None
        self.cap = None
        self.setup_ui()

    def setup_ui(self):
        # Style Configuration
        style = ttk.Style()

        # Custom button style for better visibility
        style.configure("Custom.TButton", 
                        font=("Arial", 12, "bold"), 
                        background="#4CAF50")
        style.map("Custom.TButton", 
                  background=[('active', '#45a049'), ('pressed', '#3d8b40')], 
                  foreground=[('active', 'black'), ('pressed', 'black')])

        # Widgets
        frame = ttk.Frame(self.root)
        frame.pack(pady=20)

        self.btn_browse = ttk.Button(frame, text="Select Image", command=self.browse_image, style="Custom.TButton")
        self.btn_browse.grid(row=0, column=0, padx=10)

        self.btn_webcam = ttk.Button(frame, text="Scan from Webcam", command=self.scan_from_webcam, style="Custom.TButton")
        self.btn_webcam.grid(row=0, column=1, padx=10)

        self.btn_stop_scan = ttk.Button(frame, text="Stop Scanning", command=self.stop_scanning, style="Custom.TButton", state=tk.DISABLED)
        self.btn_stop_scan.grid(row=0, column=2, padx=10)

        self.image_label = ttk.Label(self.root, background="#f9f9f9")
        self.image_label.pack(pady=10)

        result_frame = ttk.LabelFrame(self.root, text="Scan Results")
        result_frame.pack(padx=20, pady=10, fill="both", expand=True)

        self.result_textbox = tk.Text(result_frame, wrap="word", height=10, font=("Arial", 10))
        self.result_textbox.pack(padx=10, pady=10, fill="both", expand=True)

        # Add hyperlink styling
        self.result_textbox.tag_config("hyperlink", foreground="blue", underline=True)
        self.result_textbox.tag_bind("hyperlink", "<Button-1>", self.hyperlink_click)
        self.result_textbox.tag_config("bold", font=("Arial", 10, "bold"))

        action_frame = ttk.Frame(self.root)
        action_frame.pack(pady=10)

        self.copy_button = ttk.Button(action_frame, text="Copy to Clipboard", command=self.copy_to_clipboard, 
                                      state=tk.DISABLED, style="Custom.TButton")
        self.copy_button.grid(row=0, column=0, padx=10)

        self.open_browser_button = ttk.Button(action_frame, text="Open in Browser", command=self.open_in_browser, 
                                              state=tk.DISABLED, style="Custom.TButton")
        self.open_browser_button.grid(row=0, column=1, padx=10)
        self.open_browser_button.data = None  # Initialize browser button data

    def browse_image(self):
        """Browse an image file and decode QR/Barcode."""
        file_path = filedialog.askopenfilename(filetypes=[("Image Files", "*.png *.jpg *.jpeg *.bmp *.gif")])
        if file_path:
            try:
                img = Image.open(file_path)
                img.thumbnail((400, 400))
                img_tk = ImageTk.PhotoImage(img)
                self.image_label.config(image=img_tk)
                self.image_label.image = img_tk
                self.decode_image(file_path)
            except Exception as e:
                messagebox.showerror("Error", f"Could not open image: {str(e)}")

    def decode_image(self, file_path):
        """Decode QR/Barcode from the selected image."""
        try:
            img = Image.open(file_path)
            decoded_objects = decode(img)
            if decoded_objects:
                self.open_browser_button.data = None  # Reset browser button data
                self.result_textbox.delete("1.0", tk.END)

                for obj in decoded_objects:
                    data = obj.data.decode('utf-8')
                    self.result_textbox.insert(tk.END, f"Type: {obj.type}\nData: ", "bold")
                    if data.startswith("http"):
                        self.result_textbox.insert(tk.END, data + "\n\n", ("hyperlink", data))
                        self.open_browser_button.config(state=tk.NORMAL)
                        self.open_browser_button.data = data
                    else:
                        self.result_textbox.insert(tk.END, data + "\n\n")
                        self.open_browser_button.config(state=tk.DISABLED)

                self.copy_button.config(state=tk.NORMAL)  # Enable copy button
            else:
                self.result_textbox.delete("1.0", tk.END)
                self.result_textbox.insert(tk.END, "No QR/Barcode detected.")
                self.reset_ui_state()
                self.image_label.after(500, lambda: self.image_label.config(image=''))  # Hide the image label after a short delay
        except Exception as e:
            messagebox.showerror("Error", f"Error decoding image: {str(e)}")

    def scan_from_webcam(self):
        """Capture frames from the webcam and decode QR/Barcode in real time."""
        def scan_thread():
            try:
                self.cap = cv2.VideoCapture(0)
                while self.is_scanning:
                    ret, frame = self.cap.read()
                    if not ret:
                        break
                    
                    decoded_objects = decode(frame)
                    cv2.imshow("QR/Barcode Scanner", frame)

                    if decoded_objects:
                        self.root.after(0, lambda: self.process_scan_result(decoded_objects))
                        break  # Automatically stop scanning when a code is detected

                    key = cv2.waitKey(1) & 0xFF
                    if key == 27 or key == ord('q'):  # ESC or 'q' key
                        break
                
                self.cap.release()
                cv2.destroyAllWindows()
                self.is_scanning = False
                self.root.after(0, self.reset_scan_ui)  # Ensure UI is reset on the main thread
            except Exception as e:
                self.root.after(0, lambda: messagebox.showerror("Webcam Error", f"Error during webcam scanning: {str(e)}"))
                self.root.after(0, self.reset_scan_ui)

        # Prevent multiple scanning threads
        if self.is_scanning:
            self.stop_scanning()
            return

        # Set up scanning state
        self.is_scanning = True
        self.btn_webcam.config(state=tk.DISABLED)
        self.btn_browse.config(state=tk.DISABLED)
        self.btn_stop_scan.config(state=tk.NORMAL)

        # Start scanning in a separate thread
        self.webcam_thread = threading.Thread(target=scan_thread, daemon=True)
        self.webcam_thread.start()

    def stop_scanning(self):
        """Stop the webcam scanning process."""
        if self.is_scanning:
            self.is_scanning = False
            if self.cap:
                self.cap.release()  # Ensure the webcam is released
            cv2.destroyAllWindows()
            self.reset_scan_ui()

    def process_scan_result(self, decoded_objects):
        """Process the scanned result from webcam."""
        self.open_browser_button.data = None  # Reset browser button data
        self.result_textbox.delete("1.0", tk.END)

        for obj in decoded_objects:
            data = obj.data.decode('utf-8')
            self.result_textbox.insert(tk.END, f"Type: {obj.type}\nData: ", "bold")
            if data.startswith("http"):
                self.result_textbox.insert(tk.END, data + "\n\n", ("hyperlink", data))
                self.open_browser_button.config(state=tk.NORMAL)
                self.open_browser_button.data = data
            else:
                self.result_textbox.insert(tk.END, data + "\n\n")
                self.open_browser_button.config(state=tk.DISABLED)

        self.copy_button.config(state=tk.NORMAL)  # Enable copy button
        messagebox.showinfo("Scan Result", "QR/Barcode detected!")

    def reset_scan_ui(self):
        """Reset the UI after webcam scanning."""
        self.btn_webcam.config(state=tk.NORMAL)
        self.btn_browse.config(state=tk.NORMAL)
        self.btn_stop_scan.config(state=tk.DISABLED)
        self.copy_button.config(state=tk.DISABLED)
        self.open_browser_button.config(state=tk.DISABLED)

    def reset_ui_state(self):
        """Reset UI state (e.g., clear text box)."""
        self.result_textbox.delete("1.0", tk.END)
        self.copy_button.config(state=tk.DISABLED)
        self.open_browser_button.config(state=tk.DISABLED)

    def hyperlink_click(self, event):
        """Open the hyperlink in the default browser."""
        try:
            # Check if there is any selected text
            hyperlink = self.result_textbox.get(tk.SEL_FIRST, tk.SEL_LAST)
            webbrowser.open(hyperlink)
        except tk.TclError:
            # Handle the case where no text is selected
            pass

    def copy_to_clipboard(self):
        """Copy the result text to clipboard."""
        result = self.result_textbox.get("1.0", tk.END).strip()
        if result:
            self.root.clipboard_clear()
            self.root.clipboard_append(result)
            messagebox.showinfo("Copied", "Result copied to clipboard.")

    def open_in_browser(self):
        """Open the hyperlink in the browser."""
        if self.open_browser_button.data:
            webbrowser.open(self.open_browser_button.data)

if __name__ == "__main__":
    root = tk.Tk()
    app = QRBarcodeScanner(root)
    root.mainloop()
