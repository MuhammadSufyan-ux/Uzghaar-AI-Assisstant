import sys
import os
import sqlite3
import threading
from datetime import datetime
import customtkinter as ctk
import ollama
import pyperclip

# System Presentation Framework Configuration
ctk.set_appearance_mode("Light")
ctk.set_default_color_theme("blue")

class UzghaarDatabaseEngine:
    """Provides structured permanent persistence routines for sessions and text buffers using SQLite."""
    def __init__(self, db_name="uzghaar_memory.db"):
        self.db_name = db_name
        self.initialize_tables()

    def get_connection(self):
        return sqlite3.connect(self.db_name)

    def initialize_tables(self):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            # Active Thread Session Matrix Tracking Registry
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS sessions (
                    session_id TEXT PRIMARY KEY,
                    title TEXT,
                    created_at TEXT
                )
            """)
            # System Conversation Timeline Log Cache Vault
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS messages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT,
                    role TEXT,
                    content TEXT,
                    timestamp TEXT,
                    FOREIGN KEY(session_id) REFERENCES sessions(session_id) ON DELETE CASCADE
                )
            """)
            conn.commit()

    def create_new_session(self, session_id, title):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("INSERT OR IGNORE INTO sessions VALUES (?, ?, ?)", 
                           (session_id, title, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
            conn.commit()

    def fetch_all_sessions(self):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT session_id, title FROM sessions ORDER BY created_at DESC")
            return cursor.fetchall()

    def update_session_title(self, session_id, new_title):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("UPDATE sessions SET title = ? WHERE session_id = ?", (new_title, session_id))
            conn.commit()

    def delete_session_scope(self, session_id):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM sessions WHERE session_id = ?", (session_id,))
            cursor.execute("DELETE FROM messages WHERE session_id = ?", (session_id,))
            conn.commit()

    def append_chat_message(self, session_id, role, content):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO messages (session_id, role, content, timestamp) VALUES (?, ?, ?, ?)",
                           (session_id, role, content, datetime.now().strftime("%H:%M")))
            conn.commit()

    def fetch_message_history(self, session_id):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT role, content FROM messages WHERE session_id = ? ORDER BY id ASC", (session_id,))
            return [{"role": r, "content": c} for r, c in cursor.fetchall()]


class UzghaarWebEngine(ctk.CTk):
    """An advanced local AI agent client featuring dynamic canvas grids, hidden scroll channels, and SQLite data vault lines."""
    def __init__(self):
        super().__init__()

        # Boot Storage Framework Kernel
        self.db = UzghaarDatabaseEngine()

        # Operational Control Variable Allocations
        self.active_model = "qwen2.5:0.5b"
        self.current_theme = "Light"
        self.is_generating = False
        self.stop_requested = False
        self.active_session_id = None
        self.sidebar_buttons_map = {}

        # Core Application Metric Contraints
        self.title("⚡ UZGHAAR ADVANCED AUTONOMOUS ENGINE")
        self.geometry("1280x820")
        self.minsize(1100, 720)

        # Structure Master Columns
        self.grid_columnconfigure(0, weight=0, minsize=280)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.construct_clean_sidebar_rail()
        self.construct_premium_web_workspace()
        
        # Load pre-saved conversation slots or allocate a dynamic fresh one
        self.reload_sidebar_sessions_from_db()

    def construct_clean_sidebar_rail(self):
        self.sidebar_frame = ctk.CTkFrame(self, corner_radius=0, border_width=0, fg_color=("#f6f8fa", "#161b22"))
        self.sidebar_frame.grid(row=0, column=0, sticky="nsew")
        self.sidebar_frame.grid_rowconfigure(2, weight=1)
        self.sidebar_frame.grid_columnconfigure(0, weight=1)

        self.nav_title = ctk.CTkLabel(
            self.sidebar_frame, 
            text="📁 CHAT SESSIONS (SQLITE)", 
            font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"),
            text_color="#656d76"
        )
        self.nav_title.grid(row=0, column=0, padx=20, pady=(25, 10), sticky="w")

        # Session Tracker Panel Viewport Map
        self.flat_history_panel = ctk.CTkScrollableFrame(self.sidebar_frame, fg_color="transparent", label_text="")
        self.flat_history_panel.grid(row=2, column=0, padx=5, pady=5, sticky="nsew")
        self.flat_history_panel.grid_columnconfigure(0, weight=1)
        
        # BYPASS CONSTRAINT: Safely force the internal Scrollbar tracker width metric down to zero to hide it visually
        if hasattr(self.flat_history_panel, "_scrollbar"):
            self.flat_history_panel._scrollbar.configure(width=0)

        self.new_session_btn = ctk.CTkButton(
            self.sidebar_frame,
            text="➕ New Chat Scope",
            height=42,
            corner_radius=8,
            font=ctk.CTkFont(family="Segoe UI", weight="bold"),
            command=self.initialize_fresh_session
        )
        self.new_session_btn.grid(row=3, column=0, padx=15, pady=20, sticky="ew")

    def construct_premium_web_workspace(self):
        self.canvas_workspace = ctk.CTkFrame(self, corner_radius=0, fg_color=("white", "#0d1117"))
        self.canvas_workspace.grid(row=0, column=1, sticky="nsew")
        self.canvas_workspace.grid_columnconfigure(0, weight=1)
        self.canvas_workspace.grid_rowconfigure(1, weight=1)

        # --- UPPER FRAME RIBBON PACK ---
        self.header_block = ctk.CTkFrame(self.canvas_workspace, fg_color="transparent", height=60)
        self.header_block.grid(row=0, column=0, sticky="ew", padx=30, pady=(15, 5))

        self.brand_signature = ctk.CTkLabel(
            self.header_block, 
            text="Uzghaar AI Assistant", 
            font=ctk.CTkFont(family="Segoe UI", size=24, weight="bold"),
            text_color=("#1f6feb", "#58a6ff")
        )
        self.brand_signature.pack(side="left", anchor="center")

        self.theme_toggle_btn = ctk.CTkButton(
            self.header_block,
            text="🌓 Layout Theme",
            width=120,
            height=32,
            corner_radius=20,
            command=self.perform_runtime_theme_swap
        )
        self.theme_toggle_btn.pack(side="right", anchor="center")

        # --- CHAT STREAM PRESENTATION CONTENT VIEWPORT ---
        self.scroll_viewport = ctk.CTkScrollableFrame(self.canvas_workspace, fg_color="transparent")
        self.scroll_viewport.grid(row=1, column=0, padx=30, pady=10, sticky="nsew")
        self.scroll_viewport.grid_columnconfigure(0, weight=1)

        # BYPASS CONSTRAINT: Force scrolling canvas scrollbar component hidden securely from view arrays
        if hasattr(self.scroll_viewport, "_scrollbar"):
            self.scroll_viewport._scrollbar.configure(width=0)

        # --- LOWER CONTROL FIELD CONTROL LAYER ---
        self.floating_control_deck = ctk.CTkFrame(self.canvas_workspace, fg_color="transparent")
        self.floating_control_deck.grid(row=2, column=0, padx=30, pady=(5, 25), sticky="ew")
        self.floating_control_deck.grid_columnconfigure(0, weight=1)

        self.pill_input_container = ctk.CTkFrame(self.floating_control_deck, corner_radius=28, border_width=1, fg_color=("#f6f8fa", "#161b22"))
        self.pill_input_container.grid(row=0, column=0, sticky="ew")
        self.pill_input_container.grid_columnconfigure(0, weight=1)

        self.chat_input_field = ctk.CTkEntry(
            self.pill_input_container,
            placeholder_text="Ask Uzghaar AI anything... (Press Enter to execute query pipeline)",
            height=54,
            border_width=0,
            fg_color="transparent"
        )
        self.chat_input_field.grid(row=0, column=0, padx=(25, 10), pady=2, sticky="ew")
        self.chat_input_field.bind("<Return>", lambda event: self.dispatch_processing_pipeline())

        # Dropdown Model Infrastructure Configuration Router
        self.architecture_selector = ctk.CTkOptionMenu(
            self.pill_input_container,
            values=["qwen2.5:0.5b", "codegemma:2b", "qwen2.5:14b"],
            width=140,
            height=34,
            corner_radius=16,
            command=lambda m: setattr(self, 'active_model', m)
        )
        self.architecture_selector.set(self.active_model)
        self.architecture_selector.grid(row=0, column=1, padx=(5, 5), pady=2)

        # Stream Execution Interceptor Signal Node
        self.btn_stop_generation = ctk.CTkButton(
            self.pill_input_container, text="⏹", width=42, height=42, corner_radius=21,
            text_color="white", fg_color="#da3637", hover_color="#f85149", font=ctk.CTkFont(size=14, weight="bold"),
            command=lambda: setattr(self, 'stop_requested', True)
        )
        self.btn_stop_generation.grid(row=0, column=2, padx=(2, 2), pady=2)
        self.btn_stop_generation.configure(state="disabled")

        # Submit Target Trigger Arrow button Node
        self.btn_submit_action = ctk.CTkButton(
            self.pill_input_container, text="➔", width=42, height=42, corner_radius=21,
            text_color="white", font=ctk.CTkFont(size=16, weight="bold"), command=self.dispatch_processing_pipeline
        )
        self.btn_submit_action.grid(row=0, column=3, padx=(2, 10), pady=2)

    def reload_sidebar_sessions_from_db(self):
        """Re-renders historic log access triggers directly extracted out from storage tables."""
        for child in self.flat_history_panel.winfo_children():
            child.destroy()
        self.sidebar_buttons_map.clear()

        sessions = self.db.fetch_all_sessions()
        for sid, title in sessions:
            self.render_session_row_widget(sid, title)
            
        if sessions:
            self.load_selected_session_scope(sessions[0][0])
        else:
            self.initialize_fresh_session()

    def render_session_row_widget(self, session_id, title):
        """Assembles mouse hover responsive context panels inside history rails."""
        row_container = ctk.CTkFrame(self.flat_history_panel, fg_color="transparent", height=38)
        row_container.pack(fill="x", padx=2, pady=2)
        row_container.pack_propagate(False)

        btn = ctk.CTkButton(
            row_container,
            text=f"💬 {title}",
            anchor="w",
            corner_radius=6,
            fg_color="transparent",
            text_color=("#24292f", "#c9d1d9"),
            command=lambda sid=session_id: self.load_selected_session_scope(sid)
        )
        btn.pack(side="left", fill="both", expand=True, padx=(2, 0))

        # Context Panel Drop Configuration Anchor Token
        opt_btn = ctk.CTkButton(
            row_container, text="•••", width=30, height=28, corner_radius=4,
            fg_color="transparent", text_color="#656d76", hover_color=("#e1e4e8", "#30363d")
        )
        opt_btn.bind("<Button-1>", lambda e, sid=session_id: self.trigger_session_action_menu(e, sid))

        # Attach Event Trace Closures to bypass flickering state lags
        def on_enter(e):
            opt_btn.pack(side="right", padx=4, pady=4)
        def on_leave(e):
            x, y = self.winfo_pointerxy()
            widget_under_mouse = self.winfo_containing(x, y)
            if widget_under_mouse not in [row_container, btn, opt_btn]:
                opt_btn.pack_forget()

        row_container.bind("<Enter>", on_enter)
        row_container.bind("<Leave>", on_leave)
        btn.bind("<Enter>", on_enter)
        btn.bind("<Leave>", on_leave)

        self.sidebar_buttons_map[session_id] = (btn, row_container)

    def trigger_session_action_menu(self, event, session_id):
        """Generates dynamic floating dropdown windows relative to cursor coordinates."""
        menu = ctk.CTkToplevel(self)
        menu.wm_overrideredirect(True)
        menu.geometry(f"110x75+{event.x_root}+{event.y_root}")
        menu.configure(fg_color=("#ffffff", "#161b22"))
        menu.attributes("-topmost", True)
        menu.bind("<FocusOut>", lambda e: menu.destroy())

        btn_rename = ctk.CTkButton(
            menu, text="✏️ Rename", height=28, corner_radius=4, fg_color="transparent",
            text_color=("#24292f", "#c9d1d9"), anchor="w",
            command=lambda: [menu.destroy(), self.prompt_session_rename(session_id)]
        )
        btn_rename.pack(fill="x", padx=4, pady=2)

        btn_delete = ctk.CTkButton(
            menu, text="🗑️ Delete", height=28, corner_radius=4, fg_color="transparent",
            text_color="#da3637", anchor="w",
            command=lambda: [menu.destroy(), self.execute_session_purge(session_id)]
        )
        btn_delete.pack(fill="x", padx=4, pady=2)
        menu.focus_set()

    def prompt_session_rename(self, session_id):
        dialog = ctk.CTkInputDialog(text="Enter new session title label:", title="Rename Session Matrix")
        new_name = dialog.get_input()
        if new_name and new_name.strip():
            self.db.update_session_title(session_id, new_name.strip())
            self.reload_sidebar_sessions_from_db()

    def execute_session_purge(self, session_id):
        self.db.delete_session_scope(session_id)
        if self.active_session_id == session_id:
            self.active_session_id = None
        self.reload_sidebar_sessions_from_db()

    def initialize_fresh_session(self):
        self.active_session_id = datetime.now().strftime("%Y%m%m_%H%M%S_%f")
        self.db.create_new_session(self.active_session_id, "New Chat Active Scope")

        for child in self.scroll_viewport.winfo_children():
            child.destroy()

        welcome_frame = ctk.CTkFrame(self.scroll_viewport, corner_radius=12, fg_color=("#eff3f6", "#21262d"), border_width=1, border_color=("#d0d7de", "#30363d"))
        welcome_frame.pack(fill="x", padx=10, pady=15)
        
        lbl_welcome = ctk.CTkLabel(
            welcome_frame,
            text=f"🚀 [UZGHAAR CORE LOG DATABASE ACTIVE]\nEngine Ready. Scrollbar channels hidden completely for professional minimalist interface canvas layers.",
            font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"),
            pady=15
        )
        lbl_welcome.pack(fill="x")
        self.reload_sidebar_sessions_from_db()

    def load_selected_session_scope(self, session_id):
        if self.is_generating:
            return
        self.active_session_id = session_id
        
        for child in self.scroll_viewport.winfo_children():
            child.destroy()

        messages = self.db.fetch_message_history(session_id)
        for msg in messages:
            if msg["role"] == "user":
                self.render_premium_user_bubble(msg["content"])
            else:
                self.render_premium_ai_block(msg["content"])
                
        for sid, (btn, _) in self.sidebar_buttons_map.items():
            if sid == self.active_session_id:
                btn.configure(fg_color=("#1f6feb", "#21262d"), text_color="white")
            else:
                btn.configure(fg_color="transparent", text_color=("#24292f", "#c9d1d9"))

    def dispatch_processing_pipeline(self):
        prompt_content = self.chat_input_field.get().strip()
        if not prompt_content or self.is_generating:
            return

        self.is_generating = True
        self.stop_requested = False
        
        self.btn_submit_action.configure(state="disabled")
        self.btn_stop_generation.configure(state="normal")
        self.chat_input_field.delete(0, ctk.END)

        current_history = self.db.fetch_message_history(self.active_session_id)
        if len(current_history) == 0:
            truncated = prompt_content[:18] + "..." if len(prompt_content) > 18 else prompt_content
            self.db.update_session_title(self.active_session_id, truncated)

        self.db.append_chat_message(self.active_session_id, "user", prompt_content)
        self.render_premium_user_bubble(prompt_content)
        self.reload_sidebar_sessions_from_db()

        threading.Thread(target=self.consume_ollama_stream_pipeline, args=(prompt_content,), daemon=True).start()

    def render_premium_user_bubble(self, content_text):
        outer_container = ctk.CTkFrame(self.scroll_viewport, fg_color="transparent")
        outer_container.pack(fill="x", padx=10, pady=8, anchor="e")

        bubble_box = ctk.CTkFrame(outer_container, corner_radius=16, fg_color=("#ddf4ff", "#0c2d6b"), border_width=1, border_color=("#54aeff", "#1f6feb"))
        bubble_box.pack(side="right", padx=(120, 5))

        lbl_user = ctk.CTkLabel(bubble_box, text=content_text, font=ctk.CTkFont(family="Segoe UI", size=14), text_color=("#074592", "#c9d1d9"), justify="left", wraplength=600, padx=16, pady=12)
        lbl_user.pack()
        
        # Real-time window positioning automation jump to bottom
        self.scroll_viewport._parent_canvas.yview_moveto(1.0)

    def render_premium_ai_block(self, content_text):
        outer_container = ctk.CTkFrame(self.scroll_viewport, fg_color="transparent")
        outer_container.pack(fill="x", padx=10, pady=8, anchor="w")

        ai_box = ctk.CTkFrame(outer_container, corner_radius=16, fg_color=("#f6f8fa", "#161b22"), border_width=1, border_color=("#d0d7de", "#30363d"))
        ai_box.pack(side="left", fill="x", expand=True, padx=(5, 120))

        top_bar = ctk.CTkFrame(ai_box, fg_color="transparent", height=30)
        top_bar.pack(fill="x", padx=12, pady=(8, 2))
        
        lbl_identity = ctk.CTkLabel(top_bar, text="✨ Uzghaar AI Engine", font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"), text_color="#238636")
        lbl_identity.pack(side="left")

        btn_copy = ctk.CTkButton(
            top_bar, text="📋 Copy Response", width=110, height=24, corner_radius=6,
            text_color=("#24292f", "#c9d1d9"), font=ctk.CTkFont(size=11, weight="bold"), fg_color=("#eff3f6", "#21262d"),
            command=lambda: pyperclip.copy(content_text)
        )
        btn_copy.pack(side="right")

        lbl_body = ctk.CTkLabel(ai_box, text=content_text, font=ctk.CTkFont(family="Segoe UI", size=14), justify="left", wraplength=650, padx=18, pady=12)
        lbl_body.pack(anchor="w")
        
        self.scroll_viewport._parent_canvas.yview_moveto(1.0)

    def consume_ollama_stream_pipeline(self, prompt_text):
        """Asynchronously pulls raw stream structures and updates rich structured text responses."""
        system_rules = (
            "You are Uzghaar AI, an advanced AI application backend engine. You MUST generate rich text "
            "using professional content distribution architectures. Focus heavily on layout richness:\n"
            "1. Use active emojis relevant to context at start of points.\n"
            "2. Wrap important structural sections in ALL CAPS line headers.\n"
            "3. Render breakdowns cleanly with dash tokens ('-') or bullet styles.\n"
            "4. Split paragraphs using logical double-newlines spacing blocks.\n"
            "Do NOT output raw markdown symbols like asterisks tokens."
        )

        history_context = self.db.fetch_message_history(self.active_session_id)

        outer_container = ctk.CTkFrame(self.scroll_viewport, fg_color="transparent")
        outer_container.pack(fill="x", padx=10, pady=8, anchor="w")

        ai_box = ctk.CTkFrame(outer_container, corner_radius=16, fg_color=("#f6f8fa", "#161b22"), border_width=1, border_color=("#d0d7de", "#30363d"))
        ai_box.pack(side="left", fill="x", expand=True, padx=(5, 120))

        top_bar = ctk.CTkFrame(ai_box, fg_color="transparent", height=32)
        top_bar.pack(fill="x", padx=12, pady=(8, 2))

        lbl_identity = ctk.CTkLabel(top_bar, text="✨ Uzghaar AI Engine", font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"), text_color="#238636")
        lbl_identity.pack(side="left")

        lbl_stream_body = ctk.CTkLabel(ai_box, text="Thinking...", font=ctk.CTkFont(family="Segoe UI", size=14), justify="left", wraplength=650, padx=18, pady=12)
        lbl_stream_body.pack(anchor="w")

        stream_buffer = ""

        try:
            stream = ollama.chat(
                model=self.active_model,
                messages=[{"role": "system", "content": system_rules}] + history_context,
                stream=True,
                options={"temperature": 0.3}
            )

            for chunk in stream:
                if self.stop_requested:
                    stream_buffer += "\n\n⏹ [Inference generation halted by user context signal.]"
                    break

                token = chunk.get("message", {}).get("content", "")
                stream_buffer += token
                
                # Push chunks safely to the main presentation loops
                self.after(0, lambda text=stream_buffer: lbl_stream_body.configure(text=text))
                self.after(0, lambda: self.scroll_viewport._parent_canvas.yview_moveto(1.0))

            self.db.append_chat_message(self.active_session_id, "assistant", stream_buffer)

            btn_copy = ctk.CTkButton(
                top_bar, text="📋 Copy Response", width=110, height=24, corner_radius=6,
                text_color=("#24292f", "#c9d1d9"), font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"), fg_color=("#eff3f6", "#21262d"),
                command=lambda text=stream_buffer: pyperclip.copy(text)
            )
            btn_copy.pack(side="right")

        except Exception as e:
            stream_buffer = f"❌ API Stream Fault Exception: {str(e)}"
            self.after(0, lambda text=stream_buffer: lbl_stream_body.configure(text=text))

        self.after(0, self.restore_control_deck_states)

    def restore_control_deck_states(self):
        self.is_generating = False
        self.btn_submit_action.configure(state="normal")
        self.btn_stop_generation.configure(state="disabled")

    def perform_runtime_theme_swap(self):
        if self.current_theme == "Light":
            ctk.set_appearance_mode("Dark")
            self.current_theme = "Dark"
        else:
            ctk.set_appearance_mode("Light")
            self.current_theme = "Light"

if __name__ == "__main__":
    app = UzghaarWebEngine()
    app.mainloop()