import tkinter as tk


class GUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.geometry('840x725')
        self._create_view(self.root)

    def _create_view(self, root):
        self.f_top = tk.Frame(root, bg='#fdfdf0', relief='groove', bd=3, padx=5, pady=5)
        self.f_bottom = tk.Frame(root, bg='#fdfdf0', relief='groove', padx=5, pady=5)

        self.f_top_left = tk.Frame(self.f_top, height=200, width=170, bg='#f8f4e6', relief='groove')
        self.f_top_right = tk.Frame(self.f_top, bg='#f8f4e6', relief='groove', bd=3)


        self.top_panel_right_view(self.f_top_right)

        self.to_panel_left_view(self.f_top_left)

        self.f_top.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        self.f_bottom.pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True)

        self.f_top_left.pack(side=tk.LEFT, fill=tk.BOTH, expand=False)
        self.f_top_right.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

    def to_panel_left_view(self, parent):
        self.photo_canvas = tk.Canvas(self.f_top_left, bg="orange", height=200, width=150, relief="ridge")
        self.photo_canvas.place(x=0, y=0)

    def top_panel_right_view(self, parent):
        self.name_label = tk.Label(parent, text='NAME ', bg='#fdfdf0')
        self.height_label = tk.Label(parent, text='HEIGHT ', bg='#fdfdf0')
        self.weight_label = tk.Label(parent, text='WEIGHT ', bg='#fdfdf0')
        self.name_text_box = tk.Entry(parent,width=20)
        self.height_text_box = tk.Entry(parent, width=20)
        self.weight_text_box = tk.Entry(parent, width=20)

        self.name_label.grid(row=0, column=0, sticky=tk.E)
        self.height_label.grid(row=1, column=0, sticky=tk.E)
        self.weight_label.grid(row=2, column=0, sticky=tk.E)

        self.name_text_box.grid(row=0, column=1, sticky=tk.E)
        self.height_text_box.grid(row=1, column=1, sticky=tk.E)
        self.weight_text_box.grid(row=2, column=1, sticky=tk.E)


    def run(self):
        self.root.mainloop()

def main():
    gui = GUI()
    gui.run()

if __name__ == '__main__':
    main()


