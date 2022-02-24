from tkinter import CENTER, E, N, S, StringVar, Tk, W, filedialog, ttk


class CV_GUI:
    def __init__(self, root) -> None:

        root.title("Compress Video")
        mainframe = ttk.Frame(root, padding="3 3 12 12")
        mainframe.grid(column=0, row=0, sticky=(N, W, E, S))
        root.columnconfigure(0, weight=1)
        root.rowconfigure(0, weight=1)

        self.infile = StringVar()
        self.tsize = StringVar()
        self.outfile = StringVar()

        ttk.Label(mainframe, text="Input File:").grid(column=1, row=1, sticky=E)
        ttk.Label(mainframe, textvariable=self.infile).grid(column=2, row=1, sticky=(W, E))
        ttk.Button(mainframe, text="Select", command=self.get_infile).grid(
            column=3, row=1, sticky=E
        )

        ttk.Label(mainframe, text="Target Filesize:").grid(column=1, row=2, sticky=E)
        size_entry = ttk.Entry(mainframe, width=7, textvariable=self.tsize)
        size_entry.grid(column=2, row=2, sticky=(W, E))

        ttk.Label(mainframe, text="Output File:").grid(column=1, row=3, sticky=E)
        ofile_entry = ttk.Entry(mainframe, width=7, textvariable=self.outfile)
        ofile_entry.grid(column=2, row=3, sticky=(W, E))
        ttk.Button(mainframe, text="Select", command=self.get_outfile).grid(
            column=3, row=3, sticky=E
        )

        ttk.Button(
            mainframe,
            text="Add",
            command=self.add_to_queue,
        ).grid(column=2, row=4, sticky=(W, E))

        self.queue = ttk.Treeview(mainframe)
        self.queue["columns"] = ("infile", "tsize", "outfile", "status")
        self.queue.column("#0", width=1)
        self.queue.column("infile", anchor=CENTER, width=100)
        self.queue.column("tsize", anchor=CENTER, width=50)
        self.queue.column("outfile", anchor=CENTER, width=100)
        self.queue.column("status", anchor=CENTER)
        self.queue.heading("#0", text="", anchor=CENTER)
        self.queue.heading("infile", text="Input Filename", anchor=CENTER)
        self.queue.heading("tsize", text="Size", anchor=CENTER)
        self.queue.heading("outfile", text="Output Filename", anchor=CENTER)
        self.queue.heading("status", text="Status", anchor=CENTER)
        self.queue.grid(column=1, columnspan=3, row=5, sticky=(W, E))

        for child in mainframe.winfo_children():
            child.grid_configure(padx=5, pady=5)

    def get_infile(self) -> None:
        self.infile.set(filedialog.askopenfilename())

    def get_outfile(self) -> None:
        pass

    def add_to_queue(self) -> None:
        self.queue.insert(
            "",
            "end",
            None,
            values=(self.infile.get(), self.tsize.get(), self.outfile.get()),
        )
        self.infile.set("")
        self.outfile.set("")


root = Tk()
cv = CV_GUI(root)
root.mainloop()
