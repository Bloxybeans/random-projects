import tkinter as tk
from tkinter import filedialog, scrolledtext, messagebox
import subprocess
import threading
import queue
import os

class EmulatorGUI(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.master = master
        master.title("Conceptual x86-64 Emulator GUI")
        self.pack(fill=tk.BOTH, expand=True)

        self.cpp_process = None # To hold the subprocess object
        self.output_queue = queue.Queue() # Queue for thread-safe output
        self.output_thread = None # To hold the output reading thread

        self.create_widgets()

    def create_widgets(self):
        # Frame for buttons
        button_frame = tk.Frame(self)
        button_frame.pack(pady=5, padx=10, fill=tk.X)

        self.run_button = tk.Button(button_frame, text="Run Conceptual C++ Emulator", command=self.run_cpp_emulator)
        self.run_button.pack(side=tk.LEFT, padx=5)

        self.stop_button = tk.Button(button_frame, text="Stop Emulator", command=self.stop_cpp_emulator, state=tk.DISABLED)
        self.stop_button.pack(side=tk.LEFT, padx=5)

        # Output text area
        self.output_text = scrolledtext.ScrolledText(self, wrap=tk.WORD, width=80, height=25)
        self.output_text.pack(pady=10, padx=10, fill=tk.BOTH, expand=True)

    def run_cpp_emulator(self):
        """Launches the compiled C++ emulator executable."""
        if self.cpp_process is not None and self.cpp_process.poll() is None:
            messagebox.showwarning("Already Running", "The emulator is already running.")
            return

        # Clear previous output
        self.output_text.delete(1.0, tk.END)
        self.output_text.insert(tk.END, "Launching C++ emulator...\n")
        self.output_text.see(tk.END)

        try:
            # Launch the C++ executable as a subprocess
            # stdout=subprocess.PIPE allows us to capture its output
            # bufsize=1 makes the output line-buffered (useful for reading line by line)
            # text=True decodes output as text (requires Python 3.6+)
            self.cpp_process = subprocess.Popen(
                ["./test.exe"], # Command to run (assuming test.exe is in the same directory)
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT, # Redirect stderr to stdout
                bufsize=1,
                text=True,
                cwd=os.path.dirname(os.path.abspath(__file__)) # Set current directory to script location
            )

            self.run_button.config(state=tk.DISABLED)
            self.stop_button.config(state=tk.NORMAL)

            # Start a thread to read the output from the C++ process
            self.output_thread = threading.Thread(target=self.read_output)
            self.output_thread.daemon = True # Allow the thread to exit with the main program
            self.output_thread.start()

            # Start checking the queue for output
            self.after(100, self.check_output_queue) # Check every 100ms

        except FileNotFoundError:
            messagebox.showerror("Error", "C++ executable 'test.exe' not found.\n"
                                         "Please make sure you have compiled the C++ code "
                                         "and placed 'test.exe' in the same directory as this script.")
            self.reset_buttons()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to launch C++ emulator: {e}")
            self.reset_buttons()

    def read_output(self):
        """Reads output from the C++ subprocess and puts it in the queue."""
        if self.cpp_process and self.cpp_process.stdout:
            for line in iter(self.cpp_process.stdout.readline, ''):
                self.output_queue.put(line)
            self.cpp_process.stdout.close()
            # Once the process finishes, put a special marker in the queue
            self.output_queue.put(None)


    def check_output_queue(self):
        """Checks the queue for new output and updates the text widget."""
        try:
            while True:
                line = self.output_queue.get_nowait()
                if line is None: # Check for the process finished marker
                    self.output_thread.join() # Wait for the thread to finish
                    self.reset_buttons()
                    self.output_text.insert(tk.END, "\nC++ emulator process finished.\n")
                    self.output_text.see(tk.END)
                    return # Stop checking the queue
                self.output_text.insert(tk.END, line)
                self.output_text.see(tk.END)
                self.output_text.update_idletasks() # Update GUI immediately
        except queue.Empty:
            # No new output, check again later
            self.after(100, self.check_output_queue)

    def stop_cpp_emulator(self):
        """Terminates the C++ emulator subprocess."""
        if self.cpp_process and self.cpp_process.poll() is None: # Check if process is running
            self.output_text.insert(tk.END, "\nStopping C++ emulator...\n")
            self.output_text.see(tk.END)
            try:
                self.cpp_process.terminate() # Send terminate signal
                self.cpp_process.wait(timeout=5) # Wait for process to exit
                self.output_text.insert(tk.END, "C++ emulator stopped.\n")
                self.output_text.see(tk.END)
            except subprocess.TimeoutExpired:
                 self.output_text.insert(tk.END, "C++ emulator did not terminate, killing...\n")
                 self.output_text.see(tk.END)
                 self.cpp_process.kill() # Force kill if terminate failed
                 self.output_text.insert(tk.END, "C++ emulator killed.\n")
                 self.output_text.see(tk.END)
            except Exception as e:
                 messagebox.showerror("Error", f"Failed to stop C++ emulator: {e}")
            finally:
                self.reset_buttons()
        else:
            messagebox.showwarning("Not Running", "The emulator is not currently running.")

    def reset_buttons(self):
        """Resets the button states."""
        self.run_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)


# --- Main execution ---
if __name__ == "__main__":
    root = tk.Tk()
    app = EmulatorGUI(master=root)
    root.geometry("700x500") # Set a default window size
    root.mainloop()
