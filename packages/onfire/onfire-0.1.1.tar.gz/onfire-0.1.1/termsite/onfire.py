from __future__ import annotations

import argparse
import os
import random
import time
from dataclasses import dataclass
from typing import List, Sequence, Tuple

# --- Optional cross-platform system + process stats (recommended) ---
try:
    import psutil  # type: ignore
except Exception:
    psutil = None  # type: ignore

# --- Curses import (Windows needs `pip install windows-curses`) ---
try:
    import curses
except Exception as e:
    raise SystemExit(
        "Failed to import curses.\n"
        "- Linux/macOS: curses is usually included.\n"
        "- Windows: install it with: python -m pip install windows-curses\n"
        "Also recommended for CPU/RAM sampling: python -m pip install psutil"
    ) from e

# Character sets
SHADE_CHARS: Tuple[str, ...] = (" ", "░", "▒", "▓", "█")
SOLID_CHARS: Tuple[str, ...] = (" ", "█")
ASCII_CHARS: Tuple[str, ...] = (" ", ".", ":", "*", "o", "O", "#", "@")

# Partial-width blocks (left fractions): smoother gradients in a single cell width.
# U+258F..U+2588 (plus space)
BLOCK_CHARS: Tuple[str, ...] = (" ", "▏", "▎", "▍", "▌", "▋", "▊", "▉", "█")

# A simple xterm-256 "heat" ramp (foreground colors).
XTERM_HEAT_RAMP: Tuple[int, ...] = (
    16,
    52,
    88,
    124,
    160,
    196,  # reds
    202,
    208,
    214,
    220,
    226,  # oranges/yellows
    230,
    231,  # near-white
)

# Base simulation steps per second when speed == 1.0.
BASE_STEPS_PER_SEC: float = 30.0

# Status line update frequency (seconds). Higher => less CPU.
STATUS_EVERY_S: float = 0.25


@dataclass
class Config:
    fps: int = 30  # render/update rate
    speed: float = 1.0  # steps/sec = BASE_STEPS_PER_SEC * speed
    charset: str = "blocks"  # blocks|shade|solid|ascii
    color: bool = True
    show_status: bool = True
    fuel: float = 0.65  # 0..1
    cooling_min: int = 0
    cooling_max: int = 3
    wind: int = 0  # -5..5
    seed: int | None = None
    special: str | None = None  # None|"cpu"|"ram"
    sample_every: float = 2.0  # seconds

    # CPU saver on huge terminals: simulate at lower resolution and upscale.
    # 1 = full quality (most CPU). 2 halves work in that dimension.
    scale_x: int = 1
    scale_y: int = 1


@dataclass
class _CpuSample:
    total: int | None = None
    idle: int | None = None


class _UsageSampler:
    """Cache CPU/RAM usage so we only sample every N seconds."""

    __slots__ = ("mode", "every_s", "_last_t", "_last_v", "_cpu_state")

    def __init__(self, mode: str, every_s: float):
        self.mode = mode
        self.every_s = max(0.05, float(every_s))
        self._last_t = 0.0
        self._last_v: float | None = None
        self._cpu_state = _CpuSample()

    def prime(self) -> None:
        # psutil cpu_percent(interval=None) needs a prior call to be meaningful.
        if self.mode != "cpu":
            return
        if psutil is not None:
            try:
                psutil.cpu_percent(interval=None)
            except Exception:
                pass
        else:
            _cpu_usage_pct_linux_proc(self._cpu_state)

    def get(self, now: float) -> float | None:
        v = self._last_v
        if v is not None and (now - self._last_t) < self.every_s:
            return v

        if self.mode == "cpu":
            v = _cpu_usage_pct_cross_platform(self._cpu_state)
        else:
            v = _ram_usage_pct_cross_platform()

        self._last_t = now
        self._last_v = v
        return v


class _SelfSampler:
    """Cache onfire's own CPU% and RSS, sampling at most every N seconds."""

    __slots__ = ("every_s", "_last_t", "_last_cpu", "_last_rss_mib", "_proc")

    def __init__(self, every_s: float):
        self.every_s = max(0.05, float(every_s))
        self._last_t = 0.0
        self._last_cpu: float | None = None
        self._last_rss_mib: float | None = None
        self._proc = None

        if psutil is not None:
            try:
                self._proc = psutil.Process(os.getpid())
                self._proc.cpu_percent(interval=None)  # prime
            except Exception:
                self._proc = None

    def get(self, now: float) -> tuple[float | None, float | None]:
        proc = self._proc
        if proc is None:
            return None, None

        cpu = self._last_cpu
        if cpu is not None and (now - self._last_t) < self.every_s:
            return cpu, self._last_rss_mib

        cpu_v: float | None
        rss_mib: float | None

        try:
            cpu_v = float(proc.cpu_percent(interval=None))
            if cpu_v < 0.0:
                cpu_v = 0.0
            elif cpu_v > 1000.0:
                cpu_v = 1000.0
        except Exception:
            cpu_v = None

        try:
            rss = int(proc.memory_info().rss)  # bytes
            rss_mib = rss / (1024.0 * 1024.0)
            if rss_mib < 0.0:
                rss_mib = 0.0
        except Exception:
            rss_mib = None

        self._last_t = now
        self._last_cpu = cpu_v
        self._last_rss_mib = rss_mib
        return cpu_v, rss_mib


class FireSim:
    """
    AAFire-ish terminal fire.

    CPU hot path optimizations:
    - cached zeros buffer for clearing (no allocations)
    - cached left/right neighbor indices (no branches per cell)
    - getrandbits() for drift/fuel (fewer Python calls than random()+randrange())
    - step_n() to keep local variables hot across multiple sim steps
    """

    __slots__ = (
        "w",
        "h",
        "cfg",
        "rng",
        "buf",
        "next",
        "_zeros",
        "_x_l",
        "_x_r",
        "_fuel_thr",
        "_cool_min",
        "_cool_span",
    )

    def __init__(self, w: int, h: int, cfg: Config):
        self.w = max(1, w)
        self.h = max(1, h)
        self.cfg = cfg
        self.rng = random.Random(cfg.seed)
        self.buf = bytearray(self.w * self.h)
        self.next = bytearray(self.w * self.h)
        self._zeros = bytes(self.w * self.h)
        self._x_l = [0] * self.w
        self._x_r = [0] * self.w
        self._rebuild_neighbors()

        self._fuel_thr = int(max(0.0, min(1.0, cfg.fuel)) * 255.0)
        self._cool_min = max(0, cfg.cooling_min)
        self._cool_span = max(1, max(0, cfg.cooling_max) - self._cool_min + 1)

    def _rebuild_neighbors(self) -> None:
        w = self.w
        xl = self._x_l
        xr = self._x_r
        for x in range(w):
            xl[x] = x - 1 if x else 0
            xr[x] = x + 1 if x + 1 < w else w - 1

    def resize(self, w: int, h: int) -> None:
        self.w = max(1, w)
        self.h = max(1, h)
        n = self.w * self.h
        self.buf = bytearray(n)
        self.next = bytearray(n)
        self._zeros = bytes(n)
        self._x_l = [0] * self.w
        self._x_r = [0] * self.w
        self._rebuild_neighbors()

    def _ignite_bottom(self) -> None:
        w = self.w
        row = (self.h - 1) * w
        buf = self.buf
        rng = self.rng
        thr = self._fuel_thr

        for x in range(w):
            if rng.getrandbits(8) < thr:
                buf[row + x] = 200 + (rng.getrandbits(6) % 56)  # 200..255
            else:
                buf[row + x] = 0

    def step_n(self, steps: int) -> None:
        if steps <= 0:
            return

        w = self.w
        h = self.h
        buf = self.buf
        nxt = self.next
        zeros = self._zeros
        xl = self._x_l
        xr = self._x_r
        rng = self.rng
        gb = rng.getrandbits

        # cfg.wind can change at runtime
        cfg = self.cfg
        cool_min = self._cool_min
        span = self._cool_span

        hw = h * w

        for _ in range(steps):
            self._ignite_bottom()
            nxt[:] = zeros
            wind = cfg.wind

            # Select a decay generator once per step (no function calls in inner loop).
            if span <= 1:
                # constant decay
                for y in range(h - 1):
                    yd = y * w
                    y1 = (y + 1) * w
                    y2 = (y + 2) * w
                    if y2 >= hw:
                        y2 = y1
                    for x in range(w):
                        avg = (
                            buf[y1 + x]
                            + buf[y1 + xl[x]]
                            + buf[y1 + xr[x]]
                            + buf[y2 + x]
                        ) >> 2
                        val = avg - cool_min
                        if val < 0:
                            val = 0
                        dst_x = x + wind - gb(1)
                        if dst_x < 0:
                            dst_x = 0
                        elif dst_x >= w:
                            dst_x = w - 1
                        nxt[yd + dst_x] = val

            elif span == 2:
                for y in range(h - 1):
                    yd = y * w
                    y1 = (y + 1) * w
                    y2 = (y + 2) * w
                    if y2 >= hw:
                        y2 = y1
                    for x in range(w):
                        avg = (
                            buf[y1 + x]
                            + buf[y1 + xl[x]]
                            + buf[y1 + xr[x]]
                            + buf[y2 + x]
                        ) >> 2
                        val = avg - (cool_min + gb(1))
                        if val < 0:
                            val = 0
                        dst_x = x + wind - gb(1)
                        if dst_x < 0:
                            dst_x = 0
                        elif dst_x >= w:
                            dst_x = w - 1
                        nxt[yd + dst_x] = val

            elif span <= 4:
                mod = span
                for y in range(h - 1):
                    yd = y * w
                    y1 = (y + 1) * w
                    y2 = (y + 2) * w
                    if y2 >= hw:
                        y2 = y1
                    for x in range(w):
                        avg = (
                            buf[y1 + x]
                            + buf[y1 + xl[x]]
                            + buf[y1 + xr[x]]
                            + buf[y2 + x]
                        ) >> 2
                        val = avg - (cool_min + (gb(2) % mod))
                        if val < 0:
                            val = 0
                        dst_x = x + wind - gb(1)
                        if dst_x < 0:
                            dst_x = 0
                        elif dst_x >= w:
                            dst_x = w - 1
                        nxt[yd + dst_x] = val

            elif span <= 8:
                mod = span
                for y in range(h - 1):
                    yd = y * w
                    y1 = (y + 1) * w
                    y2 = (y + 2) * w
                    if y2 >= hw:
                        y2 = y1
                    for x in range(w):
                        avg = (
                            buf[y1 + x]
                            + buf[y1 + xl[x]]
                            + buf[y1 + xr[x]]
                            + buf[y2 + x]
                        ) >> 2
                        val = avg - (cool_min + (gb(3) % mod))
                        if val < 0:
                            val = 0
                        dst_x = x + wind - gb(1)
                        if dst_x < 0:
                            dst_x = 0
                        elif dst_x >= w:
                            dst_x = w - 1
                        nxt[yd + dst_x] = val

            else:
                rr = rng.randrange
                mod = span
                for y in range(h - 1):
                    yd = y * w
                    y1 = (y + 1) * w
                    y2 = (y + 2) * w
                    if y2 >= hw:
                        y2 = y1
                    for x in range(w):
                        avg = (
                            buf[y1 + x]
                            + buf[y1 + xl[x]]
                            + buf[y1 + xr[x]]
                            + buf[y2 + x]
                        ) >> 2
                        val = avg - (cool_min + rr(mod))
                        if val < 0:
                            val = 0
                        dst_x = x + wind - gb(1)
                        if dst_x < 0:
                            dst_x = 0
                        elif dst_x >= w:
                            dst_x = w - 1
                        nxt[yd + dst_x] = val

            lo = (h - 1) * w
            nxt[lo : lo + w] = buf[lo : lo + w]
            buf, nxt = nxt, buf

        self.buf = buf
        self.next = nxt


def _pick_charset(name: str) -> Tuple[str, ...]:
    n = name.lower()
    if n == "blocks":
        return BLOCK_CHARS
    if n == "shade":
        return SHADE_CHARS
    if n == "solid":
        return SOLID_CHARS
    if n == "ascii":
        return ASCII_CHARS
    raise ValueError(f"unknown charset: {name}")


def _build_char_lut(chars: Sequence[str], scale_x: int) -> list[str]:
    """Map intensity 0..255 -> rendered string (character tiled scale_x times)."""
    if not chars:
        chars = (" ",)
    n = len(chars)
    tile = max(1, int(scale_x))

    if n == 2:
        lut = [""] * 256
        off = chars[0] * tile
        on = chars[1] * tile
        for i in range(256):
            lut[i] = on if i >= 80 else off
        return lut

    lut = [""] * 256
    max_i = n - 1
    for i in range(256):
        idx = (i * max_i) // 255
        lut[i] = chars[idx] * tile
    return lut


def _cpu_usage_pct_linux_proc(state: _CpuSample) -> float | None:
    try:
        with open("/proc/stat", "r", encoding="utf-8") as f:
            line = f.readline()
    except OSError:
        return None

    parts = line.split()
    if not parts or parts[0] != "cpu" or len(parts) < 5:
        return None

    try:
        values = [int(p) for p in parts[1:]]
    except ValueError:
        return None

    idle = values[3] + (values[4] if len(values) > 4 else 0)
    total = sum(values)

    if state.total is None:
        state.total = total
        state.idle = idle
        return None

    total_delta = total - state.total
    idle_delta = idle - (state.idle or 0)
    state.total = total
    state.idle = idle

    if total_delta <= 0:
        return None

    usage = 100.0 * (1.0 - idle_delta / total_delta)
    if usage < 0.0:
        return 0.0
    if usage > 100.0:
        return 100.0
    return usage


def _ram_usage_pct_linux_proc() -> float | None:
    try:
        with open("/proc/meminfo", "r", encoding="utf-8") as f:
            lines = f.readlines()
    except OSError:
        return None

    total = None
    avail = None
    for line in lines:
        if line.startswith("MemTotal:"):
            try:
                total = int(line.split()[1])
            except Exception:
                total = None
        elif line.startswith("MemAvailable:"):
            try:
                avail = int(line.split()[1])
            except Exception:
                avail = None
        if total is not None and avail is not None:
            break

    if not total or not avail or total <= 0:
        return None

    used = total - avail
    usage = 100.0 * (used / total)
    if usage < 0.0:
        return 0.0
    if usage > 100.0:
        return 100.0
    return usage


def _cpu_usage_pct_cross_platform(state: _CpuSample) -> float | None:
    if psutil is not None:
        try:
            v = float(psutil.cpu_percent(interval=None))
            if v < 0.0:
                return 0.0
            if v > 100.0:
                return 100.0
            return v
        except Exception:
            return None
    return _cpu_usage_pct_linux_proc(state)


def _ram_usage_pct_cross_platform() -> float | None:
    if psutil is not None:
        try:
            v = float(psutil.virtual_memory().percent)
            if v < 0.0:
                return 0.0
            if v > 100.0:
                return 100.0
            return v
        except Exception:
            return None
    return _ram_usage_pct_linux_proc()


def _setup_colors() -> Tuple[bool, List[int]]:
    try:
        if not curses.has_colors():
            return False, [0] * 256
        curses.start_color()
    except curses.error:
        return False, [0] * 256

    try:
        curses.use_default_colors()
        default_bg = -1
    except curses.error:
        default_bg = curses.COLOR_BLACK

    try:
        colors = curses.COLORS
    except Exception:
        colors = 0

    if colors >= 256:
        ramp = [c for c in XTERM_HEAT_RAMP if c < colors]
        if not ramp:
            ramp = [curses.COLOR_RED, curses.COLOR_YELLOW, curses.COLOR_WHITE]
    else:
        ramp = [
            curses.COLOR_BLACK,
            curses.COLOR_RED,
            curses.COLOR_YELLOW,
            curses.COLOR_WHITE,
        ]

    for i, fg in enumerate(ramp, start=1):
        try:
            curses.init_pair(i, fg, default_bg)
        except curses.error:
            return False, [0] * 256

    attrs = [0] * 256
    n = len(ramp)
    for inten in range(256):
        if inten < 10:
            attrs[inten] = 0
            continue
        idx = (inten * (n - 1)) // 255
        attrs[inten] = curses.color_pair(idx + 1)

    return True, attrs


def _usage_scalars(cfg: Config, usage_pct: float | None) -> Tuple[float, float]:
    """Return (steps_per_second, size_factor)."""
    base_sps = BASE_STEPS_PER_SEC * max(0.0, cfg.speed)
    if usage_pct is None:
        return base_sps, 1.0

    u = usage_pct / 100.0
    if u < 0.0:
        u = 0.0
    elif u > 1.0:
        u = 1.0

    return base_sps * (0.25 + 0.75 * u), 0.35 + 0.65 * u


def _clear_lines(stdscr, y0: int, y1: int, w: int) -> None:
    if y1 <= y0:
        return
    blank = " " * max(1, w - 1)
    for y in range(y0, y1):
        try:
            stdscr.addstr(y, 0, blank)
        except curses.error:
            pass


def _format_status(
    cfg: Config,
    *,
    color: bool,
    steps_per_second: float,
    self_cpu_pct: float | None,
    self_rss_mib: float | None,
    usage_pct: float | None,
) -> str:
    parts = [
        "onfire",
        "|",
        "q/Esc quit",
        f"s charset({cfg.charset})",
        f"c color({int(color)})",
        f"[ ] wind({cfg.wind})",
        f"fps({cfg.fps})",
        f"speed({cfg.speed:.2f})",
        f"sps({steps_per_second:6.1f})",
    ]

    if self_cpu_pct is None:
        parts.append("selfcpu:--%")
    else:
        parts.append(f"selfcpu:{self_cpu_pct:5.1f}%")

    if self_rss_mib is None:
        parts.append("selfram:--MiB")
    else:
        parts.append(f"selfram:{self_rss_mib:6.1f}MiB")

    if cfg.special:
        parts.append(f"sample({cfg.sample_every:.0f}s)")
        if usage_pct is None:
            parts.append(f"{cfg.special}:--%")
        else:
            parts.append(f"{cfg.special}:{usage_pct:5.1f}%")

    if cfg.scale_x != 1 or cfg.scale_y != 1:
        parts.append(f"scale({cfg.scale_x}x{cfg.scale_y})")

    if psutil is None:
        parts.append("(tip: pip install psutil)")

    return "  ".join(parts)


def _render(
    stdscr,
    sim: FireSim,
    attrs: Sequence[int],
    color: bool,
    size_factor: float,
    steps_per_second: float,
    usage_pct: float | None,
    self_cpu_pct: float | None,
    self_rss_mib: float | None,
    *,
    view_h: int,
    view_w: int,
    char_lut: Sequence[str],
    scale_x: int,
    scale_y: int,
    status_line: str,
    show_status: bool,
) -> None:
    flame_h = max(1, view_h - (1 if show_status else 0))

    target_h = int(flame_h * size_factor)
    if target_h < 1:
        target_h = 1
    elif target_h > flame_h:
        target_h = flame_h

    sx = max(1, scale_x)
    sy = max(1, scale_y)

    # ceil horizontally so we cover full width (avoid right-edge garbage)
    sim_w = max(1, (view_w + sx - 1) // sx)

    # floor vertically to avoid writing into status line (sy>1 edge case)
    sim_h = max(1, target_h // sy)

    if sim.w != sim_w or sim.h != sim_h:
        sim.resize(sim_w, sim_h)

    sw = sim.w
    scaled_h = sim.h * sy
    offset_y = flame_h - scaled_h
    if offset_y < 0:
        offset_y = 0

    mv = memoryview(sim.buf)

    if offset_y > 0:
        _clear_lines(stdscr, 0, offset_y, view_w)

    if not color:
        maxw = max(0, view_w - 1)
        for y in range(sim.h):
            row = mv[y * sw : (y + 1) * sw]
            row_str = "".join(map(char_lut.__getitem__, row))
            screen_y0 = offset_y + y * sy
            line = row_str[:maxw]
            for dy in range(sy):
                try:
                    stdscr.addstr(screen_y0 + dy, 0, line)
                except curses.error:
                    pass
    else:
        a = attrs
        maxw = max(0, view_w - 1)
        for y in range(sim.h):
            row = mv[y * sw : (y + 1) * sw]
            screen_y0 = offset_y + y * sy

            x = 0
            while x < sw:
                inten = row[x]
                attr = a[inten]

                start = x
                x += 1
                while x < sw and a[row[x]] == attr:
                    x += 1

                col = start * sx
                if col >= maxw:
                    continue

                seg = "".join(map(char_lut.__getitem__, row[start:x]))
                seg = seg[: maxw - col]

                for dy in range(sy):
                    try:
                        stdscr.addstr(screen_y0 + dy, col, seg, attr)
                    except curses.error:
                        pass

        bottom = offset_y + scaled_h
        if bottom < flame_h:
            _clear_lines(stdscr, bottom, flame_h, view_w)

    # Status line
    if show_status:
        try:
            stdscr.addstr(view_h - 1, 0, status_line[: max(0, view_w - 1)])
        except curses.error:
            pass


def _cycle_charset(current: str) -> str:
    order = ["blocks", "shade", "solid", "ascii"]
    try:
        i = order.index(current)
    except ValueError:
        return "blocks"
    return order[(i + 1) % len(order)]


def _run(stdscr, cfg: Config) -> None:
    try:
        curses.set_escdelay(25)
    except Exception:
        pass

    try:
        curses.curs_set(0)
    except curses.error:
        pass

    stdscr.nodelay(True)
    stdscr.keypad(True)

    color_enabled, attrs = _setup_colors()
    color = cfg.color and color_enabled

    chars = _pick_charset(cfg.charset)
    char_lut = _build_char_lut(chars, cfg.scale_x)

    sampler: _UsageSampler | None = None
    if cfg.special in ("cpu", "ram"):
        sampler = _UsageSampler(cfg.special, cfg.sample_every)
        sampler.prime()

    self_sampler = _SelfSampler(cfg.sample_every)

    term_h, term_w = stdscr.getmaxyx()
    sim = FireSim(
        max(1, (term_w + cfg.scale_x - 1) // max(1, cfg.scale_x)),
        max(1, (term_h - 1) // max(1, cfg.scale_y)),
        cfg,
    )

    frame_dt = 1.0 / max(1, cfg.fps)
    last_tick = time.monotonic()
    sim_accum = 0.0

    status_cache_t = 0.0
    status_line = ""

    while True:
        frame_start = time.monotonic()
        dt = frame_start - last_tick
        last_tick = frame_start
        if dt < 0.0:
            dt = 0.0
        elif dt > 0.25:
            dt = 0.25

        # Drain input queue
        while True:
            try:
                key = stdscr.getch()
            except curses.error:
                key = -1

            if key == -1:
                break

            if key in (27, ord("q")):
                return
            if key == ord("s"):
                cfg.charset = _cycle_charset(cfg.charset)
                chars = _pick_charset(cfg.charset)
                char_lut = _build_char_lut(chars, cfg.scale_x)
            elif key == ord("c"):
                color = (not color) and color_enabled
            elif key == ord("["):
                cfg.wind = max(-5, cfg.wind - 1)
            elif key == ord("]"):
                cfg.wind = min(5, cfg.wind + 1)
            elif key == curses.KEY_RESIZE:
                pass

        view_h, view_w = stdscr.getmaxyx()

        usage_pct: float | None = None
        if sampler is not None:
            usage_pct = sampler.get(frame_start)

        self_cpu_pct, self_rss_mib = self_sampler.get(frame_start)

        steps_per_second, size_factor = _usage_scalars(cfg, usage_pct)

        sim_accum += dt * max(0.0, steps_per_second)
        steps = int(sim_accum)
        sim_accum -= steps

        if steps > 400:
            steps = 400
            sim_accum = 0.0

        sim.step_n(steps)

        if cfg.show_status and (
            (frame_start - status_cache_t) >= STATUS_EVERY_S or not status_line
        ):
            status_cache_t = frame_start
            status_line = _format_status(
                cfg,
                color=color,
                steps_per_second=steps_per_second,
                self_cpu_pct=self_cpu_pct,
                self_rss_mib=self_rss_mib,
                usage_pct=usage_pct,
            )
        elif not cfg.show_status:
            status_line = ""

        _render(
            stdscr,
            sim,
            attrs,
            color,
            size_factor,
            steps_per_second,
            usage_pct,
            self_cpu_pct,
            self_rss_mib,
            view_h=view_h,
            view_w=view_w,
            char_lut=char_lut,
            scale_x=cfg.scale_x,
            scale_y=cfg.scale_y,
            status_line=status_line,
            show_status=cfg.show_status,
        )

        # refresh() is the standard full-screen update in curses
        stdscr.refresh()

        elapsed = time.monotonic() - frame_start
        if elapsed < frame_dt:
            time.sleep(frame_dt - elapsed)


def cli(argv: list[str] | None = None) -> None:
    p = argparse.ArgumentParser(
        prog="onfire", description="AAFire-style terminal flames (Python + curses)."
    )
    p.add_argument("--fps", type=int, default=30, help="Render/update rate in FPS.")
    p.add_argument(
        "--speed",
        type=float,
        default=1.0,
        help=f"Flame movement rate multiplier. steps/sec = {BASE_STEPS_PER_SEC:g} * speed.",
    )
    p.add_argument("--no-color", action="store_true", help="Disable color output.")
    p.add_argument("--no-statusbar", action="store_true", help="Hide the status bar.")
    p.add_argument(
        "--charset",
        choices=["blocks", "shade", "solid", "ascii"],
        default="blocks",
        help="Character set: blocks uses ▏▎▍▌▋▊▉█ (default).",
    )
    p.add_argument("--fuel", type=float, default=0.65, help="0..1 heat source density.")
    p.add_argument("--cool-min", type=int, default=0, help="Minimum cooling per step.")
    p.add_argument("--cool-max", type=int, default=3, help="Maximum cooling per step.")
    p.add_argument("--wind", type=int, default=0, help="Wind drift (-5..5).")
    p.add_argument(
        "--seed", type=int, default=None, help="RNG seed for repeatable fire."
    )
    p.add_argument(
        "--special",
        choices=["cpu", "ram"],
        help="Scale flame height + movement rate based on CPU or RAM usage percent.",
    )
    p.add_argument(
        "--sample-every",
        type=float,
        default=2.0,
        help="Sample CPU/RAM/self at most every N seconds (default: 2.0).",
    )
    p.add_argument(
        "--scale-x",
        type=int,
        default=1,
        help="Sim resolution divider horizontally (1=full quality, 2=~half CPU).",
    )
    p.add_argument(
        "--scale-y",
        type=int,
        default=1,
        help="Sim resolution divider vertically (1=full quality, 2=~half CPU).",
    )

    args = p.parse_args(argv)

    cfg = Config(
        fps=max(1, args.fps),
        speed=max(0.0, args.speed),
        charset=args.charset,
        color=not args.no_color,
        show_status=not args.no_statusbar,
        fuel=min(1.0, max(0.0, args.fuel)),
        cooling_min=max(0, args.cool_min),
        cooling_max=max(0, args.cool_max),
        wind=max(-5, min(5, args.wind)),
        seed=args.seed,
        special=args.special,
        sample_every=max(0.05, float(args.sample_every)),
        scale_x=max(1, int(args.scale_x)),
        scale_y=max(1, int(args.scale_y)),
    )
    if cfg.cooling_max < cfg.cooling_min:
        cfg.cooling_max = cfg.cooling_min

    curses.wrapper(_run, cfg)


if __name__ == "__main__":
    cli()
