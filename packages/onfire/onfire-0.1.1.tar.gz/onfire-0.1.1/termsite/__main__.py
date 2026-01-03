from __future__ import annotations

import argparse
import curses
import locale
import random
import time
from dataclasses import dataclass
from typing import List, Sequence, Tuple

# Make Unicode blocks behave in curses.
locale.setlocale(locale.LC_ALL, "")

# Character sets
SHADE_CHARS: Tuple[str, ...] = (" ", "░", "▒", "▓", "█")
SOLID_CHARS: Tuple[str, ...] = (" ", "█")
ASCII_CHARS: Tuple[str, ...] = (" ", ".", ":", "*", "o", "O", "#", "@")

_XTERM_LEVELS = (0, 95, 135, 175, 215, 255)


def _clamp(x: int, lo: int, hi: int) -> int:
    return lo if x < lo else hi if x > hi else x


def _rgb_to_xterm_256(r: int, g: int, b: int) -> int:
    """Approximate RGB -> xterm-256 index (0..255)."""
    r = _clamp(r, 0, 255)
    g = _clamp(g, 0, 255)
    b = _clamp(b, 0, 255)

    # Grayscale ramp (232..255) is often smoother for near-equal RGB.
    if abs(r - g) < 8 and abs(g - b) < 8:
        v = (r + g + b) // 3
        if v < 8:
            return 16
        if v > 238:
            return 231
        return 232 + ((v - 8) // 10)

    def nearest_level(v: int) -> int:
        best_i = 0
        best_d = 10**9
        for i, lv in enumerate(_XTERM_LEVELS):
            d = abs(lv - v)
            if d < best_d:
                best_d = d
                best_i = i
        return best_i

    ri = nearest_level(r)
    gi = nearest_level(g)
    bi = nearest_level(b)
    return 16 + 36 * ri + 6 * gi + bi


def _make_fire_ramp(steps: int = 64) -> List[int]:
    """
    Build a smooth fire gradient as xterm-256 color indices.
    Interpolates across a few hand-picked RGB stops, then quantizes to xterm.
    """
    stops = [
        (0, 0, 0),  # black
        (40, 0, 0),  # very dark red
        (140, 0, 0),  # red
        (255, 60, 0),  # orange-red
        (255, 160, 0),  # orange
        (255, 230, 80),  # yellow-ish
        (255, 255, 255),  # white
    ]

    if steps < 8:
        steps = 8

    segs = len(stops) - 1
    out: List[int] = []
    for i in range(steps):
        t = i / (steps - 1)
        s = min(segs - 1, int(t * segs))
        local_t = (t * segs) - s
        r0, g0, b0 = stops[s]
        r1, g1, b1 = stops[s + 1]
        r = int(r0 + (r1 - r0) * local_t)
        g = int(g0 + (g1 - g0) * local_t)
        b = int(b0 + (b1 - b0) * local_t)
        out.append(_rgb_to_xterm_256(r, g, b))

    # De-duplicate adjacent repeats (xterm quantization can cause duplicates).
    dedup: List[int] = [out[0]]
    for c in out[1:]:
        if c != dedup[-1]:
            dedup.append(c)
    return dedup


@dataclass
class Config:
    fps: int = 30
    speed: float = 1.0  # simulation steps per frame (fractional allowed)
    charset: str = "shade"  # shade|solid|ascii
    color: bool = True
    fuel: float = 0.65  # 0..1, heat source density
    cooling_min: int = 0
    cooling_max: int = 3
    wind: int = 0  # negative=left, positive=right
    sparks: int = 2  # number of embers injected per step
    blur: int = 1  # 0=off, 1=light
    gamma: float = 0.85  # mapping curve for chars/colors
    seed: int | None = None


class FireSim:
    """
    AAFire-ish terminal fire, tuned for smooth motion at low speed.

    Main differences vs your original:
    - Heat source has inertia (less flicker).
    - Supports partial updates (alpha blending) so speed<1 still animates.
    - Optional sparks and light blur for more “alive” flames.
    """

    def __init__(self, w: int, h: int, cfg: Config):
        self.cfg = cfg
        self.rng = random.Random(cfg.seed)
        self.resize(w, h)

    def resize(self, w: int, h: int) -> None:
        self.w = max(1, w)
        self.h = max(1, h)
        self.buf = bytearray(self.w * self.h)
        self.next = bytearray(self.w * self.h)
        self._source = bytearray(self.w)  # smoothed heat source per column

    def _ignite(self, alpha: float) -> None:
        """
        Smoothed heat source: columns drift toward either 0 or "hot",
        with update rate scaled by alpha (so low speed remains stable).
        """
        w = self.w
        # How quickly the source chases its target.
        # Low alpha => gentler changes => smooth at low speeds.
        k = 0.05 + 0.22 * alpha  # 0.05..0.27
        hot_lo, hot_hi = 210, 255

        for x in range(w):
            target = 0
            if self.rng.random() < self.cfg.fuel:
                target = self.rng.randint(hot_lo, hot_hi)

            cur = self._source[x]
            # Exponential smoothing: cur += k*(target-cur)
            cur_f = cur + int((target - cur) * k)
            self._source[x] = _clamp(cur_f, 0, 255)

        y = self.h - 1
        row = y * w
        self.buf[row : row + w] = self._source

    def _add_sparks(self) -> None:
        if self.cfg.sparks <= 0 or self.h < 4:
            return
        w = self.w
        # Inject embers just above the source line
        for _ in range(self.cfg.sparks):
            x = self.rng.randrange(0, w)
            y = self.h - 2 - self.rng.randrange(0, 3)  # h-2..h-4
            i = y * w + x
            self.buf[i] = 255

    def step(self, alpha: float = 1.0) -> None:
        """
        alpha in (0..1]:
        - alpha=1 => full step
        - alpha<1 => blend toward next state for smooth slow motion
        """
        if alpha <= 0.0:
            return
        if alpha > 1.0:
            alpha = 1.0

        w, h = self.w, self.h
        self._ignite(alpha)
        self._add_sparks()

        # Compute next (raw)
        self.next[:] = b"\x00" * (w * h)

        # Propagate upward
        for y in range(h - 1):
            yd = y * w
            y1 = (y + 1) * w
            y2 = (y + 2) * w if (y + 2) < h else y1

            for x in range(w):
                xm1 = x - 1 if x > 0 else 0
                xp1 = x + 1 if x + 1 < w else w - 1

                # More samples = smoother flame body.
                b0 = self.buf[y1 + x]
                b1 = self.buf[y1 + xm1]
                b2 = self.buf[y1 + xp1]
                b3 = self.buf[y2 + x]
                b4 = self.buf[y2 + xm1]
                b5 = self.buf[y2 + xp1]
                avg = (b0 + b1 + b2 + b3 + b4 + b5) // 6

                decay = self.rng.randrange(
                    self.cfg.cooling_min, self.cfg.cooling_max + 1
                )
                val = avg - decay
                if val < 0:
                    val = 0

                # Drift with less bias than the classic "always left" look
                drift = self.rng.choice((-1, 0, 0, 1))  # weighted toward 0
                dst_x = x + self.cfg.wind + drift
                if dst_x < 0:
                    dst_x = 0
                elif dst_x >= w:
                    dst_x = w - 1

                self.next[yd + dst_x] = val

        # Keep bottom row from current heat source.
        self.next[(h - 1) * w : h * w] = self.buf[(h - 1) * w : h * w]

        # Light horizontal blur to reduce jaggies (optional).
        if self.cfg.blur > 0 and w >= 3:
            for y in range(h - 1):
                base = y * w
                left = self.next[base]
                mid = self.next[base + 1]
                for x in range(1, w - 1):
                    right = self.next[base + x + 1]
                    # 2*mid + left + right / 4  (keeps detail but smooths)
                    self.next[base + x] = (mid * 2 + left + right) >> 2
                    left, mid = mid, right

        # Blend toward next for smooth slow motion.
        if alpha >= 0.999:
            self.buf, self.next = self.next, self.buf
        else:
            a = int(alpha * 256)
            inv = 256 - a
            for i in range(w * h):
                self.buf[i] = (self.buf[i] * inv + self.next[i] * a) >> 8


def _pick_charset(name: str) -> Tuple[str, ...]:
    name = name.lower()
    if name == "shade":
        return SHADE_CHARS
    if name == "solid":
        return SOLID_CHARS
    if name == "ascii":
        return ASCII_CHARS
    raise ValueError(f"unknown charset: {name}")


def _build_char_lut(chars: Sequence[str], gamma: float) -> List[str]:
    if not chars:
        return [" "] * 256
    n = len(chars)
    out = [" "] * 256
    g = gamma if gamma > 0 else 1.0

    for i in range(256):
        t = (i / 255) ** g
        idx = int(t * (n - 1) + 1e-9)
        if idx < 0:
            idx = 0
        elif idx >= n:
            idx = n - 1
        out[i] = chars[idx]
    return out


def _setup_colors(cfg: Config) -> Tuple[bool, List[int]]:
    """
    Returns (color_enabled, attr_by_intensity_0_255).
    Uses xterm-256 ramp when available, otherwise a small basic ramp.
    """
    if not curses.has_colors():
        return False, [0] * 256

    curses.start_color()

    try:
        curses.use_default_colors()
        default_bg = -1
    except curses.error:
        default_bg = curses.COLOR_BLACK

    colors = getattr(curses, "COLORS", 0) or 0
    pairs = getattr(curses, "COLOR_PAIRS", 0) or 0

    ramp: List[int]
    if colors >= 256 and pairs >= 32:
        ramp = _make_fire_ramp(steps=64)
        ramp = [c for c in ramp if c < colors]
        if not ramp:
            ramp = [curses.COLOR_RED, curses.COLOR_YELLOW, curses.COLOR_WHITE]
    else:
        ramp = [
            curses.COLOR_BLACK,
            curses.COLOR_RED,
            curses.COLOR_YELLOW,
            curses.COLOR_WHITE,
        ]

    # We need one pair per ramp entry. Cap to COLOR_PAIRS-1.
    max_pairs = (pairs - 1) if pairs > 0 else len(ramp)
    ramp = ramp[: max(1, min(len(ramp), max_pairs))]

    for i, fg in enumerate(ramp, start=1):
        try:
            curses.init_pair(i, fg, default_bg)
        except curses.error:
            return False, [0] * 256

    attrs = [0] * 256
    n = len(ramp)
    g = cfg.gamma if cfg.gamma > 0 else 1.0
    for inten in range(256):
        if inten < 8:
            attrs[inten] = 0
            continue

        t = (inten / 255) ** g
        idx = int(t * (n - 1) + 1e-9)
        if idx < 0:
            idx = 0
        elif idx >= n:
            idx = n - 1

        a = curses.color_pair(idx + 1)
        # Extra “pop” at the hottest parts, subtle dim at low heat.
        if inten > 210:
            a |= curses.A_BOLD
        elif inten < 40:
            a |= curses.A_DIM

        attrs[inten] = a

    return True, attrs


def _render(
    stdscr, sim: FireSim, char_lut: Sequence[str], attr_lut: Sequence[int], color: bool
) -> None:
    h, w = stdscr.getmaxyx()
    view_h = max(1, h - 1)
    view_w = max(1, w)

    if sim.w != view_w or sim.h != view_h:
        sim.resize(view_w, view_h)

    buf = sim.buf
    sw = sim.w

    # Draw by attribute runs for fewer addstr calls.
    for y in range(view_h):
        base = y * sw
        x = 0
        while x < view_w:
            inten = buf[base + x]
            attr = attr_lut[inten] if color else 0
            start = x

            pieces = [char_lut[inten]]
            x += 1
            while x < view_w:
                inten2 = buf[base + x]
                attr2 = attr_lut[inten2] if color else 0
                if attr2 != attr:
                    break
                pieces.append(char_lut[inten2])
                x += 1

            try:
                stdscr.addstr(y, start, "".join(pieces), attr)
            except curses.error:
                pass

    status = (
        f"onfire  |  q/Esc quit  s charset({sim.cfg.charset})  c color({int(color)})  "
        f"[ ] wind({sim.cfg.wind})  fps({sim.cfg.fps})  speed({sim.cfg.speed:.2f})  "
        f"sparks({sim.cfg.sparks})  blur({sim.cfg.blur})"
    )
    try:
        stdscr.addstr(view_h, 0, status[: max(0, view_w - 1)])
    except curses.error:
        pass


def _cycle_charset(current: str) -> str:
    order = ["shade", "solid", "ascii"]
    try:
        i = order.index(current)
    except ValueError:
        return "shade"
    return order[(i + 1) % len(order)]


def _run(stdscr, cfg: Config) -> None:
    curses.curs_set(0)
    stdscr.nodelay(True)
    stdscr.keypad(True)

    color_enabled, attrs = _setup_colors(cfg)
    color = cfg.color and color_enabled

    chars = _pick_charset(cfg.charset)
    char_lut = _build_char_lut(chars, cfg.gamma)

    term_h, term_w = stdscr.getmaxyx()
    sim = FireSim(term_w, max(1, term_h - 1), cfg)

    frame_dt = 1.0 / max(1, cfg.fps)
    last = time.monotonic()

    while True:
        try:
            key = stdscr.getch()
        except curses.error:
            key = -1

        if key != -1:
            if key in (27, ord("q")):
                return

            if key == curses.KEY_RESIZE:
                # Handled by render/resize path; just force a repaint.
                stdscr.erase()

            if key == ord("s"):
                cfg.charset = _cycle_charset(cfg.charset)
                chars = _pick_charset(cfg.charset)
                char_lut = _build_char_lut(chars, cfg.gamma)

            if key == ord("c"):
                color = (not color) and color_enabled

            if key == ord("["):
                cfg.wind = max(-5, cfg.wind - 1)
            if key == ord("]"):
                cfg.wind = min(5, cfg.wind + 1)

            # Bonus controls (feel free to delete)
            if key in (curses.KEY_UP, ord("+"), ord("=")):
                cfg.speed = min(4.0, cfg.speed + 0.1)
            if key in (curses.KEY_DOWN, ord("-"), ord("_")) and cfg.speed > 0:
                cfg.speed = max(0.0, cfg.speed - 0.1)
            if key == ord("b"):
                cfg.blur = 0 if cfg.blur else 1
            if key == ord("e"):
                cfg.sparks = 0 if cfg.sparks else 2

        # Full + fractional steps (this is what makes low speed smooth)
        steps = int(cfg.speed)
        rem = cfg.speed - steps

        for _ in range(steps):
            sim.step(1.0)
        if rem > 1e-6:
            sim.step(rem)

        stdscr.erase()
        _render(stdscr, sim, char_lut, attrs, color)
        stdscr.refresh()

        now = time.monotonic()
        elapsed = now - last
        if elapsed < frame_dt:
            time.sleep(frame_dt - elapsed)
            last = now + (frame_dt - elapsed)
        else:
            last = now


def cli(argv: list[str] | None = None) -> None:
    p = argparse.ArgumentParser(
        prog="onfire", description="AAFire-style terminal flames (Python + curses)."
    )
    p.add_argument("--fps", type=int, default=30)
    p.add_argument(
        "--speed",
        type=float,
        default=1.0,
        help="Simulation speed multiplier (fractional ok).",
    )
    p.add_argument("--no-color", action="store_true")
    p.add_argument("--charset", choices=["shade", "solid", "ascii"], default="shade")
    p.add_argument("--fuel", type=float, default=0.65)
    p.add_argument("--cool-min", type=int, default=0)
    p.add_argument("--cool-max", type=int, default=3)
    p.add_argument("--wind", type=int, default=0)
    p.add_argument(
        "--sparks", type=int, default=2, help="Embers injected per step (0 disables)."
    )
    p.add_argument("--blur", type=int, default=1, help="0=off, 1=light blur.")
    p.add_argument(
        "--gamma", type=float, default=0.85, help="Intensity curve (lower = brighter)."
    )
    p.add_argument("--seed", type=int, default=None)
    args = p.parse_args(argv)

    cfg = Config(
        fps=max(1, args.fps),
        speed=max(0.0, args.speed),
        charset=args.charset,
        color=not args.no_color,
        fuel=min(1.0, max(0.0, args.fuel)),
        cooling_min=max(0, args.cool_min),
        cooling_max=max(0, args.cool_max),
        wind=max(-5, min(5, args.wind)),
        sparks=max(0, args.sparks),
        blur=1 if args.blur else 0,
        gamma=max(0.1, args.gamma),
        seed=args.seed,
    )
    if cfg.cooling_max < cfg.cooling_min:
        cfg.cooling_max = cfg.cooling_min

    curses.wrapper(_run, cfg)


if __name__ == "__main__":
    cli()
