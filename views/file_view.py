import os
import asyncio
import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter import ttk
from controllers.file_controller import FileController
from models.services.logging_service import LogService
from models.helpers.file_extensions import FileExtensions
from models.helpers.formatter_extensions import FormatterExtensions
from PIL import Image, ImageTk

class FileView:
    def __init__(self) -> None:
        self.controller = FileController()
        self.log_service = LogService()



    def start(self):
        self.root = tk.Tk()
        ico = Image.open('resources/images/delete.png')
        topIcon = ImageTk.PhotoImage(ico)
        self.root.wm_iconphoto(False, topIcon)
        self.root.title("Duplicate File Finder")
        self.root.geometry("800x400")

        # Frame to contain the buttons side by side
        button_frame = tk.Frame(self.root)
        button_frame.pack()

        self.menubar = tk.Menu(self.root)
        file_menu = tk.Menu(self.menubar, tearoff=False)
        file_menu.add_command(label="Browse", command=self.browse_directory)
        file_menu.add_command(label="About", command=self.show_about)
        file_menu.add_command(label="Exit", command=self.close)
        self.menubar.add_cascade(menu=file_menu, label="File")
        staging = tk.Menu(self.menubar, tearoff=False)
        staging.add_command(label="Set Directory", command=self.set_staging)
        staging.add_command(label="Clear All", command=self.clear_staging)
        staging.add_command(label="Show Files", command=self.show_staging)
        self.menubar.add_cascade(menu=staging, label="Staging")
        self.menubar.add_command(label="Browse Directory", command=self.browse_directory)
        self.menubar.add_command(label="Delete", state=tk.DISABLED, command=self.delete_selected)
        #btn_browse = ttk.Button(button_frame, text="Browse Directory", command=self.browse_directory)
        #btn_browse.pack(side=tk.LEFT, padx=5, pady=5)

        #self.delete_button = tk.Button(button_frame, text="Delete", state=tk.DISABLED, command=self.delete_selected)
        #self.delete_button.pack(side=tk.LEFT, padx=5, pady=5)

        self.treeview = ttk.Treeview(self.root, columns=("file_path", "size", "last_updated"))
        self.treeview.heading("#0", text="File Name")
        self.treeview.heading("file_path", text="File Path")
        self.treeview.heading("size", text="Size")
        self.treeview.heading("last_updated", text="Last Modified")
        #self.treeview.heading("duplicate_count", text="Duplicates Count")
        self.treeview.pack(fill="both", expand=True)

        # align the "size" and "last modified" columns to the center
        self.treeview.column("size", anchor="center")
        self.treeview.column("last_updated", anchor="center")

        self.populate_treeview()

        self.treeview.bind("<ButtonRelease-1>", self.on_item_select)

        self.progress_bar = ttk.Progressbar(self.root, orient="horizontal", length=300, mode="determinate")
        self.progress_bar.pack(pady=10)
        self.root.config(menu=self.menubar)
        self.root.mainloop()

    def close(self):
        self.root.quit()

    def show_about(self):
        tk.messagebox.showinfo("About Us", "This program is developed for final project in 2nd semester.")

    def set_staging(self):
        directory = filedialog.askdirectory()
        if directory:
            file = open("resources/staging/staginglocation.txt", "w")
            file.write(directory)
            tk.messagebox.showinfo("Success", "Staging location set")
    def clear_staging(self):
        tk.messagebox.showinfo("TBD", "---")

    def show_staging(self):
        tk.messagebox.showinfo("TBD", "---")

    def browse_directory(self):
        directory = filedialog.askdirectory()
        if directory:
            # start the file scanning process asynchronously
            self.progress_bar["value"] = 0
            asyncio.run(self.scan_directory_async(directory))

            self.populate_treeview()

            if not self.controller.duplicate_files:
            #     self.handle_duplicates(self.controller.duplicate_files)
            #     messagebox.showinfo("Duplicate File Finder", "Duplicate files have been handled.")
            # else:
                messagebox.showinfo("Duplicate File Finder", "No duplicates found in the selected directory.")
            self.log_service.handle_insert('scan', directory)

    async def scan_directory_async(self, directory):
        await self.controller.scan_directory_async(directory, self.update_progress)

    def update_progress(self, progress):
        self.progress_bar["value"] = progress
        self.root.update_idletasks()


    def populate_treeview(self):
        self.treeview.delete(*self.treeview.get_children())  # Clear existing data

        grouped_duplicates = self.group_duplicates_by_directory()

        for group_key, files in grouped_duplicates.items():
            group_name = os.path.basename(group_key) if group_key else "No Directory"
            parent_item = self.treeview.insert("", "end", text=group_name)

            for file_path, file_size, last_modified in files:
                self.treeview.insert(parent_item, "end", text=os.path.basename(file_path), 
                                     values=(file_path, FormatterExtensions.format_size(file_size), FormatterExtensions.format_time(last_modified), len(files)))

        # for files in self.controller.duplicate_files:
        #     file_name = os.path.basename(files[0])
        #     parent_item = self.treeview.insert("", "end", text=file_name, values=(files[0], len(files)))

        #     for file_path in files[1:]:
        #         self.treeview.insert(parent_item, "end", text=os.path.basename(file_path), values=(file_path,))

    def group_duplicates_by_directory(self):
        grouped_duplicates = {}
        for files in self.controller.duplicate_files:
            file_name = os.path.basename(files[0])
            for file_path in files:
                if os.path.isfile(file_path):
                    #directory = os.path.dirname(file_path)
                    file_size = os.path.getsize(file_path)
                    last_modified = os.path.getmtime(file_path)
                    grouped_duplicates.setdefault(file_name, []).append((file_path, file_size, last_modified))
        return grouped_duplicates

    def on_item_select(self, event):
        selected_item = self.treeview.focus()
        if selected_item:
            children = self.treeview.get_children(selected_item)
            if children:  # If the item has children, it's a parent node (group)
                self.menubar.entryconfig(4, state=tk.DISABLED) #disable delete menu
            else:
                self.menubar.entryconfig(4, state=tk.NORMAL) #enable delete menu

    def delete_selected(self):
        selected_item = self.treeview.focus()
        if selected_item:
            item = self.treeview.item(selected_item)
            file_name = item["values"][0]#[item["values"][0] for item in self.treeview.get_children(selected_item)]
            if messagebox.askyesno("Delete Files", f"Do you want to delete {file_name}?"):
                #for file_path in file_paths:
                FileExtensions.delete_file(file_name)
                self.log_service.handle_insert('delete', file_name)
                self.populate_treeview()
                self.menubar.entryconfig(4, state=tk.DISABLED)  #disable delete menu

    # def handle_duplicates(self, duplicate_files):
    #     for files in duplicate_files:
    #         if messagebox.askyesno("Duplicate Found", f"Found {len(files)} duplicates of {os.path.basename(files[0])}. Do you want to delete them?"):
    #             for file_path in files:
    #                 if FileExtensions.delete_file(file_path):
    #                     print(f"Deleted {file_path}")
    #                 else:
    #                     print(f"Failed to delete {file_path}")
