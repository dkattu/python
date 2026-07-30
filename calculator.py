import ast
import math
import tkinter as tk
from tkinter import ttk


class SafeEvaluator(ast.NodeVisitor):
    allowed_nodes = {
        ast.Expression,
        ast.BinOp,
        ast.UnaryOp,
        ast.Constant,
        ast.Call,
        ast.Name,
        ast.Add,
        ast.Sub,
        ast.Mult,
        ast.Div,
        ast.Pow,
        ast.Mod,
        ast.USub,
        ast.UAdd,
        ast.FloorDiv,
        ast.LShift,
        ast.RShift,
        ast.BitAnd,
        ast.BitOr,
        ast.BitXor,
        ast.Invert,
    }

    def visit(self, node):
        if type(node) not in self.allowed_nodes:
            raise ValueError(f"Unsupported expression: {type(node).__name__}")
        return super().visit(node)

    def visit_Expression(self, node):
        return self.visit(node.body)

    def visit_BinOp(self, node):
        left = self.visit(node.left)
        right = self.visit(node.right)
        op_type = type(node.op)
        if op_type is ast.Add:
            return left + right
        if op_type is ast.Sub:
            return left - right
        if op_type is ast.Mult:
            return left * right
        if op_type is ast.Div:
            return left / right
        if op_type is ast.FloorDiv:
            return left // right
        if op_type is ast.Mod:
            return left % right
        if op_type is ast.Pow:
            return left ** right
        if op_type is ast.LShift:
            return left << right
        if op_type is ast.RShift:
            return left >> right
        if op_type is ast.BitAnd:
            return left & right
        if op_type is ast.BitOr:
            return left | right
        if op_type is ast.BitXor:
            return left ^ right
        raise ValueError(f"Unsupported operator: {op_type.__name__}")

    def visit_UnaryOp(self, node):
        value = self.visit(node.operand)
        if isinstance(node.op, ast.UAdd):
            return +value
        if isinstance(node.op, ast.USub):
            return -value
        if isinstance(node.op, ast.Invert):
            return ~value
        raise ValueError(f"Unsupported unary operator: {type(node.op).__name__}")

    def visit_Constant(self, node):
        if isinstance(node.value, (int, float)):
            return node.value
        raise ValueError(f"Unsupported constant: {node.value}")

    def visit_Call(self, node):
        if len(node.args) != 1 or node.keywords:
            raise ValueError("Only single-argument function calls are supported")
        if not isinstance(node.func, ast.Name):
            raise ValueError("Only simple function names are supported")

        func_name = node.func.id.lower()
        argument = self.visit(node.args[0])
        if func_name == "sin":
            return math.sin(argument)
        if func_name == "cos":
            return math.cos(argument)
        if func_name == "tan":
            return math.tan(argument)
        if func_name == "sqrt":
            return math.sqrt(argument)
        raise ValueError(f"Unsupported function: {node.func.id}")

    def visit_Name(self, node):
        if node.id == "pi":
            return math.pi
        if node.id == "e":
            return math.e
        raise ValueError(f"Unsupported name: {node.id}")


class CalculatorHistory:
    def __init__(self):
        self._entries = []

    def add_entry(self, expression: str, result: str) -> None:
        self._entries.append((expression, result))

    def get_entries(self):
        return list(self._entries)

    def replay(self, index: int):
        if 0 <= index < len(self._entries):
            return self._entries[index]
        raise IndexError("history index out of range")

    def clear(self) -> None:
        self._entries.clear()


class CalculatorApp:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Modern Calculator")
        self.root.configure(bg="#171717")
        self.root.resizable(False, False)

        self.style = ttk.Style(self.root)
        self.style.theme_use("clam")
        self._configure_styles()

        self.expression = ""
        self.display_var = tk.StringVar(value="0")
        self.history = CalculatorHistory()
        self.scientific_mode = False

        self._build_ui()
        self._bind_keys()

    def _configure_styles(self):
        self.style.configure("Display.TLabel", background="#171717", foreground="#FFFFFF", font=("Segoe UI", 28, "bold"), padding=(16, 16))
        self.style.configure("TButton", font=("Segoe UI", 16, "bold"), foreground="#FFFFFF", borderwidth=0, focuscolor="")
        self.style.map(
            "TButton",
            background=[("active", "#333333"), ("!disabled", "#1F2937")],
            foreground=[("active", "#FFFFFF"), ("!disabled", "#FFFFFF")],
        )
        self.style.configure("Operator.TButton", background="#2563EB", foreground="#FFFFFF")
        self.style.map(
            "Operator.TButton",
            background=[("active", "#1D4ED8"), ("!disabled", "#2563EB")],
        )
        self.style.configure("Action.TButton", background="#374151", foreground="#FFFFFF")
        self.style.map(
            "Action.TButton",
            background=[("active", "#4B5563"), ("!disabled", "#374151")],
        )

    def _build_ui(self):
        display_frame = ttk.Frame(self.root, style="Display.TLabel")
        display_frame.grid(row=0, column=0, columnspan=4, sticky="nsew", padx=12, pady=12)

        self.display_label = ttk.Label(display_frame, textvariable=self.display_var, style="Display.TLabel", anchor="e")
        self.display_label.pack(fill="both", expand=True)

        history_frame = ttk.Frame(self.root, padding=(8, 0, 8, 8))
        history_frame.grid(row=1, column=0, columnspan=4, sticky="nsew")

        history_title = ttk.Label(history_frame, text="History", font=("Segoe UI", 11, "bold"))
        history_title.pack(anchor="w")

        self.history_listbox = tk.Listbox(history_frame, height=4, font=("Segoe UI", 10), activestyle="none")
        self.history_listbox.pack(fill="both", expand=True, pady=(4, 6))
        self.history_listbox.bind("<<ListboxSelect>>", self._on_history_select)
        self.history_listbox.bind("<Double-Button-1>", self._replay_selected_history)

        history_buttons = ttk.Frame(history_frame)
        history_buttons.pack(fill="x")
        ttk.Button(history_buttons, text="Clear", command=self.clear_history).pack(side="right")

        self.scientific_toggle = ttk.Button(history_frame, text="Scientific mode: Off", command=self.toggle_scientific_mode)
        self.scientific_toggle.pack(fill="x", pady=(6, 4))

        self.scientific_frame = ttk.Frame(history_frame)
        self.scientific_frame.pack(fill="x")
        self.scientific_frame.pack_forget()

        scientific_buttons = [
            ("sin", lambda: self.append_text("sin(")),
            ("cos", lambda: self.append_text("cos(")),
            ("tan", lambda: self.append_text("tan(")),
            ("√", lambda: self.append_text("sqrt(")),
            ("π", lambda: self.append_text("pi")),
            ("e", lambda: self.append_text("e")),
            ("(", lambda: self.append_text("(")),
            (")", lambda: self.append_text(")")),
            ("^", lambda: self.append_text("^")),
        ]
        for index, (label, command) in enumerate(scientific_buttons):
            ttk.Button(self.scientific_frame, text=label, command=command).grid(row=0, column=index, padx=2, pady=2, sticky="ew")
        for index in range(len(scientific_buttons)):
            self.scientific_frame.grid_columnconfigure(index, weight=1)

        self._refresh_history()

        button_layout = [
            [("CE", self.clear_entry, "Action.TButton"), ("C", self.clear_all, "Action.TButton"), ("⌫", self.backspace, "Action.TButton"), ("÷", lambda: self.append_operator("/"), "Operator.TButton")],
            [("7", lambda: self.add_digit("7"), None), ("8", lambda: self.add_digit("8"), None), ("9", lambda: self.add_digit("9"), None), ("×", lambda: self.append_operator("*"), "Operator.TButton")],
            [("4", lambda: self.add_digit("4"), None), ("5", lambda: self.add_digit("5"), None), ("6", lambda: self.add_digit("6"), None), ("-", lambda: self.append_operator("-"), "Operator.TButton")],
            [("1", lambda: self.add_digit("1"), None), ("2", lambda: self.add_digit("2"), None), ("3", lambda: self.add_digit("3"), None), ("+", lambda: self.append_operator("+"), "Operator.TButton")],
            [("±", self.toggle_sign, "Action.TButton"), ("0", lambda: self.add_digit("0"), None), (".", lambda: self.add_decimal_point(), None), (("=", self.calculate_result, "Operator.TButton"))],
        ]

        for row_index, row in enumerate(button_layout, start=2):
            for col_index, button_def in enumerate(row):
                if isinstance(button_def[0], tuple):
                    label, command, style_name = button_def[0]
                else:
                    label, command, style_name = button_def
                style = style_name or "TButton"
                button = ttk.Button(self.root, text=label, command=command, style=style)
                button.grid(row=row_index, column=col_index, padx=6, pady=6, sticky="nsew", ipadx=8, ipady=14)

        for i in range(4):
            self.root.grid_columnconfigure(i, weight=1)
        for i in range(1, 8):
            self.root.grid_rowconfigure(i, weight=1)

        self.root.grid_rowconfigure(0, weight=0)

    def _bind_keys(self):
        keys = {
            "<Key-0>": lambda e: self.add_digit("0"),
            "<Key-1>": lambda e: self.add_digit("1"),
            "<Key-2>": lambda e: self.add_digit("2"),
            "<Key-3>": lambda e: self.add_digit("3"),
            "<Key-4>": lambda e: self.add_digit("4"),
            "<Key-5>": lambda e: self.add_digit("5"),
            "<Key-6>": lambda e: self.add_digit("6"),
            "<Key-7>": lambda e: self.add_digit("7"),
            "<Key-8>": lambda e: self.add_digit("8"),
            "<Key-9>": lambda e: self.add_digit("9"),
            "<Key-=>": lambda e: self.calculate_result(),
            "<Return>": lambda e: self.calculate_result(),
            "<Key-plus>": lambda e: self.append_operator("+"),
            "<Key-minus>": lambda e: self.append_operator("-"),
            "<Key-slash>": lambda e: self.append_operator("/"),
            "<Key-asterisk>": lambda e: self.append_operator("*"),
            "<Key-period>": lambda e: self.add_decimal_point(),
            "<BackSpace>": lambda e: self.backspace(),
            "<Delete>": lambda e: self.clear_all(),
            "<Escape>": lambda e: self.clear_all(),
        }
        for event, handler in keys.items():
            self.root.bind(event, handler)

    def add_digit(self, digit: str) -> None:
        if self.display_var.get() == "0" or self.expression == "ERROR":
            self.expression = digit
        else:
            self.expression += digit
        self._update_display()

    def append_text(self, text: str) -> None:
        if self.expression == "ERROR":
            self.expression = text
        elif not self.expression or self.expression == "0":
            self.expression = text
        else:
            self.expression += text
        self._update_display()

    def add_decimal_point(self) -> None:
        if self.expression and self.expression[-1].isdigit() and "." not in self._last_number():
            self.expression += "."
        elif not self.expression or not self.expression[-1].isdigit():
            self.expression += "0."
        self._update_display()

    def toggle_sign(self) -> None:
        if self.expression.startswith("-"):
            self.expression = self.expression[1:]
        elif self.expression and self.expression[0].isdigit():
            self.expression = f"-{self.expression}"
        self._update_display()

    def append_operator(self, operator: str) -> None:
        if not self.expression or self.expression == "ERROR":
            return
        if self.expression[-1] in "+-*/":
            self.expression = self.expression[:-1] + operator
        else:
            self.expression += operator
        self._update_display()

    def clear_entry(self) -> None:
        self.expression = self.expression[:-1]
        self._update_display()

    def clear_all(self) -> None:
        self.expression = ""
        self.display_var.set("0")

    def backspace(self) -> None:
        self.clear_entry()

    def toggle_scientific_mode(self) -> None:
        self.scientific_mode = not self.scientific_mode
        if self.scientific_mode:
            self.scientific_frame.pack(fill="x")
            self.scientific_toggle.configure(text="Scientific mode: On")
        else:
            self.scientific_frame.pack_forget()
            self.scientific_toggle.configure(text="Scientific mode: Off")

    def clear_history(self) -> None:
        self.history.clear()
        self._refresh_history()

    def _refresh_history(self) -> None:
        self.history_listbox.delete(0, tk.END)
        entries = self.history.get_entries()
        if not entries:
            self.history_listbox.insert(tk.END, "No calculations yet")
            return
        for expression, result in entries:
            self.history_listbox.insert(tk.END, f"{expression} = {result}")

    def _on_history_select(self, _event=None) -> None:
        selection = self.history_listbox.curselection()
        if not selection:
            return
        index = selection[0]
        try:
            expression, _result = self.history.replay(index)
        except IndexError:
            return
        self.expression = expression
        self._update_display()

    def _replay_selected_history(self, _event=None) -> None:
        self._on_history_select(_event)

    def calculate_result(self) -> None:
        if not self.expression:
            return
        try:
            original_expression = self.expression
            expression = original_expression.replace("×", "*").replace("÷", "/").replace("^", "**")
            tree = ast.parse(expression, mode="eval")
            evaluator = SafeEvaluator()
            result = evaluator.visit(tree)
            result_text = str(result)
            self.expression = result_text
            self.display_var.set(self.expression)
            self.history.add_entry(original_expression, result_text)
            self._refresh_history()
        except Exception:
            self.expression = "ERROR"
            self.display_var.set("ERROR")

    def _last_number(self) -> str:
        tokens = []
        for ch in reversed(self.expression):
            if ch.isdigit() or ch == ".":
                tokens.append(ch)
            else:
                break
        return "".join(reversed(tokens))

    def _update_display(self) -> None:
        self.display_var.set(self.expression or "0")


def main() -> None:
    root = tk.Tk()
    app = CalculatorApp(root)
    root.geometry("360x540")
    root.mainloop()


if __name__ == "__main__":
    main()
