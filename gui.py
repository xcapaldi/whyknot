import tkinter as tk


class Gui:
    def __init__(self, root):
        self.root = root
        self.entry = tk.Entry(root)
        stvar = tk.StringVar()
        stvar.set("one")

        self.canvas = tk.Canvas(root, width=300, height=200, background="white")
        self.canvas.grid(row=0, column=1)

        frame = tk.Frame(self.root)
        frame.grid(row=0, column=0, sticky="n")

        self.option = tk.OptionMenu(frame, stvar, "one", "two", "three")
        label1 = tk.Label(frame, text="Figure").grid(row=0, column=0, sticky="nw")
        label2 = tk.Label(frame, text="X").grid(row=1, column=0, sticky="w")
        label3 = tk.Label(frame, text="Y").grid(row=2, column=0, sticky="w")
        self.option.grid(row=0, column=1, sticky="nwe")
        entry = tk.Entry(frame).grid(row=1, column=1, sticky=tk.E + tk.W)
        entry1 = tk.Entry(frame).grid(row=2, column=1, sticky=tk.E)
        Button1 = tk.Button(frame, text="Draw").grid(row=3, column=1, sticky="we")
        figure1 = self.canvas.create_rectangle(80, 80, 120, 120, fill="blue")

        # Grid.columnconfigure(self.root,1,weight=1, size=200)


if __name__ == "__main__":
    root = tk.Tk()
    gui = Gui(root)
    root.mainloop()
