import tkinter as tk
from tkinter import ttk


class gui(ttk.Frame):
    def __init__(self):
        super().__init__()

        self.initUI()

    def initUI(self):

        self.master.title("whyknot")
        self.pack(fill=tk.BOTH, expand=True)

        self.columnconfigure(1, weight=1)
        self.columnconfigure(3, pad=7)
        self.rowconfigure(3, weight=1)
        self.rowconfigure(5, pad=7)

        lbl = ttk.Label(self, text="whyknot")
        lbl.grid(sticky=tk.W, pady=4, padx=5)

        area = tk.Text(self)
        area.grid(
            row=1,
            column=0,
            columnspan=2,
            rowspan=4,
            padx=5,
            sticky=tk.E + tk.W + tk.S + tk.N,
        )

        abtn = ttk.Button(self, text="Select file")
        abtn.grid(row=1, column=3)

        cbtn = ttk.Button(self, text="Close")
        cbtn.grid(row=2, column=3, pady=4)

        hbtn = ttk.Button(self, text="Help")
        hbtn.grid(row=5, column=0, padx=5)

        obtn = ttk.Button(self, text="Check knot")
        obtn.grid(row=5, column=3)


def main():

    root = tk.Tk()
    root.geometry("350x300+300+300")
    app = gui()
    root.mainloop()


if __name__ == "__main__":
    main()
