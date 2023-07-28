import os
import asyncio
import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter import ttk
from controllers.file_controller import FileController
from models.helpers.file_extensions import FileExtensions
from models.helpers.formatter_extensions import FormatterExtensions


class FileView:
    def __init__(self) -> None:
        self.controller = FileController()


    def start(self):
        self.root = tk.Tk()
        self.root.title("Duplicate File Finder")
        self.root.geometry("800x400")

        # Frame to contain the buttons side by side
        button_frame = tk.Frame(self.root)
        button_frame.pack()

        btn_browse = ttk.Button(button_frame, text="Browse Directory", command=self.browse_directory)
        btn_browse.pack(side=tk.LEFT, padx=5, pady=5)

        self.delete_button = tk.Button(button_frame, text="Delete", state=tk.DISABLED, command=self.delete_selected)
        self.delete_button.pack(side=tk.LEFT, padx=5, pady=5)

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

        self.root.mainloop()


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
                self.delete_button.config(state=tk.DISABLED)
            else:
                self.delete_button.config(state=tk.NORMAL)

    def delete_selected(self):
        selected_item = self.treeview.focus()
        if selected_item:
            item = self.treeview.item(selected_item)
            file_name = item["values"][0]#[item["values"][0] for item in self.treeview.get_children(selected_item)]
            if messagebox.askyesno("Delete Files", f"Do you want to delete {file_name}?"):
                #for file_path in file_paths:
                FileExtensions.delete_file(file_name)
                self.populate_treeview()
                self.delete_button.config(state=tk.DISABLED)

    # def handle_duplicates(self, duplicate_files):
    #     for files in duplicate_files:
    #         if messagebox.askyesno("Duplicate Found", f"Found {len(files)} duplicates of {os.path.basename(files[0])}. Do you want to delete them?"):
    #             for file_path in files:
    #                 if FileExtensions.delete_file(file_path):
    #                     print(f"Deleted {file_path}")
    #                 else:
    #                     print(f"Failed to delete {file_path}")