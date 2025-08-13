import tkinter as tk
from tkinter import filedialog, Label, messagebox, ttk, Frame, Scale
from PIL import Image, ImageTk
import os

# Import backend functions
from NEW import (
    load_image, compute_histogram, compute_pdf, compute_mean_and_average_pdf,
    compute_adaptive_pdf, modify_image_with_pdf, compute_cdf, compute_mean_and_average_cdf,
    compute_adaptive_cdf, modify_image_with_cdf, contrast_adjustment, gamma_correction,
    multi_scale_enhancement
)

def create_placeholder_icon(frame, size=200):
    """Create a placeholder icon when no image is loaded"""
    placeholder = Frame(frame, width=size, height=size, bg='#34495E')
    placeholder.pack(expand=True)
    
    # Create image icon
    icon_frame = Frame(placeholder, bg='#2C3E50', width=100, height=100)
    icon_frame.place(relx=0.5, rely=0.5, anchor='center')
    
    # Add image icon symbol
    image_symbol = Label(icon_frame, 
                        text="🖼️",
                        font=("Segoe UI Emoji", 48),
                        bg='#2C3E50',
                        fg='#ECF0F1')
    image_symbol.place(relx=0.5, rely=0.5, anchor='center')
    
    # Add "No Image" text
    no_image_text = Label(placeholder,
                         text="No Image Loaded\nClick 'Open Image' to begin",
                         font=("Helvetica", 12),
                         bg='#34495E',
                         fg='#ECF0F1')
    no_image_text.place(relx=0.5, rely=0.85, anchor='center')
    
    return placeholder

def button_press(button):
    """Simulate button press effect"""
    button.state(['pressed'])
    root.after(100, lambda: button.state(['!pressed']))

def open_image():
    global img_array, original_image

    file_path = filedialog.askopenfilename(filetypes=[("Image Files", "*.jpg *.png *.jpeg *.bmp")])
    if not file_path:
        return

    img_array = load_image(file_path)
    original_image = Image.fromarray(img_array)
    display_original_image(original_image)

def display_original_image(image):
    global original_img_display
    
    # Clear any existing placeholder
    for widget in original_img_label.winfo_children():
        widget.destroy()
    
    # Resize image to fit display area while maintaining aspect ratio
    display_width = 500  # Reduced width for side-by-side display
    display_height = 600
    
    width, height = image.size
    ratio = min(display_width/width, display_height/height)
    new_size = (int(width*ratio), int(height*ratio))
    
    resized_image = image.resize(new_size, Image.Resampling.LANCZOS)
    original_img_display = ImageTk.PhotoImage(image=resized_image)
    original_img_label.config(image=original_img_display)
    original_img_label.image = original_img_display
    original_img_label_title.config(text="Original Image")

def display_enhanced_image(image, title):
    global enhanced_img_display
    
    # Clear any existing placeholder
    for widget in enhanced_img_label.winfo_children():
        widget.destroy()
    
    # Resize image to fit display area while maintaining aspect ratio
    display_width = 500  # Reduced width for side-by-side display
    display_height = 600
    
    width, height = image.size
    ratio = min(display_width/width, display_height/height)
    new_size = (int(width*ratio), int(height*ratio))
    
    resized_image = image.resize(new_size, Image.Resampling.LANCZOS)
    enhanced_img_display = ImageTk.PhotoImage(image=resized_image)
    enhanced_img_label.config(image=enhanced_img_display)
    enhanced_img_label.image = enhanced_img_display
    enhanced_img_label_title.config(text=title)

def save_image(image, prompt):
    file_path = filedialog.asksaveasfilename(defaultextension=".jpg", 
                                           filetypes=[("JPEG", "*.jpg"), ("PNG", "*.png")])
    if file_path:
        image.save(file_path)
        messagebox.showinfo("Success", f"{prompt} saved to: {file_path}")

def enhance_pdf():
    if img_array is None:
        messagebox.showerror("Error", "Please load an image first.")
        return

    histogram = compute_histogram(img_array)
    pdf = compute_pdf(histogram)
    mean_pdf, average_pdf = compute_mean_and_average_pdf(pdf)
    adaptive_pdf = compute_adaptive_pdf(pdf, mean_pdf, average_pdf)
    enhanced_image = modify_image_with_pdf(img_array, adaptive_pdf)

    pdf_enhanced_image = Image.fromarray(enhanced_image)
    display_enhanced_image(pdf_enhanced_image, "PDF Enhanced Image")
    save_button.config(command=lambda: save_image(pdf_enhanced_image, "PDF Enhanced Image"))

def enhance_cdf():
    if img_array is None:
        messagebox.showerror("Error", "Please load an image first.")
        return

    histogram = compute_histogram(img_array)
    cdf = compute_cdf(histogram)
    mean_cdf, average_cdf = compute_mean_and_average_cdf(cdf)
    adaptive_cdf = compute_adaptive_cdf(cdf, mean_cdf, average_cdf)
    enhanced_image = modify_image_with_cdf(img_array, adaptive_cdf)

    cdf_enhanced_image = Image.fromarray(enhanced_image)
    display_enhanced_image(cdf_enhanced_image, "CDF Enhanced Image")
    save_button.config(command=lambda: save_image(cdf_enhanced_image, "CDF Enhanced Image"))

def show_contrast_controls():
    contrast_window = tk.Toplevel(root)
    contrast_window.title("Contrast Controls")
    contrast_window.geometry("300x300")
    contrast_window.configure(bg='#2C3E50')
    
    # Alpha Slider (Contrast)
    Label(contrast_window, text="Contrast (Alpha)", bg='#2C3E50', fg='#ECF0F1').pack(pady=10)
    alpha_slider = Scale(contrast_window, from_=0.1, to=5.0, resolution=0.1, orient='horizontal',
                        bg='#2C3E50', fg='#ECF0F1')
    alpha_slider.set(2.5)
    alpha_slider.pack(fill='x', padx=20)
    
    # Beta Slider (Brightness)
    Label(contrast_window, text="Brightness (Beta)", bg='#2C3E50', fg='#ECF0F1').pack(pady=10)
    beta_slider = Scale(contrast_window, from_=0.1, to=3.0, resolution=0.1, orient='horizontal',
                       bg='#2C3E50', fg='#ECF0F1')
    beta_slider.set(1.5)
    beta_slider.pack(fill='x', padx=20)
    
    def apply_contrast():
        if img_array is None:
            messagebox.showerror("Error", "Please load an image first.")
            return

        alpha = alpha_slider.get()
        beta = beta_slider.get()
        enhanced_image = contrast_adjustment(img_array, alpha=alpha, beta=beta)
        contrast_enhanced_image = Image.fromarray(enhanced_image)
        display_enhanced_image(contrast_enhanced_image, "Contrast Adjusted Image")
        save_button.config(command=lambda: save_image(contrast_enhanced_image, "Contrast Enhanced Image"))
        contrast_window.destroy()
    
    button_frame = Frame(contrast_window, bg='#2C3E50')
    button_frame.pack(side='bottom', fill='x', pady=20)
    
    apply_btn = ttk.Button(button_frame, text="Apply", command=apply_contrast, style='Modern.TButton')
    apply_btn.pack(pady=10, padx=20, fill='x')

def show_gamma_controls():
    gamma_window = tk.Toplevel(root)
    gamma_window.title("Gamma Controls")
    gamma_window.geometry("300x200")  # Increased height to ensure button visibility
    gamma_window.configure(bg='#2C3E50')
    
    # Gamma Slider
    Label(gamma_window, text="Gamma", bg='#2C3E50', fg='#ECF0F1').pack(pady=10)
    gamma_slider = Scale(gamma_window, from_=0.1, to=5.0, resolution=0.1, orient='horizontal',
                        bg='#2C3E50', fg='#ECF0F1')
    gamma_slider.set(2.2)
    gamma_slider.pack(fill='x', padx=20)
    
    def apply_gamma_correction():
        if img_array is None:
            messagebox.showerror("Error", "Please load an image first.")
            return

        gamma = gamma_slider.get()
        enhanced_image = gamma_correction(img_array, gamma=gamma)
        gamma_corrected_image = Image.fromarray(enhanced_image)
        display_enhanced_image(gamma_corrected_image, "Gamma Corrected Image")
        save_button.config(command=lambda: save_image(gamma_corrected_image, "Gamma Corrected Image"))
        gamma_window.destroy()
    
    # Container frame for button to ensure visibility
    button_frame = Frame(gamma_window, bg='#2C3E50')
    button_frame.pack(side='bottom', fill='x', pady=20)
    
    apply_btn = ttk.Button(button_frame, text="Apply", command=apply_gamma_correction, style='Modern.TButton')
    apply_btn.pack(pady=10, padx=20, fill='x')

def multi_scale():
    if img_array is None:
        messagebox.showerror("Error", "Please load an image first.")
        return

    # Create settings window
    settings_window = tk.Toplevel(root)
    settings_window.title("Multi-Scale Settings")
    settings_window.geometry("300x250")
    settings_window.configure(bg='#2C3E50')

    # Clip Limit dropdown
    Label(settings_window, text="Clip Limit", bg='#2C3E50', fg='#ECF0F1').pack(pady=10)
    clip_limit_var = tk.StringVar(value="3.5")
    clip_limit_options = ["1.0", "2.0", "3.0", "3.5", "4.0", "5.0"]
    clip_limit_dropdown = ttk.Combobox(settings_window, textvariable=clip_limit_var, values=clip_limit_options)
    clip_limit_dropdown.pack(pady=5)

    # Tile Grid Size dropdown
    Label(settings_window, text="Tile Grid Size", bg='#2C3E50', fg='#ECF0F1').pack(pady=10)
    grid_size_var = tk.StringVar(value="(10, 10)")
    grid_size_options = ["(2,2)","(8, 8)", "(10, 10)", "(12, 12)", "(14, 14)"]
    grid_size_dropdown = ttk.Combobox(settings_window, textvariable=grid_size_var, values=grid_size_options)
    grid_size_dropdown.pack(pady=5)

    def apply_multi_scale():
        clip_limit = float(clip_limit_var.get())
        grid_size = eval(grid_size_var.get())
        
        enhanced_image = multi_scale_enhancement(img_array)
        multi_scale_enhanced_image = Image.fromarray(enhanced_image)
        display_enhanced_image(multi_scale_enhanced_image, "Multi-Scale Enhanced Image")
        save_button.config(command=lambda: save_image(multi_scale_enhanced_image, "Multi-Scale Enhanced Image"))
        settings_window.destroy()

    # Apply button
    button_frame = Frame(settings_window, bg='#2C3E50')
    button_frame.pack(side='bottom', fill='x', pady=20)
    
    apply_btn = ttk.Button(button_frame, text="Apply", command=apply_multi_scale, style='Modern.TButton')
    apply_btn.pack(pady=10, padx=20, fill='x')

def update_image(*args):
    if img_array is not None:
        adjust_contrast()

# GUI Setup with modern dark theme
root = tk.Tk()
root.title("Advanced Image Enhancement Suite")
root.geometry("1400x900")  # Wider window for side-by-side display
root.configure(bg='#2C3E50')  # Dark blue-gray background

img_array = None
original_image = None

# Create main container with horizontal layout
main_container = Frame(root, bg='#2C3E50')
main_container.pack(expand=True, fill='both', padx=20, pady=20)

# Title with modern font and color
title_label = Label(main_container, 
                   text="image enhancement", 
                   font=("Helvetica", 28, "bold"),
                   bg='#2C3E50',
                   fg='#ECF0F1')
title_label.pack(pady=15)

# Create horizontal container for buttons and images
content_container = Frame(main_container, bg='#2C3E50')
content_container.pack(expand=True, fill='both')

# Left side - Control buttons
button_frame = Frame(content_container, bg='#2C3E50', width=200)
button_frame.pack(side='left', fill='y', padx=20)

# Modern button styles
style = ttk.Style()
style.theme_use('clam')
style.configure('Modern.TButton', 
                font=('Helvetica', 12),
                padding=12,
                background='#3498DB',
                foreground='#ECF0F1',
                borderwidth=10,
                relief='raised')
style.map('Modern.TButton',
          background=[('active', '#5DADE2'),
                     ('pressed', '#2980B9')])  # Darker blue when pressed

# Configure button corner radius
root.tk.call('tk', 'scaling', 1.0)  # Ensure consistent scaling
root.tk.call('ttk::style', 'configure', 'Modern.TButton', '-corner-radius', 8)

# Control buttons with hover effects and press animation
buttons_data = [
    ("Open Image", lambda b=None: [button_press(b), open_image()]),
    ("PDF Enhancement", lambda b=None: [button_press(b), enhance_pdf()]),
    ("CDF Enhancement", lambda b=None: [button_press(b), enhance_cdf()]),
    ("Contrast Adjustment", lambda b=None: [button_press(b), show_contrast_controls()]),
    ("Gamma Correction", lambda b=None: [button_press(b), show_gamma_controls()]),
    ("Multi-Scale Enhancement", lambda b=None: [button_press(b), multi_scale()])
]

for text, command in buttons_data:
    btn = ttk.Button(button_frame, 
                     text=text,
                     style='Modern.TButton')
    btn.configure(command=lambda b=btn, cmd=command: cmd(b))
    btn.pack(pady=15, padx=10, fill='x')

# Save button
save_button = ttk.Button(button_frame, 
                        text="Save Enhanced Image",
                        style='Modern.TButton')
save_button.pack(pady=25, padx=10, fill='x')

# Middle - Original image
original_frame = Frame(content_container, bg='#34495E', bd=2, relief='solid')
original_frame.pack(side='left', padx=10, expand=True, fill='both')

original_img_label_title = Label(original_frame, 
                               text="Original Image", 
                               font=("Helvetica", 18),
                               bg='#34495E',
                               fg='#ECF0F1')
original_img_label_title.pack(pady=10)

original_img_label = Label(original_frame, bg='#34495E')
original_img_label.pack(expand=True)

# Add placeholder to original image frame
original_placeholder = create_placeholder_icon(original_img_label)

# Right - Enhanced image
enhanced_frame = Frame(content_container, bg='#34495E', bd=2, relief='solid')
enhanced_frame.pack(side='left', padx=10, expand=True, fill='both')

enhanced_img_label_title = Label(enhanced_frame, 
                               text="Enhanced Image", 
                               font=("Helvetica", 18),
                               bg='#34495E',
                               fg='#ECF0F1')
enhanced_img_label_title.pack(pady=10)

enhanced_img_label = Label(enhanced_frame, bg='#34495E')
enhanced_img_label.pack(expand=True)

# Add placeholder to enhanced image frame
enhanced_placeholder = create_placeholder_icon(enhanced_img_label)

# Modern status bar
status_bar = Label(root, 
                  text="Ready", 
                  bd=1, 
                  relief='sunken', 
                  anchor='w',
                  bg='#34495E',
                  fg='#ECF0F1',
                  font=("Helvetica", 10))
status_bar.pack(side='bottom', fill='x', pady=5)

root.mainloop()
