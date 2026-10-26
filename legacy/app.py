#!/usr/bin/env python3
import gi
import os
import json
import socket
import subprocess
import threading
from datetime import datetime, timezone
from pathlib import Path

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Gio, GLib, Gdk, Gdk

APP_ID = "io.yoga.MediaPlayer"
SOCKET = f"/run/user/{os.getuid()}/yoga-media-mpv.sock"

class MediaPlayer(Gtk.Application):
    def __init__(self):
        super().__init__(
            application_id=APP_ID,
            flags=Gio.ApplicationFlags.FLAGS_NONE
        )
        self.window = None
        self.player = None

    def command(self, *args):
        try:
            with socket.socket(socket.AF_UNIX) as s:
                s.settimeout(1)
                s.connect(SOCKET)
                s.sendall((json.dumps({
                    "command": list(args)
                }) + "\n").encode())
                data = b""
                while b"\n" not in data:
                    chunk = s.recv(4096)
                    if not chunk:
                        break
                    data += chunk
                return json.loads(data.split(b"\n")[0])
        except (OSError, ValueError, IndexError):
            return {"error": "Player not ready"}

    def start_player(self):
        if self.player and self.player.poll() is None:
            return

        if Path(SOCKET).exists():
            try:
                test = self.command("get_property", "mpv-version")
                if test.get("error") == "success":
                    return
            except Exception:
                pass
            Path(SOCKET).unlink(missing_ok=True)

        self.player = subprocess.Popen([
            "/usr/bin/mpv",
            "--idle=yes",
            "--fullscreen=no",
            "--autofit=800x450",
            "--keepaspect=yes",
            "--video-align-x=0",
            "--video-align-y=0",
            "--video-zoom=0",
            "--force-window=no",
            "--vo=gpu",
            "--gpu-api=opengl",
            "--gpu-context=wayland",
            "--hwdec=vaapi",
            "--prefetch-playlist",
            "--ytdl-raw-options=yes-playlist=",
            "--ytdl-format=bestvideo[height<=480][vcodec^=avc1]+bestaudio/best[height<=480]",
            f"--input-ipc-server={SOCKET}",
            "--no-terminal"
        ], stdout=subprocess.DEVNULL,
           stderr=subprocess.DEVNULL)

    def save_history(self, url):
        path = Path.home() / ".local/share/yoga-media-player/history.json"
        try:
            history = json.loads(path.read_text())
            if not isinstance(history, list):
                history = []
        except (OSError, ValueError):
            history = []

        history = [
            item for item in history
            if isinstance(item, dict) and item.get("url") != url
        ]
        history.insert(0, {
            "url": url,
            "opened": datetime.now(timezone.utc).isoformat()
        })

        temporary = path.with_suffix(".json.tmp")
        temporary.write_text(json.dumps(history[:100], indent=2) + "\n")
        temporary.replace(path)

    def play_preserving_queue(self, url):
        state = self.command("get_property", "idle-active")
        if state.get("error") != "success":
            return state

        if state.get("data") is True:
            result = self.command("loadfile", url, "append-play")
            if result.get("error") != "success":
                return result

            count = self.command("get_property", "playlist-count")
            if count.get("error") != "success":
                return count

            total = count.get("data", 0)
            if total > 1:
                moved = self.command("playlist-move", total - 1, 0)
                if moved.get("error") != "success":
                    return moved

            return result

        result = self.command("loadfile", url, "insert-next-play")
        if result.get("error") != "success":
            return result

        return self.command("playlist-next", "force")

    def play_url(self, button):
        url = self.url.get_text().strip()
        if not url:
            self.status.set_text("Enter a media URL first")
            return

        result = self.play_preserving_queue(url)
        if result.get("error") == "success":
            self.save_history(url)
            self.status.set_text("Loading media...")
        else:
            self.status.set_text("Player not ready")

    def get_open_media(self):
        url = self.open_entry.get_text().strip()

        if not url:
            self.open_status.set_text("Select a file or enter a URL")
            return None

        if url.lower().split("?", 1)[0].endswith(".m3u"):
            self.open_status.set_text(
                "Select a channel from the playlist first"
            )
            return None

        return url

    def play_open_media(self, button):
        url = self.get_open_media()
        if not url:
            return

        result = self.play_preserving_queue(url)

        if result.get("error") == "success":
            self.save_history(url)
            self.url.set_text(url)
            self.open_status.set_text("Loading selected media...")
        else:
            self.open_status.set_text(
                "Playback failed: " + result.get("error", "unknown")
            )

    def queue_open_media(self, button):
        url = self.get_open_media()
        if not url:
            return

        result = self.command("loadfile", url, "append")

        if result.get("error") == "success":
            self.open_status.set_text("Added to playback queue")
            self.refresh_queue()
        else:
            self.open_status.set_text(
                "Queue failed: " + result.get("error", "unknown")
            )

    def control(self, button, action):
        result = self.command(*action)
        if result.get("error") != "success":
            self.status.set_text("Player not ready")








    def refresh_history(self, button=None):
        self.history_store.clear()
        path = Path.home() / ".local/share/yoga-media-player/history.json"
        try:
            records = json.loads(path.read_text())
        except (OSError, ValueError):
            records = []

        cache_path = Path.home() / ".local/share/yoga-media-player/titles.json"
        try:
            titles = json.loads(cache_path.read_text())
            if not isinstance(titles, dict):
                titles = {}
        except (OSError, ValueError):
            titles = {}

        for item in records:
            if isinstance(item, dict) and item.get("url"):
                url = item["url"]
                title = titles.get(url) or item.get("title") or url
                self.history_store.append([
                    item.get("opened", "")[:16].replace("T", " "),
                    title,
                    url
                ])

    def selected_history_url(self):
        model, selected = self.history_view.get_selection().get_selected()
        return model[selected][2] if selected is not None else None

    def replay_history(self, button):
        url = self.selected_history_url()
        if not url:
            self.status.set_text("Select a history entry first")
            return
        self.url.set_text(url)
        self.play_url(None)
        self.refresh_history()
        self.notebook.set_current_page(0)

    def queue_history(self, button):
        url = self.selected_history_url()
        if not url:
            return

        result = self.command("loadfile", url, "append")

        if result.get("error") == "success":
            self.refresh_queue()
            self.status.set_text("Added history item to queue")
        else:
            self.status.set_text(
                "Queue failed: " + result.get("error", "unknown")
            )

    def copy_history(self, button):
        url = self.selected_history_url()
        if url:
            Gtk.Clipboard.get(Gdk.SELECTION_CLIPBOARD).set_text(url, -1)

    def delete_history(self, button):
        url = self.selected_history_url()
        if not url:
            return

        path = Path.home() / ".local/share/yoga-media-player/history.json"
        try:
            records = json.loads(path.read_text())
            records = [item for item in records if item.get("url") != url]
            temporary = path.with_suffix(".json.tmp")
            temporary.write_text(json.dumps(records, indent=2) + "\\n")
            temporary.replace(path)
            self.refresh_history()
        except (OSError, ValueError) as e:
            self.status.set_text(str(e))


    def search_youtube(self, button):
        query = self.search_entry.get_text().strip()
        if not query:
            self.search_status.set_text("Enter a search term")
            return

        self.search_button.set_sensitive(False)
        self.search_status.set_text("Searching...")
        self.search_results.clear()

        threading.Thread(
            target=self.search_worker,
            args=(query,),
            daemon=True
        ).start()

    def search_worker(self, query):
        try:
            import json as json_module

            result = subprocess.run(
                [
                    str(Path.home() / ".local/bin/yt-dlp"),
                    "--flat-playlist",
                    "--dump-json",
                    "--no-warnings",
                    "ytsearch6:" + query
                ],
                capture_output=True,
                text=True,
                timeout=45
            )

            entries = []
            for line in result.stdout.splitlines():
                item = json_module.loads(line)
                entries.append((
                    item.get("id", ""),
                    item.get("title", "Untitled"),
                    item.get("duration")
                ))

            error = (
                result.stderr.strip().splitlines()[-1]
                if result.returncode and result.stderr.strip()
                else ""
            )

            GLib.idle_add(
                self.show_search_results, entries, error
            )

        except Exception as e:
            GLib.idle_add(
                self.show_search_results, [], str(e)
            )

    def cache_search_titles(self, entries):
        path = Path.home() / ".local/share/yoga-media-player/titles.json"

        try:
            cache = json.loads(path.read_text())
            if not isinstance(cache, dict):
                cache = {}
        except (OSError, ValueError):
            cache = {}

        for video_id, title, duration in entries:
            if video_id and title:
                url = "https://www.youtube.com/watch?v=" + video_id
                cache[url] = title

        temporary = path.with_suffix(".json.tmp")
        temporary.write_text(
            json.dumps(cache, ensure_ascii=False, indent=2) + "\n"
        )
        temporary.replace(path)

    def show_search_results(self, entries, error):
        try:
            self.cache_search_titles(entries)
        except OSError as e:
            print("Title cache error:", e)

        for video_id, title, duration in entries:
            if not video_id:
                continue

            minutes = ""
            if isinstance(duration, (int, float)):
                minutes = f" ({int(duration)//60}:{int(duration)%60:02d})"

            self.search_results.append([
                title + minutes,
                "https://www.youtube.com/watch?v=" + video_id
            ])

        self.search_status.set_text(
            f"{len(self.search_results)} results"
            if entries else (error or "No results")
        )
        self.search_button.set_sensitive(True)
        return False


    def selected_search_url(self):
        model, selected = self.search_view.get_selection().get_selected()
        if selected is None:
            self.search_status.set_text("Select a video first")
            return None
        return model[selected][1]

    def play_search_result(self, button):
        url = self.selected_search_url()
        if not url:
            return

        result = self.play_preserving_queue(url)
        if result.get("error") == "success":
            self.save_history(url)
            self.url.set_text(url)
            self.search_status.set_text("Loading selected video...")
        else:
            self.search_status.set_text(
                "Playback failed: " + result.get("error", "unknown")
            )

    def queue_search_result(self, button):
        url = self.selected_search_url()
        if not url:
            return

        result = self.command("loadfile", url, "append")
        if result.get("error") == "success":
            self.search_status.set_text("Added to playback queue")
        else:
            self.search_status.set_text(
                "Queue failed: " + result.get("error", "unknown")
            )


    def update_playback_status(self):
        result = self.command("get_property", "idle-active")

        if result.get("error") != "success":
            return True

        if result.get("data") is True:
            state = "Stopped"
        else:
            paused = self.command("get_property", "pause")
            state = "Paused" if paused.get("data") is True else "Playing"

        self.status.set_text(state)
        self.search_status.set_text(state)
        return True

    def play_selected_queue(self, button):
        model, selected = self.queue_view.get_selection().get_selected()
        if selected is None:
            self.queue_status.set_text("Select a track first")
            return

        index = model[selected][1] - 1
        result = self.command("set_property", "playlist-pos", index)

        if result.get("error") == "success":
            self.command("set_property", "pause", False)
            self.queue_status.set_text("Starting selected track...")
        else:
            self.queue_status.set_text(
                "Could not select track: " + result.get("error", "unknown")
            )

    def play_queue(self, button):
        result = self.command("get_property", "playlist-count")
        if result.get("error") != "success" or not result.get("data"):
            self.queue_status.set_text("Queue is empty")
            return

        result = self.command("set_property", "playlist-pos", 0)
        if result.get("error") == "success":
            self.command("set_property", "pause", False)
            self.queue_status.set_text("Starting queue...")
        else:
            self.queue_status.set_text(
                "Could not start queue: " + result.get("error", "unknown")
            )

    def remove_selected_queue(self, button):
        model, selected = self.queue_view.get_selection().get_selected()
        if selected is None:
            self.queue_status.set_text("Select a track first")
            return

        index = model[selected][1] - 1
        result = self.command("playlist-remove", index)

        if result.get("error") == "success":
            self.refresh_queue()
        else:
            self.queue_status.set_text(
                "Remove failed: " + result.get("error", "unknown")
            )

    def clear_queue(self, button):
        dialog = Gtk.MessageDialog(
            transient_for=self.window,
            modal=True,
            message_type=Gtk.MessageType.QUESTION,
            buttons=Gtk.ButtonsType.YES_NO,
            text="Clear the entire queue?"
        )
        response = dialog.run()
        dialog.destroy()

        if response != Gtk.ResponseType.YES:
            return

        result = self.command("playlist-clear")

        if result.get("error") == "success":
            self.refresh_queue()
        else:
            self.queue_status.set_text(
                "Clear failed: " + result.get("error", "unknown")
            )

    def refresh_queue(self, button=None):
        result = self.command("get_property", "playlist")
        if result.get("error") != "success":
            return True

        entries = result.get("data") or []

        selection = self.queue_view.get_selection()
        model, selected = selection.get_selected()
        selected_index = model[selected][1] - 1 if selected is not None else None

        self.queue_store.clear()

        cache_path = Path.home() / ".local/share/yoga-media-player/titles.json"
        try:
            titles = json.loads(cache_path.read_text())
            if not isinstance(titles, dict):
                titles = {}
        except (OSError, ValueError):
            titles = {}

        for i, item in enumerate(entries):
            url = item.get("filename") or ""
            title = titles.get(url) or item.get("title") or url or "Unknown"
            marker = "▶" if item.get("current") else ""
            self.queue_store.append([marker, i + 1, title])

        if selected_index is not None and selected_index < len(entries):
            selection.select_path(Gtk.TreePath.new_from_indices([selected_index]))

        self.queue_status.set_text(f"{len(entries)} queued")
        return True

    def browse_media(self, button):
        dialog = Gtk.FileChooserDialog(
            title="Select Media or Playlist",
            transient_for=self.window,
            action=Gtk.FileChooserAction.OPEN
        )
        dialog.add_buttons(
            "Cancel", Gtk.ResponseType.CANCEL,
            "Open", Gtk.ResponseType.OK
        )
        dialog.set_default_size(700, 500)

        response = dialog.run()
        if response == Gtk.ResponseType.OK:
            filename = dialog.get_filename()
            if filename:
                self.open_entry.set_text(filename)
                self.open_status.set_text(
                    "Selected: " + Path(filename).name
                )
                if filename.lower().endswith(".m3u"):
                    self.load_m3u_browser(filename)
                else:
                    self.m3u_panel.hide()
                    self.m3u_panel.set_no_show_all(True)
                    self.m3u_entries = []

        dialog.destroy()

    def load_m3u_browser(self, filename):
        import re

        entries = []
        name = ""
        group = "Ungrouped"

        try:
            with open(filename, encoding="utf-8-sig",
                      errors="replace") as playlist:
                for raw in playlist:
                    line = raw.strip()
                    if line.startswith("#EXTINF:"):
                        name = line.split(",", 1)[-1].strip()
                        match = re.search(
                            r'group-title="([^"]*)"', line
                        )
                        group = (
                            match.group(1).strip()
                            if match and match.group(1).strip()
                            else "Ungrouped"
                        )
                    elif line and not line.startswith("#"):
                        entries.append((name or line, group, line))
                        name = ""
                        group = "Ungrouped"
        except OSError as error:
            self.open_status.set_text(str(error))
            return

        self.m3u_entries = entries
        if entries:
            self.m3u_panel.set_no_show_all(False)
            self.m3u_panel.show_all()
        else:
            self.m3u_panel.hide()
            self.m3u_panel.set_no_show_all(True)

        self.m3u_group.remove_all()
        self.m3u_group.append_text("All Channels")

        groups = sorted(
            {entry[1] for entry in entries},
            key=str.casefold
        )
        for group in groups:
            self.m3u_group.append_text(group)

        self.m3u_group.set_active(0)
        self.filter_m3u_browser()
        self.open_status.set_text(
            f"Loaded {len(entries)} channels from "
            f"{Path(filename).name}"
        )

    def filter_m3u_browser(self, *args):
        if not hasattr(self, "m3u_entries"):
            return

        query = self.m3u_search.get_text().strip().casefold()
        group = self.m3u_group.get_active_text()

        self.m3u_store.clear()
        matches = 0

        for name, category, url in self.m3u_entries:
            if query and query not in name.casefold():
                continue
            if group and group != "All Channels" and category != group:
                continue

            matches += 1
            if matches <= 100:
                self.m3u_store.append([name, category, url])

        self.m3u_count.set_text(
            f"{matches} matching channels"
            + (" (showing first 100)" if matches > 100 else "")
        )

    def select_m3u_channel(self, selection):
        model, iterator = selection.get_selected()
        if iterator is not None:
            name = model[iterator][0]
            url = model[iterator][2]
            self.open_entry.set_text(url)
            self.open_status.set_text("Selected: " + name)

    def do_activate(self):
        if self.window:
            self.window.show_all()
            self.window.present()
            return

        self.start_player()

        self.window = Gtk.ApplicationWindow(application=self)
        self.window.set_title("Yoga Media Player")
        self.window.set_default_size(800, 600)

        header = Gtk.HeaderBar()
        header.set_title("Media Player")

        hide = Gtk.Button(label="Hide")
        hide.connect("clicked", lambda b: self.window.hide())
        header.pack_end(hide)

        close = Gtk.Button(label="Close")
        close.connect("clicked", lambda b: self.quit())
        header.pack_end(close)

        self.window.set_titlebar(header)

        notebook = Gtk.Notebook()
        self.notebook = notebook

        self.notebook = notebook


        playing = Gtk.Box(
            orientation=Gtk.Orientation.VERTICAL,
            spacing=15
        )
        playing.set_border_width(20)

        self.url = Gtk.Entry()
        self.url.set_placeholder_text("Paste media URL")
        playing.pack_start(self.url, False, False, 0)

        buttons = Gtk.Box(
            orientation=Gtk.Orientation.HORIZONTAL,
            spacing=8
        )

        actions = [
            ("Play URL", self.play_url),
            ("Previous", lambda b: self.control(b, ("playlist-prev", "weak"))),
            ("Pause / Resume", lambda b: self.control(b, ("cycle", "pause"))),
            ("Next", lambda b: self.control(b, ("playlist-next", "weak")))
        ]

        for name, callback in actions:
            btn = Gtk.Button(label=name)
            btn.connect("clicked", callback)
            buttons.pack_start(btn, True, True, 0)

        playing.pack_start(buttons, False, False, 0)

        seek_buttons = Gtk.Box(spacing=8)

        for label, seconds in [
            ("Back 30s", -30),
            ("Back 10s", -10),
            ("Forward 10s", 10),
            ("Forward 30s", 30)
        ]:
            button = Gtk.Button(label=label)
            button.connect(
                "clicked",
                lambda b, n=seconds: self.control(
                    b, ("seek", n, "relative")
                )
            )
            seek_buttons.pack_start(button, True, True, 0)

        playing.pack_start(seek_buttons, False, False, 0)

        self.status = Gtk.Label(label="Player starting...")
        playing.pack_start(self.status, False, False, 0)

        notebook.append_page(
            playing, Gtk.Label(label="Now Playing")
        )

        search_box = Gtk.Box(
            orientation=Gtk.Orientation.VERTICAL, spacing=10
        )
        search_box.set_border_width(12)

        self.search_entry = Gtk.Entry()
        self.search_entry.set_placeholder_text("Search YouTube")
        self.search_entry.connect("activate", self.search_youtube)
        search_box.pack_start(self.search_entry, False, False, 0)

        self.search_button = Gtk.Button(label="Search")
        self.search_button.connect("clicked", self.search_youtube)
        search_box.pack_start(self.search_button, False, False, 0)

        self.search_status = Gtk.Label(label="Ready to search")
        search_box.pack_start(self.search_status, False, False, 0)

        self.search_results = Gtk.ListStore(str, str)
        self.search_view = Gtk.TreeView(model=self.search_results)
        self.search_view.set_headers_visible(False)

        renderer = Gtk.CellRendererText()
        renderer.set_property("wrap-width", 500)
        renderer.set_property("wrap-mode", 2)

        column = Gtk.TreeViewColumn(
            "Results", renderer, text=0
        )
        self.search_view.append_column(column)

        scroll = Gtk.ScrolledWindow()
        scroll.add(self.search_view)
        search_box.pack_start(scroll, True, True, 0)

        search_actions = Gtk.Box(spacing=8)

        play_button = Gtk.Button(label="Play Now")
        play_button.connect("clicked", self.play_search_result)
        search_actions.pack_start(play_button, True, True, 0)

        queue_button = Gtk.Button(label="Add to Queue")
        queue_button.connect("clicked", self.queue_search_result)
        search_actions.pack_start(queue_button, True, True, 0)

        search_box.pack_start(search_actions, False, False, 0)

        notebook.append_page(
            search_box, Gtk.Label(label="Search")
        )

        queue_box = Gtk.Box(
            orientation=Gtk.Orientation.VERTICAL, spacing=10
        )
        queue_box.set_border_width(12)

        self.queue_status = Gtk.Label(label="Queue loading...")
        queue_box.pack_start(self.queue_status, False, False, 0)

        self.queue_store = Gtk.ListStore(str, int, str)
        self.queue_view = Gtk.TreeView(model=self.queue_store)

        for index, heading in enumerate(["", "#", "Track"]):
            renderer = Gtk.CellRendererText()
            if index == 2:
                renderer.set_property("ellipsize", 3)
            column = Gtk.TreeViewColumn(
                heading, renderer, text=index
            )
            self.queue_view.append_column(column)

        scroll = Gtk.ScrolledWindow()
        scroll.set_policy(
            Gtk.PolicyType.AUTOMATIC,
            Gtk.PolicyType.AUTOMATIC
        )
        scroll.add(self.queue_view)
        queue_box.pack_start(scroll, True, True, 0)

        queue_actions = Gtk.Box(spacing=8)

        for label, callback in [
            ("Play Selected", self.play_selected_queue),
            ("Play Queue", self.play_queue),
            ("Remove", self.remove_selected_queue),
            ("Clear Queue", self.clear_queue)
        ]:
            button = Gtk.Button(label=label)
            button.connect("clicked", callback)
            queue_actions.pack_start(button, True, True, 0)

        queue_box.pack_start(queue_actions, False, False, 0)

        refresh_button = Gtk.Button(label="Refresh Queue")
        refresh_button.connect("clicked", self.refresh_queue)
        queue_box.pack_start(refresh_button, False, False, 0)

        notebook.append_page(
            queue_box, Gtk.Label(label="Queue")
        )

        self.refresh_queue()
        GLib.timeout_add_seconds(3, self.refresh_queue)

        open_box = Gtk.Box(
            orientation=Gtk.Orientation.VERTICAL, spacing=12
        )
        open_box.set_border_width(12)

        self.open_entry = Gtk.Entry()
        self.open_entry.set_placeholder_text(
            "Media URL, stream URL or local file"
        )
        open_box.pack_start(self.open_entry, False, False, 0)

        browse_button = Gtk.Button(label="Browse Files")
        browse_button.connect("clicked", self.browse_media)
        open_box.pack_start(browse_button, False, False, 0)

        open_actions = Gtk.Box(spacing=8)

        self.open_play_button = Gtk.Button(label="Play Now")
        self.open_play_button.connect(
            "clicked", self.play_open_media
        )
        open_actions.pack_start(
            self.open_play_button, True, True, 0
        )

        self.open_queue_button = Gtk.Button(label="Add to Queue")
        self.open_queue_button.connect(
            "clicked", self.queue_open_media
        )
        open_actions.pack_start(
            self.open_queue_button, True, True, 0
        )

        open_box.pack_start(open_actions, False, False, 0)

        self.open_status = Gtk.Label(
            label="Supports media files, URLs, M3U, M3U8 and PLS"
        )
        self.open_status.set_line_wrap(True)
        open_box.pack_start(self.open_status, False, False, 0)

        self.m3u_panel = Gtk.Box(
            orientation=Gtk.Orientation.VERTICAL, spacing=8
        )
        self.m3u_panel.set_border_width(6)
        self.m3u_panel.set_no_show_all(True)

        self.m3u_search = Gtk.SearchEntry()
        self.m3u_search.set_placeholder_text("Search channels")
        self.m3u_search.connect(
            "search-changed", self.filter_m3u_browser
        )
        self.m3u_panel.pack_start(self.m3u_search, False, False, 0)

        self.m3u_group = Gtk.ComboBoxText()
        self.m3u_group.append_text("All Channels")
        self.m3u_group.set_active(0)
        self.m3u_group.connect(
            "changed", self.filter_m3u_browser
        )
        self.m3u_panel.pack_start(self.m3u_group, False, False, 0)

        self.m3u_count = Gtk.Label(
            label="Choose an M3U file to browse channels"
        )
        self.m3u_panel.pack_start(self.m3u_count, False, False, 0)

        self.m3u_store = Gtk.ListStore(str, str, str)
        self.m3u_view = Gtk.TreeView(model=self.m3u_store)

        for index, heading in enumerate(["Channel", "Group"]):
            renderer = Gtk.CellRendererText()
            renderer.set_property("ellipsize", 3)
            column = Gtk.TreeViewColumn(
                heading, renderer, text=index
            )
            column.set_resizable(True)
            if index == 0:
                column.set_sizing(Gtk.TreeViewColumnSizing.FIXED)
                column.set_fixed_width(300)
                column.set_min_width(150)
            self.m3u_view.append_column(column)

        self.m3u_view.get_selection().connect(
            "changed", self.select_m3u_channel
        )

        m3u_scroll = Gtk.ScrolledWindow()
        m3u_scroll.set_policy(
            Gtk.PolicyType.AUTOMATIC,
            Gtk.PolicyType.AUTOMATIC
        )
        m3u_scroll.add(self.m3u_view)
        self.m3u_panel.pack_start(m3u_scroll, True, True, 0)

        open_layout = Gtk.Box(
            orientation=Gtk.Orientation.HORIZONTAL,
            spacing=8, homogeneous=True
        )
        open_layout.pack_start(open_box, True, True, 0)
        open_layout.pack_start(self.m3u_panel, True, True, 0)

        notebook.append_page(
            open_layout, Gtk.Label(label="Open")
        )





        history_box = Gtk.Box(
            orientation=Gtk.Orientation.VERTICAL, spacing=10
        )
        history_box.set_border_width(12)

        self.history_store = Gtk.ListStore(str, str, str)
        self.history_view = Gtk.TreeView(model=self.history_store)
        self.history_view.set_headers_visible(True)

        for index, heading in enumerate(["Opened", "Title"]):
            renderer = Gtk.CellRendererText()
            renderer.set_property("ellipsize", 3)
            column = Gtk.TreeViewColumn(heading, renderer, text=index)
            column.set_resizable(True)
            self.history_view.append_column(column)

        self.history_view.connect(
            "row-activated", lambda *args: self.replay_history(None)
        )

        scroll = Gtk.ScrolledWindow()
        scroll.set_policy(
            Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC
        )
        scroll.add(self.history_view)
        history_box.pack_start(scroll, True, True, 0)

        history_buttons = Gtk.Box(spacing=8)
        for label, callback in [
            ("Replay", self.replay_history),
            ("Add to Queue", self.queue_history),
            ("Copy URL", self.copy_history),
            ("Delete", self.delete_history),
            ("Refresh", self.refresh_history)
        ]:
            button = Gtk.Button(label=label)
            button.connect("clicked", callback)
            history_buttons.pack_start(button, True, True, 0)

        history_box.pack_start(history_buttons, False, False, 0)
        notebook.append_page(history_box, Gtk.Label(label="History"))
        self.refresh_history()

        self.window.add(notebook)
        self.window.show_all()

        GLib.timeout_add(500, self.check_player)
        GLib.timeout_add_seconds(2, self.update_playback_status)

    def check_player(self):
        result = self.command("get_property", "mpv-version")
        if result.get("error") == "success":
            if self.status.get_text() == "Player starting...":
                self.status.set_text("Player ready")
            return False

        if self.player and self.player.poll() is not None:
            self.status.set_text("mpv failed to start")
            return False

        return True

    def do_shutdown(self):
        if self.player and self.player.poll() is None:
            self.player.terminate()
        Gtk.Application.do_shutdown(self)

MediaPlayer().run()
