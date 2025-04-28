# iptv_player.py

import tkinter as tk
from tkinter import messagebox, simpledialog, Listbox, Scrollbar
import vlc
import platform
import os
import json

CHANNELS_FILE = "channels.json"

class IPTVPlayer:
    def __init__(self, root):
        self.root = root
        self.root.title("IPTV Player")

        # VLC Player
        self.Instance = vlc.Instance()
        self.player = self.Instance.media_player_new()

        # Video Frame
        self.video_frame = tk.Frame(self.root, bg="black")
        self.video_frame.pack(fill=tk.BOTH, expand=1)

        self.canvas = tk.Canvas(self.video_frame, bg="black")
        self.canvas.pack(fill=tk.BOTH, expand=1)

        # Search bar
        self.search_var = tk.StringVar()
        self.search_var.trace("w", self.update_channel_list)
        self.search_entry = tk.Entry(self.root, textvariable=self.search_var)
        self.search_entry.pack(fill=tk.X, padx=5, pady=5)
        self.search_entry.insert(0, "Search channel...")

        # Controls
        controls_frame = tk.Frame(self.root)
        controls_frame.pack(fill=tk.X)

        self.add_channel_button = tk.Button(controls_frame, text="Add Channel", command=self.add_channel)
        self.add_channel_button.pack(side=tk.LEFT, padx=5, pady=5)

        self.play_button = tk.Button(controls_frame, text="Play", command=self.play_channel)
        self.play_button.pack(side=tk.LEFT, padx=5, pady=5)

        self.pause_button = tk.Button(controls_frame, text="Pause", command=self.pause_channel)
        self.pause_button.pack(side=tk.LEFT, padx=5, pady=5)

        self.stop_button = tk.Button(controls_frame, text="Stop", command=self.stop_channel)
        self.stop_button.pack(side=tk.LEFT, padx=5, pady=5)

        self.volume_scale = tk.Scale(controls_frame, from_=0, to=100, orient=tk.HORIZONTAL, label="Volume", command=self.set_volume)
        self.volume_scale.set(50)
        self.volume_scale.pack(side=tk.RIGHT, padx=5, pady=5)

        # List of Channels
        self.channels_frame = tk.Frame(self.root)
        self.channels_frame.pack(fill=tk.BOTH, expand=1)

        self.scrollbar = Scrollbar(self.channels_frame)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.channels_listbox = Listbox(self.channels_frame, yscrollcommand=self.scrollbar.set)
        self.channels_listbox.pack(fill=tk.BOTH, expand=1)

        self.scrollbar.config(command=self.channels_listbox.yview)

        # Full Channels list
        self.channels = []         # List of dicts {'nombre', 'url'}
        self.filtered_channels = []  # List of dicts according to search

        self.update_video_frame()
        self.load_channels()

    def update_video_frame(self):
        """Attach VLC video to the Tkinter canvas."""
        if platform.system() == "Windows":
            self.player.set_hwnd(self.canvas.winfo_id())
        else:
            self.player.set_xwindow(self.canvas.winfo_id())

    def load_channels(self):
        """Load channels from a JSON file."""
        if os.path.exists(CHANNELS_FILE):
            with open(CHANNELS_FILE, "r", encoding="utf-8") as f:
                self.channels = json.load(f)
                self.filtered_channels = self.channels.copy()
                self.refresh_channel_list()
        else:
            messagebox.showwarning("Channels File Missing", f"{CHANNELS_FILE} not found!")

    def save_channels(self):
        """Save current channels to the JSON file."""
        with open(CHANNELS_FILE, "w", encoding="utf-8") as f:
            json.dump(self.channels, f, indent=2, ensure_ascii=False)

    def refresh_channel_list(self):
        """Refresh listbox with filtered channels."""
        self.channels_listbox.delete(0, tk.END)
        for channel in self.filtered_channels:
            self.channels_listbox.insert(tk.END, channel["nombre"])

    def update_channel_list(self, *args):
        """Update the list when searching."""
        search_term = self.search_var.get().lower()
        self.filtered_channels = [c for c in self.channels if search_term in c["nombre"].lower()]
        self.refresh_channel_list()

    def add_channel(self):
        nombre = simpledialog.askstring("Input", "Enter Channel Name:")
        if not nombre:
            return
        url = simpledialog.askstring("Input", "Enter IPTV stream URL:")
        if url:
            new_channel = {"nombre": nombre, "url": url}
            self.channels.append(new_channel)
            self.update_channel_list()
            self.save_channels()
            messagebox.showinfo("Channel Added", f"Channel added: {nombre}")

    def play_channel(self):
        selection = self.channels_listbox.curselection()
        if not selection:
            messagebox.showwarning("No Channel Selected", "Please select a channel from the list.")
            return

        index = selection[0]
        channel_url = self.filtered_channels[index]["url"]
        media = self.Instance.media_new(channel_url)
        self.player.set_media(media)
        self.player.play()

    def pause_channel(self):
        self.player.pause()

    def stop_channel(self):
        self.player.stop()

    def set_volume(self, volume):
        self.player.audio_set_volume(int(volume))

    def close(self):
        self.player.stop()
        self.root.quit()

if __name__ == "__main__":
    root = tk.Tk()
    player = IPTVPlayer(root)
    root.protocol("WM_DELETE_WINDOW", player.close)
    root.mainloop()
