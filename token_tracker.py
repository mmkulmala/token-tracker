import os
import tkinter as tk
from tkinter import filedialog, ttk

# Folders to ignore during scanning
IGNORE_FOLDERS = {".git", "node_modules", "venv", ".venv", "__pycache__", "build", "dist"}


def load_language_map(path=None):
    if path is None:
        path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "language_map.txt")
    language_map = {}
    try:
        with open(path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                parts = line.split(None, 1)
                if len(parts) != 2:
                    continue
                ext, language = parts
                language_map[ext.lower()] = language
    except FileNotFoundError:
        pass
    return language_map


# Extension to Language mapping (loaded from text file at startup)
LANGUAGE_MAP = load_language_map()

class TokenTrackerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Kilo Code - Token Tracker & Tier Advisor")
        self.root.geometry("850x650")
        self.root.minsize(750, 500)
        
        self.project_path = ""
        self.total_input_tokens = 0
        
        self.create_widgets()
        
    def create_widgets(self):
        # Top Control Panel
        top_frame = ttk.Frame(self.root, padding="10")
        top_frame.pack(fill=tk.X)
        
        self.btn_browse = ttk.Button(top_frame, text="Select Game Project Folder...", command=self.browse_folder)
        self.btn_browse.pack(side=tk.LEFT, padx=5)
        
        self.lbl_path = ttk.Label(top_frame, text="No folder selected", font=("Arial", 10, "italic"), foreground="gray")
        self.lbl_path.pack(side=tk.LEFT, padx=10, fill=tk.X, expand=True)

        # Main Layout: Left (File List) and Right (Analysis & Tier Configuration)
        main_paned = ttk.Panedwindow(self.root, orient=tk.HORIZONTAL)
        main_paned.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Left Frame: File TreeView
        left_frame = ttk.LabelFrame(main_paned, text=" Project Files & Detected Languages ", padding="10")
        main_paned.add(left_frame, weight=3)
        
        columns = ("name", "lang", "size", "tokens")
        self.tree = ttk.Treeview(left_frame, columns=columns, show="headings")
        self.tree.heading("name", text="File Name")
        self.tree.heading("lang", text="Detected Language")
        self.tree.heading("size", text="Size (KB)")
        self.tree.heading("tokens", text="Est. Tokens")
        
        self.tree.column("name", width=250, anchor=tk.W)
        self.tree.column("lang", width=130, anchor=tk.CENTER)
        self.tree.column("size", width=80, anchor=tk.E)
        self.tree.column("tokens", width=90, anchor=tk.E)
        
        scrollbar = ttk.Scrollbar(left_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Right Frame: Analysis & Parameters
        right_frame = ttk.LabelFrame(main_paned, text=" Usage & Tier Diagnostics ", padding="10")
        main_paned.add(right_frame, weight=2)
        
        # Inputs config
        ttk.Label(right_frame, text="Daily Iterations (Prompts):", font=("Arial", 10, "bold")).pack(anchor=tk.W, pady=(5, 2))
        self.var_iterations = tk.IntVar(value=40)
        self.scale_iterations = ttk.Scale(right_frame, from_=5, to=200, variable=self.var_iterations, orient=tk.HORIZONTAL, command=self.update_analysis)
        self.scale_iterations.pack(fill=tk.X, pady=2)
        
        self.lbl_iterations_val = ttk.Label(right_frame, text="40 iterations / day")
        self.lbl_iterations_val.pack(anchor=tk.E, pady=(0, 15))
        
        # Output tokens prompt estimate
        ttk.Label(right_frame, text="Est. Claude Output per Prompt:", font=("Arial", 10, "bold")).pack(anchor=tk.W, pady=(5, 2))
        self.var_output_tokens = tk.IntVar(value=1500)
        self.scale_output = ttk.Scale(right_frame, from_=500, to=8000, variable=self.var_output_tokens, orient=tk.HORIZONTAL, command=self.update_analysis)
        self.scale_output.pack(fill=tk.X, pady=2)
        
        self.lbl_output_val = ttk.Label(right_frame, text="1,500 tokens / response")
        self.lbl_output_val.pack(anchor=tk.E, pady=(0, 20))
        
        # Results Separator
        ttk.Separator(right_frame, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=10)
        
        # Metrics Display
        self.lbl_total_context = ttk.Label(right_frame, text="Project Codebase: 0 tokens", font=("Arial", 11))
        self.lbl_total_context.pack(anchor=tk.W, pady=3)
        
        self.lbl_daily_volume = ttk.Label(right_frame, text="Est. Daily Volume: 0 tokens", font=("Arial", 11))
        self.lbl_daily_volume.pack(anchor=tk.W, pady=3)
        
        ttk.Separator(right_frame, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=15)
        
        # Recommendation Area
        ttk.Label(right_frame, text="Recommended Claude Tier:", font=("Arial", 11, "bold")).pack(anchor=tk.W)
        self.lbl_tier_recommendation = ttk.Label(right_frame, text="N/A (Select folder first)", font=("Arial", 14, "bold"), foreground="darkblue", wraplength=280)
        self.lbl_tier_recommendation.pack(anchor=tk.W, pady=10)
        
    def browse_folder(self):
        selected = filedialog.askdirectory(title="Select Game Project Folder")
        if selected:
            self.project_path = selected
            self.lbl_path.config(text=os.path.basename(selected))
            self.scan_project()
            
    def scan_project(self):
        # Clear previous rows
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        self.total_input_tokens = 0
        
        for root_dir, dirs, files in os.walk(self.project_path):
            # Dynamic pruning of hidden/ignored directories
            dirs[:] = [d for d in dirs if d not in IGNORE_FOLDERS]
            
            for file in files:
                ext = os.path.splitext(file)[1].lower()
                if ext in LANGUAGE_MAP:
                    file_path = os.path.join(root_dir, file)
                    try:
                        file_size_bytes = os.path.getsize(file_path)
                        file_size_kb = round(file_size_bytes / 1024, 2)
                        
                        # Basic character-to-token heuristic (~4 chars per token)
                        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                            content = f.read()
                            tokens = max(1, len(content) // 4)
                            
                        self.total_input_tokens += tokens
                        lang = LANGUAGE_MAP[ext]
                        
                        # Insert relative or absolute path name into the tree view
                        display_name = os.path.relpath(file_path, self.project_path)
                        self.tree.insert("", tk.END, values=(display_name, lang, f"{file_size_kb:,}", f"{tokens:,}"))
                    except Exception:
                        pass # Safeguard against locked/system files
                        
        self.update_analysis()
        
    def update_analysis(self, *args):
        iterations = self.var_iterations.get()
        output_estimate = self.var_output_tokens.get()
        
        self.lbl_iterations_val.config(text=f"{iterations} iterations / day")
        self.lbl_output_val.config(text=f"{output_estimate:,} tokens / response")
        
        if not self.project_path:
            return
            
        # Calculation: Every code prompt sends the WHOLE codebase context (Input) + gets some response (Output)
        daily_input_total = self.total_input_tokens * iterations
        daily_output_total = output_estimate * iterations
        daily_grand_total = daily_input_total + daily_output_total
        
        self.lbl_total_context.config(text=f"Project Codebase: {self.total_input_tokens:,} tokens")
        self.lbl_daily_volume.config(text=f"Est. Daily Volume: {daily_grand_total:,} tokens/day")
        
        # Tier Recommendation Logic based on project context limits and workload volume
        if self.total_input_tokens == 0:
            recommendation = "No compatible code files found."
        elif self.total_input_tokens > 150000 or daily_grand_total > 5000000:
            recommendation = "MAX 20x ($200/mo)\n- Massive codebase or ultra-heavy coding workload."
        elif self.total_input_tokens > 60000 or daily_grand_total > 1500000:
            recommendation = "MAX 5x ($100/mo)\n- Moderate to large project. Standard Pro will throttle quickly."
        elif daily_grand_total > 200000:
            recommendation = "PRO Tier ($20/mo)\n- Perfect fit for standard independent game development."
        else:
            recommendation = "FREE Tier ($0/mo)\n- Tiny project or very casual tweaking."
            
        self.lbl_tier_recommendation.config(text=recommendation)

if __name__ == "__main__":
    root = tk.Tk()
    app = TokenTrackerApp(root)
    root.mainloop()
