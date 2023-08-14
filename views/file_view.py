import os
import asyncio
import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter import ttk
from controllers.file_controller import FileController
from models.constants import CONSTANTS
from models.enums import ActionType
from models.helpers.formatter_extensions import FormatterExtensions
from PIL import Image, ImageTk


class FileView:
    def __init__(self) -> None:
        self.controller = FileController()
        self.is_staging = False
        self.icon = Image.open(CONSTANTS.ICON_PATH)

    def start(self):
        self.root = tk.Tk()
        self.top_icon = ImageTk.PhotoImage(self.icon)
        self.root.wm_iconphoto(False, self.top_icon)
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

        history = tk.Menu(self.menubar, tearoff=False)
        history.add_command(label="View All", command=self.show_history)
        history.add_command(label="Clear All", command=self.clear_history)
        self.menubar.add_cascade(menu=history, label="History")

        staging = tk.Menu(self.menubar, tearoff=False)
        staging.add_command(label="Set Directory", command=self.set_staging)
        staging.add_command(label="Clear All", command=self.clear_staging)
        staging.add_command(label="Show Files", command=self.show_staging)
        self.menubar.add_cascade(menu=staging, label="Staging")

        self.menubar.add_command(label="Browse Directory", command=self.browse_directory)
        self.menubar.add_command(label="Delete", state=tk.DISABLED, command=self.delete_duplicate)
        self.menubar.add_command(label="Stage", state=tk.DISABLED, command=self.move_duplicate)
        self.menubar.add_command(label="Staging Directory: ", state=tk.DISABLED)

        self.treeview = ttk.Treeview(self.root, columns=("file_name", "file_path", "size", "last_updated"))
        self.treeview.heading("file_name", text="File Name")
        self.treeview.heading("file_path", text="File Path")
        self.treeview.heading("size", text="Size")
        self.treeview.heading("last_updated", text="Last Modified")
        self.treeview.pack(fill="both", expand=True)

        # align the "size" and "last modified" columns to the center
        self.treeview.column("size", anchor="center")
        self.treeview.column("last_updated", anchor="center")

        self.populate_treeview()
        self.treeview.bind("<ButtonRelease-1>", self.on_item_select)
        self.progress_bar = ttk.Progressbar(self.root, orient="horizontal", length=300, mode="determinate")
        self.progress_bar.pack(pady=10)
        self.root.config(menu=self.menubar)
        
        self.update_current_directory()
        self.root.mainloop()

    def close(self):
        self.root.quit()

    def show_about(self):
        tk.messagebox.showinfo("About Us", "This program is developed for final project in 2nd semester.")

    def set_staging(self):
        directory = filedialog.askdirectory()
        if directory:
            with open(CONSTANTS.STAGING_PATH, 'w') as file:
                file.write(directory)
                file.flush()  # Flush the buffer to write immediately
                self.update_current_directory()
            tk.messagebox.showinfo("Success", "Staging location set")

    def clear_staging(self):
        dir = self.controller.get_staging_directory()
        if dir:
            response = messagebox.askyesno("Warning", f"This action cannot be undone. Are you sure you want to delete all files in {dir}?")
            if response:
                if self.controller.delete_all_in_directory(dir):
                    messagebox.showinfo("Success", "Staging directory has been cleared.")
                                

    def show_staging(self):
        dir = self.controller.get_staging_directory()
        if dir:
            self.controller.open_directory(dir)

    def update_current_directory(self):
        dir = self.controller.get_staging_directory()
        if dir:
            curr_dir = "Staging Directory: " + dir
            self.menubar.entryconfig(7, label=curr_dir)  # Update Staging directory label
            

    def browse_directory(self):
        directory = filedialog.askdirectory()
        if directory:
            # start the file scanning process asynchronously
            self.progress_bar["value"] = 0
            asyncio.run(self.scan_directory_async(directory))
            if directory == self.controller.get_staging_directory():
                self.is_staging = True
            else:
                self.is_staging = False
            self.populate_treeview()

            if not self.controller.duplicate_files:
                messagebox.showinfo("Duplicate File Finder", "No duplicates found in the selected directory.")
            self.controller.create_log('scan', directory)

    async def scan_directory_async(self, directory):
        await self.controller.scan_directory_async(directory, self.update_progress)

    async def update_progress(self, progress):
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

    def group_duplicates_by_directory(self):
        grouped_duplicates = {}
        for files in self.controller.duplicate_files:
            file_name = os.path.basename(files[0])
            for file_path in files:
                if os.path.isfile(file_path):
                    file_size = os.path.getsize(file_path)
                    last_modified = os.path.getmtime(file_path)
                    grouped_duplicates.setdefault(file_name, []).append((file_path, file_size, last_modified))
        return grouped_duplicates

    def on_item_select(self, event):
        selected_item = self.treeview.focus()
        if selected_item:
            children = self.treeview.get_children(selected_item)
            if children:  # If the item has children, it's a parent node (group)
                self.menubar.entryconfig(5, state=tk.DISABLED) #disable delete menu
                self.menubar.entryconfig(6, state=tk.DISABLED) #disable move menu
            else:
                self.menubar.entryconfig(5, state=tk.NORMAL) #enable delete menu
                if not self.is_staging:
                    self.menubar.entryconfig(6, state=tk.NORMAL) #enable move menu

    def delete_duplicate(self):
        selected_item = self.treeview.focus()
        if selected_item:
            item = self.treeview.item(selected_item)
            file_name = item["values"][0]
            if messagebox.askyesno("Delete Files", f"Do you want to delete {file_name}?"):
                self.controller.delete_file(file_name)
                self.controller.create_log(ActionType.DELETE, file_name)
                self.populate_treeview()
                self.menubar.entryconfig(5, state=tk.DISABLED)  #disable delete menu
                self.menubar.entryconfig(6, state=tk.DISABLED)  #disable move menu

    def move_duplicate(self):
        selected_item = self.treeview.focus()
        if selected_item:
            item = self.treeview.item(selected_item)
            file_name = item["values"][0]
            if messagebox.askyesno("Move File", f"Do you want to move {file_name} to staging?"):
                dir = self.controller.get_staging_directory()
                if dir:
                    self.controller.move_file_to_directory(file_name, dir)
                    self.controller.create_log(ActionType.MOVE, file_name)
                    self.populate_treeview()
                    self.menubar.entryconfig(5, state=tk.DISABLED)  #disable delete menu
                    self.menubar.entryconfig(6, state=tk.DISABLED)  #disable move menu
                else:
                    messagebox.showerror("Error", "Staging directory is not set. Please set it first.")

    def show_history(self):
        history_pop = tk.Toplevel(self.root)
        history_pop.title("History")
        history_pop.geometry("800x400")
        history_pop.wm_iconphoto(False, self.top_icon)
        history_pop.config(background='white')
        history_treeview = ttk.Treeview(history_pop, columns=("DateTime", "Message"), show='headings')
        history_treeview.heading("#1", text="Created date", anchor='w')
        history_treeview.heading("#2", text="Message", anchor='w')
        history_treeview.pack(fill="both", expand=True)
        logs = self.controller.get_logs()
        for log in logs:
            history_treeview.insert("", tk.END, values=(log.timestamp, log.message))

    def clear_history(self):
        self.controller.clear_logs()
        messagebox.showinfo("History", "Scan history is cleared.")
