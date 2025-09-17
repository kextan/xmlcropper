import tkinter as tk
from tkinter import filedialog, simpledialog, messagebox, Menu
from PIL import Image, ImageTk
import xml.etree.ElementTree as ET
import os
import shutil

APPDATA = os.getenv("APPDATA")
CACHE_DIR = os.path.join(APPDATA, "XMLCIMGTemp", "cache")
os.makedirs(CACHE_DIR, exist_ok=True)


class SpriteMapper:
    def __init__(self, root):
        self.root = root
        self.root.title("Kextans Basic XML Cropper")

        # main canvas
        self.canvas = tk.Canvas(root, bg="grey", cursor="cross")
        self.canvas.pack(fill=tk.BOTH, expand=True)

        # bottom preview bar
        self.preview_frame = tk.Frame(root, height=100, bg="#ddd")
        self.preview_frame.pack(fill=tk.X, side=tk.BOTTOM)

        self.preview_canvas = tk.Canvas(self.preview_frame, bg="#eee", height=100)
        self.preview_canvas.pack(fill=tk.X, expand=True, side=tk.LEFT)

        # scroll for previews if many
        self.scroll_x = tk.Scrollbar(
            self.preview_frame, orient="horizontal", command=self.preview_canvas.xview
        )
        self.scroll_x.pack(fill=tk.X, side=tk.BOTTOM)
        self.preview_canvas.configure(xscrollcommand=self.scroll_x.set)

        self.preview_inner = tk.Frame(self.preview_canvas, bg="#eee")
        self.preview_canvas.create_window((0, 0), window=self.preview_inner, anchor="nw")

        self.preview_inner.bind(
            "<Configure>",
            lambda e: self.preview_canvas.configure(
                scrollregion=self.preview_canvas.bbox("all")
            ),
        )

        # menu
        self.menubar = tk.Menu(root)
        root.config(menu=self.menubar)

        filemenu = tk.Menu(self.menubar, tearoff=0)
        filemenu.add_command(label="Open Image", command=self.open_image)
        filemenu.add_command(label="Open XML", command=self.open_xml)
        filemenu.add_command(label="Save XML", command=self.save_xml)
        filemenu.add_separator()
        filemenu.add_command(label="Exit", command=self.on_close)
        self.menubar.add_cascade(label="File", menu=filemenu)

        self.image = None
        self.tkimage = None
        self.sprites = []  # dicts: {"name","x","y","w","h","rect_id","preview","cachefile"}
        self.filename = None
        self.cache_image_path = None

        # rectangle drawing
        self.start_x = None
        self.start_y = None
        self.rect = None

        self.canvas.bind("<ButtonPress-1>", self.on_button_press)
        self.canvas.bind("<B1-Motion>", self.on_move_press)
        self.canvas.bind("<ButtonRelease-1>", self.on_button_release)
        self.canvas.bind("<Button-3>", self.on_right_click_rect)

        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

    def open_image(self):
        filepath = filedialog.askopenfilename(filetypes=[("Image Files", "*.png;*.jpg;*.jpeg")])
        if not filepath:
            return

        # save a copy into cache
        img_name = os.path.basename(filepath)
        self.cache_image_path = os.path.join(CACHE_DIR, img_name)
        shutil.copyfile(filepath, self.cache_image_path)

        self.image = Image.open(self.cache_image_path)
        self.tkimage = ImageTk.PhotoImage(self.image)
        self.canvas.delete("all")
        self.canvas.create_image(0, 0, anchor="nw", image=self.tkimage)
        self.sprites = []
        for widget in self.preview_inner.winfo_children():
            widget.destroy()
        self.filename = img_name

    def open_xml(self):
        xmlfile = filedialog.askopenfilename(filetypes=[("XML Files", "*.xml")])
        if not xmlfile:
            return
        if not self.image:
            messagebox.showerror("Error", "Open the corresponding image first!")
            return
        tree = ET.parse(xmlfile)
        root = tree.getroot()
        self.sprites = []
        for widget in self.preview_inner.winfo_children():
            widget.destroy()
        self.canvas.delete("all")
        self.canvas.create_image(0, 0, anchor="nw", image=self.tkimage)

        for sprite_el in root.findall("sprite"):
            name = sprite_el.attrib.get("name")
            x = int(sprite_el.attrib.get("x", 0))
            y = int(sprite_el.attrib.get("y", 0))
            w = int(sprite_el.attrib.get("width", 0))
            h = int(sprite_el.attrib.get("height", 0))
            rect_id = self.canvas.create_rectangle(x, y, x + w, y + h, outline="red")

            crop = self.image.crop((x, y, x + w, y + h))
            cachefile = os.path.join(CACHE_DIR, f"{name}.png")
            crop.save(cachefile)
            thumb = crop.copy()
            thumb.thumbnail((80, 80))
            tkthumb = ImageTk.PhotoImage(thumb)

            frame = tk.Frame(self.preview_inner, bg="white", padx=5, pady=5)
            frame.pack(side=tk.LEFT, padx=5, pady=5)
            img_label = tk.Label(frame, image=tkthumb)
            img_label.image = tkthumb
            img_label.pack()
            text_label = tk.Label(frame, text=name, bg="white")
            text_label.pack()

            menu = Menu(self.root, tearoff=0)
            menu.add_command(label="Delete", command=lambda n=name: self.delete_crop(n))

            def on_right_click(event, m=menu):
                m.tk_popup(event.x_root, event.y_root)

            frame.bind("<Button-3>", on_right_click)
            img_label.bind("<Button-3>", on_right_click)
            text_label.bind("<Button-3>", on_right_click)

            self.sprites.append(
                {
                    "name": name,
                    "x": x,
                    "y": y,
                    "w": w,
                    "h": h,
                    "rect_id": rect_id,
                    "preview": frame,
                    "cachefile": cachefile,
                }
            )

    def on_button_press(self, event):
        if not self.image:
            return
        self.start_x = self.canvas.canvasx(event.x)
        self.start_y = self.canvas.canvasy(event.y)
        self.rect = self.canvas.create_rectangle(
            self.start_x, self.start_y, self.start_x, self.start_y, outline="red"
        )

    def on_move_press(self, event):
        if not self.image or not self.rect:
            return
        cur_x, cur_y = (self.canvas.canvasx(event.x), self.canvas.canvasy(event.y))
        self.canvas.coords(self.rect, self.start_x, self.start_y, cur_x, cur_y)

    def on_button_release(self, event):
        if not self.image or not self.rect:
            return
        end_x, end_y = (self.canvas.canvasx(event.x), self.canvas.canvasy(event.y))
        x1, y1, x2, y2 = map(int, [self.start_x, self.start_y, end_x, end_y])

        if x2 < x1: x1, x2 = x2, x1
        if y2 < y1: y1, y2 = y2, y1

        if x2 > x1 and y2 > y1:
            name = simpledialog.askstring("Sprite Name", "Enter name for this part:")
            if name and name.strip():
                name = name.strip()
                w, h = x2 - x1, y2 - y1
                crop = self.image.crop((x1, y1, x2, y2))

                cachefile = os.path.join(CACHE_DIR, f"{name}.png")
                crop.save(cachefile)

                thumb = crop.copy()
                thumb.thumbnail((80, 80))
                tkthumb = ImageTk.PhotoImage(thumb)

                frame = tk.Frame(self.preview_inner, bg="white", padx=5, pady=5)
                frame.pack(side=tk.LEFT, padx=5, pady=5)
                img_label = tk.Label(frame, image=tkthumb)
                img_label.image = tkthumb
                img_label.pack()
                text_label = tk.Label(frame, text=name, bg="white")
                text_label.pack()

                menu = Menu(self.root, tearoff=0)
                menu.add_command(label="Delete", command=lambda n=name: self.delete_crop(n))

                def on_right_click(event, m=menu):
                    m.tk_popup(event.x_root, event.y_root)

                frame.bind("<Button-3>", on_right_click)
                img_label.bind("<Button-3>", on_right_click)
                text_label.bind("<Button-3>", on_right_click)

                self.sprites.append(
                    {
                        "name": name,
                        "x": x1,
                        "y": y1,
                        "w": w,
                        "h": h,
                        "rect_id": self.rect,
                        "preview": frame,
                        "cachefile": cachefile,
                    }
                )
            else:
                self.canvas.delete(self.rect)
        else:
            self.canvas.delete(self.rect)
        self.rect = None

    def on_right_click_rect(self, event):
        """Right-click while drawing cancels the rectangle."""
        if self.rect:
            self.canvas.delete(self.rect)
            self.rect = None

    def delete_crop(self, name):
        for sprite in self.sprites:
            if sprite["name"] == name:
                self.canvas.delete(sprite["rect_id"])
                sprite["preview"].destroy()
                if os.path.exists(sprite["cachefile"]):
                    os.remove(sprite["cachefile"])
        self.sprites = [s for s in self.sprites if s["name"] != name]

    def save_xml(self):
        if not self.sprites:
            messagebox.showerror("Error", "No sprites defined!")
            return
        filepath = filedialog.asksaveasfilename(
            defaultextension=".xml", filetypes=[("XML Files", "*.xml")]
        )
        if filepath:
            root = ET.Element("spritesheet", attrib={"image": self.filename})
            for s in self.sprites:
                ET.SubElement(
                    root,
                    "sprite",
                    attrib={
                        "name": s["name"],
                        "x": str(s["x"]),
                        "y": str(s["y"]),
                        "width": str(s["w"]),
                        "height": str(s["h"]),
                    },
                )
            tree = ET.ElementTree(root)
            tree.write(filepath, encoding="utf-8", xml_declaration=True)
            messagebox.showinfo("Saved", f"XML saved to {filepath}")

    def on_close(self):
        if os.path.exists(CACHE_DIR):
            shutil.rmtree(CACHE_DIR, ignore_errors=True)
        self.root.destroy()


if __name__ == "__main__":
    root = tk.Tk()
    app = SpriteMapper(root)
    root.mainloop()
