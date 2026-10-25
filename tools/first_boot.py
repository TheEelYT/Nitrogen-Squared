#!/usr/bin/env python3
"""Early Windows first-run import UI. No playable runtime is wired in yet."""
import json
import queue
import threading
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

from n2o_disc import ROOT, default_data_dir, prepare


def main():
    root = tk.Tk()
    root.title("Nitrogen Squared — Initial setup")
    root.geometry("560x290")
    root.minsize(560, 290)
    body = ttk.Frame(root, padding=24)
    body.pack(fill="both", expand=True)
    ttk.Label(body, text="Bring your own N2O disc", font=("Segoe UI", 18, "bold")).pack(anchor="w")
    ttk.Label(body, text="Select the USA CUE file with its BIN beside it.\nKeep the complete disc, including all ten audio tracks.",
              wraplength=500).pack(anchor="w", pady=(16, 12))
    status = tk.StringVar(value="Investigation build: imports disc inputs; gameplay is not available yet.")
    ttk.Label(body, textvariable=status, wraplength=500).pack(anchor="w", pady=(0, 12))
    bar = ttk.Progressbar(body, mode="indeterminate")
    bar.pack(fill="x", pady=(0, 12))
    events = queue.Queue()
    busy = False

    def choose():
        nonlocal busy
        path = filedialog.askopenfilename(title="Select your complete N2O disc", filetypes=[("CUE sheet", "*.cue")])
        if not path:
            return
        from pathlib import Path
        identity = json.loads((ROOT / "configs/disc_usa.json").read_text())
        busy = True
        button.configure(state="disabled")
        bar.start()

        def worker():
            try:
                destination = default_data_dir() / "SLUS-00637"
                prepare(Path(path), destination, identity, lambda s: events.put(("progress", s)))
                events.put(("done", str(destination)))
            except Exception as e:
                events.put(("error", str(e)))
        threading.Thread(target=worker, daemon=False).start()

    def poll():
        nonlocal busy
        try:
            while True:
                kind, text = events.get_nowait()
                if kind == "progress":
                    status.set(text)
                else:
                    busy = False
                    bar.stop()
                    button.configure(state="normal")
                    if kind == "done":
                        status.set("Disc inputs prepared. The playable runtime is still in development.")
                        messagebox.showinfo("Disc prepared", f"Local inputs saved to:\n{text}\n\nKeep the original CUE/BIN in place.")
                    else:
                        status.set("Preparation did not finish. Your disc and existing data were not replaced.")
                        messagebox.showerror("Cannot prepare this disc", text)
        except queue.Empty:
            pass
        root.after(100, poll)

    def close():
        if busy:
            messagebox.showinfo("Disc preparation", "Please wait for preparation to finish before closing setup.")
        else:
            root.destroy()

    button = ttk.Button(body, text="Choose CUE file…", command=choose)
    button.pack(anchor="w")
    root.protocol("WM_DELETE_WINDOW", close)
    poll()
    root.mainloop()


if __name__ == "__main__":
    main()
