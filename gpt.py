import tkinter as tk
from tkinter import scrolledtext
import threading
import time
import sys
import io
import re
import traceback
import random

class GPTEngineerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("GPT-Engineer (CatSeek 0.1 R1 1.X Engine)")
        self.root.geometry("800x550")
        
        # --- Color Palette (GPT-Engineer / Modern Dev Tool Dark Theme) ---
        self.colors = {
            "bg_main": "#0d1117",       # Deep dark background
            "bg_sidebar": "#010409",    # Darker sidebar
            "bg_input": "#161b22",      # Slightly lighter input box
            "bg_terminal": "#010409",   # Terminal background
            "fg_primary": "#e6edf3",    # Primary text
            "fg_secondary": "#7d8590",  # Secondary/dim text
            "accent": "#2f81f7",        # Blue accent (links, user)
            "success": "#238636",       # Green accent (run button)
            "warning": "#d29922",       # Yellow accent
            "error": "#f85149",         # Red accent
            "system_tag": "#8b949e",    # System messages
            "agent_tag": "#a5d6ff"      # Agent name tag
        }
        
        self.root.configure(bg=self.colors["bg_main"])

        # --- Sidebar ---
        self.sidebar = tk.Frame(self.root, bg=self.colors["bg_sidebar"], width=180, bd=0, highlightthickness=1, highlightbackground="#30363d")
        self.sidebar.pack(side=tk.LEFT, fill=tk.Y)
        self.sidebar.pack_propagate(False)

        title_lbl = tk.Label(self.sidebar, text="GPT-ENGINEER", bg=self.colors["bg_sidebar"], fg=self.colors["fg_primary"], font=("Helvetica", 13, "bold"), tracking=1)
        title_lbl.pack(pady=(25, 2))

        version_lbl = tk.Label(self.sidebar, text="v1.x • CatSeek Mode", bg=self.colors["bg_sidebar"], fg=self.colors["fg_secondary"], font=("Helvetica", 9))
        version_lbl.pack(pady=(0, 30))

        # Badges
        self._create_badge("File Output: OFF", self.colors["warning"], "#3b2e0e")
        self._create_badge("Engine: CatSeek 1-bit", self.colors["success"], "#11341c")
        self._create_badge("Env: Python 3", self.colors["accent"], "#112a4d")
        self._create_badge("Workspace: Memory", self.colors["fg_secondary"], "#21262d")

        # --- Right Side Container ---
        self.right_frame = tk.Frame(self.root, bg=self.colors["bg_main"])
        self.right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        # --- Main Split Area (Chat vs Terminal) ---
        self.paned_window = tk.PanedWindow(self.right_frame, orient=tk.VERTICAL, bg="#30363d", bd=0, sashwidth=2)
        self.paned_window.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        # Chat Window Container
        chat_container = tk.Frame(self.paned_window, bg=self.colors["bg_main"])
        self.chat_display = scrolledtext.ScrolledText(
            chat_container, bg=self.colors["bg_main"], fg=self.colors["fg_primary"], 
            font=("Helvetica", 11), wrap=tk.WORD, state=tk.DISABLED, bd=0, padx=20, pady=20,
            insertbackground=self.colors["fg_primary"], selectbackground="#264f78"
        )
        self.chat_display.pack(fill=tk.BOTH, expand=True)
        self.paned_window.add(chat_container, minsize=200)

        # Terminal Window
        term_container = tk.Frame(self.paned_window, bg=self.colors["bg_terminal"])
        term_header_frame = tk.Frame(term_container, bg="#161b22", height=24)
        term_header_frame.pack(fill=tk.X)
        term_header_frame.pack_propagate(False)
        
        term_header = tk.Label(term_header_frame, text="TERMINAL", bg="#161b22", fg=self.colors["fg_secondary"], font=("Helvetica", 8, "bold"))
        term_header.pack(side=tk.LEFT, padx=10, pady=2)
        
        self.terminal_display = scrolledtext.ScrolledText(
            term_container, bg=self.colors["bg_terminal"], fg="#7ee787", font=("Consolas", 10), 
            wrap=tk.WORD, state=tk.DISABLED, bd=0, padx=15, pady=10
        )
        self.terminal_display.pack(fill=tk.BOTH, expand=True)
        self.paned_window.add(term_container, minsize=120)

        # --- Input Area ---
        self.input_container = tk.Frame(self.right_frame, bg=self.colors["bg_main"], pady=15, padx=20)
        self.input_container.pack(side=tk.BOTTOM, fill=tk.X)

        self.input_frame = tk.Frame(self.input_container, bg=self.colors["bg_input"], bd=1, highlightthickness=1, highlightbackground="#30363d")
        self.input_frame.pack(fill=tk.X)

        self.prompt_entry = tk.Text(
            self.input_frame, height=3, bg=self.colors["bg_input"], fg=self.colors["fg_primary"], 
            font=("Helvetica", 11), bd=0, insertbackground=self.colors["fg_primary"], padx=10, pady=10
        )
        self.prompt_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        self.prompt_entry.bind("<Return>", self.handle_enter)

        self.send_btn = tk.Button(
            self.input_frame, text="Generate", bg=self.colors["success"], fg="#ffffff", 
            activebackground="#2ea043", activeforeground="#ffffff", 
            bd=0, command=self.send_prompt, width=10, font=("Helvetica", 10, "bold"),
            cursor="hand2", relief=tk.FLAT
        )
        self.send_btn.pack(side=tk.RIGHT, padx=10, pady=10, fill=tk.Y)

        # Initialize Fixed Algorithm Dataset
        self._initialize_dataset()

        self.append_to_chat("System", "GPT-Engineer initialized.\nMode: 1-bit Local Engine (/files = off).\nEngine: CatSeek 0.1 R1 1.X.\nOutput: Embedded Terminal Execution.\n\nReady for instructions. Try asking for 'fibonacci', 'calculator', 'sort array', or 'random'.")

    def _initialize_dataset(self):
        """
        The Fixed Dataset: Maps specific programming intents/heuristics to pre-written code blocks.
        """
        self.dataset = {
            "hello": {
                "keywords": ["hello", "world", "greet", "hi", "test"],
                "desc": "A basic output script to test the environment.",
                "code": "print('Hello, World!')\nprint('The terminal sandbox is active.')"
            },
            "loop": {
                "keywords": ["loop", "iterate", "for", "while", "count"],
                "desc": "A simple iterative loop.",
                "code": "print('Counting 1 to 5:')\nfor i in range(1, 6):\n    print(f'Iteration: {i}')"
            },
            "fibonacci": {
                "keywords": ["fibonacci", "sequence", "fib"],
                "desc": "An algorithm to generate the Fibonacci sequence.",
                "code": "def fibonacci(n):\n    sequence = [0, 1]\n    while len(sequence) < n:\n        sequence.append(sequence[-1] + sequence[-2])\n    return sequence\n\nprint(f'First 10 Fibonacci numbers: {fibonacci(10)}')\n"
            },
            "math_calculator": {
                "keywords": ["math", "calculator", "add", "multiply", "divide", "subtract", "calculate"],
                "desc": "A basic math demonstration using variables.",
                "code": "a = 24\nb = 7\nprint(f'Values: a={a}, b={b}')\nprint(f'Addition: {a + b}')\nprint(f'Subtraction: {a - b}')\nprint(f'Multiplication: {a * b}')\nprint(f'Division: {a / b:.2f}')"
            },
            "sort": {
                "keywords": ["sort", "order", "array", "list", "bubble"],
                "desc": "An algorithm demonstrating list sorting.",
                "code": "import random\n# Generate random list\nmy_list = [random.randint(1, 100) for _ in range(8)]\nprint(f'Original: {my_list}')\n\n# Sort list\nmy_list.sort()\nprint(f'Sorted:   {my_list}')"
            },
            "random": {
                "keywords": ["random", "dice", "roll", "chance", "guess"],
                "desc": "A randomized generation script.",
                "code": "import random\nrolls = [random.randint(1, 6) for _ in range(5)]\nprint('Rolling 5 six-sided dice...')\nprint(f'Results: {rolls}')\nprint(f'Total Sum: {sum(rolls)}')\n"
            },
            "time": {
                "keywords": ["time", "date", "clock", "now"],
                "desc": "A script that fetches the current system time.",
                "code": "import time\nimport datetime\n\nnow = datetime.datetime.now()\nprint(f'Current Date and Time: {now.strftime(\"%Y-%m-%d %H:%M:%S\")}')"
            }
        }

    def _create_badge(self, text, fg_color, bg_color):
        badge = tk.Label(self.sidebar, text=text, bg=bg_color, fg=fg_color, font=("Helvetica", 8, "bold"), pady=4)
        badge.pack(pady=4, padx=15, fill=tk.X)

    def handle_enter(self, event):
        if not event.state & 0x1: 
            self.send_prompt()
            return "break"

    def append_to_chat(self, sender, text):
        self.chat_display.config(state=tk.NORMAL)
        
        if sender == "System":
            self.chat_display.insert(tk.END, f"{sender}\n", "system")
        elif sender == "User":
            self.chat_display.insert(tk.END, f"You\n", "user")
        else:
            self.chat_display.insert(tk.END, f"CatSeek 0.1\n", "agent")
            
        self.chat_display.insert(tk.END, f"{text}\n\n", "body")
        
        self.chat_display.tag_config("system", foreground=self.colors["system_tag"], font=("Helvetica", 9, "bold"))
        self.chat_display.tag_config("user", foreground=self.colors["accent"], font=("Helvetica", 10, "bold"))
        self.chat_display.tag_config("agent", foreground=self.colors["agent_tag"], font=("Helvetica", 10, "bold"))
        self.chat_display.tag_config("body", foreground=self.colors["fg_primary"], font=("Helvetica", 11))
        
        self.chat_display.config(state=tk.DISABLED)
        self.chat_display.yview(tk.END)

    def append_to_terminal(self, text, tag=None):
        self.terminal_display.config(state=tk.NORMAL)
        if tag == "error":
            self.terminal_display.insert(tk.END, text, "error")
            self.terminal_display.tag_config("error", foreground=self.colors["error"])
        else:
            self.terminal_display.insert(tk.END, text)
        self.terminal_display.config(state=tk.DISABLED)
        self.terminal_display.yview(tk.END)

    def execute_code(self, code_string):
        self.append_to_terminal(f"> Executing CatSeek generated code...\n")
        old_stdout = sys.stdout
        redirected_output = sys.stdout = io.StringIO()
        try:
            # Execute dynamically in its own sandbox namespace
            exec(code_string, {})
            output = redirected_output.getvalue()
            self.append_to_terminal(output if output else "(No standard output)\n")
        except Exception as e:
            self.append_to_terminal(traceback.format_exc() + "\n", tag="error")
        finally:
            sys.stdout = old_stdout
        self.append_to_terminal("\n")

    def send_prompt(self):
        prompt = self.prompt_entry.get("1.0", tk.END).strip()
        if not prompt:
            return

        self.prompt_entry.delete("1.0", tk.END)
        self.append_to_chat("User", prompt)
        
        self.send_btn.config(state=tk.DISABLED, text="Inferencing...", bg="#21262d", fg=self.colors["fg_secondary"])
        
        # Run local generation
        threading.Thread(target=self.run_catseek_engine, args=(prompt,), daemon=True).start()

    def run_catseek_engine(self, prompt):
        """
        The CatSeek 0.1 R1 1.X Algorithm: Simulates 1-bit inference by tokenizing 
        the user's prompt and matching it against the dataset using a scoring mechanism.
        """
        # Simulate processing time for 1-bit LLM
        time.sleep(1.2)
        
        try:
            # 1. Tokenize prompt into words and lowercase
            words = set(re.findall(r'\w+', prompt.lower()))
            
            best_match_key = None
            highest_score = 0
            
            # 2. Heuristic Scoring (Simulating 1-bit quantization weight mapping)
            for key, data in self.dataset.items():
                score = sum(1 for kw in data["keywords"] if kw in words)
                if score > highest_score:
                    highest_score = score
                    best_match_key = key
                    
            # 3. Code Assembly
            if best_match_key:
                match = self.dataset[best_match_key]
                text_response = (
                    f"[CatSeek 0.1 R1 1.X] 1-bit inference complete. Pattern matched: '{best_match_key}' (confidence score {highest_score}).\n"
                    f"{match['desc']}\n\n"
                    f"```python\n{match['code']}\n```"
                )
            else:
                fallback_code = (
                    "print('CatSeek Error: Inference collapsed. Unrecognized prompt.')\n"
                    "print('My 1-bit weights are currently tuned for keywords like:')\n"
                    "print(' - fibonacci\\n - sort\\n - math\\n - random\\n - loop\\n - time')"
                )
                text_response = (
                    f"[CatSeek 0.1 R1 1.X] 1-bit inference failed to map to a valid code structure. Weights unresolved.\n\n"
                    f"Executing fallback script:\n\n"
                    f"```python\n{fallback_code}\n```"
                )
                
        except Exception as e:
            text_response = f"CatSeek Execution Error: {e}"
            
        self.root.after(0, self.handle_llm_response, text_response)

    def handle_llm_response(self, text):
        self.append_to_chat("Agent", text)
        self.send_btn.config(state=tk.NORMAL, text="Generate", bg=self.colors["success"], fg="#ffffff")
        
        # Extract and execute python block
        code_blocks = re.findall(r'```python\n(.*?)\n```', text, re.DOTALL)
        for block in code_blocks:
            self.execute_code(block)

if __name__ == "__main__":
    root = tk.Tk()
    app = GPTEngineerApp(root)
    root.mainloop()
