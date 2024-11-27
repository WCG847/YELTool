import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from YukesParse.SYM import SYMParser
from YukesParse.HCTP import HCTPParser
import json

class YelToolApp:
    def __init__(self, root):
        self.root = root
        self.root.title("YelTool")
        
        # Initialize parsers
        self.current_parser = None
        self.entries = []
        self.file_type = None  # Tracks whether SYM or HCTP was loaded

        # Setup GUI
        self._setup_menu()
        self._setup_treeview()

    def _setup_menu(self):
        menu_bar = tk.Menu(self.root)

        # File menu
        file_menu = tk.Menu(menu_bar, tearoff=0)
        file_menu.add_command(label="Load SYM", command=self.load_sym)
        file_menu.add_command(label="Load HCTP", command=self.load_hctp)
        file_menu.add_separator()
        file_menu.add_command(label="Deserialise", command=self.deserialise_to_json)
        file_menu.add_command(label="Serialise", command=self.serialise_to_binary)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)
        menu_bar.add_cascade(label="File", menu=file_menu)

        self.root.config(menu=menu_bar)

    def _setup_treeview(self):
        # Treeview frame
        tree_frame = ttk.Frame(self.root)
        tree_frame.pack(fill=tk.BOTH, expand=True)

        # Treeview widget
        self.tree = ttk.Treeview(tree_frame, columns=("Asset ID", "Unlock ID", "Asset Name"), show="headings")
        self.tree.heading("Asset ID", text="Asset ID")
        self.tree.heading("Unlock ID", text="Unlock ID")
        self.tree.heading("Asset Name", text="Asset Name")
        self.tree.pack(fill=tk.BOTH, expand=True)

    def _populate_treeview(self):
        # Clear existing rows
        for row in self.tree.get_children():
            self.tree.delete(row)

        # Insert new rows
        for entry in self.entries:
            self.tree.insert("", tk.END, values=(entry.get("asset_id"), entry.get("unlock_id"), entry.get("asset_name")))

    def load_sym(self):
        file_path = filedialog.askopenfilename(title="Select SYM File", filetypes=[("Data Files", "*.dat")])
        if not file_path:
            return

        try:
            with open(file_path, "rb") as file:
                binary_data = file.read()
            parser = SYMParser(binary_data)
            self.current_parser = parser
            self.file_type = "SYM"
            self.entries = parser.entries
            self._populate_treeview()
            messagebox.showinfo("Success", "SYM file loaded successfully!")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load SYM file: {e}")

    def load_hctp(self):
        file_path = filedialog.askopenfilename(title="Select HCTP File", filetypes=[("Data Files", "*.dat")])
        if not file_path:
            return

        try:
            with open(file_path, "rb") as file:
                binary_data = file.read()
            parser = HCTPParser(binary_data)
            self.current_parser = parser
            self.file_type = "HCTP"
            self.entries = parser.entries
            self._populate_treeview()
            messagebox.showinfo("Success", "HCTP file loaded successfully!")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load HCTP file: {e}")

    def deserialise_to_json(self):
        if not self.current_parser:
            messagebox.showerror("Error", "No data to deserialise. Please load a file first.")
            return

        file_path = filedialog.asksaveasfilename(title="Save JSON File", defaultextension=".json", filetypes=[("JSON Files", "*.json")])
        if not file_path:
            return

        try:
            json_data = self.current_parser.to_json()
            data_with_header = {"header_key": self.file_type, "entries": self.current_parser.entries}

            with open(file_path, "w") as file:
                file.write(json.dumps(data_with_header, indent=4))
            messagebox.showinfo("Success", "JSON file saved successfully!")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save JSON file: {e}")

    def serialise_to_binary(self):
        file_path = filedialog.askopenfilename(title="Select JSON File", filetypes=[("JSON Files", "*.json")])
        if not file_path:
            return

        try:
            with open(file_path, "r") as file:
                json_data = file.read()

            if isinstance(self.current_parser, SYMParser):
                parser = SYMParser()
                parser.from_json(json_data)
            elif isinstance(self.current_parser, HCTPParser):
                parser = HCTPParser()
                parser.from_json(json_data)
            else:
                raise ValueError("No parser loaded. Load SYM or HCTP first.")

            binary_data = parser.to_binary()

            output_file_path = filedialog.asksaveasfilename(title="Save Binary File", defaultextension=".dat", filetypes=[("Data Files", "*.dat")])
            if not output_file_path:
                return

            with open(output_file_path, "wb") as file:
                file.write(binary_data)

            messagebox.showinfo("Success", "Binary file saved successfully!")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to serialise JSON to binary: {e}")


if __name__ == "__main__":
    root = tk.Tk()
    app = YelToolApp(root)
    root.resizable(True, True)
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    window_width = int(screen_width * 0.8)
    window_height = int(screen_height * 0.8)
    root.geometry(f"{window_width}x{window_height}")
    root.mainloop()
