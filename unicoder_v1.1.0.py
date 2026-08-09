import tkinter as tk
import re
import sys
import base64
import random
from tkinter import filedialog, ttk
import pywinstyles
from PIL import Image

class CyberDecoder:
    def __init__(self, root):
        self.root = root
        
        try:
            import os
            if hasattr(sys, '_MEIPASS'):
                icon_path = os.path.join(sys._MEIPASS, "unicoder_logo.ico")
            else:
                icon_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "unicoder_logo.ico")
            
            if os.path.exists(icon_path):
                self.root.iconbitmap(icon_path)
        except:
            pass
            
        self.root.title("UNICODER v1.1.0")
        self.root.geometry("1180x880")
        self.root.configure(bg="#030305")
        
        try:
            raw_icon = (
                b"iVBORw0KGgoAAAANSUhEUgAAACAAAAAgCAYAAABzenr0AAAABHNCSVQICAgIfAhkiAAAALVJREFU"
                b"WI3t100KwzAMBOCwreX+1+6S0gYshXbChm9yH8wPloi3ZLN28VpET5IetfM8Al6Al+AleAlegpfg"
                b"JXgJXoKX4CV4CV7i6b8mET0T4D5egpfgJXgJXoKX4CV4CV6Cl+Alegle4um/JhEAnvMIgMc8AuAx"
                b"jwB4zCMAHvMIgMc8AuAxjwB4zCMAHvMIgMc8AuAxjwB4zCMAHvMIgMc8AuAxjwB4zCMAHvMInmP5"
                b"A88b0XhW6mX3AAAAAElFTkSuQmCC"
            )
            self.app_img = tk.PhotoImage(data=base64.b64decode(raw_icon))
            self.root.iconphoto(True, self.app_img)
        except:
            pass
            
        pywinstyles.apply_style(self.root, "dark")
        
        self.byte_array = bytearray()
        self.SCALE = 2
        self.w_val = 64
        self.h_val = 64
        
        self.radio_mode = 1
        self.frame_skip_bytes = 0
        self.line_shift_bits = 0
        self.frame_len_shift = 0
        
        self.frames = []
        self.current_frame = 0
        self.is_playing = False
        self.fps = 50
        
        self.load_custom_styles()
        self.setup_ui()

    def load_custom_styles(self):
        st = ttk.Style()
        st.theme_use('default')
        st.configure("TNotebook", background="#030305", borderwidth=0, highlightthickness=0)
        st.configure("TNotebook.Tab", background="#121624", foreground="#00F0FF", font=("Consolas", 9, "bold"), borderwidth=1, focuscolor="")
        st.map("TNotebook.Tab", background=[("selected", "#080911")], foreground=[("selected", "#FF0055")])

    def draw_hud(self, canvas_obj, w, h):
        canvas_obj.create_rectangle(0, 0, w, h, fill="#080911", outline="#1A2233")
        for i in range(0, w, 20): canvas_obj.create_line(i, 0, i, h, fill="#0D111A")
        for j in range(0, h, 20): canvas_obj.create_line(0, j, w, j, fill="#0D111A")
            
        canvas_obj.create_polygon(0, 0, 15, 0, 0, 15, fill="#030305", outline="#1A2233")
        canvas_obj.create_polygon(w, h, w-15, h, w, h-15, fill="#030305", outline="#1A2233")
        canvas_obj.create_polygon(w, 0, w-20, 0, w, 20, fill="#FCEE09", outline="")
        canvas_obj.create_line(15, 4, w-25, 4, fill="#00F0FF")
        canvas_obj.create_line(4, 15, 4, h-15, fill="#FF0055", width=2)
        canvas_obj.create_line(w-4, 25, w-4, h-15, fill="#00F0FF")

    def make_btn(self, canvas_obj, btn_w, btn_h, text, cmd, is_main=False):
        safe_str = "".join([c for c in text if c.isalnum()])[:5].lower()
        btn_tag = f"tag_{safe_str}_{random.randint(100, 999)}"
        
        c_bg = "#FCEE09" if is_main else "#121624"
        c_brd = "#FCEE09" if is_main else "#00F0FF"
        c_txt = "#000000" if is_main else "#00F0FF"
        
        canvas_obj.create_polygon(0, 0, btn_w, 0, btn_w, btn_h-8, btn_w-8, btn_h, 0, btn_h, fill=c_bg, outline="", tags=btn_tag)
        canvas_obj.create_line(0, 0, btn_w, 0, btn_w, btn_h-8, btn_w-8, btn_h, 0, btn_h, 0, 0, fill=c_brd, width=1, joinstyle="miter", tags=btn_tag)
        canvas_obj.create_text(btn_w // 2, btn_h // 2, text=text, fill=c_txt, font=("Consolas", 8, "bold"), tags=btn_tag)
        
        canvas_obj.tag_raise(btn_tag)
        canvas_obj.tag_bind(btn_tag, "<Button-1>", lambda event: cmd())
        canvas_obj.tag_bind(btn_tag, "<Enter>", lambda event: canvas_obj.config(cursor="hand2"))
        canvas_obj.tag_bind(btn_tag, "<Leave>", lambda event: canvas_obj.config(cursor=""))

    def make_hud_slider(self, prnt, txt, min_v, max_v, df_v, cb):
        f = tk.Frame(prnt, bg="#080911")
        tk.Label(f, text=txt, bg="#080911", fg="#547585", font=("Consolas", 8, "bold")).pack(anchor="w", padx=10, pady=(2, 0))
        c = tk.Canvas(f, bg="#080911", width=310, height=22, highlightthickness=0, bd=0)
        c.pack(fill="x", pady=(1, 5), padx=10)
        c.create_line(5, 11, 305, 11, fill="#1A2233", width=2)
        hx = 5 + int(((df_v - min_v) / (max_v - min_v) if max_v != min_v else 0) * 300)
        f_br = c.create_line(5, 11, hx, 11, fill="#00F0FF", width=2)
        hd = c.create_polygon(hx-5, 3, hx+5, 4, hx+5, 18, hx-5, 18, fill="#00F0FF")
        def move(e):
            nx = max(5, min(305, e.x))
            c.coords(hd, nx-5, 3, nx+5, 4, nx+5, 18, nx-5, 18); c.coords(f_br, 5, 11, nx, 11)
            cb(min_v + int(((nx - 5) / 300) * (max_v - min_v)))
        c.tag_bind(hd, "<B1-Motion>", move)
        return f

    def setup_ui(self):
        self.sidebar_canvas = tk.Canvas(self.root, bg="#030305", width=380, height=840, highlightthickness=0, bd=0)
        self.sidebar_canvas.pack(side="left", padx=15, pady=15); self.draw_hud(self.sidebar_canvas, 380, 840)
        
        self.notebook = ttk.Notebook(self.sidebar_canvas, width=340, height=430)
        self.notebook.place(x=20, y=20)
        
        self.tab_dec = tk.Frame(self.notebook, bg="#080911")
        self.tab_enc = tk.Frame(self.notebook, bg="#080911")
        
        self.notebook.add(self.tab_dec, text=" HEX DECODING ")
        self.notebook.add(self.tab_enc, text=" HEX ENCODING ")
        
        tk.Label(self.tab_dec, text="// DECODER_CORE_v2.0", bg="#080911", fg="#FF0055", font=("Consolas", 10, "bold")).pack(anchor="w", pady=(8, 2), padx=10)
        tk.Label(self.tab_dec, text="TARGET: MEMORY_STREAM", bg="#080911", fg="#FFFFFF", font=("Consolas", 12, "bold")).pack(anchor="w", pady=(0, 8), padx=10)
        
        c_b1 = tk.Canvas(self.tab_dec, bg="#080911", width=320, height=38, highlightthickness=0)
        c_b1.pack(fill="x", pady=(2, 6), padx=10)
        self.make_btn(c_b1, 320, 38, "💾  LOAD DUMP FILE (.txt / .h)", self.load_file, True)
        
        self.txt_input = tk.Text(self.tab_dec, bg="#06080F", fg="#00F0FF", insertbackground="#FF0055", bd=1, relief="solid", font=("Consolas", 9), height=3)
        self.txt_input.pack(fill="x", pady=(2, 6), padx=10)
        self.txt_input.insert("1.0", "0x00, 0x00")
        
        c_b2 = tk.Canvas(self.tab_dec, bg="#080911", width=320, height=30, highlightthickness=0)
        c_b2.pack(fill="x", pady=(2, 8), padx=10)
        self.make_btn(c_b2, 320, 30, "⚡  INJECT TEXT CODE BUFFER", self.parse_text)
        
        self.make_hud_slider(self.tab_dec, "DELAY (SPEED)", 10, 200, 50, self.update_delay).pack(fill="x", pady=2)
        self.make_hud_slider(self.tab_dec, "FRAME_SKIP (VERT)", 0, 16, 0, self.update_skip).pack(fill="x", pady=2)
        self.make_hud_slider(self.tab_dec, "ALIGN_SHIFT (BYTES)", -8, 8, 0, self.update_len_shift).pack(fill="x", pady=2)
        
        ctf = tk.Frame(self.tab_dec, bg="#080911")
        ctf.pack(fill="x", pady=(8, 4), padx=10)
        c_p1 = tk.Canvas(ctf, bg="#080911", width=140, height=26, highlightthickness=0); c_p1.pack(side="left")
        self.make_btn(c_p1, 140, 26, "▶ PLAY", self.play_anim)
        c_p2 = tk.Canvas(ctf, bg="#080911", width=140, height=26, highlightthickness=0); c_p2.pack(side="right")
        self.make_btn(c_p2, 140, 26, "⏸ PAUSE", self.pause_anim)
        
                # ZAKŁADKA 2: HEX ENCODING
        tk.Label(self.tab_enc, text="// IMAGE_ENCODER_v1.0", bg="#080911", fg="#00F0FF", font=("Consolas", 10, "bold")).pack(anchor="w", pady=(8, 2), padx=10)
        tk.Label(self.tab_enc, text="CONVERT IMAGE TO HEX", bg="#080911", fg="#FFFFFF", font=("Consolas", 12, "bold")).pack(anchor="w", pady=(0, 5), padx=10)
        
        c_b_img = tk.Canvas(self.tab_enc, bg="#080911", width=320, height=36, highlightthickness=0)
        c_b_img.pack(fill="x", pady=(5, 5), padx=10)
        self.make_btn(c_b_img, 320, 36, "🖼️  LOAD & CONVERT SINGLE IMAGE", self.convert_image_to_hex, True)

        c_b_batch = tk.Canvas(self.tab_enc, bg="#080911", width=320, height=36, highlightthickness=0)
        c_b_batch.pack(fill="x", pady=(5, 10), padx=10)
        self.make_btn(c_b_batch, 320, 36, "🎞️  BATCH CONVERT TO ANIMATION", self.batch_convert_images)
        
        tk.Label(self.tab_enc, text="Selected assets will be scaled to X/Y bounds", bg="#080911", fg="#547585", font=("Consolas", 9)).pack(anchor="w", padx=10, pady=2)
        tk.Label(self.tab_enc, text="and merged sequentially into a loopable stream.", bg="#080911", fg="#547585", font=("Consolas", 9)).pack(anchor="w", padx=10, pady=2)

        self.geom_frame = tk.Frame(self.sidebar_canvas, bg="#080911")
        self.geom_frame.place(x=20, y=475, width=340, height=350)
        
        tk.Label(self.geom_frame, text=">> DEVICE_MATRIX_GEOMETRY", bg="#080911", fg="#00F0FF", font=("Consolas", 10, "bold")).pack(anchor="w", pady=(5, 5), padx=10)
        
        df = tk.Frame(self.geom_frame, bg="#080911")
        df.pack(anchor="w", pady=(2, 8), padx=10)
        tk.Label(df, text="X: ", bg="#080911", fg="#547585", font=("Consolas", 9, "bold")).pack(side="left")
        self.w_entry = tk.Entry(df, bg="#06080F", fg="#FCEE09", bd=1, relief="solid", font=("Consolas", 10, "bold"), justify="center", width=5)
        self.w_entry.insert(0, "64"); self.w_entry.pack(side="left", padx=(0, 20))
        tk.Label(df, text="Y: ", bg="#080911", fg="#547585", font=("Consolas", 9, "bold")).pack(side="left")
        self.h_entry = tk.Entry(df, bg="#06080F", fg="#FCEE09", bd=1, relief="solid", font=("Consolas", 10, "bold"), justify="center", width=5)
        self.h_entry.insert(0, "64"); self.h_entry.pack(side="left")
        
        self.make_hud_slider(self.geom_frame, "X-WIDTH SCALE", 4, 500, 64, lambda v: self.update_dim(v, True)).pack(fill="x", pady=2)
        self.make_hud_slider(self.geom_frame, "Y-HEIGHT SCALE", 4, 500, 64, lambda v: self.update_dim(v, False)).pack(fill="x", pady=2)
        tk.Label(self.geom_frame, text=">> BITSTREAM_DECODE_PROTOCOL", bg="#080911", fg="#00F0FF", font=("Consolas", 10, "bold")).pack(anchor="w", pady=(8, 2), padx=10)
        self.c_rad = tk.Canvas(self.geom_frame, bg="#080911", width=320, height=20, highlightthickness=0)
        self.c_rad.pack(fill="x", pady=2, padx=10)
        self.p_lsb = self.c_rad.create_polygon(5, 4, 17, 10, 5, 16, fill="#030305", outline="#1A2233", width=2)
        self.t_lsb = self.c_rad.create_text(27, 10, text="STANDARD_LSB", fill="#3F5866", font=("Consolas", 9, "bold"), anchor="w")
        self.p_msb = self.c_rad.create_polygon(165, 4, 177, 10, 165, 16, fill="#FF0055", outline="#FF0055", width=2)
        self.t_msb = self.c_rad.create_text(187, 10, text="REVERSE_MSB", fill="#FFFFFF", font=("Consolas", 9, "bold"), anchor="w")
        self.c_rad.create_rectangle(5, 2, 145, 18, fill="", outline="", tags="r_lsb")
        self.c_rad.create_rectangle(165, 2, 305, 18, fill="", outline="", tags="r_msb")
        self.c_rad.tag_bind("r_lsb", "<Button-1>", lambda e: self.toggle_radio(0))
        self.c_rad.tag_bind("r_msb", "<Button-1>", lambda e: self.toggle_radio(1))
        
        self.status_lbl = tk.Label(self.geom_frame, text="SYSTEM_IDLE // READY", bg="#080911", fg="#00F0FF", font=("Consolas", 10, "bold"))
        self.status_lbl.pack(anchor="w", pady=(8, 0), padx=10)

        self.display_container = tk.Canvas(self.root, bg="#030305", width=740, height=850, highlightthickness=0, bd=0)
        self.display_container.pack(side="right", fill="both", expand=True, padx=15, pady=15); self.display_container.bind("<Configure>", self.resize)
        self.canvas = tk.Canvas(self.display_container, width=450, height=450, bg="#000000", highlightthickness=1, highlightbackground="#1A2233", bd=0)
        self.canvas.pack(expand=True, padx=30, pady=60)

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
            self.notebook.select(self.tab_dec)
        except Exception as e:
            self.status_lbl.config(text=f"CONVERT ERROR: {str(e)[:15]}", fg="#FF0055")
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
            self.notebook.select(self.tab_dec)
        except Exception as e:
            self.status_lbl.config(text=f"BATCH ERROR: {str(e)[:15]}", fg="#FF0055")

    def toggle_radio(self, val):
        self.radio_mode = val
        self.root.after(1, lambda: self.c_rad.itemconfig(self.p_lsb, fill="#FF0055" if val==0 else "#030305", outline="#FF0055" if val==0 else "#1A2233"))
        self.root.after(1, lambda: self.c_rad.itemconfig(self.t_lsb, fill="#FFFFFF" if val==0 else "#3F5866"))
        self.root.after(1, lambda: self.c_rad.itemconfig(self.p_msb, fill="#FF0055" if val==1 else "#030305", outline="#FF0055" if val==1 else "#1A2233"))
        self.root.after(1, lambda: self.c_rad.itemconfig(self.t_msb, fill="#FFFFFF" if val==1 else "#3F5866"))
        self.slice_frames()

    def update_dim(self, v, is_w):
        if is_w: 
            self.w = v
            self.w_entry.delete(0, tk.END)
            self.w_entry.insert(0, str(v))
        else: 
            self.h = v
            self.h_entry.delete(0, tk.END)
            self.h_entry.insert(0, str(v))
        self.slice_frames()

    def update_delay(self, v): self.fps = v
    def update_skip(self, v): self.frame_skip_bytes = v; self.slice_frames()
    def update_len_shift(self, v): self.frame_len_shift = v; self.slice_frames()

    def resize(self, e):
        self.display_container.delete("hud"); self.draw_hud(self.display_container, e.width, e.height)
        self.display_container.tag_lower("all"); self.display_container.create_text(25, 35, text="// MONITOR_STREAM_OUTPUT", fill="#00F0FF", font=("Consolas", 11, "bold"), anchor="w", tags="hud")

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
                return True
        return False

    def proc(self, text, src):
        hx = re.findall(r"0x[0-9a-fA-F]{2}", text)
        if not hx: self.status_lbl.config(text="ERROR: NO_HEX_STREAM", fg="#FF0055"); return
        self.byte_array = bytearray([int(h, 16) for h in hx])
        auto = self.auto_interpret(len(self.byte_array))
        self.slice_frames()
        self.status_lbl.config(text=f"{'AUTO' if auto else 'RAW'} // FRAMES: {len(self.frames)} // SRC: {src[:10].upper()}", fg="#00F0FF")

    def sync_text(self):
        try: 
            self.w, self.h = int(self.w_entry.get()), int(self.h_entry.get())
            self.slice_frames()
        except: pass
	
#	i fucking hate python
#       if anyone is trying to fix this bullshit. good luck.	
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
        self.canvas = tk.Canvas(self.display_container, width=self.h*self.SCALE, height=self.w*self.SCALE, bg="#000000", highlightthickness=1, highlightbackground="#1A2233", bd=0)
        self.canvas.pack(expand=True, padx=30, pady=60)
        
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
                        self.canvas.create_rectangle(rx*self.SCALE, ry*self.SCALE, (rx+1)*self.SCALE, (ry+1)*self.SCALE, fill="#FF0055", outline="")

if __name__ == "__main__":
    root = tk.Tk()
    app = CyberDecoder(root)
    root.mainloop()
