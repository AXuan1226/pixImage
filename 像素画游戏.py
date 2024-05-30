import tkinter as tk
from tkinter import colorchooser, simpledialog, filedialog, messagebox, ttk
import os
from PIL import Image, ImageDraw
import time
import pyperclip

class PixelArtGame(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("像素画游戏")
        self.geometry("1600x1200")
        self.configure(bg="#f0f0f0")

        self.canvas_width = 800
        self.canvas_height = 800

        self.selected_color = "#000000"
        self.grid_size = (8, 8)
        self.undo_stack = []
        self.redo_stack = []
        self.eraser_size = 1
        self.is_eraser_mode = False

        self.brush_colors = {}  # 保存常用画笔
        self.author_name = "axuan"
        self.game_hint = "这是测试游戏"
        self.is_dragging = False

        self.init_ui()

    def init_ui(self):
        # 顶部框架
        top_frame = tk.Frame(self, bg="#f0f0f0")
        top_frame.pack(side=tk.TOP, pady=10)

        # 显示作者名字和提示语
        self.author_label = tk.Label(top_frame, text=f"作者：{self.author_name}", font=("Arial", 14), bg="#f0f0f0")
        self.author_label.pack(side=tk.LEFT, padx=10)
        
        self.hint_label = tk.Label(top_frame, text=self.game_hint, font=("Arial", 14), bg="#f0f0f0")
        self.hint_label.pack(side=tk.LEFT, padx=10)

        # 选择画纸大小
        self.grid_size_var = tk.StringVar(value="8x8")
        grid_size_menu = ttk.Combobox(top_frame, textvariable=self.grid_size_var, values=["8x8", "16x16", "32x32", "64x64"], state="readonly")
        grid_size_menu.pack(side=tk.LEFT, padx=10)
        grid_size_menu.bind("<<ComboboxSelected>>", lambda event: self.change_grid_size(event.widget.get()))

        custom_grid_button = tk.Button(top_frame, text="自定义大小", command=self.custom_grid_size, bg="#4CAF50", fg="white", font=("Arial", 12), relief="flat")
        custom_grid_button.pack(side=tk.LEFT, padx=10)

        reset_button = tk.Button(top_frame, text="重新开始", command=self.reset_canvas, bg="#f44336", fg="white", font=("Arial", 12), relief="flat")
        reset_button.pack(side=tk.LEFT, padx=10)

        self.color_button = tk.Menubutton(top_frame, text="画笔颜色", bg="#2196F3", fg="white", font=("Arial", 12), relief="flat")
        self.color_menu = tk.Menu(self.color_button, tearoff=0)
        self.color_button["menu"] = self.color_menu
        self.color_button.pack(side=tk.LEFT, padx=10)

        eraser_button = tk.Button(top_frame, text="橡皮擦", command=self.choose_eraser, bg="#FF9800", fg="white", font=("Arial", 12), relief="flat")
        eraser_button.pack(side=tk.LEFT, padx=10)

        export_button = tk.Button(top_frame, text="导出图片", command=self.export_image, bg="#9C27B0", fg="white", font=("Arial", 12), relief="flat")
        export_button.pack(side=tk.LEFT, padx=10)

        undo_button = tk.Button(top_frame, text="撤销", command=self.undo, bg="#607D8B", fg="white", font=("Arial", 12), relief="flat")
        undo_button.pack(side=tk.LEFT, padx=10)

        redo_button = tk.Button(top_frame, text="恢复", command=self.redo, bg="#8BC34A", fg="white", font=("Arial", 12), relief="flat")
        redo_button.pack(side=tk.LEFT, padx=10)

        save_brush_button = tk.Button(top_frame, text="保存画笔", command=self.save_brush_color, bg="#FFC107", fg="white", font=("Arial", 12), relief="flat")
        save_brush_button.pack(side=tk.LEFT, padx=10)

        advanced_settings_button = tk.Button(top_frame, text="高级设置", command=self.advanced_settings, bg="#00BCD4", fg="white", font=("Arial", 12), relief="flat")
        advanced_settings_button.pack(side=tk.LEFT, padx=10)

        export_binary_button = tk.Button(top_frame, text="导出二进制数模", command=self.export_binary, bg="#FF5722", fg="white", font=("Arial", 12), relief="flat")
        export_binary_button.pack(side=tk.LEFT, padx=10)

        # 侧边框架
        side_frame = tk.Frame(self, bg="#f0f0f0")
        side_frame.pack(side=tk.LEFT, pady=10)

        self.click_mode = tk.BooleanVar(value=True)
        single_click_checkbox = tk.Checkbutton(side_frame, text="单击", variable=self.click_mode, bg="#f0f0f0", font=("Arial", 12))
        single_click_checkbox.pack(anchor=tk.W)

        self.drag_mode = tk.BooleanVar(value=False)
        long_press_checkbox = tk.Checkbutton(side_frame, text="长按", variable=self.drag_mode, bg="#f0f0f0", font=("Arial", 12))
        long_press_checkbox.pack(anchor=tk.W)

        # 画布框架
        self.canvas_frame = tk.Frame(self, bg="#f0f0f0")
        self.canvas_frame.pack(expand=True)

        self.canvas = tk.Canvas(self.canvas_frame, bg="white", width=self.canvas_width, height=self.canvas_height)
        self.canvas.pack()

        self.update_canvas_position()

        self.create_grid()

        self.bind("<Configure>", lambda event: self.update_canvas_position())

    def update_canvas_position(self):
        self.canvas.update()
        canvas_x = (self.winfo_width() - self.canvas_width) // 2
        canvas_y = (self.winfo_height() - self.canvas_height - 50) // 2  # 50 is approximate height of top frame
        self.canvas_frame.place(x=canvas_x, y=canvas_y)

    def create_grid(self):
        self.cell_width = self.canvas_width // self.grid_size[0]
        self.cell_height = self.canvas_height // self.grid_size[1]
        self.cells = {}

        for y in range(self.grid_size[1]):
            for x in range(self.grid_size[0]):
                x1 = x * self.cell_width
                y1 = y * self.cell_height
                x2 = x1 + self.cell_width
                y2 = y1 + self.cell_height

                cell_id = self.canvas.create_rectangle(x1, y1, x2, y2, fill="white", outline="black")
                self.cells[(x, y)] = cell_id

        self.canvas.bind("<Button-1>", self.start_paint)
        self.canvas.bind("<B1-Motion>", self.paint_cell)
        self.canvas.bind("<ButtonRelease-1>", self.stop_paint)
        self.canvas.bind("<Button-3>", self.clear_cell)

    def start_paint(self, event):
        self.is_dragging = True
        self.paint_cell(event)

    def stop_paint(self, event):
        self.is_dragging = False

    def paint_cell(self, event):
        if not self.is_dragging and self.drag_mode.get():
            return
        x = event.x // self.cell_width
        y = event.y // self.cell_height

        if (x, y) in self.cells:
            if self.is_eraser_mode:
                self.apply_eraser(x, y)
            else:
                previous_color = self.canvas.itemcget(self.cells[(x, y)], "fill")
                self.canvas.itemconfig(self.cells[(x, y)], fill=self.selected_color)
                self.undo_stack.append(((x, y), previous_color, self.selected_color))
                self.redo_stack.clear()

    def apply_eraser(self, x, y):
        eraser_range = range(-self.eraser_size // 2, self.eraser_size // 2 + 1)
        for dy in eraser_range:
            for dx in eraser_range:
                nx, ny = x + dx, y + dy
                if (nx, ny) in self.cells:
                    previous_color = self.canvas.itemcget(self.cells[(nx, ny)], "fill")
                    self.canvas.itemconfig(self.cells[(nx, ny)], fill="white")
                    self.undo_stack.append(((nx, ny), previous_color, "white"))
                    self.redo_stack.clear()

    def clear_cell(self, event):
        x = event.x // self.cell_width
        y = event.y // self.cell_height

        if (x, y) in self.cells:
            previous_color = self.canvas.itemcget(self.cells[(x, y)], "fill")
            self.canvas.itemconfig(self.cells[(x, y)], fill="white")
            self.undo_stack.append(((x, y), previous_color, "white"))
            self.redo_stack.clear()

    def undo(self):
        if self.undo_stack:
            x, y, previous_color, new_color = self.undo_stack.pop()
            self.canvas.itemconfig(self.cells[(x, y)], fill=previous_color)
            self.redo_stack.append(((x, y), new_color, previous_color))

    def redo(self):
        if self.redo_stack:
            x, y, new_color, previous_color = self.redo_stack.pop()
            self.canvas.itemconfig(self.cells[(x, y)], fill=new_color)
            self.undo_stack.append(((x, y), previous_color, new_color))

    def change_grid_size(self, size):
        width, height = map(int, size.split('x'))
        self.grid_size = (width, height)
        self.canvas.delete("all")
        self.create_grid()
        self.update_canvas_position()

    def custom_grid_size(self):
        width = simpledialog.askinteger("自定义宽度", "请输入画纸宽度（格子数）：", minvalue=1)
        height = simpledialog.askinteger("自定义高度", "请输入画纸高度（格子数）：", minvalue=1)
        if width and height:
            self.grid_size = (width, height)
            self.canvas.delete("all")
            self.create_grid()
            self.update_canvas_position()

    def reset_canvas(self):
        confirm = messagebox.askokcancel("重新开始", "确定要重新开始吗？所有进度将会丢失。")
        if confirm:
            self.canvas.delete("all")
            self.create_grid()
            self.undo_stack.clear()
            self.redo_stack.clear()

    def choose_color(self):
        color = colorchooser.askcolor()[1]
        if color:
            self.selected_color = color
            self.is_eraser_mode = False

    def choose_eraser(self):
        size = simpledialog.askinteger("橡皮擦大小", "请输入橡皮擦大小（1-10）：", minvalue=1, maxvalue=10)
        if size:
            self.eraser_size = size
            self.is_eraser_mode = True

    def save_brush_color(self):
        name = simpledialog.askstring("保存画笔颜色", "请输入画笔颜色名称：")
        if name:
            self.brush_colors[name] = self.selected_color
            self.update_color_menu()

    def update_color_menu(self):
        self.color_menu.delete(0, tk.END)
        self.color_menu.add_command(label="选择颜色", command=self.choose_color)
        for name, color in self.brush_colors.items():
            self.color_menu.add_command(label=name, command=lambda color=color: self.set_brush_color(color))

    def set_brush_color(self, color):
        self.selected_color = color
        self.is_eraser_mode = False

    def export_image(self):
        export_dir = "img"
        if not os.path.exists(export_dir):
            os.makedirs(export_dir)

        default_name = time.strftime("%Y%m%d%H%M%S") + ".png"
        file_path = filedialog.asksaveasfilename(initialdir=export_dir, initialfile=default_name, defaultextension=".png",
                                                 filetypes=[("PNG 文件", "*.png")])

        if file_path:
            self.save_image(file_path)

    def save_image(self, file_path):
        image = Image.new("RGB", (self.canvas_width, self.canvas_height), "white")
        draw = ImageDraw.Draw(image)

        for (x, y), cell_id in self.cells.items():
            cell_color = self.canvas.itemcget(cell_id, "fill")
            x1 = x * self.cell_width
            y1 = y * self.cell_height
            x2 = x1 + self.cell_width
            y2 = y1 + self.cell_height

            draw.rectangle([x1, y1, x2, y2], fill=cell_color, outline="black")

        image.save(file_path)
        messagebox.showinfo("导出成功", f"图片已保存为 {file_path}")

    def advanced_settings(self):
        vip_code = simpledialog.askstring("VIP设置", "请输入高级VIP码：")
        if vip_code == "your_vip_code":  # 假设your_vip_code是正确的VIP码
            new_author = simpledialog.askstring("修改作者", "请输入新的作者名字：")
            new_hint = simpledialog.askstring("修改提示语", "请输入新的提示语：")
            if new_author:
                self.author_name = new_author
                self.author_label.config(text=f"作者：{self.author_name}")
            if new_hint:
                self.game_hint = new_hint
                self.hint_label.config(text=self.game_hint)

    def export_binary(self):
        self.convert_module_interface()  # 留出接口供后期实现

    def convert_module_interface(self):
        binary_window = tk.Toplevel(self)
        binary_window.title("导出二进制数模")
        binary_window.geometry("600x400")

        conversion_methods = ["列行", "行列", "逐行", "逐列"]
        method_var = tk.StringVar(value=conversion_methods[0])
        method_label = tk.Label(binary_window, text="取模方式：", font=("Arial", 12))
        method_label.pack()
        for method in conversion_methods:
            rb = tk.Radiobutton(binary_window, text=method, variable=method_var, value=method, font=("Arial", 12))
            rb.pack(anchor=tk.W)

        binary_modes = ["阴码", "阳码"]
        mode_var = tk.StringVar(value=binary_modes[0])
        mode_label = tk.Label(binary_window, text="阴阳码：", font=("Arial", 12))
        mode_label.pack()
        for mode in binary_modes:
            rb = tk.Radiobutton(binary_window, text=mode, variable=mode_var, value=mode, font=("Arial", 12))
            rb.pack(anchor=tk.W)

        export_button = tk.Button(binary_window, text="导出", command=lambda: self.export_binary_data(method_var.get(), mode_var.get()))
        export_button.pack()

    def export_binary_data(self, method, mode):
        binary_data = self.convert_to_binary(method, mode)
        binary_window = tk.Toplevel(self)
        binary_window.title("导出二进制数模")
        binary_window.geometry("600x400")
        text_widget = tk.Text(binary_window, wrap="none")
        text_widget.pack(expand=True, fill=tk.BOTH)
        text_widget.insert(tk.END, binary_data)

        copy_button = tk.Button(binary_window, text="复制到剪贴板", command=lambda: self.copy_to_clipboard(binary_data))
        copy_button.pack()

    def convert_to_binary(self, method, mode):
        data = []
        for y in range(self.grid_size[1]):
            for x in range(self.grid_size[0]):
                cell_color = self.canvas.itemcget(self.cells[(x, y)], "fill")
                data.append('1' if cell_color != "white" else '0')
        binary_data = "const uint8_t Data[] = {\n" + ", ".join(data) + "\n};\n"
        binary_data += f"const Image Img = {{{self.grid_size[0]}, {self.grid_size[1]}, Data}};"
        return binary_data

    def copy_to_clipboard(self, text):
        pyperclip.copy(text)
        messagebox.showinfo("复制成功", "已复制到剪贴板")

if __name__ == "__main__":
    app = PixelArtGame()
    app.mainloop()
