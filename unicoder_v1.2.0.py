import tkinter as tk
import re
import sys
import base64
import random
import os
from tkinter import filedialog
import customtkinter as ctk
from PIL import Image

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class CyberDecoder:
    def __init__(self, root):
        self.root = root
        
        try:
            import ctypes
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("guts787.unicoder.v1")
        except:
            pass
            
        self.root.title("UNICODER v1.2.0")
        self.root.geometry("1200x950")
        self.root.configure(bg="#1E1F22")
        
        try:
            if hasattr(sys, '_MEIPASS'):
                icon_path = os.path.join(sys._MEIPASS, "unicoder_logo.ico")
            else:
                icon_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "unicoder_logo.ico")
            
            if os.path.exists(icon_path):
                self.root.iconbitmap(icon_path)
        except:
            pass
            
        self.byte_array = bytearray()
        self.SCALE = 2
        self.w = 64
        self.h = 64
        self.radio_mode = 1
        
        self.frames = []
        self.current_frame = 0
        self.is_playing = False
        self.fps = 50
        
        self.frame_skip_bytes = 0
        self.line_shift_bits = 0
        self.frame_len_shift = 0
        
        self.setup_ui()
    def setup_ui(self):
        self.root.grid_columnconfigure(0, weight=0)
        self.root.grid_columnconfigure(1, weight=1)
        self.root.grid_rowconfigure(0, weight=1)

        self.sidebar = ctk.CTkScrollableFrame(self.root, width=420, corner_radius=12, fg_color="#2B2D31", label_text="")
        self.sidebar.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")

        self.tab_view = ctk.CTkTabview(self.sidebar, width=390, height=460)
        self.tab_view._segmented_button.configure(font=("Trebuchet MS", 12, "bold"))
        self.tab_view.pack(padx=10, pady=(5, 5), fill="both", expand=True)

        self.tab_dec = self.tab_view.add("DECODING")
        self.tab_enc = self.tab_view.add("ENCODING")

        ctk.CTkLabel(self.tab_dec, text="MEMORY DECODER ENGINE", font=("Trebuchet MS", 14, "bold"), text_color="#F2F3F5").pack(anchor="w", padx=15, pady=(15, 10))
        
        self.btn_load = ctk.CTkButton(self.tab_dec, text="LOAD DUMP FILE (.txt / .h)", command=self.load_file, font=("Trebuchet MS", 12, "bold"), fg_color="#404249", hover_color="#5865F2", height=40)
        self.btn_load.pack(fill="x", padx=15, pady=8)

        self.txt_input = ctk.CTkTextbox(self.tab_dec, height=85, font=("Lucida Console", 11), fg_color="#1E1F22", text_color="#F2F3F5")
        self.txt_input.pack(fill="x", padx=15, pady=8)
        self.txt_input.insert("1.0", "0x00, 0x00")

        self.btn_inject = ctk.CTkButton(self.tab_dec, text="INJECT CODE BUFFER", command=self.parse_text, font=("Trebuchet MS", 12, "bold"), fg_color="#404249", hover_color="#5865F2", height=40)
        self.btn_inject.pack(fill="x", padx=15, pady=8)

        ctk.CTkLabel(self.tab_dec, text="DELAY (SPEED)", font=("Trebuchet MS", 11, "bold"), text_color="#949BA4").pack(anchor="w", padx=15, pady=(12, 2))
        self.sld_speed = ctk.CTkSlider(self.tab_dec, from_=10, to=200, number_of_steps=190, command=self.update_delay)
        self.sld_speed.set(50); self.sld_speed.pack(fill="x", padx=15, pady=6)

        ctk.CTkLabel(self.tab_dec, text="FRAME_SKIP (VERT)", font=("Trebuchet MS", 11, "bold"), text_color="#949BA4").pack(anchor="w", padx=15, pady=(12, 2))
        self.sld_skip = ctk.CTkSlider(self.tab_dec, from_=0, to=16, number_of_steps=16, command=self.update_skip)
        self.sld_skip.set(0); self.sld_skip.pack(fill="x", padx=15, pady=6)

        ctk.CTkLabel(self.tab_dec, text="ALIGN_SHIFT (BYTES)", font=("Trebuchet MS", 11, "bold"), text_color="#949BA4").pack(anchor="w", padx=15, pady=(12, 2))
        self.sld_shift = ctk.CTkSlider(self.tab_dec, from_=-8, to=8, number_of_steps=16, command=self.update_len_shift)
        self.sld_shift.set(0); self.sld_shift.pack(fill="x", padx=15, pady=6)

        pf = ctk.CTkFrame(self.tab_dec, fg_color="transparent")
        pf.pack(fill="x", padx=15, pady=(16, 10))
        self.btn_play = ctk.CTkButton(pf, text="PLAY", width=165, command=self.play_anim, font=("Trebuchet MS", 13, "bold"), fg_color="#23a55a", hover_color="#1a7d43", height=36)
        self.btn_play.pack(side="left")
        self.btn_pause = ctk.CTkButton(pf, text="PAUSE", width=165, command=self.pause_anim, font=("Trebuchet MS", 13, "bold"), fg_color="#da373c", hover_color="#a92b2f", height=36)
        self.btn_pause.pack(side="right")

        ctk.CTkLabel(self.tab_enc, text="IMAGE RECONVERTER", font=("Trebuchet MS", 14, "bold"), text_color="#F2F3F5").pack(anchor="w", padx=15, pady=(15, 10))
        
        self.btn_single = ctk.CTkButton(self.tab_enc, text="LOAD SINGLE IMAGE", command=self.convert_image_to_hex, font=("Trebuchet MS", 12, "bold"), fg_color="#404249", hover_color="#5865F2", height=42)
        self.btn_single.pack(fill="x", padx=15, pady=8)

        self.btn_batch = ctk.CTkButton(self.tab_enc, text="BATCH CONVERT ANIMATION", command=self.batch_convert_images, font=("Trebuchet MS", 12, "bold"), fg_color="#404249", hover_color="#5865F2", height=42)
        self.btn_batch.pack(fill="x", padx=15, pady=8)

        self.geom_frame = ctk.CTkFrame(self.sidebar, corner_radius=8, fg_color="#1E1F22", width=390)
        self.geom_frame.pack(padx=10, pady=(10, 10), fill="both", expand=True)

        ctk.CTkLabel(self.geom_frame, text="MATRIX GEOMETRY CONFIG", font=("Trebuchet MS", 12, "bold"), text_color="#F2F3F5").pack(anchor="w", padx=20, pady=(12, 6))

        df = ctk.CTkFrame(self.geom_frame, fg_color="transparent")
        df.pack(anchor="w", padx=20, pady=8)
        ctk.CTkLabel(df, text="X: ", font=("Trebuchet MS", 11, "bold"), text_color="#949BA4").pack(side="left")
        self.w_entry = ctk.CTkEntry(df, width=70, height=28, font=("Trebuchet MS", 11, "bold"), justify="center")
        self.w_entry.insert(0, "64"); self.w_entry.pack(side="left", padx=(0, 35))
        ctk.CTkLabel(df, text="Y: ", font=("Trebuchet MS", 11, "bold"), text_color="#949BA4").pack(side="left")
        self.h_entry = ctk.CTkEntry(df, width=70, height=28, font=("Trebuchet MS", 11, "bold"), justify="center")
        self.h_entry.insert(0, "64"); self.h_entry.pack(side="left")

        ctk.CTkLabel(self.geom_frame, text="X-WIDTH SCALE", font=("Trebuchet MS", 10, "bold"), text_color="#949BA4").pack(anchor="w", padx=20, pady=(6, 2))
        self.sld_w = ctk.CTkSlider(self.geom_frame, from_=4, to=500, number_of_steps=496, command=lambda v: self.update_dim(v, True))
        self.sld_w.set(64); self.sld_w.pack(fill="x", padx=20, pady=6)

        ctk.CTkLabel(self.geom_frame, text="Y-HEIGHT SCALE", font=("Trebuchet MS", 10, "bold"), text_color="#949BA4").pack(anchor="w", padx=20, pady=(6, 2))
        self.sld_h = ctk.CTkSlider(self.geom_frame, from_=4, to=500, number_of_steps=496, command=lambda v: self.update_dim(v, False))
        self.sld_h.set(64); self.sld_h.pack(fill="x", padx=20, pady=6)
        ctk.CTkLabel(self.geom_frame, text="BITSTREAM PROTOCOL", font=("Trebuchet MS", 12, "bold"), text_color="#F2F3F5").pack(anchor="w", padx=20, pady=(14, 2))
        
        self.radio_var = tk.IntVar(value=1)
        rb_f = ctk.CTkFrame(self.geom_frame, fg_color="transparent")
        rb_f.pack(fill="x", padx=20, pady=6)
        
        self.rb1 = ctk.CTkRadioButton(rb_f, text="STANDARD_LSB", variable=self.radio_var, value=0, command=self.toggle_radio, font=("Trebuchet MS", 11, "bold"), radiobutton_width=16, radiobutton_height=16)
        self.rb1.pack(side="left", padx=(0, 35))
        self.rb2 = ctk.CTkRadioButton(rb_f, text="REVERSE_MSB", variable=self.radio_var, value=1, command=self.toggle_radio, font=("Trebuchet MS", 11, "bold"), radiobutton_width=16, radiobutton_height=16)
        self.rb2.pack(side="left")
        
        self.status_lbl = ctk.CTkLabel(self.geom_frame, text="SYSTEM_IDLE // READY", font=("Trebuchet MS", 11, "bold"), text_color="#23a55a")
        self.status_lbl.pack(anchor="w", padx=20, pady=15)

        self.display_container = ctk.CTkFrame(self.root, fg_color="#111214", corner_radius=12)
        self.display_container.grid(row=0, column=1, padx=20, pady=20, sticky="nsew")
        
        self.canvas = tk.Canvas(self.display_container, width=450, height=450, bg="#000000", highlightthickness=1, highlightbackground="#2B2D31", bd=0)
        self.canvas.pack(expand=True, padx=30, pady=30)

    def convert_image_to_hex(self):
        fp = filedialog.askopenfilename(filetypes=[("Images", "*.png *.jpg *.jpeg *.bmp")])
        if not fp: return
        try:
            w, h = int(self.w_entry.get()), int(self.h_entry.get())
            img = Image.open(fp).convert("L").resize((w, h), Image.Resampling.LANCZOS)
            hex_list = []
            b_col = (h + 7) // 8
            for col in range(w):
                for b_idx in range(b_col):
                    byte_val = 0
                    for bit_pos in range(8):
                        row = b_idx * 8 + bit_pos
                        if row < h:
                            px = img.getpixel((col, row))
                            bit = 1 if px < 128 else 0
                            if self.radio_mode == 0:
                                byte_val |= (bit << bit_pos)
                            else:
                                byte_val |= (bit << (7 - bit_pos))
                    hex_list.append(f"0x{byte_val:02X}")
            code_str = ", ".join(hex_list)
            self.txt_input.delete("1.0", tk.END)
            self.txt_input.insert("1.0", code_str)
            self.proc(code_str, fp.split('/')[-1])
            self.tab_view.set("DECODING")
        except Exception as e:
            self.status_lbl.configure(text=f"CONVERT ERROR: {str(e)[:15]}", text_color="#da373c")

    def batch_convert_images(self):
        fps = filedialog.askopenfilenames(filetypes=[("Images", "*.png *.jpg *.jpeg *.bmp")])
        if not fps: return
        try:
            sorted_fps = sorted(list(fps))
            w, h = int(self.w_entry.get()), int(self.h_entry.get())
            b_col = (h + 7) // 8
            full_hex_list = []
            
            for fp in sorted_fps:
                img = Image.open(fp).convert("L").resize((w, h), Image.Resampling.LANCZOS)
                for col in range(w):
                    for b_idx in range(b_col):
                        byte_val = 0
                        for bit_pos in range(8):
                            row = b_idx * 8 + bit_pos
                            if row < h:
                                px = img.getpixel((col, row))
                                bit = 1 if px < 128 else 0
                                if self.radio_mode == 0:
                                    byte_val |= (bit << bit_pos)
                                else:
                                    byte_val |= (bit << (7 - bit_pos))
                        full_hex_list.append(f"0x{byte_val:02X}")
                        
            code_str = ", ".join(full_hex_list)
            self.txt_input.delete("1.0", tk.END)
            self.txt_input.insert("1.0", code_str)
            self.proc(code_str, f"BATCH_{len(sorted_fps)}F")
            self.tab_view.set("DECODING")
        except Exception as e:
            self.status_lbl.configure(text=f"BATCH ERROR: {str(e)[:15]}", text_color="#da373c")

    def toggle_radio(self):
        self.radio_mode = self.radio_var.get()
        self.slice_frames()

    def update_dim(self, v, is_w):
        val = int(v)
        if is_w: 
            self.w = val
            self.w_entry.delete(0, tk.END)
            self.w_entry.insert(0, str(val))
        else: 
            self.h = val
            self.h_entry.delete(0, tk.END)
            self.h_entry.insert(0, str(val))
        self.slice_frames()

    def update_delay(self, v): self.fps = int(v)
    def update_skip(self, v): self.frame_skip_bytes = int(v); self.slice_frames()
    def update_len_shift(self, v): self.frame_len_shift = int(v); self.slice_frames()

    def load_file(self):
        fp = filedialog.askopenfilename(filetypes=[("Matrix Data", "*.txt *.h")])
        if fp:
            with open(fp, "r", encoding="utf-8", errors="ignore") as f: self.proc(f.read(), fp.split('/')[-1])

    def parse_text(self): self.proc(self.txt_input.get("1.0", tk.END), "BUFFER")

    def auto_interpret(self, total_bytes):
        for w_sz, h_sz in [(128, 128), (64, 64), (128, 64), (32, 32), (16, 16), (240, 240)]:
            b_frame = (((h_sz + 7) // 8) * w_sz) + self.frame_skip_bytes + self.frame_len_shift
            if b_frame > 0 and total_bytes % b_frame == 0:
                self.w, self.h = w_sz, h_sz
                self.w_entry.delete(0, tk.END); self.w_entry.insert(0, str(w_sz))
                self.h_entry.delete(0, tk.END); self.h_entry.insert(0, str(h_sz))
                self.sld_w.set(w_sz); self.sld_h.set(h_sz)
                return True
        return False

    def proc(self, text, src):
        hx = re.findall(r"0x[0-9a-fA-F]{2}", text)
        if not hx: self.status_lbl.configure(text="ERROR: NO_HEX_STREAM", text_color="#da373c"); return
        self.byte_array = bytearray([int(h, 16) for h in hx])
        auto = self.auto_interpret(len(self.byte_array))
        self.slice_frames()
        self.status_lbl.configure(text=f"{'AUTO' if auto else 'RAW'} // FRAMES: {len(self.frames)} // SRC: {src[:10].upper()}", text_color="#5865F2")

    def sync_text(self):
        try: 
            self.w, self.h = int(self.w_entry.get()), int(self.h_entry.get())
            self.slice_frames()
        except: pass

    def slice_frames(self):
        if not self.byte_array: return
        b_col = (self.h + 7) // 8
        bytes_per_frame = (b_col * self.w) + self.frame_skip_bytes + self.frame_len_shift
        if bytes_per_frame == 0: return
        t_bytes = len(self.byte_array)
        self.frames = [self.byte_array[i*bytes_per_frame:(i+1)*bytes_per_frame] for i in range(t_bytes // bytes_per_frame)] if t_bytes > bytes_per_frame else [self.byte_array]
        self.current_frame = 0; self.render_frame()

    def play_anim(self):
        if not self.frames or self.is_playing or len(self.frames) <= 1: return
        self.is_playing = True; self.loop_anim()

    def pause_anim(self): self.is_playing = False

    def loop_anim(self):
        if not self.is_playing or not self.frames: return
        self.render_frame(); self.current_frame = (self.current_frame + 1) % len(self.frames)
        self.root.after(self.fps, self.loop_anim)

    def render_frame(self):
        self.canvas.destroy()
        self.canvas = tk.Canvas(self.display_container, width=self.h*self.SCALE, height=self.w*self.SCALE, bg="#000000", highlightthickness=1, highlightbackground="#2B2D31", bd=0)
        self.canvas.pack(expand=True, padx=30, pady=30)
        
        if not self.frames: return
        frame_data = self.frames[self.current_frame][self.frame_skip_bytes:]
        iw, ih, mode = self.w, self.h, self.radio_mode
        b_col = (ih + 7) // 8
        
        for col in range(iw):
            for row in range(ih):
                idx = (col * b_col) + (row // 8)
                if idx < len(frame_data):
                    bit = (7 - (row % 8)) if mode == 1 else (row % 8)
                    if (frame_data[idx] >> bit) & 1:
                        rx, ry = ih - 1 - row, col
                        self.canvas.create_rectangle(rx*self.SCALE, ry*self.SCALE, (rx+1)*self.SCALE, (ry+1)*self.SCALE, fill="#5865F2", outline="")

if __name__ == "__main__":
    root = ctk.CTk()
    app = CyberDecoder(root)
    root.mainloop()
