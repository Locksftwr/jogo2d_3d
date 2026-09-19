"""
Banco Matemático 3D (versão)

Requisitos:  pip install ursina
Precisa do mesmo arquivo questions_by_difficulty.py do jogo em tkinter,
na mesma pasta (QUESTIONS_BY_DIFFICULTY, DIFFICULTY_LABELS, HOUSE_RULES).
"""
import textwrap
from ursina import *
import random 
from questions_by_difficulty import QUESTIONS_BY_DIFFICULTY, DIFFICULTY_LABELS, HOUSE_RULES

DEFAULT_RULE = {"points": 1, "penalty": 1, "effect": "normal"}
EFFECT_SHORT = {"advance": "+2", "back": "-2", "skip": "PASSA"}
PLAYER_COLORS = [color.red, color.azure, color.lime, color.yellow]
TILE_COLORS = [color.hex("#FFF0B3"), color.hex("#CBE8FF"), color.hex("#E5D5FF"), color.hex("#FFD6C2")]


def normalize(value):
    return str(value).strip().lower().replace(" ", "")


def create_cells():
    cells = [(col, 0) for col in range(10)]
    cells += [(9, row) for row in range(1, 7)]
    cells += [(col, 6) for col in range(8, -1, -1)]
    cells += [(0, row) for row in range(5, 0, -1)]
    return cells


CELLS = create_cells()


def cell_pos(i):
    col, row = CELLS[i]
    return Vec3(col - 4.5, 0, row - 3)


app = Ursina(title="Banco Matemático 3D (versão bem ruim)")
window.color = color.hex("#102238")
camera.position = (0, 14, -10)
camera.rotation_x = 55
camera.fov = 55


def build_board():
    Entity(model="cube", color=color.hex("#7A4B26"), position=(0, -0.35, 0), scale=(12, 0.4, 9))
    for i in range(len(CELLS)):
        rule = HOUSE_RULES.get(i, DEFAULT_RULE)
        effect = rule["effect"]
        if i == 0:
            tile_color, label = color.lime, "INICIO\nCHEGADA"
        elif effect == "advance":
            tile_color, label = color.green, EFFECT_SHORT[effect]
        elif effect == "back":
            tile_color, label = color.salmon, EFFECT_SHORT[effect]
        elif effect == "skip":
            tile_color, label = color.orange, EFFECT_SHORT[effect]
        else:
            tile_color, label = TILE_COLORS[i % 4], str(i + 1)
        p = cell_pos(i)
        Entity(model="cube", color=tile_color, position=p, scale=(0.95, 0.2, 0.95))
        Text(text=label, parent=scene, position=(p.x, 0.12, p.z), rotation_x=90,
             scale=9, origin=(0, 0), color=color.black)


class Game:
    def __init__(self):
        self.players = []
        self.cur = 0
        self.busy = False
        self.finished = False
        self.special = False
        self.answered = False
        self.difficulty = "médio"
        self.question = None
        self.rule = DEFAULT_RULE

        self.dice = Entity(model="cube", color=color.white, position=(0, 1.8, 0), scale=1.2)
        self.build_hud()
        self.build_question_panel()
        self.menu = Entity(parent=camera.ui)
        self.menu_players()

    # ---------- UI ----------
    def build_hud(self):
        self.hud = Entity(parent=camera.ui, enabled=False)
        self.turn_label = Text(parent=self.hud, text="", position=(-0.85, 0.47), scale=1.8)
        self.msg = Text(parent=self.hud, text="", position=(-0.85, -0.36), scale=1.2, color=color.light_gray)
        self.score_texts = []
        self.dice_label = Text(parent=self.hud, text="?", position=(0.6, -0.22), scale=5, color=color.white)
        self.roll_btn = Button(parent=self.hud, text="RODAR O DADO", color=color.yellow, text_color=color.black,
                               position=(0.65, -0.38), scale=(0.3, 0.08), on_click=self.roll)
        Button(parent=self.hud, text="NOVA PARTIDA", color=color.gray, position=(0.65, -0.47),
               scale=(0.3, 0.06), on_click=self.new_game)
        self.win_text = Text(parent=self.hud, text="", origin=(0, 0), position=(0, 0.1), scale=3,
                             color=color.yellow, enabled=False)

    def build_question_panel(self):
        self.qpanel = Entity(parent=camera.ui, enabled=False, z=-1)
        Entity(parent=self.qpanel, model="quad", color=color.hex("#183653"), scale=(1.1, 0.65), z=0.1)
        self.q_title = Text(parent=self.qpanel, text="", origin=(0, 0), y=0.25, scale=1.5, color=color.yellow)
        self.q_rule = Text(parent=self.qpanel, text="", origin=(0, 0), y=0.19, scale=1.1, color=color.light_gray)
        self.q_text = Text(parent=self.qpanel, text="", origin=(0, 0), y=0.08, scale=1.6)
        self.q_input = InputField(parent=self.qpanel, y=-0.05, max_lines=1)
        self.q_feedback = Text(parent=self.qpanel, text="", origin=(0, 0), y=-0.14, scale=1.1)
        self.q_btn = Button(parent=self.qpanel, text="CONFERIR", color=color.lime, text_color=color.black,
                            y=-0.23, scale=(0.35, 0.07), on_click=self.submit)

    def say(self, text):
        self.msg.text = textwrap.fill(text, 55)

    def update_hud(self):
        if not self.players:
            return
        p = self.players[self.cur]
        self.turn_label.text = f"VEZ DE {p['name'].upper()}"
        self.turn_label.color = p["color"]
        for i, (pl, t) in enumerate(zip(self.players, self.score_texts)):
            mark = "> " if i == self.cur else "   "
            t.text = f"{mark}{pl['name']}  casa {pl['pos'] + 1}  |  {pl['score']} pts"

    # ---------- menu ----------
    def clear_menu(self):
        for child in self.menu.children[:]:
            destroy(child)

    def menu_players(self):
        self.clear_menu()
        self.hud.enabled = False
        self.menu.enabled = True
        Text(parent=self.menu, text="QUEM VAI JOGAR?", origin=(0, 0), y=0.3, scale=2.5, color=color.yellow)
        for n in range(1, 5):
            Button(parent=self.menu, text=f"{n} jogador" + ("es" if n > 1 else ""), y=0.15 - (n - 1) * 0.11,
                   scale=(0.35, 0.09), on_click=lambda n=n: self.menu_difficulty(n))

    def menu_difficulty(self, amount):
        self.clear_menu()
        Text(parent=self.menu, text="QUAL A DIFICULDADE?", origin=(0, 0), y=0.3, scale=2.5, color=color.yellow)
        for k, (value, label) in enumerate(DIFFICULTY_LABELS):
            Button(parent=self.menu, text=label, y=0.15 - k * 0.11, scale=(0.35, 0.09),
                   on_click=lambda v=value: self.start_game(amount, v))

    def new_game(self):
        if self.busy and not self.finished:
            return
        self.qpanel.enabled = False
        self.win_text.enabled = False
        self.menu_players()

    # ---------- jogo ----------
    def pawn_pos(self, cell, idx):
        base = cell_pos(cell)
        return Vec3(base.x + ((idx % 2) - 0.5) * 0.4, 0.35, base.z + ((idx // 2) - 0.5) * 0.4)

    def start_game(self, amount, difficulty):
        for p in self.players:
            destroy(p["pawn"])
        for t in self.score_texts:
            destroy(t)
        self.players, self.score_texts = [], []
        self.difficulty = difficulty
        self.cur = 0
        self.busy = self.finished = self.special = False
        self.win_text.enabled = False
        for i in range(amount):
            pawn = Entity(model="sphere", color=PLAYER_COLORS[i], scale=0.45, position=self.pawn_pos(0, i))
            self.players.append({"name": f"Jogador {i + 1}", "pos": 0, "score": 0,
                                 "color": PLAYER_COLORS[i], "pawn": pawn})
            self.score_texts.append(Text(parent=self.hud, text="", position=(0.45, 0.47 - i * 0.05),
                                         scale=1.2, color=PLAYER_COLORS[i]))
        self.menu.enabled = False
        self.hud.enabled = True
        self.dice_label.text = "?"
        self.update_hud()
        self.say(f"Dificuldade: {difficulty.upper()}. Jogador 1, rode o dado!")

    def roll(self):
        if self.busy or self.finished or not self.players or self.qpanel.enabled:
            return
        self.busy = True
        self.dice_label.text = "..."
        self.dice.animate_rotation((random.randint(360, 720), random.randint(360, 720), 0),
                                   duration=0.8, curve=curve.out_expo)
        invoke(self.after_roll, delay=0.85)

    def after_roll(self):
        result = random.randint(1, 6)
        self.dice_label.text = str(result)
        p = self.players[self.cur]
        self.say(f"{p['name']} tirou {result}.")
        self.move(self.cur, result, 1, self.after_forward)

    def put_pawn(self, idx):
        p = self.players[idx]
        p["pawn"].animate_position(self.pawn_pos(p["pos"], idx), duration=0.2, curve=curve.linear)

    def move(self, idx, steps, direction, done):
        p = self.players[idx]
        if steps == 0:
            done()
            return
        if direction > 0 and p["pos"] == len(CELLS) - 1:
            # deu a volta inteira: chegou na casa 0 (CHEGADA)
            p["pos"] = 0
            self.put_pawn(idx)
            self.win(p)
            return
        p["pos"] = (p["pos"] + direction) % len(CELLS)
        self.put_pawn(idx)
        self.update_hud()
        invoke(self.move, idx, steps - 1, direction, done, delay=0.25)

    def after_forward(self):
        if self.special:
            self.special = False
            self.next_turn("Efeito concluído. Nenhum ponto.")
        else:
            self.land()

    def land(self):
        p = self.players[self.cur]
        rule = HOUSE_RULES.get(p["pos"], DEFAULT_RULE)
        effect = rule["effect"]
        if effect == "advance":
            self.special = True
            self.say(f"{p['name']} caiu em +2 CASAS. Avançando!")
            self.move(self.cur, 2, 1, self.after_forward)
        elif effect == "back":
            self.say(f"{p['name']} caiu em -2 CASAS. Voltando!")
            self.move(self.cur, 2, -1, lambda: self.next_turn("Efeito concluído. Nenhum ponto."))
        elif effect == "skip":
            self.next_turn(f"{p['name']} caiu em PASSA VEZ.")
        else:
            self.rule = rule
            self.say(f"{p['name']} chegou à casa {p['pos'] + 1}. Resolva a questão!")
            invoke(self.ask, delay=0.3)

    def next_turn(self, message=None):
        self.cur = (self.cur + 1) % len(self.players)
        self.busy = False
        self.update_hud()
        self.say((message + " " if message else "") + f"Agora é a vez do Jogador {self.cur + 1}!")

    def win(self, p):
        self.finished = True
        self.busy = False
        self.update_hud()
        self.win_text.text = f"PARABÉNS, {p['name'].upper()}!\n{p['score']} ponto(s)"
        self.win_text.enabled = True
        self.say(f"{p['name']} completou todo o percurso!")

    # ---------- pergunta ----------
    def ask(self):
        self.question = random.choice(QUESTIONS_BY_DIFFICULTY[self.difficulty])
        p = self.players[self.cur]
        self.q_title.text = f"{p['name'].upper()} - {self.question['tipo']}"
        self.q_rule.text = f"Acertar: +{self.rule['points']}   Errar: -{self.rule['penalty']}"
        self.q_text.text = textwrap.fill(str(self.question["pergunta"]), 40)
        self.q_feedback.text = ""
        self.q_input.text = ""
        self.q_btn.text = "CONFERIR"
        self.answered = False
        self.qpanel.enabled = True
        self.q_input.active = True

    def submit(self):
        if not self.qpanel.enabled:
            return
        if self.answered:
            self.qpanel.enabled = False
            self.next_turn()
            return
        p = self.players[self.cur]
        if normalize(self.q_input.text) == normalize(self.question["resposta"]):
            p["score"] += self.rule["points"]
            self.q_feedback.text = f"Correto! +{self.rule['points']} ponto(s)."
            self.q_feedback.color = color.lime
        else:
            p["score"] = max(0, p["score"] - self.rule["penalty"])
            self.q_feedback.text = textwrap.fill(
                f"Errado. Dica: {self.question['dica']} (-{self.rule['penalty']} ponto(s))", 60)
            self.q_feedback.color = color.salmon
        self.answered = True
        self.q_btn.text = "PRÓXIMO JOGADOR"
        self.update_hud()


build_board()
game = Game()


def input(key):
    if key == "enter" and game.qpanel.enabled:
        game.submit()


app.run()
