import tkinter as tk, webbrowser
from tkinter import ttk, filedialog
from linuxcmdscan.scanner import RepositoryScanner
from linuxcmdscan.exporters import export_all

def launch_ui():
    r=tk.Tk(); r.title("linuxcmdscan")
    p=tk.StringVar()
    ttk.Entry(r,textvariable=p,width=80).grid(row=0,column=0)
    ttk.Button(r,text="Browse",command=lambda:p.set(filedialog.askdirectory())).grid(row=0,column=1)
    def scan():
        res=RepositoryScanner().scan(p.get())
        export_all(res)
        webbrowser.open("reports/linuxcmdscan_report.html")
    ttk.Button(r,text="Scan",command=scan).grid(row=1,column=0)
    r.mainloop()