import ttkbootstrap as ttkb
from ttkbootstrap.constants import *
from tkinter import filedialog, messagebox
from tkinter import ttk
from PIL import Image, ImageDraw, ImageFont, ImageTk
import os

class ImageGridApp:
    def __init__(self, root):
        self.root = root
        self.root.title("图片拼接工具")
        self.root.geometry("1400x900")

        self.images = []
        self.image_paths = []
        self.final_image = None
        self.zoom_scale = 1.0

        self.thumbnail_labels = []
        self.dragging_label = None

        title = ttkb.Label(root, text="图片拼接工具", font=("", 20))
        title.pack(pady=10)

        frame_main = ttkb.Frame(root)
        frame_main.pack(fill=BOTH, expand=True, padx=20, pady=10)

        frame_left = ttkb.Frame(frame_main)
        frame_left.pack(side=LEFT, fill=Y)

        frame_right = ttkb.Frame(frame_main)
        frame_right.pack(side=RIGHT, fill=BOTH, expand=True)

        frame_select = ttkb.Labelframe(frame_left, text="图片选择", padding=10)
        frame_select.pack(fill=X, pady=10)

        self.select_button = ttkb.Button(frame_select, text="选择图片", command=self.select_images, bootstyle=PRIMARY)
        self.select_button.pack(fill=X, pady=5)

        self.image_count_label = ttkb.Label(frame_select, text="已选择 0 张图片")
        self.image_count_label.pack(fill=X, pady=5)

        frame_params = ttkb.Labelframe(frame_left, text="参数设置", padding=10)
        frame_params.pack(fill=BOTH, expand=True, pady=10)

        self.rows_entry = self.add_param(frame_params, "行数:", 0)
        self.cols_entry = self.add_param(frame_params, "列数:", 1)

        self.add_label_var = ttkb.BooleanVar()
        ttkb.Checkbutton(frame_params, text="是否加标签", variable=self.add_label_var, bootstyle=SUCCESS).grid(row=2, column=0, columnspan=2, pady=5, sticky='w')

        self.label_entry_var = ttkb.StringVar()
        self.add_combobox(frame_params, "标签内容:", self.label_entry_var, [
            "(a) (b) (c) (d) (e) (f) (g) (h) (i)",
            "(1) (2) (3) (4) (5) (6) (7) (8) (9)",
            "(i) (ii) (iii) (iv) (v) (vi) (vii) (viii) (ix)",
            "(A) (B) (C) (D) (E) (F) (G) (H) (I)",
            "(I) (II) (III) (IV) (V) (VI) (VII) (VIII) (IX)"
        ], 3)

        self.label_position_var = ttkb.StringVar()
        self.add_combobox(frame_params, "标签位置:", self.label_position_var, [
            "上左", "上中", "上右",
            "左上", "左中", "左下",
            "下左", "下中", "下右",
            "右上", "右中", "右下"
        ], 4)

        self.font_choice_var = ttkb.StringVar()
        self.add_combobox(frame_params, "字体选择:", self.font_choice_var, [
            "Times New Roman", "Arial", "SimSun", "微软雅黑", "黑体", "Calibri", "Cambria"
        ], 5)

        self.font_size_entry = self.add_param(frame_params, "字体大小:", 6)
        self.label_space_entry = self.add_param(frame_params, "标签区域大小:", 7)
        self.dpi_entry = self.add_param(frame_params, "保存DPI:", 8)
        self.dpi_entry.insert(0, "600")  # 默认600DPI

        frame_buttons = ttkb.Frame(frame_right)
        frame_buttons.pack(fill=X, pady=10)

        self.preview_button = ttkb.Button(frame_buttons, text="预览", command=self.preview, bootstyle=INFO)
        self.preview_button.pack(side=LEFT, padx=10, expand=True, fill=X)

        self.clear_button = ttkb.Button(frame_buttons, text="清空图片", command=self.clear_images, bootstyle=SECONDARY)
        self.clear_button.pack(side=LEFT, padx=10, expand=True, fill=X)

        self.save_button = ttkb.Button(frame_buttons, text="保存", command=self.save, bootstyle=SUCCESS)
        self.save_button.pack(side=LEFT, padx=10, expand=True, fill=X)

        self.frame_preview = ttkb.Labelframe(frame_right, text="预览区域", padding=10)
        self.frame_preview.pack(fill=BOTH, expand=True, pady=10)

        self.canvas = ttkb.Frame(self.frame_preview)
        self.canvas.pack(fill=BOTH, expand=True)

    def add_param(self, frame, text, row):
        ttkb.Label(frame, text=text).grid(row=row, column=0, sticky='e', pady=5)
        entry = ttkb.Entry(frame)
        entry.grid(row=row, column=1, pady=5)
        return entry

    def add_combobox(self, frame, text, var, values, row):
        ttkb.Label(frame, text=text).grid(row=row, column=0, sticky='e', pady=5)
        combo = ttkb.Combobox(frame, textvariable=var, values=values)
        combo.grid(row=row, column=1, pady=5)
        combo.current(0)

    def select_images(self):
        files = filedialog.askopenfilenames(title="选择图片", filetypes=[("Image Files", "*.png *.jpg *.jpeg *.tiff *.bmp")])
        if files:
            self.image_paths.extend(files)
            self.images.extend([Image.open(f) for f in files])
            self.image_count_label.config(text=f"已选择 {len(self.images)} 张图片")
            self.update_thumbnails()

    def clear_images(self):
        self.images.clear()
        self.image_paths.clear()
        self.final_image = None
        self.image_count_label.config(text="已选择 0 张图片")
        for widget in self.canvas.winfo_children():
            widget.destroy()

    def update_thumbnails(self):
        for widget in self.canvas.winfo_children():
            widget.destroy()
        self.thumbnail_labels.clear()

        for idx, img in enumerate(self.images):
            thumb = img.copy()
            thumb.thumbnail((200, 200))  # 【缩略图放大】
            thumb_tk = ImageTk.PhotoImage(thumb)
            lbl = ttkb.Label(self.canvas, image=thumb_tk, relief="solid", borderwidth=1)
            lbl.image = thumb_tk
            lbl.grid(row=idx // 5, column=idx % 5, padx=5, pady=5)
            lbl.bind("<Button-1>", lambda e, i=idx: self.start_drag(e, i))
            lbl.bind("<ButtonRelease-1>", self.end_drag)
            lbl.bind("<B1-Motion>", self.drag_motion)   # 【拖动中交换】
            self.thumbnail_labels.append(lbl)

    def start_drag(self, event, index):
        self.dragging_label = index
        self.thumbnail_labels[index].configure(borderwidth=3, bootstyle="primary")

    def drag_motion(self, event):
        if self.dragging_label is None:
            return

        x, y = event.widget.winfo_pointerxy()
        target = event.widget.winfo_containing(x, y)

        if isinstance(target, ttkb.Label) and target in self.thumbnail_labels:
            target_index = self.thumbnail_labels.index(target)
            if target_index != self.dragging_label:
                self.images[self.dragging_label], self.images[target_index] = self.images[target_index], self.images[self.dragging_label]
                self.dragging_label = target_index
                self.update_thumbnails()

    def end_drag(self, event):
        if self.dragging_label is not None:
            self.thumbnail_labels[self.dragging_label].configure(borderwidth=1, bootstyle="secondary")
        self.dragging_label = None

    def preview(self):
        if not self.images:
            messagebox.showerror("错误", "请先选择图片！")
            return

        try:
            rows = int(self.rows_entry.get())
            cols = int(self.cols_entry.get())
            label_space = int(self.label_space_entry.get()) if self.add_label_var.get() else 0
        except:
            messagebox.showerror("错误", "请正确输入行列数和标签区域大小！")
            return

        min_width = min(img.width for img in self.images)
        min_height = min(img.height for img in self.images)

        pos = self.label_position_var.get()
        main_dir = pos[0] if pos else '上'
        sub_dir = pos[1] if len(pos) > 1 else '中'

        unit_width, unit_height = min_width, min_height
        if main_dir in ['上', '下']:
            unit_height += label_space
        elif main_dir in ['左', '右']:
            unit_width += label_space

        canvas_width = cols * unit_width
        canvas_height = rows * unit_height

        canvas = Image.new('RGB', (canvas_width, canvas_height), color=(255, 255, 255))
        draw = ImageDraw.Draw(canvas)

        fontname = {
            "Times New Roman": "times.ttf",
            "SimSun": "simsun.ttc",
            "微软雅黑": "msyh.ttc",
            "黑体": "simhei.ttf",
            "Arial": "arial.ttf",
            "Calibri": "calibri.ttf",
            "Cambria": "cambria.ttc"
        }.get(self.font_choice_var.get(), "arial.ttf")

        try:
            font = ImageFont.truetype(fontname, int(self.font_size_entry.get()))
        except:
            font = ImageFont.load_default()

        labels = self.label_entry_var.get().split()
        label_list = labels * ((len(self.images) + len(labels) - 1) // len(labels))
        label_list = label_list[:len(self.images)]

        for idx, img in enumerate(self.images):
            if idx >= rows * cols:
                break

            row_idx = idx // cols
            col_idx = idx % cols
            base_x = col_idx * unit_width
            base_y = row_idx * unit_height

            if main_dir == '上':
                img_x, img_y = base_x, base_y + label_space
            elif main_dir == '下':
                img_x, img_y = base_x, base_y
            elif main_dir == '左':
                img_x, img_y = base_x + label_space, base_y
            elif main_dir == '右':
                img_x, img_y = base_x, base_y
            else:
                img_x, img_y = base_x, base_y

            img_resized = img.resize((min_width, min_height))
            canvas.paste(img_resized, (img_x, img_y))

            if self.add_label_var.get():
                text = label_list[idx]
                bbox = font.getbbox(text)
                text_w = bbox[2] - bbox[0]
                text_h = bbox[3] - bbox[1]

                if main_dir in ['上', '下']:
                    tx = base_x + {
                        '左': 5,
                        '中': (min_width - text_w) // 2,
                        '右': (min_width - text_w - 5)
                    }.get(sub_dir, (min_width - text_w) // 2)
                    ty = base_y + (label_space - text_h) // 2 if main_dir == '上' else base_y + min_height + (label_space - text_h) // 2
                else:
                    ty = base_y + {
                        '上': 5,
                        '中': (min_height - text_h) // 2,
                        '下': (min_height - text_h - 5)
                    }.get(sub_dir, (min_height - text_h) // 2)
                    tx = base_x + (label_space - text_w) // 2 if main_dir == '左' else base_x + min_width + (label_space - text_w) // 2

                draw.text((tx, ty), text, fill='black', font=font)

        self.final_image = canvas.copy()
        self.show_final_image()

    def show_final_image(self):
        for widget in self.canvas.winfo_children():
            widget.destroy()

        img = self.final_image.copy()
        img.thumbnail((800, 800))
        img_tk = ImageTk.PhotoImage(img)
        lbl = ttkb.Label(self.canvas, image=img_tk)
        lbl.image = img_tk
        lbl.pack()

    def save(self):
        if self.final_image is None:
            messagebox.showerror("错误", "请先预览生成拼接图！")
            return

        file_path = filedialog.asksaveasfilename(defaultextension=".png", filetypes=[("PNG", "*.png"), ("JPEG", "*.jpg"), ("TIFF", "*.tiff")])
        if file_path:
            try:
                dpi_value = int(self.dpi_entry.get())
            except:
                dpi_value = 600
            self.final_image.save(file_path, dpi=(dpi_value, dpi_value))
            messagebox.showinfo("成功", f"拼接图已保存，DPI={dpi_value}！")

if __name__ == "__main__":
    app = ttkb.Window(themename="cosmo")
    ImageGridApp(app)
    app.mainloop()
