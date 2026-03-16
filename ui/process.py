import threading
import psutil
import customtkinter as ctk
import heapq
import logging

class ProcessUI:
    def __init__(self, app, parent_frame):
        self.app = app
        self.frame = parent_frame
        
        self._proc_rows = []
        self._proc_thread_running = False
        
        self.build_ui()

    def build_ui(self):
        """Constructs the Process Viewer UI elements."""
        self.process_title = ctk.CTkLabel(self.frame, text="Top Memory Processes", font=("Century Gothic", 18, "bold"), text_color="#FFFFFF")
        self.process_title.pack(pady=(10, 25))

        self.process_scroll = ctk.CTkScrollableFrame(self.frame, fg_color="transparent", corner_radius=0,
                                                     scrollbar_button_color="#27272A", scrollbar_button_hover_color="#3F3F46")
        self.process_scroll.pack(fill="both", expand=True, pady=5)
        
        for i in range(10):
            row_frame = ctk.CTkFrame(self.process_scroll, fg_color=self.app.card_color, corner_radius=8)
            
            lbl_name = ctk.CTkLabel(row_frame, text="", font=("Century Gothic", 13, "bold"), text_color="#FFFFFF")
            lbl_name.pack(side="left", padx=15, pady=12)

            btn_kill = ctk.CTkButton(row_frame, text="Kill", width=60, height=28, corner_radius=6,
                                     fg_color="#3F3F46", hover_color="#EF4444", text_color="#FFFFFF",
                                     font=("Century Gothic", 12, "bold"))
            btn_kill.pack(side="right", padx=15, pady=12)

            lbl_mem = ctk.CTkLabel(row_frame, text="", font=("Century Gothic", 13, "bold"))
            lbl_mem.pack(side="right", padx=15, pady=12)

            row_frame.pack_forget()

            self._proc_rows.append({
                "frame": row_frame,
                "name": lbl_name,
                "btn": btn_kill,
                "mem": lbl_mem
            })

    def process_page_loop(self):
        """Maintains the cyclic update loop for rendering top processes when the tab is active."""
        if not getattr(self.app, '_proc_refresh_active', False): return
        if self._proc_thread_running: return
        threading.Thread(target=self._fetch_processes_thread, daemon=True).start()
        self.app._proc_loop_id = self.app.after(3000, self.process_page_loop)

    def _fetch_processes_thread(self):
        """Gathers system process stats by memory usage on a background thread."""
        self._proc_thread_running = True
        try:
            process_list = []
            for proc in psutil.process_iter(['pid', 'name', 'memory_info']):
                try:
                    if proc.info['pid'] == 0:  
                        continue
                    mem_bytes = proc.info['memory_info'].rss
                    process_list.append({
                        'pid': proc.info['pid'],
                        'name': proc.info['name'],
                        'mem_mb': mem_bytes / (1024 * 1024)
                    })
                except Exception as e:
                    logging.debug(f"[process] {e}")
                    continue
                    
            top_10 = heapq.nlargest(10, process_list, key=lambda x: x['mem_mb'])
            
            self.app.after(0, lambda: self._render_processes(top_10))
        finally:
            self._proc_thread_running = False

    def _render_processes(self, top_processes):
        """Applies the fetched top processes to the pre-rendered UI rows."""
        for i in range(10):
            if i < len(top_processes):
                p = top_processes[i]
                row = self._proc_rows[i]
                
                row["frame"].pack(fill="x", pady=4, padx=8)
                row["name"].configure(text=p['name'])
                row["btn"].configure(command=lambda pid=p['pid'], name=p['name']: self.kill_process(pid, name))

                mem_mb = p['mem_mb']
                if mem_mb < 200: color = "#10B981" 
                elif mem_mb < 500: color = "#F59E0B" 
                else: color = "#EF4444" 
                    
                row["mem"].configure(text=f"{mem_mb:.1f} MB", text_color=color)
            else:
                self._proc_rows[i]["frame"].pack_forget()

    def kill_process(self, pid, name):
        """Attempts to terminate a target process by PID."""
        try:
            psutil.Process(pid).terminate()
            if hasattr(self.app, 'show_toast'):
                self.app.show_toast(f"Terminated {name} (PID: {pid})", "#10B981")
            threading.Thread(target=self._fetch_processes_thread, daemon=True).start()
        except psutil.AccessDenied:
            if hasattr(self.app, 'show_toast'):
                self.app.show_toast(f"Access Denied: Cannot kill {name}", "#EF4444")
        except Exception as e:
            if hasattr(self.app, 'show_toast'):
                self.app.show_toast(f"Error: Could not kill {name}", "#EF4444")
            logging.debug(f"[process] kill error: {e}")