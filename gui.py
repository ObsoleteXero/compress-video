import threading
from pathlib import Path
from tkinter import CENTER, DISABLED, NORMAL, E, N, S, StringVar, Tk, W, filedialog, ttk

from main import Compress, parse_filesize


class CV_GUI(Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title("Compress Video")
        mainframe = ttk.Frame(self, padding="3 3 12 12")
        mainframe.grid(column=0, row=0, sticky=(N, W, E, S))
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

        self.infile = StringVar()
        self.tsize = StringVar()
        self.outfile = StringVar()

        # Input file labels and button
        ttk.Label(mainframe, text="Input File:").grid(column=1, row=1, sticky=E)
        ttk.Label(mainframe, textvariable=self.infile).grid(
            column=2, row=1, sticky=(W, E)
        )
        ttk.Button(mainframe, text="Select", command=self.get_infile).grid(
            column=3, row=1, sticky=E
        )

        # Target file size label and input
        ttk.Label(mainframe, text="Target Filesize:").grid(column=1, row=2, sticky=E)
        size_entry = ttk.Entry(mainframe, width=7, textvariable=self.tsize)
        size_entry.grid(column=2, row=2, sticky=(W, E))

        # Output file labels and button
        ttk.Label(mainframe, text="Output File:").grid(column=1, row=3, sticky=E)
        ttk.Label(mainframe, textvariable=self.outfile).grid(
            column=2, row=3, sticky=(W, E)
        )
        ttk.Button(mainframe, text="Select", command=self.get_outfile).grid(
            column=3, row=3, sticky=E
        )

        self.button_add = ttk.Button(
            mainframe, text="Add", command=self.add_to_queue, state=DISABLED
        )
        self.button_add.grid(column=2, row=4, sticky=(W, E))

        # Queue Display Table
        self.queue = ttk.Treeview(mainframe)
        self.queue["columns"] = (
            "infile",
            "inpath",
            "tsize",
            "outfile",
            "outpath",
            "status",
        )
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
        self.queue["displaycolumns"] = ("infile", "tsize", "outfile", "status")
        self.queue.grid(column=1, columnspan=3, row=5, sticky=(W, E))

        self.button_start = ttk.Button(
            mainframe, text="Start", command=self.start, state=DISABLED
        )
        self.button_start.grid(column=2, row=6, sticky=(W, E))

        mainframe.pack()
        for child in mainframe.winfo_children():
            child.grid_configure(padx=5, pady=5)

    def get_infile(self) -> None:
        """Get input file name and set output file name to default"""
        infile = filedialog.askopenfilename()
        if infile:
            infile = Path(infile)
            self.infile.set(infile)
            outfile = infile.with_name(f"compressed_{infile.stem}.mkv")
            self.outfile.set(outfile)
            self.button_add["state"] = NORMAL
        elif not self.infile:
            self.button_add["state"] = DISABLED

    def get_outfile(self) -> None:
        """Get output file name"""
        outfile = filedialog.asksaveasfilename(
            defaultextension="mkv", filetypes=[("Matroska Media Container", "*.mkv")]
        )
        if outfile:
            outfile = Path(outfile).with_suffix(".mkv")
            self.outfile.set(outfile)

    def add_to_queue(self) -> None:
        """Add described task to queue"""
        infile = self.infile.get()
        tsize = self.tsize.get()
        outfile = self.outfile.get()

        if not all((infile, parse_filesize(tsize), outfile)):
            return

        self.queue.insert(
            "",
            "end",
            None,
            values=(Path(infile).name, infile, tsize, Path(outfile).name, outfile),
        )
        self.infile.set("")
        self.outfile.set("")
        self.button_add["state"] = DISABLED
        self.button_start["state"] = NORMAL

    def start(self) -> None:
        self.button_start["state"] = DISABLED
        self.button_add["state"] = DISABLED
        for item in self.queue.get_children():
            if self.queue.set(item, "status") != "Complete":
                self.queue.set(item, "status", "Pending")
        thread = threading.Thread(target=self.process_queue)
        thread.start()

    def process_queue(self) -> None:
        for item in self.queue.get_children():
            if self.queue.set(item, "status") == "Pending":
                infile = self.queue.set(item, "inpath")
                tsize = parse_filesize(self.queue.set(item, "tsize"))
                outfile = self.queue.set(item, "outpath")
                self.task = Compress(infile, tsize, outfile)
                self.thread = threading.Thread(target=self.task.x264)
                self.thread.start()
                self.monitor_progress(item)
                self.thread.join()
        self.button_add["state"] = NORMAL
        self.button_start["state"] = NORMAL

    def monitor_progress(self, queue_item) -> None:
        if self.thread.is_alive():
            self.queue.set(queue_item, "status", self.task.progress)
            self.after(100, lambda: self.monitor_progress(queue_item))
        else:
            self.queue.set(queue_item, "status", "Complete")


if __name__ == "__main__":
    cv = CV_GUI()
    cv.mainloop()
