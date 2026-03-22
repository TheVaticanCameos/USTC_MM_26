# Copyright 2026, Yumeng Liu @ USTC
"""
地铁路径规划 —— 交互式 GUI 模块

基于 Tkinter + Matplotlib，提供：
  - 城市选择 → 绘制全网络
  - 起终站下拉选择 → 即时高亮
  - 求解按钮 → Dijkstra 最短路径高亮 + 文本输出
"""


import tkinter as tk
from pathlib import Path
from tkinter import ttk

import matplotlib
import numpy as np
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.collections import LineCollection
from matplotlib.figure import Figure

from metro_algorithm import Graph, MetroSystem, detect_cities

matplotlib.use("TkAgg")


# ============================================================
# 布局算法（Fruchterman-Reingold 弹簧模型）
# ============================================================

def spring_layout(graph: Graph, seed: int = 42, iterations: int = 80) -> dict[int, tuple[float, float]]:
    """
    计算图的 Fruchterman-Reingold 弹簧布局。

    返回 {node_id: (x, y)} 坐标字典，坐标归一化到 [0.05, 0.95]。
    """
    node_ids = list(graph.nodes.keys())
    n = len(node_ids)
    if n == 0:
        return {}

    rng = np.random.RandomState(seed)
    pos = rng.rand(n, 2)
    idx = {nid: i for i, nid in enumerate(node_ids)}

    k = 1.0 / np.sqrt(n)
    temp = 1.0
    edge_list = graph.edges()

    for _ in range(iterations):
        disp = np.zeros((n, 2))

        # 斥力：所有节点对
        for i in range(n):
            diff = pos[i] - pos
            dist = np.sqrt((diff ** 2).sum(axis=1))
            dist = np.clip(dist, 0.001, None)
            force = k * k / dist
            force[i] = 0.0
            disp[i] += (diff * force[:, np.newaxis]).sum(axis=0)

        # 引力：沿边
        for u, v, _w in edge_list:
            i, j = idx[u], idx[v]
            diff = pos[i] - pos[j]
            dist = max(np.sqrt((diff ** 2).sum()), 0.001)
            f = dist / k
            disp[i] -= diff * f / dist
            disp[j] += diff * f / dist

        # 更新
        mag = np.sqrt((disp ** 2).sum(axis=1))
        mag = np.clip(mag, 0.001, None)
        pos += disp * np.minimum(temp, mag)[:, np.newaxis] / mag[:, np.newaxis]
        temp *= 0.95

    # 归一化到 [0.05, 0.95]
    lo = pos.min(axis=0)
    hi = pos.max(axis=0)
    span = hi - lo
    span = np.where(span < 1e-6, 1.0, span)
    pos = (pos - lo) / span * 0.9 + 0.05

    return {nid: (pos[i, 0], pos[i, 1]) for i, nid in enumerate(node_ids)}


# ============================================================
# GUI 主类
# ============================================================

class MetroApp:
    """基于 Tkinter 的交互式地铁路径规划界面。"""

    BG_COLOR = "#f5f5f5"
    PANEL_COLOR = "#ffffff"
    EDGE_COLOR = "#bdbdbd"
    NODE_COLOR = "#90caf9"
    NODE_EDGE_COLOR = "#1565c0"
    SRC_COLOR = "#2e7d32"
    DST_COLOR = "#e65100"
    PATH_EDGE_COLOR = "#e53935"
    PATH_NODE_COLOR = "#ffcdd2"
    PATH_NODE_EDGE = "#b71c1c"
    SIDEBAR_WIDTH = 320

    def __init__(self, data_root: str | Path):
        self.data_root = Path(data_root)
        self.cities = detect_cities(self.data_root)

        self.metro: MetroSystem | None = None
        self.pos: dict[int, tuple[float, float]] = {}

        # 视图交互状态
        self._dragging = False
        self._drag_start_pixels: tuple[float, float] | None = None
        self._drag_start_view: dict[str, tuple[float, float]] | None = None
        self._view_initialized = False
        self._base_view_span: tuple[float, float] | None = None
        self._status_var = None

        self._build_ui()

    # ================================================================
    # UI 构建
    # ================================================================

    def _configure_styles(self):
        style = ttk.Style()
        try:
            style.theme_use("clam")
        except tk.TclError:
            pass

        style.configure("App.TFrame", background=self.BG_COLOR)
        style.configure("Card.TFrame", background=self.PANEL_COLOR)
        style.configure("TLabel", background=self.BG_COLOR, font=("Segoe UI", 10))
        style.configure("TButton", font=("Segoe UI", 10), padding=(8, 5))
        style.configure("TCombobox", padding=4)
        style.configure("TLabelframe", background=self.BG_COLOR)
        style.configure("TLabelframe.Label", background=self.BG_COLOR, font=("Segoe UI", 10, "bold"))

    def _build_ui(self):
        self.root = tk.Tk()
        self._status_var = tk.StringVar(master=self.root, value="Ready")
        self.root.title("Metro Shortest Path Finder")
        self.root.configure(bg=self.BG_COLOR)
        self.root.geometry("1400x850")

        self._configure_styles()

        self.root.columnconfigure(0, weight=1)
        self.root.columnconfigure(1, weight=0, minsize=self.SIDEBAR_WIDTH)
        self.root.rowconfigure(0, weight=1)

        canvas_frame = ttk.Frame(self.root, style="App.TFrame")
        canvas_frame.grid(row=0, column=0, sticky="nsew", padx=(5, 0), pady=5)
        canvas_frame.columnconfigure(0, weight=1)
        canvas_frame.rowconfigure(1, weight=1)

        toolbar_frame = ttk.Frame(canvas_frame, style="App.TFrame")
        toolbar_frame.grid(row=0, column=0, sticky="ew", pady=(0, 6))

        plot_frame = ttk.Frame(canvas_frame, style="Card.TFrame")
        plot_frame.grid(row=1, column=0, sticky="nsew")
        plot_frame.columnconfigure(0, weight=1)
        plot_frame.rowconfigure(0, weight=1)

        status_frame = ttk.Frame(canvas_frame, style="App.TFrame")
        status_frame.grid(row=2, column=0, sticky="ew", pady=(6, 0))

        self.fig = Figure(figsize=(10, 7), dpi=100, facecolor=self.BG_COLOR)
        self.ax = self.fig.add_subplot(111)
        self.canvas = FigureCanvasTkAgg(self.fig, master=plot_frame)
        self.canvas.get_tk_widget().grid(row=0, column=0, sticky="nsew")

        self._build_plot_toolbar(toolbar_frame)
        ttk.Label(status_frame, textvariable=self._status_var, anchor="w").pack(fill=tk.X)

        sidebar = ttk.Frame(self.root, width=self.SIDEBAR_WIDTH, style="App.TFrame")
        sidebar.grid(row=0, column=1, sticky="nsew", padx=(0, 5), pady=5)
        sidebar.grid_propagate(False)
        self._build_sidebar(sidebar)

        self._bind_canvas_events()

    def _build_plot_toolbar(self, parent: ttk.Frame):
        ttk.Button(parent, text="Zoom In", command=lambda: self._zoom(0.85)).pack(side=tk.LEFT, padx=(0, 6))
        ttk.Button(parent, text="Zoom Out", command=lambda: self._zoom(1.18)).pack(side=tk.LEFT, padx=(0, 6))
        ttk.Button(parent, text="Fit View", command=self._fit_view).pack(side=tk.LEFT, padx=(0, 6))

    def _build_sidebar(self, sidebar: ttk.Frame):
        px, py = 10, 6

        sec = ttk.LabelFrame(sidebar, text="City", padding=8)
        sec.pack(fill=tk.X, padx=px, pady=py)
        self.city_var = tk.StringVar()
        cb = ttk.Combobox(sec, textvariable=self.city_var,
                          values=self.cities, state="readonly")
        cb.pack(fill=tk.X)
        cb.bind("<<ComboboxSelected>>", self._on_city_selected)

        sec = ttk.LabelFrame(sidebar, text="Station Selection", padding=8)
        sec.pack(fill=tk.X, padx=px, pady=py)

        ttk.Label(sec, text="From:").pack(anchor=tk.W)
        self.src_var = tk.StringVar()
        self.src_cb = ttk.Combobox(sec, textvariable=self.src_var, state="readonly")
        self.src_cb.pack(fill=tk.X, pady=(0, 8))
        self.src_cb.bind("<<ComboboxSelected>>", self._on_station_selected)

        ttk.Label(sec, text="To:").pack(anchor=tk.W)
        self.dst_var = tk.StringVar()
        self.dst_cb = ttk.Combobox(sec, textvariable=self.dst_var, state="readonly")
        self.dst_cb.pack(fill=tk.X, pady=(0, 8))
        self.dst_cb.bind("<<ComboboxSelected>>", self._on_station_selected)

        btn_frame = ttk.Frame(sec)
        btn_frame.pack(fill=tk.X, pady=(4, 0))
        ttk.Button(btn_frame, text="Find Shortest Path",
                   command=self._on_solve).pack(side=tk.LEFT, expand=True, fill=tk.X, padx=(0, 4))
        ttk.Button(btn_frame, text="Reset",
                   command=self._on_reset).pack(side=tk.LEFT, expand=True, fill=tk.X, padx=(4, 0))

        out = ttk.LabelFrame(sidebar, text="Route Output", padding=8)
        out.pack(fill=tk.BOTH, expand=True, padx=px, pady=py)
        self.output_text = tk.Text(out, wrap=tk.WORD, font=("Consolas", 11),
                                   bg="#fafafa", relief=tk.FLAT, padx=8, pady=6)
        scrollbar = ttk.Scrollbar(out, command=self.output_text.yview)
        self.output_text.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.output_text.pack(fill=tk.BOTH, expand=True)

    # ================================================================
    # 视图交互
    # ================================================================

    def _bind_canvas_events(self):
        self.canvas.mpl_connect("scroll_event", self._on_scroll)
        self.canvas.mpl_connect("button_press_event", self._on_mouse_press)
        self.canvas.mpl_connect("button_release_event", self._on_mouse_release)
        self.canvas.mpl_connect("motion_notify_event", self._on_mouse_move)

    def _on_scroll(self, event):
        if event.inaxes != self.ax:
            return
        scale = 0.9 if event.button == "up" else 1.1
        self._zoom(scale, center=(event.xdata, event.ydata))

    def _on_mouse_press(self, event):
        if event.inaxes != self.ax or event.button != 1:
            return
        if event.x is None or event.y is None:
            return
        self._dragging = True
        self._drag_start_pixels = (event.x, event.y)
        self._drag_start_view = self._get_view_state()

    def _on_mouse_release(self, _event):
        self._dragging = False
        self._drag_start_pixels = None
        self._drag_start_view = None

    def _on_mouse_move(self, event):
        if not self._dragging:
            return
        if event.x is None or event.y is None:
            return
        if self._drag_start_pixels is None or self._drag_start_view is None:
            return

        start_x, start_y = self._drag_start_pixels
        dx_pix = event.x - start_x
        dy_pix = event.y - start_y

        x0, x1 = self._drag_start_view["xlim"]
        y0, y1 = self._drag_start_view["ylim"]
        bbox = self.ax.bbox
        if bbox.width <= 1 or bbox.height <= 1:
            return

        dx_data = dx_pix * (x1 - x0) / bbox.width
        dy_data = dy_pix * (y1 - y0) / bbox.height

        self.ax.set_xlim(x0 - dx_data, x1 - dx_data)
        self.ax.set_ylim(y0 - dy_data, y1 - dy_data)
        self._apply_dynamic_text_scale()
        self.canvas.draw_idle()

    def _zoom(self, scale_factor: float, center=None):
        if not self.pos:
            return

        x0, x1 = self.ax.get_xlim()
        y0, y1 = self.ax.get_ylim()
        width = x1 - x0
        height = y1 - y0
        if abs(width) < 1e-12 or abs(height) < 1e-12:
            return

        if center is None:
            cx = (x0 + x1) / 2
            cy = (y0 + y1) / 2
            relx = 0.5
            rely = 0.5
        else:
            cx, cy = center
            if cx is None or cy is None:
                return
            relx = (cx - x0) / width
            rely = (cy - y0) / height

        new_width = width * scale_factor
        new_height = height * scale_factor

        self.ax.set_xlim(cx - relx * new_width, cx + (1 - relx) * new_width)
        self.ax.set_ylim(cy - rely * new_height, cy + (1 - rely) * new_height)
        self._apply_dynamic_text_scale()
        self.canvas.draw_idle()

    def _fit_view(self):
        if not self.pos:
            return

        xs = [p[0] for p in self.pos.values()]
        ys = [p[1] for p in self.pos.values()]
        pad_x = max((max(xs) - min(xs)) * 0.08, 0.03)
        pad_y = max((max(ys) - min(ys)) * 0.08, 0.03)

        xlim = (min(xs) - pad_x, max(xs) + pad_x)
        ylim = (min(ys) - pad_y, max(ys) + pad_y)
        self.ax.set_xlim(*xlim)
        self.ax.set_ylim(*ylim)
        self._base_view_span = (xlim[1] - xlim[0], ylim[1] - ylim[0])
        self._apply_dynamic_text_scale()
        self.canvas.draw_idle()

    def _get_view_state(self):
        return {"xlim": self.ax.get_xlim(), "ylim": self.ax.get_ylim()}

    def _set_view_state(self, state):
        if not state:
            return
        self.ax.set_xlim(*state["xlim"])
        self.ax.set_ylim(*state["ylim"])


    def _current_zoom_factor(self) -> float:
        if self._base_view_span is None:
            return 1.0
        base_w, base_h = self._base_view_span
        cur_x0, cur_x1 = self.ax.get_xlim()
        cur_y0, cur_y1 = self.ax.get_ylim()
        cur_w = max(abs(cur_x1 - cur_x0), 1e-12)
        cur_h = max(abs(cur_y1 - cur_y0), 1e-12)
        zx = base_w / cur_w
        zy = base_h / cur_h
        return max(zx, zy)

    @staticmethod
    def _clamp(value: float, lo: float, hi: float) -> float:
        return max(lo, min(hi, value))

    def _apply_dynamic_text_scale(self):
        zoom = self._current_zoom_factor()
        factor = zoom ** 0.45

        station_size = self._clamp(5.5 * factor, 4.0, 12.0)
        endpoint_size = self._clamp(7.5 * factor, 5.0, 13.0)

        for text in self.ax.texts:
            gid = text.get_gid()
            if gid == "station_label":
                text.set_fontsize(station_size)
            elif gid == "endpoint_label":
                text.set_fontsize(endpoint_size)

    # ================================================================
    # 事件处理
    # ================================================================

    def _on_city_selected(self, _event=None):
        city = self.city_var.get()
        self.metro = MetroSystem(self.data_root / city)

        names = self.metro.sorted_station_names()
        self.src_cb["values"] = names
        self.dst_cb["values"] = names
        self.src_var.set("")
        self.dst_var.set("")

        n_nodes = self.metro.graph.number_of_nodes()
        if n_nodes > 0:
            self.pos = spring_layout(self.metro.graph)
            self._view_initialized = False
        else:
            self.pos = {}
            self._view_initialized = False

        self._draw_base()
        self._status_var.set(f"Loaded {city}")
        self._log("Loaded {}: {} stations, {} edges".format(
            city, len(self.metro.stations), self.metro.graph.number_of_edges()))
        if n_nodes == 0:
            self._log("  [Note] Graph is empty — build_graph() not yet implemented?")

    def _on_station_selected(self, _event=None):
        if self.metro is None:
            return
        self._draw_base()
        self._highlight_endpoints()
        self.canvas.draw_idle()

    def _on_solve(self):
        if self.metro is None:
            return
        src_name = self.src_var.get()
        dst_name = self.dst_var.get()
        if not src_name or not dst_name:
            self._status_var.set("Please select both source and destination")
            self._log("Please select both a source and a destination station.")
            return
        if src_name == dst_name:
            self._status_var.set("Source and destination are the same")
            self._log("Source and destination are the same station.")
            return

        cost, path = self.metro.shortest_path(src_name, dst_name)
        if not path:
            self._status_var.set("No path found")
            self._log("No path found from {} to {}.".format(src_name, dst_name))
            if self.metro.graph.number_of_nodes() == 0:
                self._log("  [Hint] build_graph() or dijkstra() not yet implemented?")
            return

        self._draw_base()
        self._draw_path(path, cost)
        self.canvas.draw_idle()

        names = [self.metro.stations[nid] for nid in path]
        self._status_var.set(f"Route found: {len(path)} stations, {cost:.3f} km")
        self._log(
            "{line}\n"
            "  {src}  ->  {dst}\n"
            "  Distance : {cost:.3f} km\n"
            "  Stops    : {stops}\n"
            "  Route    : {route}\n"
            "{line}".format(
                line="-" * 40, src=src_name, dst=dst_name,
                cost=cost, stops=len(path), route=" -> ".join(names),
            )
        )

    def _on_reset(self):
        self.src_var.set("")
        self.dst_var.set("")
        if self.metro is not None:
            self._draw_base()
            self.canvas.draw_idle()
        self.output_text.delete("1.0", tk.END)
        self._status_var.set("Reset")

    def _draw_base(self):
        """绘制底层地铁网络。"""
        view_state = self._get_view_state() if self._view_initialized else None

        self.ax.clear()
        self.ax.set_facecolor(self.BG_COLOR)

        if not self.pos:
            self.ax.set_title("{} Metro Network".format(
                self.metro.city if self.metro else ""),
                fontsize=7.0, fontweight="bold", pad=16)
            self.ax.axis("off")
            self.fig.subplots_adjust(left=0.02, right=0.98, bottom=0.03, top=0.88)
            self.canvas.draw_idle()
            return

        G = self.metro.graph

        # 边
        segments = []
        for u, v, _w in G.edges():
            if u in self.pos and v in self.pos:
                segments.append([self.pos[u], self.pos[v]])
        if segments:
            lc = LineCollection(segments, colors=self.EDGE_COLOR,
                                linewidths=0.8, alpha=0.6)
            self.ax.add_collection(lc)

        # 节点
        xs = [self.pos[nid][0] for nid in G.nodes if nid in self.pos]
        ys = [self.pos[nid][1] for nid in G.nodes if nid in self.pos]
        self.ax.scatter(xs, ys, s=25, c=self.NODE_COLOR,
                        edgecolors=self.NODE_EDGE_COLOR, linewidths=0.4, zorder=3)

        self.ax.set_title("{} Metro Network".format(self.metro.city),
                          fontsize=7.0, fontweight="bold", pad=16)
        self.ax.axis("off")

        if view_state is not None:
            self._set_view_state(view_state)
        else:
            self._fit_view()
            self._view_initialized = True

        self._apply_dynamic_text_scale()
        self.fig.subplots_adjust(left=0.02, right=0.98, bottom=0.03, top=0.88)
        self.canvas.draw_idle()

    def _annotate_station(self, nid, color, marker, label, size=180):
        if nid not in self.pos:
            return
        x, y = self.pos[nid]
        self.ax.scatter(x, y, s=size, c=color, marker=marker,
                        zorder=5, edgecolors="white", linewidths=2)
        ann = self.ax.annotate(
            "[{}] {}".format(label, self.metro.stations[nid]), (x, y),
            textcoords="offset points", xytext=(8, 8),
            fontsize=7.5, fontweight="bold", color=color,
            bbox=dict(boxstyle="round,pad=0.2", fc="white",
                      alpha=0.85, ec=color, lw=0.8),
        )
        ann.set_gid("endpoint_label")

    def _highlight_endpoints(self):
        for var, color, marker, label in [
            (self.src_var, self.SRC_COLOR, "o", "From"),
            (self.dst_var, self.DST_COLOR, "s", "To"),
        ]:
            name = var.get()
            if name:
                nid = self.metro.name_to_id.get(name)
                if nid is not None and nid in self.pos:
                    self._annotate_station(nid, color, marker, label)

    def _draw_path(self, path: list[int], cost: float):
        """在底层网络上绘制最短路径高亮。"""
        stations = self.metro.stations

        # 高亮边
        segments = []
        for i in range(len(path) - 1):
            u, v = path[i], path[i + 1]
            if u in self.pos and v in self.pos:
                segments.append([self.pos[u], self.pos[v]])
        if segments:
            lc = LineCollection(segments, colors=self.PATH_EDGE_COLOR,
                                linewidths=3.0, alpha=0.9, zorder=4)
            self.ax.add_collection(lc)

        # 高亮节点
        pxs = [self.pos[nid][0] for nid in path if nid in self.pos]
        pys = [self.pos[nid][1] for nid in path if nid in self.pos]
        self.ax.scatter(pxs, pys, s=70, c=self.PATH_NODE_COLOR,
                        edgecolors=self.PATH_NODE_EDGE, linewidths=1.5, zorder=4)

        # 路径站名标签
        for nid in path:
            if nid in self.pos:
                x, y = self.pos[nid]
                txt = self.ax.text(x, y, stations[nid], fontsize=5.5, fontweight="bold",
                                   color=self.PATH_NODE_EDGE, ha="center", va="bottom",
                                   transform=self.ax.transData)
                txt.set_gid("station_label")

        # 起终点标记
        self._annotate_station(path[0], self.SRC_COLOR, "o", "From", size=220)
        self._annotate_station(path[-1], self.DST_COLOR, "s", "To", size=220)

        self.ax.set_title(
            "{city} Metro Network\n"
            "Shortest Path: {src} -> {dst}\n(distance = {cost:.3f} km)".format(
                city=self.metro.city,
                src=stations[path[0]], dst=stations[path[-1]], cost=cost),
            fontsize=7.0, fontweight="bold", pad=18,
        )

    # ================================================================
    # 工具
    # ================================================================

    def _log(self, text):
        self.output_text.insert(tk.END, text + "\n")
        self.output_text.see(tk.END)

    def run(self):
        self.root.mainloop()
