from manim import *
import numpy as np

# ═══════════════════════════════════════════════════════════════
#  Global Configuration
# ═══════════════════════════════════════════════════════════════
FONT = "Times New Roman"
BG_COLOR = "#0C1222"

# Color Palette
TX1_COLOR = "#FF6B6B"   # Red — Antenna 1
TX2_COLOR = "#4ECDC4"   # Teal — Antenna 2
RX1_COLOR = "#FFD93D"   # Gold — Rx Antenna 1
RX2_COLOR = "#C084FC"   # Purple — Rx Antenna 2
BIT_COLOR = "#FBBF24"   # Yellow — Bit stream
NOISE_COLOR = "#6B7280" # Grey — Noise
DECISION_COLOR = "#34D399"  # Green — Correct decision
ACCENT = "#818CF8"      # Indigo — Section headers
BLOCK_BG = "#1E293B"    # Dark slate — Block background
BLOCK_BORDER = "#475569"    # Slate — Block border
LABEL_COLOR = "#E2E8F0"    # Light grey — Labels

# Gray mapping: (b1,b2) -> PAM level
GRAY_MAP = {(0, 0): -3, (0, 1): -1, (1, 1): 1, (1, 0): 3}
GRAY_MAP_INV = {v: k for k, v in GRAY_MAP.items()}


# ═══════════════════════════════════════════════════════════════
#  Helper Functions
# ═══════════════════════════════════════════════════════════════

def get_qam16_constellation():
    """Return list of (I, Q, bits_str) for all 16-QAM points (Gray coded)."""
    points = []
    for ib in [(0, 0), (0, 1), (1, 1), (1, 0)]:
        for qb in [(0, 0), (0, 1), (1, 1), (1, 0)]:
            I = GRAY_MAP[ib]
            Q = GRAY_MAP[qb]
            bits_str = f"{ib[0]}{ib[1]}{qb[0]}{qb[1]}"
            points.append((I, Q, bits_str))
    return points


def create_block(label, width=2.5, height=0.8,
                 color=BLOCK_BORDER, fill_color=BLOCK_BG, font_size=20):
    """Create a labeled rounded-rectangle processing block."""
    rect = RoundedRectangle(
        corner_radius=0.15, width=width, height=height,
        stroke_color=color, stroke_width=2,
        fill_color=fill_color, fill_opacity=0.85,
    )
    txt = Text(label, font=FONT, font_size=font_size, color=LABEL_COLOR)
    txt.move_to(rect.get_center())
    return VGroup(rect, txt)


def create_antenna(color=WHITE, label_text=""):
    """Create a simple antenna icon as a VGroup."""
    base = Line(ORIGIN, UP * 0.6, stroke_color=color, stroke_width=3)
    left_arm = Line(UP * 0.6, UP * 0.9 + LEFT * 0.2,
                    stroke_color=color, stroke_width=3)
    right_arm = Line(UP * 0.6, UP * 0.9 + RIGHT * 0.2,
                     stroke_color=color, stroke_width=3)
    tip = Dot(UP * 0.6, color=color, radius=0.04)
    antenna = VGroup(base, left_arm, right_arm, tip)
    if label_text:
        lbl = Text(label_text, font=FONT, font_size=16, color=color)
        lbl.next_to(antenna, DOWN, buff=0.15)
        antenna.add(lbl)
    return antenna


def make_signal_curve(x_start, x_end, y_center, num_pts=200,
                      color=TX1_COLOR, seed=42):
    """Generate a random-looking time-domain waveform VMobject."""
    rng = np.random.RandomState(seed)
    t = np.linspace(0, 4 * np.pi, num_pts)
    sig = (np.sin(t) * 0.4 + 0.25 * np.sin(3 * t + rng.uniform(0, 2))
           + 0.12 * np.sin(7 * t + rng.uniform(0, 2)))
    xs = np.linspace(x_start, x_end, num_pts)
    pts = [np.array([x, y_center + s, 0]) for x, s in zip(xs, sig)]
    curve = VMobject(color=color, stroke_width=2)
    curve.set_points_smoothly(pts)
    return curve


# ═══════════════════════════════════════════════════════════════
#  UNIFIED SCENE — Full MIMO-OFDM Pipeline
# ═══════════════════════════════════════════════════════════════

class MIMOOFDMScene(Scene):
    """Single unified scene: Transmitter -> Channel -> Receiver."""

    def construct(self):
        self.camera.background_color = BG_COLOR
        # ── Opening title ──
        self.play_intro()
        # ── Phase 1: Transmitter ──
        self.play_phase_banner("Phase 1: Transmitter",
                               "Bit Generation → 16-QAM → Alamouti STBC → OFDM")
        self.play_qam_mapping()
        self.play_alamouti_encoder()
        self.play_ofdm_mod()
        # ── Phase 2: Channel ──
        self.play_phase_banner("Phase 2: Wireless Channel",
                               "Multipath Rayleigh Fading + AWGN")
        self.play_channel()
        # ── Phase 3: Receiver ──
        self.play_phase_banner("Phase 3: Receiver",
                               "OFDM Demod → Alamouti Decode → ML Detection")
        self.play_ofdm_demod()
        self.play_alamouti_decoder()
        self.play_ml_detection()
        self.play_demapping()

    def play_intro(self):
        title = Text("2×2 MIMO-OFDM with Alamouti STBC",
                      font=FONT, font_size=38, color=WHITE)
        line1 = Text("Modulation: 16-QAM  |  Nfft = 64  |  CP = 16",
                      font=FONT, font_size=18, color=LABEL_COLOR)
        line2 = Text("Channel: 6-tap Rayleigh  |  2 Tx, 2 Rx antennas",
                      font=FONT, font_size=18, color=LABEL_COLOR)
        params = VGroup(line1, line2).arrange(DOWN, buff=0.2)
        group = VGroup(title, params).arrange(DOWN, buff=0.4)

        self.play(Write(title), run_time=1.5)
        self.play(FadeIn(params, shift=UP * 0.2), run_time=1)
        self.wait(2)
        self.play(FadeOut(group))

    def play_phase_banner(self, phase_text, subtitle_text):
        """Show a quick phase transition banner."""
        phase = Text(phase_text, font=FONT, font_size=34, color=WHITE)
        sub = Text(subtitle_text, font=FONT, font_size=18, color=ACCENT)
        g = VGroup(phase, sub).arrange(DOWN, buff=0.25)
        self.play(FadeIn(g, scale=1.1), run_time=1)
        self.wait(1.5)
        self.play(FadeOut(g, scale=0.9), run_time=0.8)

    def play_qam_mapping(self):
        header = Text("Step 1: Bit Generation & 16-QAM Mapping",
                       font=FONT, font_size=26, color=ACCENT).to_edge(UP, buff=0.3)
        self.play(Write(header), run_time=1.5)
        self.wait(1)

        # ── 1a. Show the 8-bit input stream ──
        bit_str = "10110010"
        bits_vg = VGroup(*[Text(b, font=FONT, font_size=30, color=BIT_COLOR)
                           for b in bit_str])
        bits_vg.arrange(RIGHT, buff=0.15).shift(UP * 2)
        stream_label = Text("Random bit stream: 8 bits",
                            font=FONT, font_size=18, color=LABEL_COLOR)
        stream_label.next_to(bits_vg, UP, buff=0.2)
        self.play(Write(stream_label), run_time=1)
        self.wait(0.5)
        # Animate bits appearing one by one
        for bt in bits_vg:
            self.play(FadeIn(bt, scale=1.5), run_time=0.3)
        self.wait(1)

        # ── 1b. Group into 2 symbols of 4 bits each ──
        group_label = Text("Group every 4 bits -> 1 QAM symbol",
                           font=FONT, font_size=18, color=LABEL_COLOR)
        group_label.next_to(bits_vg, DOWN, buff=0.6)
        self.play(Write(group_label), run_time=1.5)
        self.wait(1)

        braces = VGroup()
        sym_colors = [TX1_COLOR, TX2_COLOR]
        for i in range(2):
            chunk = VGroup(*[bits_vg[j] for j in range(i * 4, i * 4 + 4)])
            br = Brace(chunk, DOWN, color=sym_colors[i], buff=0.06)
            lb = Text(f"s{i+1}", font=FONT, font_size=20, color=sym_colors[i])
            lb.next_to(br, DOWN, buff=0.06)
            braces.add(VGroup(br, lb))
            self.play(Create(br), Write(lb), run_time=1)
            self.wait(0.5)
        self.wait(1.5)

        # ── 1c. Show Gray mapping table ──
        self.play(FadeOut(stream_label), FadeOut(group_label))
        table_title = Text("16-QAM Gray Mapping Table",
                           font=FONT, font_size=20, color=ACCENT)
        table_title.shift(DOWN * 0.5 + LEFT * 4)
        gray_entries = [
            ("00", "-3"), ("01", "-1"), ("11", "+1"), ("10", "+3")
        ]
        table_rows = VGroup()
        for bits, level in gray_entries:
            row = Text(f"  {bits}  ->  {level}", font=FONT, font_size=16,
                       color=LABEL_COLOR)
            table_rows.add(row)
        table_rows.arrange(DOWN, buff=0.12, aligned_edge=LEFT)
        table_rows.next_to(table_title, DOWN, buff=0.2)

        self.play(Write(table_title), run_time=1)
        for row in table_rows:
            self.play(Write(row), run_time=0.6)
        self.wait(1.5)

        # ── 1d. Map s1 = "1011" step by step ──
        s1_title = Text("Mapping s1 = 1011", font=FONT, font_size=22,
                        color=TX1_COLOR)
        s1_title.shift(DOWN * 0.5 + RIGHT * 1.5)
        self.play(Write(s1_title), run_time=1)
        self.wait(0.5)

        # Split into I-bits and Q-bits
        s1_split = MathTex(r"\text{s1} = \underbrace{10}_{I} \underbrace{11}_{Q}",
                           font_size=28, color=TX1_COLOR)
        s1_split.next_to(s1_title, DOWN, buff=0.3)
        self.play(Write(s1_split), run_time=1.5)
        self.wait(1)

        # Lookup I and Q
        s1_i_lookup = MathTex(r"I\text{-bits} = 10 \xrightarrow{\text{Gray}} +3",
                              font_size=24, color=TX1_COLOR)
        s1_q_lookup = MathTex(r"Q\text{-bits} = 11 \xrightarrow{\text{Gray}} +1",
                              font_size=24, color=TX1_COLOR)
        s1_lookups = VGroup(s1_i_lookup, s1_q_lookup).arrange(DOWN, buff=0.15)
        s1_lookups.next_to(s1_split, DOWN, buff=0.3)
        self.play(Write(s1_i_lookup), run_time=1.2)
        self.wait(0.8)
        self.play(Write(s1_q_lookup), run_time=1.2)
        self.wait(0.8)

        # Normalization
        s1_norm = MathTex(
            r"s_1 = \frac{3 + j \cdot 1}{\sqrt{10}} = (0.95 + 0.32j)",
            font_size=22, color=TX1_COLOR)
        s1_norm.next_to(s1_lookups, DOWN, buff=0.3)
        self.play(Write(s1_norm), run_time=1.5)
        self.wait(1.5)

        # ── 1e. Map s2 = "0010" step by step ──
        # Clear s1 details, keep table
        self.play(FadeOut(s1_title), FadeOut(s1_split),
                  FadeOut(s1_lookups), FadeOut(s1_norm))

        s2_title = Text("Mapping s2 = 0010", font=FONT, font_size=22,
                        color=TX2_COLOR)
        s2_title.shift(DOWN * 0.5 + RIGHT * 1.5)
        self.play(Write(s2_title), run_time=1)
        self.wait(0.5)

        s2_split = MathTex(r"\text{s2} = \underbrace{00}_{I} \underbrace{10}_{Q}",
                           font_size=28, color=TX2_COLOR)
        s2_split.next_to(s2_title, DOWN, buff=0.3)
        self.play(Write(s2_split), run_time=1.5)
        self.wait(1)

        s2_i_lookup = MathTex(r"I\text{-bits} = 00 \xrightarrow{\text{Gray}} -3",
                              font_size=24, color=TX2_COLOR)
        s2_q_lookup = MathTex(r"Q\text{-bits} = 10 \xrightarrow{\text{Gray}} +3",
                              font_size=24, color=TX2_COLOR)
        s2_lookups = VGroup(s2_i_lookup, s2_q_lookup).arrange(DOWN, buff=0.15)
        s2_lookups.next_to(s2_split, DOWN, buff=0.3)
        self.play(Write(s2_i_lookup), run_time=1.2)
        self.wait(0.8)
        self.play(Write(s2_q_lookup), run_time=1.2)
        self.wait(0.8)

        s2_norm = MathTex(
            r"s_2 = \frac{-3 + j \cdot 3}{\sqrt{10}} = (-0.95 + 0.95j)",
            font_size=22, color=TX2_COLOR)
        s2_norm.next_to(s2_lookups, DOWN, buff=0.3)
        self.play(Write(s2_norm), run_time=1.5)
        self.wait(1.5)

        # ── 1f. Show on constellation diagram ──
        self.play(*[FadeOut(m) for m in self.mobjects if m is not header])

        axes = Axes(x_range=[-4, 4, 1], y_range=[-4, 4, 1],
                    x_length=5.5, y_length=5.5,
                    axis_config={"color": "#475569", "include_tip": True,
                                 "tip_length": 0.15})
        axes.shift(DOWN * 0.3)
        x_lbl = Text("I (In-phase)", font=FONT, font_size=14, color=LABEL_COLOR)
        y_lbl = Text("Q (Quadrature)", font=FONT, font_size=14, color=LABEL_COLOR)
        x_lbl.next_to(axes.x_axis, RIGHT, buff=0.1)
        y_lbl.next_to(axes.y_axis, UP, buff=0.1)

        self.play(Create(axes), Write(x_lbl), Write(y_lbl), run_time=1.5)
        self.wait(0.5)

        # Plot all 16 ideal constellation points with Gray labels
        qam_pts = get_qam16_constellation()
        dots_lbl = VGroup()
        for I, Q, bs in qam_pts:
            d = Dot(axes.c2p(I, Q), color="#475569", radius=0.06)
            l = Text(bs, font=FONT, font_size=9, color="#64748B")
            l.next_to(d, UR, buff=0.04)
            dots_lbl.add(VGroup(d, l))
        self.play(FadeIn(dots_lbl, lag_ratio=0.04), run_time=2)
        self.wait(1)

        # Highlight s1 at (3, 1)
        s1_info = Text("s1 = 1011 -> I=3, Q=1", font=FONT, font_size=18,
                        color=TX1_COLOR)
        s1_info.to_corner(UL, buff=0.4).shift(DOWN * 0.5)
        self.play(Write(s1_info), run_time=1.2)
        self.wait(0.5)
        s1_pos = axes.c2p(3, 1)
        s1_dot = Dot(s1_pos, color=TX1_COLOR, radius=0.12)
        s1_ring = Circle(radius=0.22, color=TX1_COLOR, stroke_width=2.5
                         ).move_to(s1_pos)
        s1_coord = MathTex("(3, 1)", font_size=20, color=TX1_COLOR)
        s1_coord.next_to(s1_dot, DOWN, buff=0.15)
        self.play(FadeIn(s1_dot, scale=2), Create(s1_ring),
                  Write(s1_coord), run_time=1.5)
        self.wait(1.5)

        # Highlight s2 at (-3, 3)
        s2_info = Text("s2 = 0010 -> I=-3, Q=3", font=FONT, font_size=18,
                        color=TX2_COLOR)
        s2_info.next_to(s1_info, DOWN, buff=0.15)
        self.play(Write(s2_info), run_time=1.2)
        self.wait(0.5)
        s2_pos = axes.c2p(-3, 3)
        s2_dot = Dot(s2_pos, color=TX2_COLOR, radius=0.12)
        s2_ring = Circle(radius=0.22, color=TX2_COLOR, stroke_width=2.5
                         ).move_to(s2_pos)
        s2_coord = MathTex("(-3, 3)", font_size=20, color=TX2_COLOR)
        s2_coord.next_to(s2_dot, DOWN, buff=0.15)
        self.play(FadeIn(s2_dot, scale=2), Create(s2_ring),
                  Write(s2_coord), run_time=1.5)
        self.wait(1.5)

        note = Text("Symbols s1, s2 ready for Alamouti encoding",
                     font=FONT, font_size=18, color=DECISION_COLOR)
        note.to_edge(DOWN, buff=0.3)
        self.play(Write(note), run_time=1.2)
        self.wait(2)
        self.play(*[FadeOut(m) for m in self.mobjects])

    def play_alamouti_encoder(self):
        header = Text("Step 2: Alamouti STBC Encoder",
                       font=FONT, font_size=26, color=ACCENT).to_edge(UP, buff=0.3)
        self.play(Write(header), run_time=1.5)
        self.wait(1)

        # ── 2a. Show input symbols ──
        inp_title = Text("S/P Converter splits QAM stream -> s1 and s2",
                         font=FONT, font_size=20, color=LABEL_COLOR)
        inp_title.shift(UP * 2.2)
        self.play(Write(inp_title), run_time=1.2)
        self.wait(0.5)

        s1_val = MathTex(r"s_1 = (3 + j) / \sqrt{10}", font_size=28,
                         color=TX1_COLOR)
        s2_val = MathTex(r"s_2 = (-3 + 3j) / \sqrt{10}", font_size=28,
                         color=TX2_COLOR)
        syms = VGroup(s1_val, s2_val).arrange(DOWN, buff=0.2)
        syms.next_to(inp_title, DOWN, buff=0.3)
        self.play(Write(s1_val), run_time=1.2)
        self.wait(0.8)
        self.play(Write(s2_val), run_time=1.2)
        self.wait(1)

        # ── 2b. Show the generic Alamouti matrix ──
        gen_title = Text("Alamouti Transmission Matrix (general form):",
                         font=FONT, font_size=18, color=LABEL_COLOR)
        gen_title.shift(DOWN * 0.3 + LEFT * 0.5)
        self.play(Write(gen_title), run_time=1.2)
        self.wait(0.5)

        mat_gen = MathTex(
            r"\mathbf{X} = \begin{bmatrix} s_1 & -s_2^* \\ s_2 & s_1^* \end{bmatrix}",
            font_size=38, color=WHITE)
        mat_gen.next_to(gen_title, DOWN, buff=0.3)
        self.play(Write(mat_gen), run_time=2)
        self.wait(1.5)

        # Row / column labels
        c1 = Text("Slot 1", font=FONT, font_size=14, color=BIT_COLOR)
        c2 = Text("Slot 2", font=FONT, font_size=14, color=BIT_COLOR)
        r1 = Text("Ant 1", font=FONT, font_size=14, color=TX1_COLOR)
        r2 = Text("Ant 2", font=FONT, font_size=14, color=TX2_COLOR)
        c1.next_to(mat_gen, UP, buff=0.1).shift(LEFT * 0.55)
        c2.next_to(mat_gen, UP, buff=0.1).shift(RIGHT * 0.55)
        r1.next_to(mat_gen, LEFT, buff=0.12).shift(UP * 0.28)
        r2.next_to(mat_gen, LEFT, buff=0.12).shift(DOWN * 0.28)
        self.play(Write(c1), Write(c2), Write(r1), Write(r2), run_time=1)
        self.wait(1)

        # ── 2c. Compute conjugates step by step ──
        conj_title = Text("Step: compute conjugates",
                          font=FONT, font_size=18, color=ACCENT)
        conj_title.to_edge(DOWN, buff=1.8)
        self.play(Write(conj_title), run_time=1)
        self.wait(0.5)

        s1_conj = MathTex(r"s_1^* = (3 - j) / \sqrt{10}",
                          font_size=24, color=TX1_COLOR)
        s2_conj = MathTex(r"s_2^* = (-3 - 3j) / \sqrt{10}",
                          font_size=24, color=TX2_COLOR)
        neg_s2_conj = MathTex(r"-s_2^* = (3 + 3j) / \sqrt{10}",
                              font_size=24, color=TX2_COLOR)
        conj_steps = VGroup(s1_conj, s2_conj, neg_s2_conj).arrange(DOWN, buff=0.15)
        conj_steps.next_to(conj_title, DOWN, buff=0.2)

        self.play(Write(s1_conj), run_time=1.2)
        self.wait(1)
        self.play(Write(s2_conj), run_time=1.2)
        self.wait(1)
        self.play(Write(neg_s2_conj), run_time=1.2)
        self.wait(1.5)

        # ── 2d. Show per-slot assignments ──
        self.play(*[FadeOut(m) for m in self.mobjects
                    if m is not header])

        slot1_title = Text("Time Slot 1:", font=FONT, font_size=22,
                           color=BIT_COLOR)
        slot1_title.shift(UP * 2.5)
        self.play(Write(slot1_title), run_time=1)

        sl1_a1 = MathTex(r"\text{Ant 1} \to s_1 = (3+j)/\sqrt{10}",
                         font_size=26, color=TX1_COLOR)
        sl1_a2 = MathTex(r"\text{Ant 2} \to s_2 = (-3+3j)/\sqrt{10}",
                         font_size=26, color=TX2_COLOR)
        sl1 = VGroup(sl1_a1, sl1_a2).arrange(DOWN, buff=0.2)
        sl1.next_to(slot1_title, DOWN, buff=0.3)
        self.play(Write(sl1_a1), run_time=1.5)
        self.wait(1)
        self.play(Write(sl1_a2), run_time=1.5)
        self.wait(1.5)

        slot2_title = Text("Time Slot 2:", font=FONT, font_size=22,
                           color=BIT_COLOR)
        slot2_title.next_to(sl1, DOWN, buff=0.5)
        self.play(Write(slot2_title), run_time=1)

        sl2_a1 = MathTex(r"\text{Ant 1} \to -s_2^* = (3+3j)/\sqrt{10}",
                         font_size=26, color=TX1_COLOR)
        sl2_a2 = MathTex(r"\text{Ant 2} \to s_1^* = (3-j)/\sqrt{10}",
                         font_size=26, color=TX2_COLOR)
        sl2 = VGroup(sl2_a1, sl2_a2).arrange(DOWN, buff=0.2)
        sl2.next_to(slot2_title, DOWN, buff=0.3)
        self.play(Write(sl2_a1), run_time=1.5)
        self.wait(1)
        self.play(Write(sl2_a2), run_time=1.5)
        self.wait(1)

        note = Text("Each antenna transmits different data each slot -> diversity!",
                     font=FONT, font_size=17, color=DECISION_COLOR)
        note.to_edge(DOWN, buff=0.3)
        self.play(Write(note), run_time=1.5)
        self.wait(3)
        self.play(*[FadeOut(m) for m in self.mobjects])

    def play_ofdm_mod(self):
        header = Text("Step 3: OFDM Modulation (IFFT + Cyclic Prefix)",
                       font=FONT, font_size=26, color=ACCENT).to_edge(UP, buff=0.3)
        self.play(Write(header), run_time=1.5)
        self.wait(1)

        # ── 3a. Explain OFDM concept ──
        explain1 = Text("OFDM: map QAM symbols onto orthogonal subcarriers",
                        font=FONT, font_size=18, color=LABEL_COLOR)
        explain2 = Text("Each subcarrier carries one symbol independently",
                        font=FONT, font_size=16, color=LABEL_COLOR)
        expl_g = VGroup(explain1, explain2).arrange(DOWN, buff=0.1)
        expl_g.shift(UP * 2.2)
        self.play(Write(explain1), run_time=1.5)
        self.wait(0.5)
        self.play(Write(explain2), run_time=1.2)
        self.wait(1.5)

        # Frequency-domain bars (showing |X[k]| magnitudes)
        np.random.seed(42)
        bars = VGroup()
        bw = 0.13
        for i in range(32):
            h = np.random.uniform(0.3, 1.4)
            r = Rectangle(width=bw, height=h, fill_color=ACCENT,
                          fill_opacity=0.7, stroke_color=ACCENT, stroke_width=1)
            r.move_to(LEFT * 2.5 + RIGHT * i * (bw + 0.02) + UP * (h / 2 + 0.3))
            bars.add(r)
        freq_lbl = Text("X[k] — Frequency Domain (64 subcarriers)",
                        font=FONT, font_size=16, color=ACCENT)
        freq_lbl.next_to(bars, DOWN, buff=0.15)
        self.play(FadeIn(bars, lag_ratio=0.03), Write(freq_lbl), run_time=2)
        self.wait(1.5)

        # ── 3b. IFFT formula ──
        ifft_formula = MathTex(
            r"x[n] = \frac{1}{\sqrt{N}} \sum_{k=0}^{N-1} X[k] \, e^{j 2\pi kn/N}",
            font_size=26, color=BIT_COLOR)
        ifft_formula.shift(DOWN * 0.8)
        ifft_label = Text("64-point IFFT converts frequency -> time domain",
                          font=FONT, font_size=16, color=LABEL_COLOR)
        ifft_label.next_to(ifft_formula, UP, buff=0.2)
        self.play(Write(ifft_label), run_time=1.2)
        self.play(Write(ifft_formula), run_time=2)
        self.wait(2)

        # ── 3c. Generate COHERENT waveform for data + CP ──
        # Generate the underlying signal data (one array, same seed)
        rng = np.random.RandomState(42)
        num_pts = 200
        t = np.linspace(0, 4 * np.pi, num_pts)
        sig = (np.sin(t) * 0.4 + 0.25 * np.sin(3 * t + rng.uniform(0, 2))
               + 0.12 * np.sin(7 * t + rng.uniform(0, 2)))
        y_center = -1.2

        # Full data signal: 64 samples -> plotted over x=[-3, 3]
        data_xs = np.linspace(-3, 3, num_pts)
        data_pts = [np.array([x, y_center + s, 0])
                    for x, s in zip(data_xs, sig)]
        data_wave = VMobject(color=TX1_COLOR, stroke_width=2)
        data_wave.set_points_smoothly(data_pts)

        time_lbl = Text("x[n] — Time Domain (64 samples)",
                        font=FONT, font_size=16, color=TX1_COLOR)
        time_lbl.next_to(data_wave, UP, buff=0.15)

        self.play(FadeOut(ifft_formula), FadeOut(ifft_label))
        self.play(ReplacementTransform(bars.copy(), data_wave),
                  Write(time_lbl), run_time=2.5)
        self.wait(1.5)

        # ── 3d. CP insertion — the TAIL and CP must be IDENTICAL ──
        self.play(FadeOut(bars), FadeOut(freq_lbl), FadeOut(expl_g))

        cp_title = Text("Cyclic Prefix: Why and How",
                        font=FONT, font_size=20, color=DECISION_COLOR)
        cp_title.shift(UP * 2.5)
        self.play(Write(cp_title), run_time=1.2)
        self.wait(0.5)

        # Why CP?
        why_1 = Text("Multipath channel causes Inter-Symbol Interference (ISI)",
                      font=FONT, font_size=15, color=LABEL_COLOR)
        why_2 = Text("CP converts linear convolution -> circular convolution",
                      font=FONT, font_size=15, color=LABEL_COLOR)
        why_3 = Text("This lets FFT perfectly separate the subcarriers!",
                      font=FONT, font_size=15, color=DECISION_COLOR)
        why_g = VGroup(why_1, why_2, why_3).arrange(DOWN, buff=0.1)
        why_g.next_to(cp_title, DOWN, buff=0.25)
        for txt in [why_1, why_2, why_3]:
            self.play(Write(txt), run_time=1.5)
            self.wait(1)
        self.wait(1)

        # Step 1: Highlight the TAIL (last 25% = last 16/64 samples)
        step_1 = Text("Step 1: Identify the LAST 16 samples (= Ncp)",
                       font=FONT, font_size=16, color=BIT_COLOR)
        step_1.to_edge(DOWN, buff=1.6)
        self.play(Write(step_1), run_time=1.5)
        self.wait(0.5)

        # Tail = last 25% of data waveform
        tail_start_x = 1.5  # corresponds to last ~25% of [-3, 3]
        tail_br = Brace(Line(np.array([tail_start_x, -1.8, 0]),
                             np.array([3, -1.8, 0])),
                        DOWN, color=DECISION_COLOR, buff=0.05)
        tail_txt = Text("Tail: last 16 samples",
                        font=FONT, font_size=13, color=DECISION_COLOR)
        tail_txt.next_to(tail_br, DOWN, buff=0.08)

        # Also highlight the tail portion of the wave with a color change
        tail_idx = int(num_pts * 0.75)  # last 25%
        tail_pts = [np.array([x, y_center + s, 0])
                    for x, s in zip(data_xs[tail_idx:], sig[tail_idx:])]
        tail_highlight = VMobject(color=DECISION_COLOR, stroke_width=3.5)
        tail_highlight.set_points_smoothly(tail_pts)

        self.play(Create(tail_br), Write(tail_txt),
                  Create(tail_highlight), run_time=1.5)
        self.wait(2)

        # Step 2: COPY tail -> prepend as CP  (SAME WAVEFORM!)
        step_2 = Text("Step 2: COPY tail and PREPEND as Cyclic Prefix",
                       font=FONT, font_size=16, color=BIT_COLOR)
        step_2.next_to(step_1, DOWN, buff=0.1)
        self.play(Write(step_2), run_time=1.5)
        self.wait(0.5)

        # Build CP waveform from the EXACT SAME data (sig[tail_idx:])
        cp_x_start = -4.8
        cp_x_end = -3.0
        cp_xs = np.linspace(cp_x_start, cp_x_end, num_pts - tail_idx)
        cp_pts = [np.array([x, y_center + s, 0])
                  for x, s in zip(cp_xs, sig[tail_idx:])]
        cp_wave = VMobject(color=DECISION_COLOR, stroke_width=2.5)
        cp_wave.set_points_smoothly(cp_pts)

        cp_br = Brace(Line(np.array([cp_x_start, -1.8, 0]),
                           np.array([cp_x_end, -1.8, 0])),
                      DOWN, color=DECISION_COLOR, buff=0.05)
        cp_lbl = Text("CP (16 samples) = exact copy of tail",
                       font=FONT, font_size=13, color=DECISION_COLOR)
        cp_lbl.next_to(cp_br, DOWN, buff=0.08)

        # Animate the copy: flash tail, then appear at CP location
        self.play(tail_highlight.animate.set_stroke(width=5), run_time=0.5)
        self.play(tail_highlight.animate.set_stroke(width=3.5), run_time=0.5)
        self.play(Create(cp_wave), Create(cp_br), Write(cp_lbl), run_time=2)
        self.wait(1.5)

        # Point out they're identical
        same_note = Text("CP shape = Tail shape (identical!)",
                         font=FONT, font_size=17, color=DECISION_COLOR)
        same_note.to_edge(DOWN, buff=0.4)
        self.play(Write(same_note), run_time=1.2)
        self.wait(1.5)

        # Step 3: total length
        self.play(FadeOut(step_1), FadeOut(step_2), FadeOut(same_note))
        step_3 = Text("Total OFDM symbol: Ncp + Nfft = 16 + 64 = 80 samples",
                       font=FONT, font_size=17, color=BIT_COLOR)
        step_3.to_edge(DOWN, buff=0.5)
        self.play(Write(step_3), run_time=1.5)
        self.wait(1)

        ready = Text("P/S Converter serializes 80 samples -> Transmit!",
                      font=FONT, font_size=18, color=DECISION_COLOR)
        ready.to_edge(DOWN, buff=0.15)
        self.play(Write(ready), run_time=1.5)
        self.wait(3)
        self.play(*[FadeOut(m) for m in self.mobjects])


    def play_channel(self):
        header = Text("Multipath Rayleigh Fading Channel (6 taps)",
                       font=FONT, font_size=22, color=ACCENT).to_edge(UP, buff=0.3)
        self.play(Write(header), run_time=1.5)
        self.wait(1)

        # ── Explain channel model ──
        ch_explain = Text("2x2 MIMO: 4 independent channel links (h11, h12, h21, h22)",
                          font=FONT, font_size=17, color=LABEL_COLOR)
        ch_explain.next_to(header, DOWN, buff=0.3)
        self.play(Write(ch_explain), run_time=1.5)
        self.wait(1.5)

        # ── Tx antennas (left) ──
        tx1 = create_antenna(color=TX1_COLOR, label_text="Tx1")
        tx2 = create_antenna(color=TX2_COLOR, label_text="Tx2")
        tx_g = VGroup(tx1, tx2).arrange(DOWN, buff=1.5).shift(LEFT * 5)
        tx_lbl = Text("Transmitter", font=FONT, font_size=16,
                       color=LABEL_COLOR).next_to(tx_g, DOWN, buff=0.2)

        # ── Rx antennas (right) ──
        rx1 = create_antenna(color=RX1_COLOR, label_text="Rx1")
        rx2 = create_antenna(color=RX2_COLOR, label_text="Rx2")
        rx_g = VGroup(rx1, rx2).arrange(DOWN, buff=1.5).shift(RIGHT * 5)
        rx_lbl = Text("Receiver", font=FONT, font_size=16,
                       color=LABEL_COLOR).next_to(rx_g, DOWN, buff=0.2)

        self.play(FadeIn(tx_g), Write(tx_lbl), run_time=1.5)
        self.wait(0.5)
        self.play(FadeIn(rx_g), Write(rx_lbl), run_time=1.5)
        self.wait(1)
        self.play(FadeOut(ch_explain))

        # ── 4 channel paths — one at a time ──
        cfg = [
            (tx1, rx1, "h11: Tx1->Rx1", "#F97316"),
            (tx1, rx2, "h21: Tx1->Rx2", "#EC4899"),
            (tx2, rx1, "h12: Tx2->Rx1", "#14B8A6"),
            (tx2, rx2, "h22: Tx2->Rx2", "#A78BFA"),
        ]
        paths = VGroup()
        for idx, (tx, rx, name, col) in enumerate(cfg):
            st = tx.get_right() + RIGHT * 0.15
            en = rx.get_left() + LEFT * 0.15
            off = UP * 0.25 * (1 - idx * 0.6)
            mid = (st + en) / 2 + off
            line = CubicBezier(st, st + RIGHT * 1.5 + off,
                               en + LEFT * 1.5 + off, en,
                               color=col, stroke_width=1.5, stroke_opacity=0.5)
            lbl = Text(name, font=FONT, font_size=12, color=col)
            lbl.move_to(mid + UP * 0.2)
            path_vg = VGroup(line, lbl)
            paths.add(path_vg)
            self.play(Create(line), Write(lbl), run_time=1.2)
            self.wait(0.5)
        self.wait(1)

        # ── Multipath pulses (6 taps along each path) ──
        tap_label = Text("Each path has 6 multipath taps (exponential power delay profile)",
                          font=FONT, font_size=15, color=LABEL_COLOR)
        tap_label.to_edge(DOWN, buff=0.7)
        self.play(Write(tap_label), run_time=1.5)
        self.wait(1)

        tap_explain = Text("Tap 1 = strongest, Tap 6 = weakest (fading opacity)",
                           font=FONT, font_size=14, color=LABEL_COLOR)
        tap_explain.next_to(tap_label, DOWN, buff=0.1)
        self.play(Write(tap_explain), run_time=1.2)
        self.wait(1)

        pulse_anims = []
        for path_vg in paths:
            line = path_vg[0]
            for tap in range(6):
                opacity = max(0.2, 1.0 - tap * 0.15)
                dot = Dot(color=WHITE, radius=0.05)
                dot.set_opacity(opacity)
                dot.move_to(line.point_from_proportion(0))
                pulse_anims.append(
                    Succession(
                        Wait(tap * 0.2),
                        MoveAlongPath(dot, line, run_time=2,
                                      rate_func=smooth),
                        FadeOut(dot, run_time=0.3),
                    )
                )
                self.add(dot)
        self.play(*pulse_anims)
        self.wait(1.5)

        # ── AWGN noise ──
        self.play(FadeOut(tap_label), FadeOut(tap_explain))
        noise_lbl = Text("+ Additive White Gaussian Noise (AWGN) at each Rx antenna",
                          font=FONT, font_size=16, color=NOISE_COLOR)
        noise_lbl.to_edge(DOWN, buff=0.5)
        self.play(Write(noise_lbl), run_time=1.5)
        self.wait(1)

        rng = np.random.RandomState(7)
        noise_dots = VGroup()
        for _ in range(60):
            x = rng.uniform(3.5, 6)
            y = rng.uniform(-2.5, 2.5)
            d = Dot([x, y, 0], color=NOISE_COLOR, radius=0.03)
            d.set_opacity(rng.uniform(0.3, 0.8))
            noise_dots.add(d)
        self.play(FadeIn(noise_dots, lag_ratio=0.03), run_time=1.5)
        self.wait(0.5)

        # Jitter effect
        jitter_anims = []
        for d in noise_dots:
            offset = rng.uniform(-0.08, 0.08, 3)
            offset[2] = 0
            jitter_anims.append(d.animate.shift(offset))
        self.play(*jitter_anims, run_time=1)

        noise_eq = MathTex(r"y = Hx + n, \quad n \sim \mathcal{CN}(0, \sigma^2)",
                           font_size=24, color=NOISE_COLOR)
        noise_eq.to_edge(DOWN, buff=0.2)
        self.play(Write(noise_eq), run_time=1.5)
        self.wait(3)
        self.play(*[FadeOut(m) for m in self.mobjects])


    def play_ofdm_demod(self):
        header = Text("Step 4: OFDM Demodulation (Remove CP + FFT)",
                       font=FONT, font_size=26, color=ACCENT).to_edge(UP, buff=0.3)
        self.play(Write(header), run_time=1.5)
        self.wait(1)

        # Received signal with CP (CP = exact copy of tail of data)
        rx_lbl = Text("S/P Converter groups received serial time-domain samples",
                       font=FONT, font_size=17, color=LABEL_COLOR).shift(UP * 1.8)

        # Generate coherent waveform: data + matching CP
        rng = np.random.RandomState(42)
        num_pts = 200
        t_arr = np.linspace(0, 4 * np.pi, num_pts)
        sig = (np.sin(t_arr) * 0.35 + 0.2 * np.sin(3 * t_arr + rng.uniform(0, 2))
               + 0.1 * np.sin(7 * t_arr + rng.uniform(0, 2)))
        y_c = 0.8

        # Data portion: x in [-3, 3]
        data_xs = np.linspace(-3, 3, num_pts)
        data_pts = [np.array([x, y_c + s, 0]) for x, s in zip(data_xs, sig)]
        data_wave = VMobject(color=RX1_COLOR, stroke_width=2)
        data_wave.set_points_smoothly(data_pts)

        # CP portion = tail of data: x in [-5, -3], same sig[75%:]
        tail_idx = int(num_pts * 0.75)
        cp_xs = np.linspace(-5, -3, num_pts - tail_idx)
        cp_pts = [np.array([x, y_c + s, 0])
                  for x, s in zip(cp_xs, sig[tail_idx:])]
        cp_wave = VMobject(color=NOISE_COLOR, stroke_width=2)
        cp_wave.set_points_smoothly(cp_pts)

        cp_br = Brace(Line(np.array([-5, 0.2, 0]), np.array([-3, 0.2, 0])),
                      DOWN, color=NOISE_COLOR, buff=0.05)
        cp_txt = Text("CP (discard) — matches tail",
                       font=FONT, font_size=13, color=NOISE_COLOR)
        cp_txt.next_to(cp_br, DOWN, buff=0.08)
        data_br = Brace(Line(np.array([-3, 0.2, 0]), np.array([3, 0.2, 0])),
                        DOWN, color=RX1_COLOR, buff=0.05)
        data_txt = Text("Useful Data (64 samples)", font=FONT, font_size=13,
                         color=RX1_COLOR)
        data_txt.next_to(data_br, DOWN, buff=0.08)

        self.play(Write(rx_lbl), Create(data_wave), run_time=1.5)
        self.play(Create(cp_wave), run_time=1)
        self.wait(1)

        # Highlight that CP and tail look the same
        tail_highlight = VMobject(color=DECISION_COLOR, stroke_width=3)
        tail_pts = [np.array([x, y_c + s, 0])
                    for x, s in zip(data_xs[tail_idx:], sig[tail_idx:])]
        tail_highlight.set_points_smoothly(tail_pts)
        note = Text("Notice: CP shape = Tail shape (identical waveform)",
                     font=FONT, font_size=14, color=DECISION_COLOR)
        note.to_edge(DOWN, buff=0.3)
        self.play(Create(tail_highlight), Write(note), run_time=1.5)
        self.wait(2)
        self.play(FadeOut(tail_highlight), FadeOut(note))

        self.play(Create(cp_br), Write(cp_txt),
                  Create(data_br), Write(data_txt), run_time=1.5)
        self.wait(1.5)

        # Discard CP
        discard_lbl = Text("Remove CP: discard first 16 samples",
                           font=FONT, font_size=16, color="#EF4444")
        discard_lbl.to_edge(DOWN, buff=0.3)
        self.play(Write(discard_lbl), run_time=1)
        cross = Cross(VGroup(cp_wave, cp_br, cp_txt), color="#EF4444", stroke_width=3)
        self.play(Create(cross), run_time=1)
        self.wait(1.5)
        self.play(FadeOut(cp_wave), FadeOut(cp_br), FadeOut(cp_txt),
                  FadeOut(cross), FadeOut(discard_lbl), run_time=1)

        # FFT block
        fft_block = create_block("64-pt FFT", width=2, height=0.65,
                                 color="#F59E0B", font_size=18)
        fft_block.shift(DOWN * 1)
        a1 = Arrow(data_wave.get_bottom() + DOWN * 0.6, fft_block.get_top(),
                   color=LABEL_COLOR, stroke_width=2, buff=0.1)
        self.play(Create(a1), FadeIn(fft_block), run_time=1)
        self.wait(1)

        # Frequency domain bars
        fl = Text("Frequency Domain (Recovered Subcarriers)",
                   font=FONT, font_size=17, color=LABEL_COLOR)
        fl.shift(DOWN * 2)
        np.random.seed(55)
        bars = VGroup()
        bw = 0.13
        for i in range(32):
            h = np.random.uniform(0.2, 1.0)
            r = Rectangle(width=bw, height=h, fill_color=RX1_COLOR,
                          fill_opacity=0.6, stroke_color=RX1_COLOR, stroke_width=1)
            r.move_to(LEFT * 2.5 + RIGHT * i * (bw + 0.02) + DOWN * (3 - h / 2))
            bars.add(r)
        a2 = Arrow(fft_block.get_bottom(), fl.get_top() + UP * 0.1,
                   color=LABEL_COLOR, stroke_width=2, buff=0.1)
        self.play(Create(a2), ReplacementTransform(data_wave.copy(), bars),
                  Write(fl), run_time=2.5)
        self.wait(2)
        self.play(*[FadeOut(m) for m in self.mobjects])

    def play_alamouti_decoder(self):
        header = Text("Step 5: Alamouti STBC Decoder (Perfect CSI)",
                       font=FONT, font_size=26, color=ACCENT).to_edge(UP, buff=0.3)
        self.play(Write(header), run_time=1.5)
        self.wait(1)

        # Decoder block
        dec_box = create_block("Alamouti STBC Combiner", width=4.5, height=0.9,
                               color=ACCENT, font_size=22)
        dec_box.shift(UP * 1.5)

        # Received signals from 2 Rx antennas, 2 time slots
        r1 = Text("Rx1: y1(1), y1(2)", font=FONT, font_size=18, color=RX1_COLOR)
        r2 = Text("Rx2: y2(1), y2(2)", font=FONT, font_size=18, color=RX2_COLOR)
        rx_in = VGroup(r1, r2).arrange(RIGHT, buff=1)
        rx_in.next_to(dec_box, UP, buff=0.4)
        arr_in = Arrow(rx_in.get_bottom(), dec_box.get_top(),
                       color=LABEL_COLOR, stroke_width=2, buff=0.1)

        self.play(Write(r1), run_time=1)
        self.wait(0.5)
        self.play(Write(r2), run_time=1)
        self.wait(0.5)
        self.play(Create(arr_in), FadeIn(dec_box), run_time=1)

        # Perfect CSI label
        csi = Text("Assumes Perfect Channel State Information (CSI)",
                    font=FONT, font_size=16, color=DECISION_COLOR)
        csi.next_to(dec_box, RIGHT, buff=0.3).shift(DOWN * 0.05)
        self.play(Write(csi), run_time=1.2)
        self.wait(1)

        # Combining equations (matching MATLAB lines 131-137)
        eq1 = MathTex(
            r"\hat{s}_1 = \frac{\sum_{r} g_{r1}^* y_{r1} + g_{r2} y_{r2}^*}"
            r"{\sum_{r} |g_{r1}|^2 + |g_{r2}|^2}",
            font_size=30, color=TX1_COLOR)
        eq2 = MathTex(
            r"\hat{s}_2 = \frac{\sum_{r} g_{r2}^* y_{r1} - g_{r1} y_{r2}^*}"
            r"{\sum_{r} |g_{r1}|^2 + |g_{r2}|^2}",
            font_size=30, color=TX2_COLOR)
        eqs = VGroup(eq1, eq2).arrange(DOWN, buff=0.4)
        eqs.next_to(dec_box, DOWN, buff=0.6)

        arr_out = Arrow(dec_box.get_bottom(), eqs.get_top() + UP * 0.15,
                        color=LABEL_COLOR, stroke_width=2, buff=0.1)
        self.play(Create(arr_out), run_time=0.6)
        self.play(Write(eq1), run_time=2)
        self.wait(1.5)
        self.play(Write(eq2), run_time=2)
        self.wait(1.5)

        # Output symbols — use MathTex so hat renders correctly
        out_lbl = MathTex(r"\text{Estimated: } \hat{s}_1, \; \hat{s}_2",
                          font_size=28, color=BIT_COLOR)
        out_lbl.next_to(eqs, DOWN, buff=0.5)
        self.play(Write(out_lbl), run_time=1.2)
        self.wait(3)
        self.play(*[FadeOut(m) for m in self.mobjects])

    def play_ml_detection(self):
        header = Text("Step 6: ML Detection (Minimum Euclidean Distance)",
                       font=FONT, font_size=26, color=ACCENT).to_edge(UP, buff=0.3)
        self.play(Write(header), run_time=1.5)
        self.wait(1)

        # 16-QAM constellation
        axes = Axes(x_range=[-4, 4, 1], y_range=[-4, 4, 1],
                    x_length=5.5, y_length=5.5,
                    axis_config={"color": "#475569", "include_tip": True,
                                 "tip_length": 0.15})
        axes.shift(DOWN * 0.3)
        self.play(Create(axes), run_time=1.5)
        self.wait(0.5)

        # Ideal constellation points
        qam_pts = get_qam16_constellation()
        ideal_dots = VGroup()
        for I, Q, bs in qam_pts:
            d = Dot(axes.c2p(I, Q), color="#475569", radius=0.06)
            l = Text(bs, font=FONT, font_size=8, color="#64748B")
            l.next_to(d, UR, buff=0.03)
            ideal_dots.add(VGroup(d, l))
        self.play(FadeIn(ideal_dots, lag_ratio=0.03), run_time=1.5)
        self.wait(1)

        # Noisy received symbol (slightly offset from ideal (3, -1))
        noisy_pos = axes.c2p(2.6, -0.5)
        noisy_dot = Dot(noisy_pos, color=BIT_COLOR, radius=0.1)
        noisy_lbl = Text("Received", font=FONT, font_size=12, color=BIT_COLOR)
        noisy_lbl.next_to(noisy_dot, UP, buff=0.1)
        self.play(FadeIn(noisy_dot, scale=2), Write(noisy_lbl), run_time=1.5)
        self.wait(1.5)

        # Draw distance lines to 4 nearest candidates
        candidates = [(3, -1), (3, 1), (1, -1), (1, 1)]
        dist_lines = VGroup()
        dist_labels = VGroup()
        colors = ["#EF4444", "#EF4444", "#EF4444", "#EF4444"]
        min_dist = float("inf")
        min_idx = 0
        for i, (ci, cq) in enumerate(candidates):
            cpos = axes.c2p(ci, cq)
            d = np.sqrt((2.6 - ci)**2 + (-0.5 - cq)**2)
            if d < min_dist:
                min_dist = d
                min_idx = i
            ln = DashedLine(noisy_pos, cpos, color="#EF4444",
                            stroke_width=1.5, dash_length=0.08)
            dl = MathTex(f"d={d:.2f}", font_size=16, color="#EF4444")
            dl.move_to((np.array(noisy_pos) + np.array(cpos)) / 2
                       + np.array([0.2, 0.1, 0]))
            dist_lines.add(ln)
            dist_labels.add(dl)

        # Draw distance lines one at a time
        for i, (ln, dl) in enumerate(zip(dist_lines, dist_labels)):
            self.play(Create(ln), FadeIn(dl), run_time=1.2)
            self.wait(0.8)
        self.wait(1)

        # Highlight shortest distance (ML decision)
        best_line = dist_lines[min_idx]
        best_label = dist_labels[min_idx]
        best_line.set_color(DECISION_COLOR)
        best_line.set_stroke(width=3)
        best_label.set_color(DECISION_COLOR)

        best_pos = axes.c2p(*candidates[min_idx])
        decision_ring = Circle(radius=0.18, color=DECISION_COLOR,
                               stroke_width=3).move_to(best_pos)

        ml_text = Text("ML Decision: nearest point!",
                        font=FONT, font_size=18, color=DECISION_COLOR)
        ml_text.to_edge(DOWN, buff=0.3)

        self.play(best_line.animate.set_color(DECISION_COLOR),
                  best_label.animate.set_color(DECISION_COLOR),
                  Create(decision_ring), Write(ml_text), run_time=2)
        self.wait(3)
        self.play(*[FadeOut(m) for m in self.mobjects])

    def play_demapping(self):
        header = Text("Step 7: Symbol Demapping to Bits",
                       font=FONT, font_size=26, color=ACCENT).to_edge(UP, buff=0.3)
        self.play(Write(header), run_time=1.5)
        self.wait(1)

        # Demapper block
        demap_box = create_block("Gray Demapper", width=3.5, height=0.7,
                                 color="#F59E0B", font_size=20)
        demap_box.shift(UP * 1.8)
        self.play(FadeIn(demap_box), run_time=1)
        self.wait(0.5)

        # ── Demap s1: (3, -1) → 1001 ──
        s1_sym = MathTex(r"\hat{s}_1 \rightarrow (3,-1)",
                         font_size=28, color=TX1_COLOR)
        s1_sym.next_to(demap_box, DOWN, buff=0.4)
        self.play(Write(s1_sym), run_time=1.2)
        self.wait(0.8)

        s1_i = MathTex(r"I{=}3 \xrightarrow{\text{Gray}} (1,0)",
                       font_size=22, color=TX1_COLOR)
        s1_q = MathTex(r"Q{=}{-1} \xrightarrow{\text{Gray}} (0,1)",
                       font_size=22, color=TX1_COLOR)
        s1_map = VGroup(s1_i, s1_q).arrange(DOWN, buff=0.15)
        s1_map.next_to(s1_sym, DOWN, buff=0.25)
        self.play(Write(s1_i), run_time=1.2)
        self.wait(0.8)
        self.play(Write(s1_q), run_time=1.2)
        self.wait(0.8)

        s1_bits_vg = VGroup(*[Text(b, font=FONT, font_size=28, color=TX1_COLOR)
                              for b in "1001"])
        s1_bits_vg.arrange(RIGHT, buff=0.08)
        s1_bits_vg.next_to(s1_map, DOWN, buff=0.25)
        s1_label = Text("s1 bits:", font=FONT, font_size=16, color=LABEL_COLOR)
        s1_label.next_to(s1_bits_vg, LEFT, buff=0.2)
        self.play(Write(s1_label), run_time=0.8)
        for bt in s1_bits_vg:
            self.play(FadeIn(bt, scale=1.5), run_time=0.4)
        self.wait(1.5)

        # ── Demap s2: (-3, 3) → 0010 ──
        s2_sym = MathTex(r"\hat{s}_2 \rightarrow (-3, 3)",
                         font_size=28, color=TX2_COLOR)
        s2_sym.next_to(s1_bits_vg, DOWN, buff=0.4)
        self.play(Write(s2_sym), run_time=1.2)
        self.wait(0.8)

        s2_i = MathTex(r"I{=}{-3} \xrightarrow{\text{Gray}} (0,0)",
                       font_size=22, color=TX2_COLOR)
        s2_q = MathTex(r"Q{=}3 \xrightarrow{\text{Gray}} (1,0)",
                       font_size=22, color=TX2_COLOR)
        s2_map = VGroup(s2_i, s2_q).arrange(DOWN, buff=0.15)
        s2_map.next_to(s2_sym, DOWN, buff=0.25)
        self.play(Write(s2_i), run_time=1.2)
        self.wait(0.8)
        self.play(Write(s2_q), run_time=1.2)
        self.wait(0.8)

        s2_bits_vg = VGroup(*[Text(b, font=FONT, font_size=28, color=TX2_COLOR)
                              for b in "0010"])
        s2_bits_vg.arrange(RIGHT, buff=0.08)
        s2_bits_vg.next_to(s2_map, DOWN, buff=0.25)
        s2_label = Text("s2 bits:", font=FONT, font_size=16, color=LABEL_COLOR)
        s2_label.next_to(s2_bits_vg, LEFT, buff=0.2)
        self.play(Write(s2_label), run_time=0.8)
        for bt in s2_bits_vg:
            self.play(FadeIn(bt, scale=1.5), run_time=0.4)
        self.wait(1.5)

        # ── Combined output: all 8 bits ──
        self.play(*[FadeOut(m) for m in self.mobjects
                    if m is not header])
        self.wait(0.5)

        final_label = Text("P/S Converter Restores Serial 8-bit Output:",
                           font=FONT, font_size=22, color=LABEL_COLOR)
        final_label.shift(UP * 0.5)
        out_bits = "10010010"
        out_colors = [TX1_COLOR] * 4 + [TX2_COLOR] * 4
        final_bits = VGroup(*[Text(b, font=FONT, font_size=36, color=c)
                              for b, c in zip(out_bits, out_colors)])
        final_bits.arrange(RIGHT, buff=0.1).next_to(final_label, DOWN, buff=0.3)

        br1 = Brace(VGroup(*final_bits[:4]), DOWN, color=TX1_COLOR, buff=0.05)
        br1_l = Text("s1", font=FONT, font_size=16, color=TX1_COLOR)
        br1_l.next_to(br1, DOWN, buff=0.05)
        br2 = Brace(VGroup(*final_bits[4:]), DOWN, color=TX2_COLOR, buff=0.05)
        br2_l = Text("s2", font=FONT, font_size=16, color=TX2_COLOR)
        br2_l.next_to(br2, DOWN, buff=0.05)

        self.play(Write(final_label), run_time=1.2)
        for bt in final_bits:
            self.play(FadeIn(bt, scale=1.5), run_time=0.35)
        self.wait(0.5)
        self.play(Create(br1), Write(br1_l), Create(br2), Write(br2_l),
                  run_time=1.2)
        self.wait(1)

        done = Text("Transmission Complete! 8 bits recovered.",
                     font=FONT, font_size=26, color=DECISION_COLOR)
        done.to_edge(DOWN, buff=0.4)
        self.play(Write(done), run_time=1.5)
        self.wait(4)
        self.play(*[FadeOut(m) for m in self.mobjects])