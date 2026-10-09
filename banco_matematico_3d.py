  # -*- coding: utf-8 -*-
"""
==============================================================================
 BANCO MATEMÁTICO 3D  -  Feira de Matemática (Visual Premium Neon 30 Casas)
==============================================================================
"""

from ursina import *
from ursina.prefabs.input_field import InputField

import os
import json
import random
import textwrap
import math
import wave
import struct
from functools import partial
from math import sin, cos, pi, sqrt, hypot, radians, exp
from pathlib import Path

from panda3d.core import PNMImage, Texture as PandaTexture, TransparencyAttrib

_SHADER_MODE = os.environ.get('BM3D_SHADER', 'auto').lower()
METAL_SHADER = None
USE_SHADOWS = False
if _SHADER_MODE != 'off':
    try:
        if _SHADER_MODE in ('auto', 'lit'):
            from ursina.shaders import lit_with_shadows_shader as METAL_SHADER
            USE_SHADOWS = True
        else:
            from ursina.shaders import basic_lighting_shader as METAL_SHADER
    except Exception:
        METAL_SHADER = None

CHROME_SHADER = None
if _SHADER_MODE != 'off':
    try:
        from ursina.shaders import matcap_shader as CHROME_SHADER
    except Exception:
        CHROME_SHADER = None

try:
    from questions_by_difficulty import (
        QUESTIONS_BY_DIFFICULTY, DIFFICULTY_LABELS, HOUSE_RULES)
    USANDO_BANCO_EXTERNO = True
except ImportError:
    USANDO_BANCO_EXTERNO = False
    print("ERRO: O arquivo 'questions_by_difficulty.py' não foi encontrado na mesma pasta!")
    sys.exit()

# =============================================================================
# 1. SISTEMA DE LEADERBOARD (RECORDES)
# =============================================================================
LEADERBOARD_FILE = "leaderboard.json"

def load_leaderboard():
    if os.path.exists(LEADERBOARD_FILE):
        try:
            with open(LEADERBOARD_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return []
    return []

def save_scores(players, difficulty):
    """Salva a pontuação de todos os jogadores da partida no leaderboard.json."""
    board = load_leaderboard()
    for p in players:
        name = p["name"] if isinstance(p, dict) and "name" in p else str(p)
        score = p["score"] if isinstance(p, dict) and "score" in p else 0
        board.append({"name": name, "score": score, "difficulty": difficulty})
    # Ordena do maior para o menor e mantém apenas os 10 melhores
    board = sorted(board, key=lambda x: x["score"], reverse=True)[:10]
    with open(LEADERBOARD_FILE, 'w', encoding='utf-8') as f:
        json.dump(board, f, ensure_ascii=False, indent=4)

def save_score(name, score, difficulty):
    save_scores([{"name": name, "score": score}], difficulty)

# =============================================================================
# 2. TEMA VISUAL E CONSTANTES DE LAYOUT (TEMA NEON CYBERPUNK)
# =============================================================================
COLS, ROWS = 10, 7
TILE_GAP_SCALE = 0.92

TILE_H_NORMAL = 0.20
TILE_Y_NORMAL = 0.0
TILE_H_SUNK = 0.10
TILE_Y_SUNK = -0.10 

LABEL_Y_NORMAL = 0.101
LABEL_Y_SUNK = -0.049

STEP_TIME = 0.26
HOP_HEIGHT = 0.55
PAWN_Y = -0.05
PAWN_SCALE = 0.80

MENU3D_POS = Vec3(1.9, 2.15, -1.2)
MENU3D_W, MENU3D_H = 6.6, 6.2

C_BG         = color.hex('#030A14')
C_BOARD      = color.hex('#0F1722')
C_NEON_BLUE  = color.hex('#00E5FF')
C_HUD_BG     = color.hex('#050C14')
C_PANEL_SOFT = color.hex('#122238') 
C_TEXT       = color.hex('#F5F7FA')
C_MUTED      = color.hex('#6A85A3')
C_YELLOW     = color.hex('#FFD700') 
C_GREEN      = color.hex('#00E676')
C_RED        = color.hex('#FF1744')
C_BLUE       = color.hex('#2979FF')
C_PURPLE     = color.hex('#D500F9')
C_START      = color.hex('#FFD700') 
C_GOLD_LUCKY = color.hex('#FFB300') 
C_WOOD       = color.hex('#8B5A2B')
C_WOOD_DARK  = color.hex('#5C3B1E')

# Iluminação do tabuleiro: normal e modo Overdrive (Combo x3)
LIGHT_SUN_NORMAL     = color.rgba(1.0, 0.97, 0.90, 1)
LIGHT_SUN_OVERDRIVE  = color.rgba(0.70, 0.68, 0.62, 1)
LIGHT_FILL_NORMAL    = color.rgba(0.45, 0.60, 0.85, 1)
LIGHT_FILL_OVERDRIVE = color.rgba(0.22, 0.28, 0.42, 1)
LIGHT_AMB_NORMAL     = color.rgba(0.45, 0.50, 0.60, 1)
LIGHT_AMB_OVERDRIVE  = color.rgba(0.20, 0.22, 0.28, 1)

# Ordem dos metais conforme a quantidade de jogadores (estilo pódio):
# 1 jogador = Ouro | 2 = Ouro, Prata | 3 = + Cobre | 4 = + Bronze
PLAYER_METALS = [
    ("Ouro",   color.hex('#FFC940'), '#FFC940'),
    ("Prata",  color.hex('#D9DEE6'), '#D9DEE6'),
    ("Cobre",  color.hex('#E8835E'), '#E8835E'),
    ("Bronze", color.hex('#C89B5A'), '#C89B5A'),
]
PLAYER_HEX = [m[2] for m in PLAYER_METALS]

# Tons usados para gerar o reflexo metálico de cada peça (RGB de 0 a 1):
# sombra = parte escura do metal, base = cor principal, brilho = reflexo da luz
METAL_TONES = {
    "Ouro":   {"sombra": (0.35, 0.20, 0.03), "base": (1.00, 0.76, 0.25), "brilho": (1.00, 0.97, 0.80)},
    "Prata":  {"sombra": (0.28, 0.31, 0.36), "base": (0.80, 0.83, 0.88), "brilho": (1.00, 1.00, 1.00)},
    "Cobre":  {"sombra": (0.30, 0.09, 0.04), "base": (0.86, 0.45, 0.30), "brilho": (1.00, 0.85, 0.75)},
    "Bronze": {"sombra": (0.24, 0.14, 0.05), "base": (0.70, 0.50, 0.25), "brilho": (0.98, 0.88, 0.66)},
}
METAL_TEXTURES = {}

TEXT_ON_METAL = color.rgb32(10, 12, 16)

EFFECT_LABELS = {
    "normal": "",
    "advance": "+2 CASAS",
    "back": "-2 CASAS",
    "skip": "PASSA VEZ",
    "roulette": "ROLETA DA SORTE",
}
EFFECT_SHORT = {
    "advance": "+2\nCASAS",
    "back": "-2\nCASAS",
    "skip": "PASSA\nVEZ",
    "roulette": "ROLETA\nSORTE",
}
DEFAULT_RULE = {"points": 1, "penalty": 1, "effect": "normal"}

def wrap(texto, largura=42):
    return "\n".join(textwrap.fill(linha, largura) for linha in texto.split("\n"))

def normalize(value):
    return value.strip().lower().replace(" ", "")

# =============================================================================
# 2.5. SISTEMA DE EFEITOS SONOROS (SFX)
# =============================================================================
SFX_DIR = "sfx"

def ensure_sfx_files():
    """Gera arquivos de áudio .wav procedurais de alta qualidade caso ainda não existam no disco."""
    try:
        os.makedirs(SFX_DIR, exist_ok=True)
        sr = 44100

        def write_wav(path, samples):
            if os.path.exists(path):
                return
            with wave.open(path, 'w') as f:
                f.setnchannels(1)
                f.setsampwidth(2)
                f.setframerate(sr)
                data = bytearray()
                for s in samples:
                    val = max(-32767, min(32767, int(s * 32767)))
                    data.extend(struct.pack('<h', val))
                f.writeframes(data)

        # 1. dice_roll.wav - estalidos e rolagem de pedra/dado
        p_dice = os.path.join(SFX_DIR, "dice_roll.wav")
        if not os.path.exists(p_dice):
            dur = 0.45
            n = int(sr * dur)
            samples = [0.0] * n
            impacts = [0.00, 0.07, 0.15, 0.22, 0.29, 0.35, 0.39]
            amps = [0.85, 0.70, 0.60, 0.45, 0.35, 0.25, 0.18]
            freqs = [620, 540, 480, 580, 430, 510, 460]
            for imp, amp, f0 in zip(impacts, amps, freqs):
                start = int(imp * sr)
                sub_len = int(sr * 0.055)
                for i in range(min(sub_len, n - start)):
                    t = i / sr
                    env = math.exp(-i / (sr * 0.012))
                    noise = (random.random() * 2 - 1) * 0.45
                    tone = math.sin(2 * math.pi * f0 * t) * 0.55
                    samples[start + i] += (tone + noise) * env * amp
            m = max(abs(s) for s in samples) or 1.0
            write_wav(p_dice, [s / m * 0.9 for s in samples])

        # 2. hop_boing.wav - salto/mola elástica estilo cartoon (boing)
        p_hop = os.path.join(SFX_DIR, "hop_boing.wav")
        if not os.path.exists(p_hop):
            dur = 0.22
            n = int(sr * dur)
            samples = []
            phase = 0.0
            for i in range(n):
                t = i / sr
                k = t / dur
                freq = 170.0 + 360.0 * (k ** 0.8) + 35.0 * math.sin(2 * math.pi * 28.0 * t)
                phase += 2 * math.pi * freq / sr
                env = math.sin(math.pi * min(1.0, k * 3.5)) * math.exp(-t * 9.5)
                w = math.sin(phase) + 0.3 * math.sin(phase * 2) + 0.15 * math.sin(phase * 3)
                samples.append(w * env * 0.85)
            m = max(abs(s) for s in samples) or 1.0
            write_wav(p_hop, [s / m * 0.9 for s in samples])

        # 3. alarm_beep.wav - bipe urgente de alarme nos 5s vermelhos
        p_alarm = os.path.join(SFX_DIR, "alarm_beep.wav")
        if not os.path.exists(p_alarm):
            dur = 0.10
            n = int(sr * dur)
            samples = []
            for i in range(n):
                t = i / sr
                env = 1.0
                if t < 0.006: env = t / 0.006
                elif t > dur - 0.015: env = (dur - t) / 0.015
                tone = 0.65 * math.sin(2 * math.pi * 980 * t) + 0.35 * math.sin(2 * math.pi * 1470 * t)
                samples.append(tone * env * 0.85)
            write_wav(p_alarm, samples)

        # 4. coin_correct.wav - som de comemoração / moeda arcade ao acertar
        p_coin = os.path.join(SFX_DIR, "coin_correct.wav")
        if not os.path.exists(p_coin):
            dur = 0.36
            n = int(sr * dur)
            samples = []
            t_split = 0.08
            for i in range(n):
                t = i / sr
                if t < t_split:
                    f = 987.77  # B5
                    env = math.exp(-t * 3.0)
                else:
                    f = 1318.51 # E6
                    t2 = t - t_split
                    env = math.exp(-t2 * 7.5)
                phase = 2 * math.pi * f * t
                tone = 0.7 * math.sin(phase) + 0.2 * math.sin(phase * 2) + 0.1 * math.sin(phase * 3)
                samples.append(tone * env * 0.88)
            write_wav(p_coin, samples)
    except Exception as e:
        print(f"Aviso ao inicializar SFX: {e}")

# Garante a existência dos arquivos de som na inicialização
ensure_sfx_files()

def play_sfx(name, volume=1.0):
    """Reproduz um efeito sonoro procedural ou personalizado da pasta sfx."""
    try:
        path = os.path.join(SFX_DIR, f"{name}.wav")
        if os.path.exists(path):
            Audio(path, autoplay=True, loop=False, volume=volume)
    except Exception:
        pass

# =============================================================================
# 3. LÓGICA DO JOGO (COM SISTEMA DE COMBO)
# =============================================================================
class GameLogic:
    def __init__(self):
        self.cells = self.create_board_cells()
        self.players = []
        self.current_player = 0
        self.difficulty = "médio"
        self.finished = False
        self.current_question = None
        self.available_questions = {}

    def create_board_cells(self):
        cells = [(col, 0) for col in range(COLS)]
        cells += [(COLS - 1, row) for row in range(1, ROWS)]
        cells += [(col, ROWS - 1) for col in range(COLS - 2, -1, -1)]
        cells += [(0, row) for row in range(ROWS - 2, 0, -1)]
        return cells

    def start_game(self, amount, difficulty, names=None):
        names = names or [f"Jogador {i + 1}" for i in range(amount)]
        self.players = [{"name": names[i] if i < len(names) and names[i] else f"Jogador {i + 1}",
                         "position": 0, "score": 0, "combo": 0, # Adicionado Combo
                         "color": PLAYER_HEX[i], "metal": i,
                         "metal_name": PLAYER_METALS[i][0]}
                        for i in range(amount)]
        self.difficulty = difficulty
        self.finished = False
        self.current_player = 0
        self.current_question = None
        
        import copy
        self.available_questions = copy.deepcopy(QUESTIONS_BY_DIFFICULTY)

    @property
    def player(self):
        return self.players[self.current_player] if self.players else None

    def rule_for(self, index):
        return HOUSE_RULES.get(index, DEFAULT_RULE)

    def roll(self):
        return random.randint(1, 6)

    def step_forward(self, player_index):
        player = self.players[player_index]
        completed = player["position"] == len(self.cells) - 1
        player["position"] = (player["position"] + 1) % len(self.cells)
        return completed

    def step_backward(self, player_index):
        player = self.players[player_index]
        player["position"] = (player["position"] - 1) % len(self.cells)
        return False

    def draw_question(self):
        pool = self.available_questions[self.difficulty]
        if not pool:
            import copy
            self.available_questions[self.difficulty] = copy.deepcopy(QUESTIONS_BY_DIFFICULTY[self.difficulty])
            pool = self.available_questions[self.difficulty]
            
        self.current_question = random.choice(pool)
        pool.remove(self.current_question)
        return self.current_question

    def check_answer(self, text, timeout=False):
        player = self.players[self.current_player]
        rule = self.rule_for(player["position"])
        base_points, penalty = rule["points"], rule["penalty"]
        
        correct = False if timeout else (normalize(text) == normalize(self.current_question["resposta"]))
        
        points_awarded = 0
        if correct:
            player["combo"] += 1
            # Multiplicador máximo de x3
            multiplier = min(3, player["combo"])
            points_awarded = base_points * multiplier
            player["score"] += points_awarded
        else:
            player["combo"] = 0 # Zera o combo ao errar
            player["score"] = max(0, player["score"] - penalty)
            
        return correct, points_awarded, penalty, player["combo"]

    def advance_turn(self):
        self.current_player = (self.current_player + 1) % len(self.players)
        return self.current_player

# =============================================================================
# 4. UTILITÁRIOS 3D E MATERIAIS
# =============================================================================
def solidify(entity):
    entity.set_transparency(TransparencyAttrib.M_none)
    entity.set_bin('opaque', 0)
    entity.set_depth_write(True)
    entity.set_depth_test(True)
    for filho in entity.children:
        solidify(filho)
    return entity

def rounded_cube_mesh(radius=0.06, seg=8):
    h = 0.5 - radius
    eixos = [(Vec3(1, 0, 0), Vec3(0, 0, -1), Vec3(0, 1, 0)),
             (Vec3(-1, 0, 0), Vec3(0, 0, 1), Vec3(0, 1, 0)),
             (Vec3(0, 1, 0), Vec3(1, 0, 0), Vec3(0, 0, 1)),
             (Vec3(0, -1, 0), Vec3(1, 0, 0), Vec3(0, 0, -1)),
             (Vec3(0, 0, 1), Vec3(-1, 0, 0), Vec3(0, 1, 0)),
             (Vec3(0, 0, -1), Vec3(1, 0, 0), Vec3(0, 1, 0))]
    verts, norms, uvs, tris = [], [], [], []
    for (n, u, v) in eixos:
        i0 = len(verts)
        for i in range(seg + 1):
            for j in range(seg + 1):
                a, b = i / seg - 0.5, j / seg - 0.5
                p = n * 0.5 + u * a + v * b
                q = Vec3(max(-h, min(h, p.x)), max(-h, min(h, p.y)), max(-h, min(h, p.z)))
                d = p - q
                nd = d.normalized() if d.length() > 1e-9 else n
                verts.append(q + nd * radius)
                norms.append(nd)
                uvs.append((a + 0.5, b + 0.5))
        w = seg + 1
        for i in range(seg):
            for j in range(seg):
                k = i0 + i * w + j
                tris.append((k, k + w, k + 1)); tris.append((k + 1, k + w, k + w + 1))
    return Mesh(vertices=verts, triangles=tris, normals=norms, uvs=uvs, mode='triangle')

def make_chrome_matcap(size=256):
    img = PNMImage(size, size, 4)
    img.alphaFill(1.0)
    for py in range(size):
        ny = 1.0 - (py + 0.5) / size * 2
        for px in range(size):
            nx = (px + 0.5) / size * 2 - 1
            r = min(1.0, hypot(nx, ny))
            if r < 0.80:
                v = 1.00 - 0.18 * (r / 0.80) ** 1.8
                tint = (0.985, 0.995, 1.00)
            elif r < 0.93:
                t = (r - 0.80) / 0.13
                v = 0.82 - 0.20 * t
                tint = (0.95, 0.975, 1.00)
            elif r < 0.985:
                t = (r - 0.93) / 0.055
                v = 0.62 - 0.10 * t
                tint = (0.94, 0.965, 1.00)
            else:
                t = (r - 0.985) / 0.015
                v = 0.52 + 0.45 * t ** 0.5
                tint = (1.00, 0.99, 0.96)
            key = max(0.0, 1.0 - hypot(nx + 0.30, ny - 0.36) * 1.9) ** 2.0 * 0.45
            fill = max(0.0, 1.0 - hypot(nx - 0.42, ny + 0.30) * 1.6) ** 2.2 * 0.20
            img.setXel(px, py,
                       min(1.0, v * tint[0] + key * 1.00 + fill * 0.80),
                       min(1.0, v * tint[1] + key * 0.98 + fill * 0.90),
                       min(1.0, v * tint[2] + key * 0.92 + fill * 1.00))
    panda_tex = PandaTexture('chrome_matcap')
    panda_tex.load(img)
    panda_tex.set_format(PandaTexture.F_rgba)
    tex = Texture(panda_tex)
    tex.path = Path('chrome_matcap')
    return tex

def make_metal_matcap(nome, tons, size=128):
    """Gera um matcap colorido para um metal: sombras profundas, tom do metal
    nos meios-tons e um reflexo forte e claro, imitando metal polido."""
    sombra, base, brilho = tons["sombra"], tons["base"], tons["brilho"]
    img = PNMImage(size, size, 4)
    img.alphaFill(1.0)
    for py in range(size):
        ny = 1.0 - (py + 0.5) / size * 2
        for px in range(size):
            nx = (px + 0.5) / size * 2 - 1
            r = min(1.0, hypot(nx, ny))
            # luz principal vindo de cima/esquerda, escurecendo nas bordas
            luz = max(0.0, 1.0 - hypot(nx + 0.35, ny - 0.40) * 0.85)
            t = max(0.0, min(1.0, luz * (1.0 - 0.55 * r ** 3)))
            c = [sombra[k] + (base[k] - sombra[k]) * t for k in range(3)]
            # reflexo especular concentrado + reflexo secundário + brilho de borda
            spec = max(0.0, 1.0 - hypot(nx + 0.30, ny - 0.36) * 3.2) ** 2.5
            sec = max(0.0, 1.0 - hypot(nx - 0.45, ny + 0.35) * 2.4) ** 2.0 * 0.35
            borda = (max(0.0, (r - 0.90) / 0.10) ** 2) * 0.30
            mix = min(1.0, spec + sec + borda)
            c = [c[k] + (brilho[k] - c[k]) * mix for k in range(3)]
            img.setXel(px, py, *(min(1.0, max(0.0, v)) for v in c))
    panda_tex = PandaTexture(f'matcap_{nome}')
    panda_tex.load(img)
    panda_tex.set_format(PandaTexture.F_rgba)
    tex = Texture(panda_tex)
    tex.path = Path(f'matcap_{nome}')
    return tex

PAWN_PROFILE = [(0.000, 0.000), (0.300, 0.000), (0.300, 0.045), (0.255, 0.080),
                (0.150, 0.120), (0.112, 0.190), (0.102, 0.270), (0.140, 0.315),
                (0.158, 0.348), (0.132, 0.378), (0.092, 0.408), (0.150, 0.462),
                (0.168, 0.508), (0.150, 0.556), (0.098, 0.596), (0.000, 0.622)]

# Perfil da taça do troféu (torneamento 3D): base, haste com anel, bojo, borda e interior oco
TROPHY_PROFILE = [
    (0.000, 0.000), (0.520, 0.000), (0.520, 0.080), (0.440, 0.120),
    (0.380, 0.200), (0.260, 0.260), (0.140, 0.320), (0.180, 0.420),
    (0.130, 0.520), (0.240, 0.620), (0.420, 0.780), (0.500, 1.000),
    (0.480, 1.150), (0.520, 1.250), (0.460, 1.270), (0.400, 1.220),
    (0.320, 1.050), (0.180, 0.850), (0.000, 0.800)
]
TROPHY_POS = Vec3(-0.75, 0.02, -1.0)  # Posição central nobre, ao lado do logo da UESPI

def lathe_mesh(profile, segments=32):
    verts, norms, uvs, tris = [], [], [], []
    n_ring = len(profile)
    seg_n = []
    for i in range(n_ring - 1):
        dx = profile[i + 1][0] - profile[i][0]
        dy = profile[i + 1][1] - profile[i][1]
        ln = hypot(dx, dy) or 1e-6
        seg_n.append((dy / ln, -dx / ln))
    ring_n = []
    for i in range(n_ring):
        if i == 0:
            a = seg_n[0]
        elif i == n_ring - 1:
            a = seg_n[-1]
        else:
            a = ((seg_n[i - 1][0] + seg_n[i][0]) / 2, (seg_n[i - 1][1] + seg_n[i][1]) / 2)
        ln = hypot(*a) or 1e-6
        ring_n.append((a[0] / ln, a[1] / ln))
    for i, (r, y) in enumerate(profile):
        for j in range(segments + 1):
            ang = j / segments * 2 * pi
            verts.append(Vec3(r * cos(ang), y, r * sin(ang)))
            nr, ny = ring_n[i]
            norms.append(Vec3(nr * cos(ang), ny, nr * sin(ang)).normalized())
            uvs.append((j / segments, i / (n_ring - 1)))
    w = segments + 1
    for i in range(n_ring - 1):
        for j in range(segments):
            a = i * w + j
            tris.append((a, a + w, a + 1))
            tris.append((a + 1, a + w, a + w + 1))
    return Mesh(vertices=verts, triangles=tris, normals=norms, uvs=uvs, mode='triangle')

def low_poly_sphere(lat=5, lon=8):
    """Esfera de raio 0.5 com poucos polígonos (de longe parece uma esfera perfeita)."""
    verts, tris = [], []
    for i in range(lat + 1):
        th = pi * i / lat
        for j in range(lon + 1):
            ph = 2 * pi * j / lon
            verts.append(Vec3(sin(th) * cos(ph), cos(th), sin(th) * sin(ph)) * 0.5)
    w = lon + 1
    for i in range(lat):
        for j in range(lon):
            a = i * w + j
            tris.append((a, a + w, a + 1))
            tris.append((a + 1, a + w, a + w + 1))
    return verts, tris

def particle_field_mesh(particulas):
    """Junta várias esferas [(posição, tamanho, cor), ...] numa única malha."""
    base_v, base_t = low_poly_sphere()
    verts, tris, cols = [], [], []
    for pos, tamanho, cor in particulas:
        o = len(verts)
        verts.extend(pos + v * tamanho for v in base_v)
        tris.extend((a + o, b + o, c + o) for a, b, c in base_t)
        cols.extend([cor] * len(base_v))
    return Mesh(vertices=verts, triangles=tris, colors=cols, mode='triangle')

CHROME_TEX = None
LOGO_TEX = None
try:
    _logo_path = Path(__file__).parent / "uespi_logo.png"
    if _logo_path.exists():
        LOGO_TEX = Texture(_logo_path)
except Exception:
    LOGO_TEX = None

def grid_to_world(col, row, y=0.0):
    return Vec3(col - (COLS - 1) / 2, y, (ROWS - 1) / 2 - row)

def bold_text(texto, position, scale, cor, parent, peso=0.0042):
    x, y, z = position
    for dx, dz in ((peso, 0), (-peso, 0), (0, peso), (0, -peso)):
        Text(text=texto, parent=parent, position=(x + dx, y, z + dz), rotation_x=90,
             origin=(0, 0), scale=scale, color=cor)
    return Text(text=texto, parent=parent, position=position, rotation_x=90,
                origin=(0, 0), scale=scale, color=cor)

def flat_text(text, position, scale=6, color_=C_TEXT, parent=scene, **kwargs):
    return Text(text=text, parent=parent, position=position, rotation_x=90,
                origin=(0, 0), scale=scale, color=color_, **kwargs)

class Tile(Button):
    def __init__(self, index, grid_pos, rule, total, on_inspect=None):
        col, row = grid_pos
        self.index = index
        self.rule = rule
        self.grid_pos = grid_pos
        self.on_inspect = on_inspect
        self.sunk = False

        effect = rule["effect"]
        
        # Mapeamento de Cores NEON Original (por quadrante)
        if index == 0:
            base = C_START
        elif effect == "advance":
            base = C_GREEN
        elif effect == "back":
            base = C_RED
        elif effect == "skip":
            base = C_PURPLE
        elif effect == "roulette":
            base = C_GOLD_LUCKY
        else:
            if index < 10:
                base = color.hsv(5 + (index * 4), 0.85, 0.95)
            elif index < 16:
                base = color.hsv(110 + (index - 10) * 8, 0.85, 0.95)
            elif index < 25:
                base = color.hsv(195 + (index - 16) * 5, 0.85, 0.95)
            else:
                base = color.hsv(280 + (index - 25) * 12, 0.85, 0.95)
            
        self.base_color = base

        super().__init__(
            parent=scene,
            model=rounded_cube_mesh(radius=0.06, seg=8),
            texture='white_cube',
            color=self.base_color,
            highlight_color=self.base_color.tint(0.20),
            pressed_color=self.base_color.tint(-0.15),
            collider='box',
            double_sided=True,
            shader=METAL_SHADER,
            position=grid_to_world(col, row, TILE_Y_NORMAL),
            scale=(TILE_GAP_SCALE, TILE_H_NORMAL, TILE_GAP_SCALE),
        )
        solidify(self)

        wp = grid_to_world(col, row, LABEL_Y_NORMAL)
        self.labels = Entity(parent=scene, position=wp)
        self._build_labels()

    def _build_labels(self):
        if self.index == 0:
            bold_text("INÍCIO", (0, 0, 0.24), 7.0, TEXT_ON_METAL, self.labels)
            bold_text("CHEGADA", (0, 0, -0.24), 6.2, TEXT_ON_METAL, self.labels)
            return

        bold_text(str(self.index + 1), (0, 0, 0.29), 9.5, TEXT_ON_METAL, self.labels)

        if self.rule["effect"] == "roulette":
            bold_text("ROLETA", (0, 0, 0.08), 6.4, TEXT_ON_METAL, self.labels)
            bold_text("DA SORTE", (0, 0, -0.09), 5.3, TEXT_ON_METAL, self.labels)
            bold_text("+10 / -5", (0, 0, -0.28), 5.6, TEXT_ON_METAL, self.labels, peso=0.0028)
        elif self.rule["effect"] != "normal":
            bold_text(EFFECT_SHORT[self.rule["effect"]], (0, 0, -0.10), 6.4,
                      TEXT_ON_METAL, self.labels)
        else:
            # Mantendo os grandiosos símbolos matemáticos originais como decoração
            simbolo = ["?", "+", "x", "%", "÷"][self.index % 5]
            bold_text(simbolo, (0, 0, -0.02), 11.0, TEXT_ON_METAL, self.labels)
            bold_text(f"+{self.rule['points']} pt", (0, 0, -0.32), 5.6,
                      TEXT_ON_METAL, self.labels, peso=0.0028)

    def sink(self):
        if self.sunk: return
        self.sunk = True
        self.animate('scale_y', TILE_H_SUNK, duration=0.25, curve=curve.out_expo)
        self.animate_y(TILE_Y_SUNK, duration=0.25, curve=curve.out_expo)
        self.labels.animate_y(LABEL_Y_SUNK, duration=0.25, curve=curve.out_expo)

    def rise(self):
        if not self.sunk: return
        self.sunk = False
        self.animate('scale_y', TILE_H_NORMAL, duration=0.35, curve=curve.out_back)
        self.animate_y(TILE_Y_NORMAL, duration=0.35, curve=curve.out_back)
        self.labels.animate_y(LABEL_Y_NORMAL, duration=0.35, curve=curve.out_back)

    def on_click(self):
        if self.on_inspect:
            self.on_inspect(self)

    def reset_visual(self):
        """Restaura a cor e brilho originais da casa."""
        self.color = self.base_color
        self.default_color = self.base_color
        self.highlight_color = self.base_color.tint(0.20)

    def set_dimmed(self, factor=0.50):
        """Escurece a casa proporcionalmente durante o modo Overdrive."""
        c = self.base_color.tint(-factor)
        self.color = c
        self.default_color = c
        self.highlight_color = self.base_color.tint(-factor * 0.5)

    def set_fire_pulse(self, pulse_color):
        """Aplica a cor pulsante 'on fire' na casa do jogador em Overdrive."""
        self.color = pulse_color
        self.default_color = pulse_color
        self.highlight_color = pulse_color

class PlayerPawn(Entity):
    def __init__(self, player_index, start_position):
        super().__init__(parent=scene, position=start_position)
        self.player_index = player_index
        self.base_y = start_position.y
        nome, metal, metal_hex = PLAYER_METALS[player_index]
        self.metal_name = nome

        # Prioridade: matcap do próprio metal > matcap cromado tingido > iluminação simples
        metal_tex = METAL_TEXTURES.get(nome)
        if metal_tex is not None:
            tex, shd, cor = metal_tex, CHROME_SHADER, color.white
        elif CHROME_TEX:
            tex, shd, cor = CHROME_TEX, CHROME_SHADER, metal
        else:
            tex, shd, cor = 'white_cube', METAL_SHADER, metal

        self.body = Entity(parent=self, model=lathe_mesh(PAWN_PROFILE),
                           texture=tex, shader=shd,
                           color=cor, scale=PAWN_SCALE, double_sided=True)
        self.ring = Entity(parent=self, model=rounded_cube_mesh(radius=0.1, seg=6),
                           texture=tex, shader=shd,
                           color=cor.tint(-0.25), scale=(0.60, 0.035, 0.60),
                           y=0.012, double_sided=True, enabled=False)
        self.number = Text(text=str(player_index + 1), parent=self, billboard=True,
                           position=(0, PAWN_SCALE * 0.62 + 0.16, 0), origin=(0, 0),
                           scale=6.5, color=color.hex(metal_hex))
        solidify(self.body)
        solidify(self.ring)

    def hop_to(self, target, instant=False, duration=STEP_TIME):
        """Pula até 'target' num arco. Feito quadro a quadro em update(), porque no
        Ursina 8 duas chamadas de animate_y seguidas se cancelam (a 2ª mata a 1ª)."""
        self.base_y = target.y
        destino = Vec3(target)
        atual = getattr(self, "_hop", None)
        if not instant and atual and (atual[1] - destino).length() < 0.01:
            return  # já está pulando para esse mesmo lugar
        if instant or (destino - self.position).length() < 0.01:
            self._hop = None
            self.position = destino
            return
        play_sfx('hop_boing', volume=0.75)
        self._hop = [Vec3(self.position), destino, max(0.01, duration), 0.0]

    def update(self):
        hop = getattr(self, "_hop", None)
        if not hop:
            return
        inicio, fim, duracao, t = hop
        t += time.dt
        k = min(1.0, t / duracao)
        suave = k * k * (3 - 2 * k)               # acelera e freia no chão
        pos = inicio + (fim - inicio) * suave
        pos.y += sin(pi * k) * HOP_HEIGHT         # arco do pulo
        self.position = pos
        if k >= 1.0:
            self.position = fim
            self._hop = None
        else:
            hop[3] = t

    def set_active(self, active):
        self.ring.enabled = active
        self.body.animate_scale(PAWN_SCALE * (1.08 if active else 1.0),
                                duration=0.25, curve=curve.out_expo)

class ConfettiCube(Entity):
    """Cubinho de celebração: sai disparado, cai com gravidade, gira e some."""
    GRAVIDADE = 9.8

    def __init__(self, origem, velocidade, cor, duracao=0.5):
        tamanho = random.uniform(0.06, 0.11)
        super().__init__(parent=scene, model='cube', color=cor, unlit=True,
                         position=origem, scale=tamanho,
                         rotation=Vec3(random.uniform(0, 360), random.uniform(0, 360), random.uniform(0, 360)))
        self.vel = Vec3(velocidade)
        self.giro = Vec3(random.uniform(-720, 720), random.uniform(-720, 720), random.uniform(-720, 720))
        self.tamanho_inicial = tamanho
        self.duracao = duracao
        self.tempo = 0.0

    def update(self):
        dt = time.dt
        self.tempo += dt
        if self.tempo >= self.duracao:
            destroy(self)
            return
        self.vel.y -= self.GRAVIDADE * dt
        self.position += self.vel * dt
        self.rotation += self.giro * dt
        restante = 1.0 - self.tempo / self.duracao
        self.scale = self.tamanho_inicial * (restante ** 0.5)  # encolhe mais rápido no final

class Trophy3D(Entity):
    """Grande troféu metálico 3D torneado (lathe_mesh) que se ergue no centro do tabuleiro."""
    def __init__(self, position, winner_name="CAMPEÃO", winner_color=None, scale=1.45):
        self.final_pos = Vec3(position)
        self.final_y = position.y
        # Inicia abaixo do tampo da mesa para animação de erguer-se
        start_pos = Vec3(position.x, position.y - 2.8, position.z)
        super().__init__(parent=scene, position=start_pos, scale=scale)

        # Texturas metálicas / cromadas consistentes com as peças
        gold_tex = METAL_TEXTURES.get("Ouro") or CHROME_TEX or 'white_cube'
        shd = CHROME_SHADER if (gold_tex != 'white_cube') else METAL_SHADER
        cor_trofeu = color.white if (gold_tex != 'white_cube') else color.hex('#FFD700')
        cor_detalhe = color.hex(winner_color) if winner_color else color.hex('#FFD700')

        # 1. Base / Pedestal pesado em mármore escuro com chanfro
        self.pedestal = Entity(parent=self, model=rounded_cube_mesh(radius=0.08, seg=6),
                               color=color.hex('#0B1017'), texture='white_cube',
                               shader=METAL_SHADER, scale=(1.15, 0.22, 1.15),
                               position=(0, 0.11, 0))

        # Placa comemorativa na frente do pedestal
        Entity(parent=self.pedestal, model='quad', color=cor_detalhe,
               position=(0, 0.0, 0.51), scale=(0.82, 0.60), unlit=True)
        Text("CAMPEÃO", parent=self.pedestal, position=(0, 0.02, 0.52),
             scale=3.8, color=color.black, origin=(0, 0), billboard=False)

        # 2. Taça principal torneada com lathe_mesh
        self.cup = Entity(parent=self, model=lathe_mesh(TROPHY_PROFILE, segments=36),
                          texture=gold_tex, shader=shd, color=cor_trofeu,
                          position=(0, 0.22, 0), double_sided=True)

        # 3. Asas / Alças laterais da taça em metal polido
        handle_cyl = Cylinder(resolution=10)
        for side in (-1, 1):
            Entity(parent=self, model=handle_cyl, texture=gold_tex, shader=shd, color=cor_trofeu,
                   position=(side * 0.44, 1.32, 0), rotation_z=side * 70, scale=(0.065, 0.26, 0.065))
            Entity(parent=self, model=handle_cyl, texture=gold_tex, shader=shd, color=cor_trofeu,
                   position=(side * 0.58, 1.14, 0), rotation_z=0, scale=(0.065, 0.32, 0.065))
            Entity(parent=self, model=handle_cyl, texture=gold_tex, shader=shd, color=cor_trofeu,
                   position=(side * 0.42, 0.95, 0), rotation_z=-side * 65, scale=(0.065, 0.26, 0.065))

        # 4. Joia / Estrela da vitória flutuando no topo da taça
        self.star = Entity(parent=self, model='sphere', color=C_YELLOW, unlit=True,
                           scale=0.20, position=(0, 1.55, 0))
        self.halo = Entity(parent=self, model='circle', color=cor_detalhe, unlit=True,
                           scale=0.36, position=(0, 1.55, 0), double_sided=True)

        solidify(self)
        self.spinning = False

    def rise(self, on_finish=None):
        """Ergue o troféu no centro do tabuleiro com giro triunfal."""
        self.animate_y(self.final_y, duration=1.6, curve=curve.out_expo)
        self.animate_rotation_y(720, duration=2.2, curve=curve.out_expo)
        invoke(self._start_spin, delay=1.8)
        if on_finish:
            invoke(on_finish, delay=1.6)

    def _start_spin(self):
        self.spinning = True

    def update(self):
        if getattr(self, 'spinning', False):
            self.rotation_y += 32 * time.dt
            if hasattr(self, 'halo'):
                self.halo.rotation_x += 65 * time.dt

DIE_FACES = {
    1: (Vec3(0, 1, 0), Vec3(1, 0, 0), Vec3(0, 0, 1)),
    6: (Vec3(0, -1, 0), Vec3(1, 0, 0), Vec3(0, 0, -1)),
    3: (Vec3(1, 0, 0), Vec3(0, 0, -1), Vec3(0, 1, 0)),
    4: (Vec3(-1, 0, 0), Vec3(0, 0, 1), Vec3(0, 1, 0)),
    2: (Vec3(0, 0, -1), Vec3(1, 0, 0), Vec3(0, 1, 0)),
    5: (Vec3(0, 0, 1), Vec3(-1, 0, 0), Vec3(0, 1, 0)),
}
PIP_LAYOUT = {
    1: [(0, 0)],
    2: [(-0.20, -0.20), (0.20, 0.20)],
    3: [(-0.21, -0.21), (0, 0), (0.21, 0.21)],
    4: [(-0.20, -0.20), (-0.20, 0.20), (0.20, -0.20), (0.20, 0.20)],
    5: [(-0.21, -0.21), (-0.21, 0.21), (0, 0), (0.21, -0.21), (0.21, 0.21)],
    6: [(-0.21, -0.24), (-0.21, 0), (-0.21, 0.24), (0.21, -0.24), (0.21, 0), (0.21, 0.24)],
}

class Dice3D(Entity):
    def __init__(self, position, tamanho=0.72):
        super().__init__(parent=scene, position=position)
        self.base_y = position.y
        tex = CHROME_TEX if CHROME_TEX else 'white_cube'
        shd = CHROME_SHADER if CHROME_TEX else METAL_SHADER

        self.cube = Entity(parent=self, model=rounded_cube_mesh(radius=0.17, seg=9),
                           texture=tex, shader=shd, color=color.hsv(212, 0.05, 1.0),
                           scale=tamanho, double_sided=True)
        cor_pino = color.rgb32(20, 23, 30)
        for valor, (n, u, v) in DIE_FACES.items():
            for (a, b) in PIP_LAYOUT[valor]:
                p = n * 0.47 + u * a + v * b
                Entity(parent=self.cube, model='sphere', texture=tex, shader=shd,
                       color=cor_pino, scale=0.15, position=p)
        solidify(self)

        self.face_rotations = self._mapear_faces()
        self.value = 6
        self.rotation = self.face_rotations[self.value]

    def _mapear_faces(self):
        candidatos = [Vec3(0, 0, 0), Vec3(180, 0, 0), Vec3(0, 0, 90),
                      Vec3(0, 0, -90), Vec3(90, 0, 0), Vec3(-90, 0, 0)]
        guardada, mapa = self.rotation, {}
        for c in candidatos:
            self.rotation = c
            m = self.get_mat(scene)
            for valor, (n, _, _) in DIE_FACES.items():
                if valor in mapa: continue
                w = m.xform_vec(Vec3(n))
                if w[1] > 0.9: mapa[valor] = c
        self.rotation = guardada
        for valor in DIE_FACES: mapa.setdefault(valor, Vec3(0, 0, 0))
        return mapa

    def set_value(self, valor):
        self.value = valor
        self.rotation = self.face_rotations[valor]

    def roll_to(self, valor, on_done=None, duration=1.05):
        play_sfx('dice_roll', volume=0.85)
        alvo = self.face_rotations[valor]
        giro = Vec3(alvo.x + 360 * 2, alvo.y + 360 * 3, alvo.z + 360)
        self.animate_rotation(giro, duration=duration, curve=curve.out_expo)
        self.animate_y(self.base_y + 0.6, duration=duration * 0.35, curve=curve.out_sine)
        self.animate_y(self.base_y, duration=duration * 0.65, delay=duration * 0.35, curve=curve.in_sine)
        self.value = valor
        invoke(self.set_value, valor, delay=duration + 0.02)
        if on_done: invoke(on_done, delay=duration + 0.12)

class HUD:
    def __init__(self, game):
        self.game = game
        self.root = Entity(parent=camera.ui)

        Entity(parent=self.root, model='quad', color=C_NEON_BLUE, scale=(0.428, 0.94), position=(0.66, 0.0), z=1.15)
        self.panel = Entity(parent=self.root, model='quad', color=C_HUD_BG, scale=(0.42, 0.932), position=(0.66, 0.0), z=1.1)
        
        self.turn_text = Text("CONFIGURANDO PARTIDA", parent=self.root, origin=(0, 0),
                              position=(0.66, 0.42), scale=1.15, color=C_YELLOW)
        self.dice_text = Text("DADO: -", parent=self.root, origin=(0, 0),
                              position=(0.66, 0.36), scale=1.0, color=C_TEXT)

        Text("PLACAR", parent=self.root, position=(0.48, 0.30), scale=0.95, color=C_YELLOW)
        self.score_text = Text(" ", parent=self.root, position=(0.48, 0.265),
                               scale=0.8, color=C_TEXT, line_height=1.35)

        self.difficulty_text = Text("Dificuldade: -", parent=self.root,
                                    position=(0.48, 0.01), scale=0.8, color=C_NEON_BLUE)

        Text("COMO JOGAR", parent=self.root, position=(0.48, -0.04), scale=0.95, color=C_YELLOW)
        Text(wrap("Na sua vez, role o dado. Responder em sequência gera Combo de Pontos! "
                  "Se apresse: Você tem 30s (ou 45s no Difícil) para resolver.", 42),
             parent=self.root, position=(0.48, -0.075), scale=0.68, color=C_MUTED, line_height=1.25)

        self.message_text = Text("Escolha a quantidade de jogadores.", parent=self.root,
                                 position=(0.48, -0.20), scale=0.72, color=C_TEXT, line_height=1.3)

        self.roll_button = Button(text="ROLAR O DADO", parent=self.root,
                                  color=C_YELLOW, text_color=color.hex('#000000'),
                                  scale=(0.34, 0.075), position=(0.66, -0.28),
                                  radius=0.15, on_click=self.game.roll_dice)
        
        self.leaderboard_btn = Button(text="VER RECORDES", parent=self.root,
                                      color=C_NEON_BLUE, text_color=color.hex('#000000'),
                                      scale=(0.34, 0.06), position=(0.66, -0.36),
                                      radius=0.15, on_click=self.game.show_leaderboard)

        self.new_button = Button(text="NOVA PARTIDA", parent=self.root,
                                 color=C_PANEL_SOFT, text_color=C_TEXT,
                                 scale=(0.34, 0.06), position=(0.66, -0.43),
                                 radius=0.15, on_click=self.game.show_player_menu)

    def message(self, text):
        self.message_text.text = wrap(text, 40)

    def set_roll_enabled(self, enabled, text="ROLAR O DADO", btn_color=None):
        self.roll_button.disabled = not enabled
        self.roll_button.text = text
        if btn_color:
            self.roll_button.color = btn_color if enabled else color.rgba32(120, 130, 140, 200)
        else:
            self.roll_button.color = C_YELLOW if enabled else color.rgba32(120, 130, 140, 200)

    def refresh(self):
        logic = self.game.logic
        if logic.players:
            p = logic.player
            is_overdrive = p.get('combo', 0) >= 3
            if is_overdrive:
                self.turn_text.text = f"🔥 VEZ DE {p['name'].upper()} (OVERDRIVE x3) 🔥"
                self.turn_text.color = color.hex('#FF6D00')
            else:
                self.turn_text.text = f"VEZ DE {p['name'].upper()}"
                self.turn_text.color = color.hex(p["color"])

            linhas = []
            for i, pl in enumerate(logic.players):
                marca = ">" if i == logic.current_player else " "
                combo_val = pl.get('combo', 0)
                if combo_val >= 3:
                    combo_str = " [🔥 OVERDRIVE x3!]"
                elif combo_val > 1:
                    combo_str = f" [Combo x{combo_val}]"
                else:
                    combo_str = ""
                linhas.append(f"{marca} {pl['name']}  -  casa {pl['position'] + 1}  -  {pl['score']} pt{combo_str}")
            self.score_text.text = "\n".join(linhas)
        self.difficulty_text.text = f"Dificuldade: {logic.difficulty.upper()}"

class QuestionPanel(Entity):
    def __init__(self, game):
        super().__init__(parent=camera.ui, enabled=False, z=-3)
        self.game = game
        self.answered = False
        self.total_time = 30.0
        self.time_left = 30.0

        Entity(parent=self, model='quad', color=color.rgba32(4, 10, 20, 200), scale=(2.2, 1.2), z=1)
        
        Entity(parent=self, model='quad', color=C_NEON_BLUE, scale=(1.01, 0.70), z=0.55)
        Entity(parent=self, model='quad', color=C_HUD_BG, scale=(1.0, 0.69), z=0.5)

        self.header = Text("", parent=self, origin=(0, 0), position=(0, 0.28), scale=1.05, color=C_YELLOW)
        self.rule_text = Text("", parent=self, origin=(0, 0), position=(0, 0.21), scale=0.82, color=C_MUTED)
        self.question_text = Text(" ", parent=self, origin=(0, 0), position=(0, 0.11), scale=1.52, color=C_TEXT)
        Text("Digite a resposta e pressione ENTER", parent=self, origin=(0, 0), position=(0, 0.026), scale=0.72, color=C_MUTED)
        
        # Campo de resposta
        self.field = InputField(parent=self, default_value="", character_limit=24, position=(0, -0.042), scale=(0.55, 0.068))
        self.field.color = C_PANEL_SOFT
        self.field.text_color = C_TEXT
        self.field.on_submit = self.submit
        
        # BARRA DE TEMPO: Localizada diretamente abaixo do campo de resposta
        # Começa 100% verde e muda gradualmente para amarelo e depois vermelho conforme desce
        self.bar_width = 0.55
        self.timer_bg = Entity(parent=self, model='quad', color=C_PANEL_SOFT, scale=(self.bar_width, 0.020),
                               position=(0, -0.096), z=0.45)
        self.timer_bar = Entity(parent=self, model='quad', color=C_GREEN, origin=(-0.5, 0),
                                scale=(self.bar_width, 0.020), position=(-self.bar_width / 2, -0.096), z=0.40)
        
        # Indicador numérico do tempo restante
        self.timer_text = Text("", parent=self, origin=(0, 0), position=(0, -0.124), scale=0.82, color=C_TEXT)

        # Mensagem de feedback (acerto/erro/dica/timeout)
        self.feedback = Text(" ", parent=self, origin=(0, 0), position=(0, -0.165), scale=0.82, color=C_MUTED, line_height=1.25)
        
        # Botão de confirmação / avançar
        self.button = Button(text="CONFERIR RESPOSTA", parent=self, color=C_GREEN, text_color=color.hex('#000000'), 
                             radius=0.15, scale=(0.42, 0.072), position=(0, -0.250), on_click=self.submit)

    @staticmethod
    def get_timer_color(pct):
        """
        Calcula a cor da barra de tempo:
        - 100% a 50%: Completamente verde (C_GREEN) transicionando suavemente para amarelo (C_YELLOW).
        - 50% a 0%: Transita suavemente de amarelo (C_YELLOW) para vermelho puro (C_RED) conforme a barra desce.
        """
        pct = max(0.0, min(1.0, pct))
        if pct >= 0.5:
            t = (pct - 0.5) / 0.5
            r = C_YELLOW[0] + (C_GREEN[0] - C_YELLOW[0]) * t
            g = C_YELLOW[1] + (C_GREEN[1] - C_YELLOW[1]) * t
            b = C_YELLOW[2] + (C_GREEN[2] - C_YELLOW[2]) * t
            return color.rgba(r, g, b, 1.0)
        else:
            t = pct / 0.5
            r = C_RED[0] + (C_YELLOW[0] - C_RED[0]) * t
            g = C_RED[1] + (C_YELLOW[1] - C_RED[1]) * t
            b = C_RED[2] + (C_YELLOW[2] - C_RED[2]) * t
            return color.rgba(r, g, b, 1.0)

    @property
    def active(self):
        return self.enabled

    def open(self, question, player, rule):
        self.answered = False
        
        # Tempo de resposta: 30 segundos para Fácil e Médio; 45 segundos para Difícil
        diff = str(self.game.logic.difficulty).lower()
        self.total_time = 45.0 if ("dif" in diff) else 30.0
        self.time_left = self.total_time
        self.last_beep_second = None
        
        # Barra inicia cheia (escala total) e completamente verde
        self.timer_bar.scale_x = self.bar_width
        self.timer_bar.color = C_GREEN
        self.timer_text.text = f"Tempo restante: {int(self.total_time)}s"
        self.timer_text.color = C_TEXT
        
        mult = min(3, player['combo'] + 1)
        if player['combo'] >= 2:
            combo_txt = f" (🔥 Combo x{mult} - MODO OVERDRIVE!)"
        elif player['combo'] > 0:
            combo_txt = f" (Combo x{mult} ativado!)"
        else:
            combo_txt = ""

        self.header.text = f"{player['name'].upper()}  -  {question['tipo']}{combo_txt}"
        self.header.color = color.hex(player["color"])
        
        texto = f"Base: +{rule['points']} pt   |   Errar: -{rule['penalty']} pt (Zera Combo)"
        if EFFECT_LABELS[rule["effect"]]: texto += f"   |   Efeito: {EFFECT_LABELS[rule['effect']]}"
        self.rule_text.text = texto
        
        self.question_text.text = wrap(question["pergunta"], 46)
        self.feedback.text = ""
        self.field.text = ""
        self.button.text = "CONFERIR RESPOSTA"
        self.button.color = C_GREEN
        self.button.on_click = self.submit
        self.enabled = True
        self.field.active = True

    def update(self):
        if not self.enabled or self.answered: return
        self.time_left -= time.dt
        pct = max(0.0, min(1.0, self.time_left / self.total_time))
        self.timer_bar.scale_x = max(0.0001, pct * self.bar_width)
        
        # Cor dinâmica: Verde -> Amarelo -> Vermelho conforme a barra desce
        self.timer_bar.color = self.get_timer_color(pct)
        
        seg = max(0, int(math.ceil(self.time_left)))
        self.timer_text.text = f"Tempo restante: {seg}s"
        if pct <= 0.2:
            self.timer_text.color = C_RED
        elif pct <= 0.5:
            self.timer_text.color = C_YELLOW
        else:
            self.timer_text.color = C_TEXT

        # Bipe de alarme a cada segundo nos 5 segundos finais (zona vermelha)
        if 0 < self.time_left <= 5.0:
            sec = int(self.time_left)
            if sec != getattr(self, 'last_beep_second', None):
                self.last_beep_second = sec
                play_sfx('alarm_beep', volume=0.90)

        if self.time_left <= 0:
            self.time_left = 0
            self.timer_bar.scale_x = 0.0001
            self.timer_text.text = "Tempo esgotado!"
            self.timer_text.color = C_RED
            self.submit(timeout=True)

    def submit(self, timeout=False):
        if self.answered: return
        # Se não for timeout e o campo estiver vazio, não faz nada
        if not timeout and not self.field.text.strip(): return
        
        correct, points, penalty, combo = self.game.logic.check_answer(self.field.text, timeout=timeout)
        
        if timeout:
            self.feedback.text = f"Tempo Esgotado! (-{penalty} ponto(s))"
            self.feedback.color = C_RED
            self.game.hud.message(f"O tempo de {self.game.logic.player['name']} acabou! Penalidade: -{penalty}. Combo zerado.")
        elif correct:
            play_sfx('coin_correct', volume=0.90)
            msg = f"Correto! Você ganhou +{points} ponto(s)."
            if combo >= 3:
                msg += " 🔥 MODO OVERDRIVE ATIVADO! (Combo x3) 🔥"
                self.game.hud.message(f"🔥 {self.game.logic.player['name']} ATINGIU O MODO OVERDRIVE (Combo x3)! TABULEIRO ON FIRE! 🔥")
            elif combo > 1:
                msg += f" (Combo x{min(3, combo)})"
                self.game.hud.message(f"{self.game.logic.player['name']} acertou! +{points} ponto(s).")
            else:
                self.game.hud.message(f"{self.game.logic.player['name']} acertou! +{points} ponto(s).")
            self.feedback.text = msg
            self.feedback.color = C_GREEN
        else:
            dica = self.game.logic.current_question["dica"]
            self.feedback.text = wrap(f"Resposta incorreta. (-{penalty} ponto(s))\nDica: {dica}", 64)
            self.feedback.color = C_RED
            self.game.hud.message(f"{self.game.logic.player['name']} errou. Penalidade: -{penalty}. Combo zerado.")
            
        self.answered = True
        self.last_correct = correct
        self.field.active = False
        self.timer_text.text = ""
        self.button.text = "PRÓXIMO JOGADOR"
        self.button.color = C_NEON_BLUE
        self.button.on_click = self.close_and_continue
        self.game.hud.refresh()

    def close_and_continue(self):
        self.enabled = False
        self.field.active = False
        # O painel escurece a tela, então a explosão é disparada quando ele fecha,
        # para o jogador ver os cubinhos saindo do peão.
        if getattr(self, "last_correct", False):
            self.last_correct = False
            self.game.celebrate(self.game.logic.current_player)
            invoke(self._next_after_celebration, self.game.logic.players, delay=0.6)
        else:
            self.game.next_turn()

    def _next_after_celebration(self, players_ref):
        # Só passa a vez se ainda for a mesma partida e nenhum menu foi aberto
        if self.game.logic.players is players_ref and not self.game.menu.root.enabled:
            self.game.next_turn()

class LeaderboardPanel:
    def __init__(self, game):
        self.game = game
        self.root = Entity(parent=camera.ui, enabled=False, z=-6)
        
        Entity(parent=self.root, model='quad', color=color.rgba32(4, 10, 20, 220), scale=(2.2, 1.2), z=1)
        Entity(parent=self.root, model='quad', color=C_YELLOW, scale=(0.87, 0.77), z=0.55)
        Entity(parent=self.root, model='quad', color=C_HUD_BG, scale=(0.86, 0.76), z=0.5)

        Text("TOP 10 RECORDES", parent=self.root, origin=(0, 0), position=(0, 0.32), scale=1.8, color=C_YELLOW)
        
        self.entries_root = Entity(parent=self.root)
        
        Button(text="FECHAR", parent=self.root, color=C_PANEL_SOFT, text_color=C_TEXT, 
               radius=0.15, scale=(0.42, 0.07), position=(0, -0.32, 0.4), on_click=self.hide)

    def show(self):
        destroy(self.entries_root)
        self.entries_root = Entity(parent=self.root)
        
        board = load_leaderboard()
        if not board:
            Text("Nenhum recorde registrado ainda.", parent=self.entries_root, origin=(0,0), position=(0,0), color=C_MUTED)
        else:
            y_start = 0.20
            step = 0.055
            for i, entry in enumerate(board):
                cor = C_YELLOW if i == 0 else (C_TEXT if i < 3 else C_MUTED)
                linha = f"{i+1}º   {entry['name'][:18].ljust(18)}  {str(entry['score']).rjust(3)} pts  ({entry['difficulty']})"
                Text(linha, parent=self.entries_root, origin=(0, 0), position=(0, y_start - i*step), color=cor, scale=0.82)
                
        self.root.enabled = True

    def hide(self):
        self.root.enabled = False

class MenuOverlay:
    def __init__(self, game):
        self.game = game
        self.root = Entity(parent=camera.ui, enabled=False, z=-4)

        # Fundo escurecido suave para focar no menu
        Entity(parent=self.root, model='quad', color=color.rgba32(4, 10, 20, 200), scale=(2.2, 1.5), z=1)

        # Moldura e fundo do painel perfeitamente proporcionais (sem zoom ou distorção)
        self.panel_border = Entity(parent=self.root, model='quad', color=C_NEON_BLUE, scale=(0.60, 0.74), z=0.55)
        self.panel_bg = Entity(parent=self.root, model='quad', color=C_HUD_BG, scale=(0.588, 0.728), z=0.5)

        self.title = Text("", parent=self.root, origin=(0, 0), position=(0, 0.27), scale=1.50, color=C_YELLOW)
        self.subtitle = Text("", parent=self.root, origin=(0, 0), position=(0, 0.21), scale=0.76, color=C_MUTED)
        self.buttons = []

    def _clear(self):
        for b in self.buttons: destroy(b)
        self.buttons = []

    def show(self, title, subtitle, options):
        self._clear()
        self.title.text = title
        self.subtitle.text = subtitle

        n = len(options)
        panel_h = 0.72 if n >= 4 else 0.62
        self.panel_border.scale_y = panel_h
        self.panel_bg.scale_y = panel_h - 0.012

        top = 0.12 if n >= 4 else 0.08
        step = 0.092
        for i, (label, callback) in enumerate(options):
            b = Button(text=label, parent=self.root, color=C_PANEL_SOFT, text_color=C_TEXT,
                       radius=0.15, scale=(0.42, 0.072), position=(0, top - i * step), on_click=callback, z=0.2)
            self.buttons.append(b)
        self.root.enabled = True

    def hide(self):
        self.root.enabled = False

class NamesPanel3D:
    def __init__(self, game):
        self.game = game
        self.root = Entity(parent=camera.ui, enabled=False, z=-4)

        Entity(parent=self.root, model='quad', color=color.rgba32(4, 10, 20, 200), scale=(2.2, 1.5), z=1)
        self.panel_border = Entity(parent=self.root, model='quad', color=C_NEON_BLUE, scale=(0.68, 0.80), z=0.55)
        self.panel_bg = Entity(parent=self.root, model='quad', color=C_HUD_BG, scale=(0.668, 0.788), z=0.5)

        self.title = Text("NOMES DOS JOGADORES", parent=self.root, origin=(0, 0), position=(0, 0.31), scale=1.50, color=C_YELLOW)
        self.subtitle = Text("Digite o nome de cada jogador (ou deixe em branco)", parent=self.root, origin=(0, 0),
                             position=(0, 0.25), scale=0.75, color=C_MUTED)

        self.labels = []
        self.fields = []
        self.continue_button = None

    def _clear_fields(self):
        for l in self.labels: destroy(l)
        for f in self.fields: destroy(f)
        if self.continue_button: destroy(self.continue_button)
        self.labels, self.fields, self.continue_button = [], [], None

    def show(self, amount, on_continue):
        self._clear_fields()
        top = 0.15
        step = 0.11

        panel_h = max(0.56, 0.38 + amount * step)
        self.panel_border.scale_y = panel_h
        self.panel_bg.scale_y = panel_h - 0.012

        for i in range(amount):
            metal_hex = PLAYER_HEX[i]
            self.labels.append(Text(text=f"Jogador {i + 1}:", parent=self.root, origin=(-0.5, 0),
                                    position=(-0.28, top - i * step), scale=0.92,
                                    color=color.hex(metal_hex), z=0.2))
            field = InputField(parent=self.root, default_value='',
                               character_limit=14, position=(0.10, top - i * step), scale=(0.34, 0.068), z=0.2)
            field.color = C_PANEL_SOFT
            field.text_color = C_TEXT
            self.fields.append(field)

        def _continue():
            names = [(f.text.strip() or f"Jogador {i + 1}") for i, f in enumerate(self.fields)]
            for f in self.fields: f.active = False
            self.hide()
            on_continue(names)

        btn_y = top - amount * step - 0.055
        self.continue_button = Button(text="CONTINUAR", parent=self.root, color=C_GREEN,
                                      text_color=color.hex('#000000'), radius=0.15, scale=(0.38, 0.070),
                                      position=(0, btn_y), on_click=_continue, z=0.2)
        self.root.enabled = True

    def hide(self):
        self.root.enabled = False

class VictoryPanel:
    def __init__(self, game):
        self.game = game
        self.root = Entity(parent=camera.ui, enabled=False, z=-5)
        Entity(parent=self.root, model='quad', color=color.rgba32(4, 10, 20, 200), scale=(2.2, 1.2), z=1)
        
        Entity(parent=self.root, model='quad', color=C_NEON_BLUE, scale=(0.87, 0.57), z=0.55)
        Entity(parent=self.root, model='quad', color=C_HUD_BG, scale=(0.86, 0.56), z=0.5)
        
        self.title = Text("* PARABÉNS! *", parent=self.root, origin=(0, 0), position=(0, 0.19), scale=2.0, color=C_YELLOW)
        self.name = Text("", parent=self.root, origin=(0, 0), position=(0, 0.10), scale=1.5, color=C_TEXT)
        self.info = Text("", parent=self.root, origin=(0, 0), position=(0, 0.02), scale=0.95, color=C_MUTED, line_height=1.4)
        
        Button(text="NOVA PARTIDA", parent=self.root, color=C_GREEN, text_color=color.hex('#000000'), 
               radius=0.15, scale=(0.42, 0.08), position=(0, -0.16, 0.4), on_click=self.restart)

    def open(self, winner, difficulty):
        self.name.text = f"{winner['name']}, parabéns!"
        self.name.color = color.hex(winner["color"])
        
        # Salva a pontuação de TODOS os participantes no leaderboard.json
        all_players = self.game.logic.players if (self.game and self.game.logic and self.game.logic.players) else [winner]
        save_scores(all_players, difficulty)
        
        ranked = sorted(all_players, key=lambda p: p["score"], reverse=True)
        if len(all_players) > 1:
            placar_str = " | ".join(f"{p['name']}: {p['score']} pt" for p in ranked)
            self.info.text = wrap(f"Percurso concluído! Todos os pontos foram salvos nos Recordes.\n{placar_str}", 46)
        else:
            self.info.text = ("Você completou todo o percurso!\n" f"Pontuação final: {winner['score']} ponto(s) salva nos Recordes.")
        
        self.root.enabled = True

    def restart(self):
        self.root.enabled = False
        self.game.show_player_menu()

try:
    class _UrsinaSubclassProbe(Ursina): pass
    _GAME_BASE, _CAN_INHERIT = Ursina, True
except TypeError:
    _GAME_BASE, _CAN_INHERIT = object, False

class Game(_GAME_BASE):
    def __init__(self, **window_kwargs):
        settings = dict(title="Banco Matemático 3D", size=(1280, 720), borderless=False,
                        fullscreen=False, vsync=True, development_mode=False, editor_ui_enabled=False)
        settings.update(window_kwargs)

        if _CAN_INHERIT:
            super().__init__(**settings)
            self.app = self
        else:
            self.app = Ursina(**settings)

        global CHROME_TEX
        if CHROME_SHADER is not None:
            CHROME_TEX = make_chrome_matcap()
            for nome_metal, tons in METAL_TONES.items():
                METAL_TEXTURES[nome_metal] = make_metal_matcap(nome_metal, tons)

        window.color = C_BG
        window.exit_button.visible = False
        window.fps_counter.enabled = False

        self.logic = GameLogic()
        self.busy = False
        self.special_effect_active = False
        self.roulette_active = False

        self._build_environment()
        self._build_board()
        self.pawns = []
        self.trophy = None

        self.hud = HUD(self)
        self.question_panel = QuestionPanel(self)
        self.menu = MenuOverlay(self)
        self.names_panel = NamesPanel3D(self)
        self.victory = VictoryPanel(self)
        self.leaderboard_ui = LeaderboardPanel(self)
        self.hud.set_roll_enabled(False)

        self.focus = Vec3(1.9, 0, -1.2)
        self.orbit_yaw, self.orbit_pitch, self.orbit_dist = 0.0, 44.0, 23.0

        # Modo Overdrive (Combo x3)
        self.overdrive_intensity = 0.0
        self._was_overdrive = False

        # Câmera cinematográfica: a câmera desliza suavemente até o "alvo" atual
        self.cinematic = True                       # tecla C liga/desliga
        self.overview_focus = Vec3(1.9, 0, -1.2)    # visão geral do tabuleiro
        self.overview_dist = 23.0
        self.cam_goal_focus = Vec3(self.overview_focus)
        self.cam_goal_dist = self.overview_dist
        self.cam_follow = None                      # peão que está sendo seguido
        self.cam_speed = 2.5
        self._apply_camera()

        self.handler = Entity(input=self.on_input, update=self.on_update)
        self.show_player_menu()

    def _build_environment(self):
        self.sun = DirectionalLight(shadows=USE_SHADOWS, rotation=(45, -35, 45), color=LIGHT_SUN_NORMAL)
        try: self.sun.look_at(Vec3(1, -1.2, 1))
        except: pass
        self.fill = DirectionalLight(shadows=False, rotation=(30, 150, 0), color=LIGHT_FILL_NORMAL)
        self.ambient_light = AmbientLight(color=LIGHT_AMB_NORMAL)

        # Sem Sky padrão: o fundo é a cor escura da janela (C_BG) + campo de estrelas neon.
        # Criado DEPOIS do sol para não entrar no cálculo da área de sombra.
        self._build_space()

        Entity(model='cube', color=C_NEON_BLUE, scale=(COLS + 1.1, 0.35, ROWS + 1.1), position=(0, -0.34, 0), unlit=True)

        self.base_plate = Entity(model='cube', texture=CHROME_TEX if CHROME_TEX else 'white_cube',
                                 shader=CHROME_SHADER if CHROME_TEX else METAL_SHADER,
                                 color=color.hex('#0A0A0A'), scale=(COLS + 0.8, 0.4, ROWS + 0.8), position=(0, -0.32, 0))
        self.center_plate = Entity(model='cube', texture=CHROME_TEX if CHROME_TEX else 'white_cube',
                                   shader=CHROME_SHADER if CHROME_TEX else METAL_SHADER,
                                   color=C_BOARD, scale=(COLS - 2.3, 0.14, ROWS - 2.3), position=(0, -0.05, 0))
        solidify(self.base_plate)
        solidify(self.center_plate)

        self._build_table()

        # Textos e Logo Ajustados
        flat_text("BANCO", (1.15, 0.04, 1.60), scale=22, color_=C_NEON_BLUE)
        flat_text("MATEMÁTICO", (1.15, 0.04, 1.00), scale=14, color_=C_NEON_BLUE)

        if LOGO_TEX:
            aspect = LOGO_TEX.size[1] / LOGO_TEX.size[0]
            logo_w = 2.6
            logo_h = logo_w * aspect
            Entity(model='quad', texture=LOGO_TEX, color=color.white, unlit=True,
                  double_sided=True, rotation_x=90,
                  position=(1.15, 0.045, -1.0), scale=(logo_w, logo_h))
        else:
            flat_text("UESPI", (1.15, 0.04, -0.85), scale=22, color_=C_YELLOW)

        self.dice = Dice3D(position=Vec3(-2.55, 1.05, -1.1))

    def _build_space(self, n_estrelas=520, n_orbes=110):
        """Espaço holográfico: estrelas distantes + orbes neon flutuando perto da mesa."""
        rng = random.Random(3014)  # gerador próprio: não interfere no dado nem nas perguntas

        def escurecer(cor, brilho):
            return color.rgba(cor[0] * brilho, cor[1] * brilho, cor[2] * brilho, 1)

        # 1) Estrelas distantes: espalhadas uniformemente numa casca esférica (raio 70-120),
        #    sempre bem além do alcance máximo da câmera (zoom até 30).
        paleta_estrelas = [color.white, color.white, color.white, color.hex('#CFE8FF'),
                           color.hex('#9FD8FF'), C_NEON_BLUE, color.hex('#B388FF'), color.hex('#FFE9A8')]
        estrelas = []
        for _ in range(n_estrelas):
            y = rng.uniform(-1.0, 1.0)
            ang = rng.uniform(0, 2 * pi)
            r_xz = sqrt(1.0 - y * y)
            direcao = Vec3(r_xz * cos(ang), y, r_xz * sin(ang))
            pos = direcao * rng.uniform(70, 120)
            tamanho = rng.uniform(0.18, 0.55) if rng.random() > 0.06 else rng.uniform(0.7, 1.0)  # algumas maiores
            cor = escurecer(rng.choice(paleta_estrelas), rng.uniform(0.35, 1.0))
            estrelas.append((pos, tamanho, cor))

        # 2) Orbes holográficos: mais perto, ao redor e ABAIXO da mesa (y <= 0.3),
        #    o que dá a sensação de que o tabuleiro está flutuando. Ficam abaixo da altura
        #    mínima da câmera, então nunca passam na frente dela.
        paleta_orbes = [C_NEON_BLUE, C_NEON_BLUE, color.hex('#2979FF'), C_PURPLE,
                        color.hex('#FF4FD8'), color.hex('#7CFFCB')]
        orbes = []
        for _ in range(n_orbes):
            ang = rng.uniform(0, 2 * pi)
            raio = rng.uniform(8.5, 22.0)  # a mesa vai até ~6.3 do centro: orbes ficam fora dela
            pos = Vec3(cos(ang) * raio, rng.uniform(-11.0, 0.3), sin(ang) * raio)
            tamanho = rng.uniform(0.05, 0.16)
            cor = escurecer(rng.choice(paleta_orbes), rng.uniform(0.6, 1.0))
            orbes.append((pos, tamanho, cor))

        # Cada camada vira UMA malha só (1 chamada de desenho em vez de centenas de entidades).
        # unlit=True: ignoram a luz (brilham sempre) e não projetam sombra.
        self.space_stars = Entity(parent=scene, model=particle_field_mesh(estrelas),
                                  unlit=True, double_sided=True)
        self.space_orbs = Entity(parent=scene, model=particle_field_mesh(orbes),
                                 unlit=True, double_sided=True)

        # Garante que a câmera enxergue até as estrelas mais distantes
        try:
            if camera.clip_plane_far < 300:
                camera.clip_plane_far = 300
        except Exception:
            pass

    def _build_table(self):
        top_w = COLS + 2.6
        top_d = ROWS + 2.6
        top_h = 0.30
        base_plate_bottom = -0.32 - 0.4 / 2
        gap = 0.03
        top_y = base_plate_bottom - gap - top_h / 2

        self.table_top = Entity(model='cube', texture='white_cube', shader=METAL_SHADER,
                                color=C_WOOD, scale=(top_w, top_h, top_d),
                                position=(0, top_y, 0))
        solidify(self.table_top)

        leg_w = 0.34
        leg_h = 1.9
        leg_inset = 0.55
        leg_x = top_w / 2 - leg_inset
        leg_z = top_d / 2 - leg_inset
        leg_y = top_y - top_h / 2 - leg_h / 2

        self.table_legs = []
        for sx in (-1, 1):
            for sz in (-1, 1):
                perna = Entity(model='cube', texture='white_cube', shader=METAL_SHADER,
                               color=C_WOOD_DARK, scale=(leg_w, leg_h, leg_w),
                               position=(sx * leg_x, leg_y, sz * leg_z))
                solidify(perna)
                self.table_legs.append(perna)

    def _build_board(self):
        total = len(self.logic.cells)
        self.tiles = [Tile(i, cell, self.logic.rule_for(i), total, on_inspect=self.inspect_tile) for i, cell in enumerate(self.logic.cells)]

    def _apply_camera(self):
        yaw, pitch = radians(self.orbit_yaw), radians(self.orbit_pitch)
        r = self.orbit_dist * cos(pitch)
        camera.position = self.focus + Vec3(r * sin(yaw), self.orbit_dist * sin(pitch), -r * cos(yaw))
        camera.look_at(self.focus)

    # ---------- câmera cinematográfica ----------
    # Os métodos abaixo só definem PARA ONDE a câmera deve ir; o deslize suave
    # acontece em on_update(), quadro a quadro.
    def cam_overview(self):
        """Volta para a visão geral do tabuleiro."""
        self.cam_follow = None
        self.cam_goal_focus = Vec3(self.overview_focus)
        self.cam_goal_dist = self.overview_dist
        self.cam_speed = 2.2

    def cam_on_dice(self):
        """Close no dado durante o lançamento."""
        if not self.cinematic:
            return
        self.cam_follow = None
        self.cam_goal_focus = Vec3(self.dice.x, self.dice.base_y - 0.35, self.dice.z)
        self.cam_goal_dist = 10.0
        self.cam_speed = 3.5

    def cam_on_pawn(self, player_index):
        """Segue o peão de perto enquanto ele anda pelas casas."""
        if not self.cinematic or not (0 <= player_index < len(self.pawns)):
            return
        self.cam_follow = self.pawns[player_index]
        self.cam_goal_dist = 12.5
        self.cam_speed = 4.0

    def cam_on_trophy(self):
        """Foca a câmera cinematográfica no troféu e no centro nobre do tabuleiro."""
        if not self.cinematic:
            return
        self.cam_follow = None
        self.cam_goal_focus = Vec3(TROPHY_POS.x + 0.45, 0.75, TROPHY_POS.z)
        self.cam_goal_dist = 13.5
        self.cam_speed = 3.0

    def pawn_slot(self, player_index, position_index):
        col, row = self.logic.cells[position_index]
        base = grid_to_world(col, row, PAWN_Y)
        
        counts_per_cell = {}
        for player in self.logic.players:
            pos = player["position"]
            counts_per_cell[pos] = counts_per_cell.get(pos, 0) + 1
            
        current_offsets = {}
        for i in range(len(self.logic.players)):
            pos = self.logic.players[i]["position"]
            index_in_cell = current_offsets.get(pos, 0)
            current_offsets[pos] = index_in_cell + 1
            
            if i == player_index:
                offset_x = ((index_in_cell % 2) - 0.5) * 0.35 if counts_per_cell[pos] > 1 else 0
                offset_z = ((index_in_cell // 2) - 0.5) * 0.35 if counts_per_cell[pos] > 1 else 0
                return base + Vec3(offset_x, 0, offset_z)

    def sync_board(self, instant=False):
        ocupadas = {p["position"] for p in self.logic.players}
        for tile in self.tiles: (tile.sink if tile.index in ocupadas else tile.rise)()
        for i, pawn in enumerate(self.pawns):
            pawn.hop_to(self.pawn_slot(i, self.logic.players[i]["position"]), instant=instant)
            pawn.set_active(i == self.logic.current_player)

    def celebrate(self, player_index):
        """Explosão de 15 a 20 cubinhos coloridos saindo do topo do peão."""
        if not (0 <= player_index < len(self.pawns)):
            return
        pawn = self.pawns[player_index]
        topo = pawn.world_position + Vec3(0, PAWN_SCALE * 0.622 + 0.05, 0)
        cor_metal = color.hex(PLAYER_HEX[player_index])
        paleta = [cor_metal, cor_metal, C_YELLOW, C_GREEN, C_NEON_BLUE, C_PURPLE, C_RED, color.white]
        for _ in range(random.randint(15, 20)):
            angulo = random.uniform(0, 2 * pi)
            lateral = random.uniform(0.8, 2.0)
            subida = random.uniform(2.6, 4.2)
            velocidade = Vec3(cos(angulo) * lateral, subida, sin(angulo) * lateral)
            ConfettiCube(topo, velocidade, random.choice(paleta), duracao=0.5)

    def celebrate_trophy(self):
        """Explosão de cubinhos comemorativos ao redor do troféu no centro."""
        if not getattr(self, 'trophy', None):
            return
        topo = self.trophy.world_position + Vec3(0, 1.45 * self.trophy.scale_y, 0)
        paleta = [C_YELLOW, C_GREEN, C_NEON_BLUE, C_PURPLE, color.white, color.hex('#FFD700')]
        for _ in range(25):
            angulo = random.uniform(0, 2 * pi)
            lateral = random.uniform(1.2, 2.6)
            subida = random.uniform(3.2, 5.2)
            velocidade = Vec3(cos(angulo) * lateral, subida, sin(angulo) * lateral)
            ConfettiCube(topo, velocidade, random.choice(paleta), duracao=0.6)

    def spawn_trophy(self, player_index):
        """Cria e ergue o grande troféu 3D no centro do tabuleiro ao lado do logo UESPI."""
        if getattr(self, 'trophy', None):
            destroy(self.trophy)
            self.trophy = None
        player = self.logic.players[player_index]
        self.trophy = Trophy3D(
            position=TROPHY_POS,
            winner_name=player["name"],
            winner_color=player["color"],
            scale=1.55
        )
        self.cam_on_trophy()
        self.trophy.rise(on_finish=self.celebrate_trophy)

    def show_leaderboard(self):
        self.leaderboard_ui.show()

    def show_player_menu(self):
        self.busy = True
        if getattr(self, 'trophy', None):
            destroy(self.trophy)
            self.trophy = None
        self.cam_overview()
        self.hud.set_roll_enabled(False)
        self.menu.show("QUEM VAI JOGAR?", "Escolha a quantidade de jogadores",
                       [(f"{n} jogador" + ("es" if n > 1 else ""), partial(self.show_names_menu, n)) for n in (1, 2, 3, 4)])

    def show_names_menu(self, amount):
        self.menu.hide()
        self.names_panel.show(amount, partial(self.show_difficulty_menu, amount))

    def show_difficulty_menu(self, amount, names):
        self.menu.show("QUAL É A DIFICULDADE?", "As perguntas mudam conforme o nível",
                       [(label, partial(self.start_game, amount, value, names)) for value, label in DIFFICULTY_LABELS])

    def start_game(self, amount, difficulty, names=None):
        self.menu.hide()
        self.names_panel.hide()
        if getattr(self, 'trophy', None):
            destroy(self.trophy)
            self.trophy = None
        self.cam_overview()
        self.logic.start_game(amount, difficulty, names)
        self.special_effect_active = False
        self.roulette_active = False

        # Reinicia estado visual do Overdrive
        self.overdrive_intensity = 0.0
        self._was_overdrive = False
        if hasattr(self, 'ambient_light') and self.ambient_light:
            self.ambient_light.color = LIGHT_AMB_NORMAL
        if hasattr(self, 'fill') and self.fill:
            self.fill.color = LIGHT_FILL_NORMAL
        if hasattr(self, 'sun') and self.sun:
            self.sun.color = LIGHT_SUN_NORMAL
        if hasattr(self, 'center_plate') and self.center_plate:
            self.center_plate.color = C_BOARD
        for tile in self.tiles:
            tile.reset_visual()

        for pawn in self.pawns: destroy(pawn)
        self.pawns = [PlayerPawn(i, self.pawn_slot(i, 0)) for i in range(amount)]
        self.dice.set_value(5)
        self.sync_board(instant=True)
        self.hud.refresh()
        self.hud.set_roll_enabled(True)
        self.hud.message(f"Dificuldade: {difficulty.upper()}. É a vez do {self.logic.player['name']}. Role o dado!")
        self.busy = False

    def roll_dice(self):
        if self.busy or self.logic.finished or not self.logic.players: return
        if self.question_panel.active or self.menu.root.enabled or self.leaderboard_ui.root.enabled: return
        self.busy = True
        self.hud.set_roll_enabled(False)
        self.cam_on_dice()
        result = self.logic.roll()
        self.hud.dice_text.text = "ROLANDO..."

        if getattr(self, "roulette_active", False):
            self.roulette_active = False
            self.dice.roll_to(result, on_done=partial(self._after_roulette_roll, result))
        else:
            self.dice.roll_to(result, on_done=partial(self._after_roll, result))

    def _after_roulette_roll(self, result):
        player = self.logic.player
        self.hud.dice_text.text = f"ROLETA: {result}"

        if result <= 3:
            perda = 5
            player["score"] = max(0, player["score"] - perda)
            self.hud.message(f"AZAR! {player['name']} tirou {result} na Roleta da Sorte e perdeu {perda} pontos!")
            self.hud.refresh()
            invoke(self.cam_overview, delay=1.2)
            invoke(self.next_turn, delay=2.2)
        else:
            ganho = 10
            player["score"] += ganho
            play_sfx('coin_correct', volume=0.90)
            self.hud.message(f"SORTE GRANDE! {player['name']} tirou {result} na Roleta da Sorte e ganhou +{ganho} pontos instantâneos!")
            self.hud.refresh()
            self.celebrate(self.logic.current_player)
            invoke(self.cam_overview, delay=1.2)
            invoke(self.next_turn, delay=2.2)

    def _after_roll(self, result):
        self.hud.dice_text.text = f"DADO: {result}"
        player = self.logic.player
        self.hud.message(f"{player['name']} tirou {result}. O peão está andando...")
        self.cam_on_pawn(self.logic.current_player)
        self._move_steps(self.logic.current_player, result, 0, +1, partial(self.handle_landing, self.logic.current_player))

    def _move_steps(self, player_index, total_steps, step, direction, on_finish):
        if step >= total_steps:
            on_finish()
            return
        if direction > 0: completed = self.logic.step_forward(player_index)
        else: completed = self.logic.step_backward(player_index)
        
        self.sync_board()
        self.hud.refresh()

        if completed:
            self.logic.finished = True
            self.busy = True
            self.hud.set_roll_enabled(False)
            self.hud.message(f"{self.logic.players[player_index]['name']} completou o percurso e venceu a partida!")
            self.spawn_trophy(player_index)
            invoke(partial(self.victory.open, self.logic.players[player_index], self.logic.difficulty), delay=2.0)
            return

        invoke(partial(self._move_steps, player_index, total_steps, step + 1, direction, on_finish), delay=STEP_TIME)

    def handle_landing(self, player_index):
        if self.logic.finished: return
        player = self.logic.players[player_index]
        rule = self.logic.rule_for(player["position"])
        effect = rule["effect"]

        if effect == "advance":
            self.special_effect_active = True
            self.hud.message(f"{player['name']} caiu em +2 CASAS. Avançando sem pergunta!")
            invoke(partial(self._move_steps, player_index, 2, 0, +1, partial(self.finish_special_effect)), delay=0.45)
        elif effect == "back":
            self.special_effect_active = True
            self.hud.message(f"{player['name']} caiu em -2 CASAS. Voltando sem pergunta! Combo zerado.")
            player["combo"] = 0 # Cair em penalidade reseta o combo
            self.hud.refresh()
            invoke(partial(self._move_steps, player_index, 2, 0, -1, partial(self.finish_special_effect)), delay=0.45)
        elif effect == "skip":
            self.hud.message(f"{player['name']} caiu em PASSA VEZ. Nenhum ponto contabilizado. Combo zerado.")
            player["combo"] = 0 # Cair em penalidade reseta o combo
            self.hud.refresh()
            invoke(self.next_turn, delay=0.9)
        elif effect == "roulette":
            self.roulette_active = True
            self.busy = False
            self.hud.set_roll_enabled(True, text="GIRAR ROLETA", btn_color=C_GOLD_LUCKY)
            self.hud.message(f"ROLETA DA SORTE! {player['name']}, role o dado: [1 a 3] perde 5 pts | [4 a 6] ganha 10 pts!")
        else:
            self.hud.message(f"{player['name']} chegou à casa {player['position'] + 1}. Resolva a questão!")
            invoke(self.ask_question, delay=0.45)

    def finish_special_effect(self):
        self.special_effect_active = False
        self.hud.message("Efeito concluído. Nenhum ponto foi contabilizado.")
        invoke(self.next_turn, delay=0.6)

    def ask_question(self):
        if self.logic.finished: return
        question = self.logic.draw_question()
        player = self.logic.player
        rule = self.logic.rule_for(player["position"])
        self.question_panel.open(question, player, rule)

    def next_turn(self):
        if self.logic.finished: return
        self.roulette_active = False
        self.logic.advance_turn()
        self.cam_overview()
        self.sync_board()
        self.hud.refresh()
        self.hud.message(f"Agora é a vez do {self.logic.player['name']}! Role o dado.")
        self.hud.set_roll_enabled(True)
        self.busy = False

    def inspect_tile(self, tile):
        rule = tile.rule
        if tile.index == 0:
            self.hud.message("Casa 1: INÍCIO e CHEGADA (a mesma casa fecha a volta).")
            return
        if rule["effect"] == "roulette":
            self.hud.message(f"Casa {tile.index + 1}: ROLETA DA SORTE! Role o dado: [1 a 3] perde 5 pts | [4 a 6] ganha 10 pts instantâneos!")
            return
        extra = EFFECT_LABELS[rule["effect"]] or "questão matemática"
        self.hud.message(f"Casa {tile.index + 1}: {extra}  |  acerto +{rule['points']} pt  |  erro -{rule['penalty']} pt")

    def get_overdrive_positions(self):
        """Retorna o conjunto de índices das casas ocupadas por jogadores com Combo >= 3."""
        if not self.logic or not self.logic.players:
            return set()
        return {p["position"] for p in self.logic.players if p.get("combo", 0) >= 3}

    def update_overdrive(self):
        """Gerencia o modo Overdrive (Combo x3):
        - O tabuleiro inteiro escurece suavemente.
        - A casa atual de cada jogador em Overdrive passa a piscar intensamente ('on fire').
        - O anel do peão em Overdrive também assume a coloração flamejante pulsante.
        - Quando o combo cai abaixo de 3, o tabuleiro e as casas voltam ao normal."""
        overdrive_pos = self.get_overdrive_positions()
        target_intensity = 1.0 if len(overdrive_pos) > 0 else 0.0

        # Suavização da transição de iluminação do tabuleiro
        if abs(self.overdrive_intensity - target_intensity) > 0.002 or target_intensity > 0.0:
            self.overdrive_intensity = lerp(self.overdrive_intensity, target_intensity, min(1.0, time.dt * 5.0))
            k = self.overdrive_intensity

            if hasattr(self, 'ambient_light') and self.ambient_light:
                self.ambient_light.color = lerp(LIGHT_AMB_NORMAL, LIGHT_AMB_OVERDRIVE, k)
            if hasattr(self, 'fill') and self.fill:
                self.fill.color = lerp(LIGHT_FILL_NORMAL, LIGHT_FILL_OVERDRIVE, k)
            if hasattr(self, 'sun') and self.sun:
                self.sun.color = lerp(LIGHT_SUN_NORMAL, LIGHT_SUN_OVERDRIVE, k)
            if hasattr(self, 'center_plate') and self.center_plate:
                self.center_plate.color = lerp(C_BOARD, C_BOARD.tint(-0.45), k)

        # Se o modo Overdrive está em efeito
        if self.overdrive_intensity > 0.01:
            self._was_overdrive = True

            # Pulso rápido e intenso ('on fire')
            t = time.time() * 11.5
            pulse = (sin(t) + 1.0) * 0.5
            fire = lerp(color.hex('#FF2600'), color.hex('#FFEE00'), pulse)
            white_flare = max(0.0, sin(t)) ** 4
            cor_on_fire = lerp(fire, color.white, white_flare * 0.45)

            k_dim = 0.50 * self.overdrive_intensity
            for tile in self.tiles:
                if tile.index in overdrive_pos:
                    tile.set_fire_pulse(cor_on_fire)
                else:
                    tile.set_dimmed(k_dim)

            # Efeito no peão: anel brilha na mesma intensidade flamejante
            for i, pawn in enumerate(self.pawns):
                if i < len(self.logic.players) and self.logic.players[i].get("combo", 0) >= 3:
                    if hasattr(pawn, 'ring') and pawn.ring:
                        pawn.ring.enabled = True
                        pawn.ring.color = cor_on_fire
                elif i == self.logic.current_player:
                    if hasattr(pawn, 'ring') and pawn.ring:
                        pawn.ring.enabled = True
                        _, metal, _ = PLAYER_METALS[i]
                        pawn.ring.color = metal.tint(-0.25)

        elif self._was_overdrive:
            # Transição encerrada: restauração completa e definitiva do tabuleiro
            self._was_overdrive = False
            self.overdrive_intensity = 0.0

            if hasattr(self, 'ambient_light') and self.ambient_light:
                self.ambient_light.color = LIGHT_AMB_NORMAL
            if hasattr(self, 'fill') and self.fill:
                self.fill.color = LIGHT_FILL_NORMAL
            if hasattr(self, 'sun') and self.sun:
                self.sun.color = LIGHT_SUN_NORMAL
            if hasattr(self, 'center_plate') and self.center_plate:
                self.center_plate.color = C_BOARD

            for tile in self.tiles:
                tile.reset_visual()

            for i, pawn in enumerate(self.pawns):
                if hasattr(pawn, 'ring') and pawn.ring:
                    pawn.ring.enabled = (i == self.logic.current_player)
                    _, metal, _ = PLAYER_METALS[i]
                    pawn.ring.color = metal.tint(-0.25)

    def on_input(self, key):
        if key == 'enter' and self.question_panel.active:
            (self.question_panel.submit if not self.question_panel.answered else self.question_panel.close_and_continue)()
        elif key == 'space' and not self.question_panel.active: self.roll_dice()
        elif key == 'c':
            self.cinematic = not self.cinematic
            if not self.cinematic:
                self.cam_overview()
            self.hud.message(f"Câmera Cinematográfica: {'LIGADA' if self.cinematic else 'DESLIGADA'}")
        elif key == 'scroll up':
            self.orbit_dist = max(10.0, self.orbit_dist - 0.8)
            self._apply_camera()
        elif key == 'scroll down':
            self.orbit_dist = min(30.0, self.orbit_dist + 0.8)
            self._apply_camera()
        elif key == 'r':
            self.orbit_yaw, self.orbit_pitch, self.orbit_dist = 0.0, 44.0, 23.0
            self.focus = Vec3(1.9, 0, -1.2)
            self._apply_camera()

    def on_update(self):
        if self.names_panel.root.enabled:
            return

        # Modo Overdrive no Combo x3
        self.update_overdrive()

        # Suavização da câmera cinematográfica
        if self.cinematic:
            alvo_focus = self.cam_follow.world_position if self.cam_follow else self.cam_goal_focus
            d_focus = (alvo_focus - self.focus).length()
            d_dist = abs(self.cam_goal_dist - self.orbit_dist)
            if d_focus > 0.005 or d_dist > 0.005:
                fator = min(1.0, time.dt * self.cam_speed)
                self.focus = lerp(self.focus, alvo_focus, fator)
                self.orbit_dist = lerp(self.orbit_dist, self.cam_goal_dist, fator)
                self._apply_camera()

        girou = False
        if held_keys['left arrow'] or held_keys['a']:
            self.orbit_yaw -= 45 * time.dt
            girou = True
        if held_keys['right arrow'] or held_keys['d']:
            self.orbit_yaw += 45 * time.dt
            girou = True
        if held_keys['up arrow'] or held_keys['w']:
            self.orbit_pitch = min(80.0, self.orbit_pitch + 25 * time.dt)
            girou = True
        if held_keys['down arrow'] or held_keys['s']:
            self.orbit_pitch = max(14.0, self.orbit_pitch - 25.0 * time.dt)
            girou = True
        if girou: self._apply_camera()

    def run(self):
        self.app.run()

if __name__ == '__main__':
    game = Game()
    game.run()
