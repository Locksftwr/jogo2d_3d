import random
import tkinter as tk
from questions_by_difficulty import QUESTIONS_BY_DIFFICULTY, DIFFICULTY_LABELS, HOUSE_RULES


BG = "#102238",
PANEL = "#183653",
TEXT = "#F5F7FA",
MUTED = "#B7C9D8",
YELLOW = "#FFD166",
GREEN = "#69D391",
RED = "#FF6B6B",
BLUE = "#67B7FF",
PURPLE = "#B28DFF"

EFFECT_LABELS = {"normal": "", "advance": "+2 CASAS", "back": "-2 CASAS", "skip": "PASSA VEZ"}
EFFECT_SHORT = {"advance": "+2\nCASAS", "back": "-2\nCASAS", "skip": "PASSA\nVEZ"}

COLORS = [RED, BLUE, GREEN, YELLOW]
DICE = ["⚀", "⚁", "⚂", "⚃", "⚄", "⚅"]


def normalize(value):
    return value.strip().lower().replace(" ", "")


class BancoMatematico:
    def __init__(self, root):
        self.root = root
        self.root.title("Banco Matemático")
        self.root.geometry("1220x780")
        self.root.minsize(1000, 700)
        self.root.configure(bg=BG)
        self.cells = self.create_board_cells()
        self.players = []
        self.current_player = 0
        self.rolling = False
        self.moving = False
        self.current_question = None
        self.difficulty = "médio"
        self.finished = False
        self.skip_next = False
        self.special_effect_active = False
        self.build_ui()
        self.show_player_selection()

    def create_board_cells(self):
        # A casa 0 é compartilhada: ela é INÍCIO e também CHEGADA.
        cells = [(col, 0) for col in range(10)]
        cells += [(9, row) for row in range(1, 7)]
        cells += [(col, 6) for col in range(8, -1, -1)]
        cells += [(0, row) for row in range(5, 0, -1)]
        return cells

    def build_ui(self):
        header = tk.Frame(self.root, bg=BG)
        header.pack(fill="x", padx=28, pady=(18, 8))
        tk.Label(header, text="BANCO", font=("Arial", 28, "bold"), fg=YELLOW, bg=BG).pack(side="left")
        tk.Label(header, text=" MATEMÁTICO", font=("Arial", 28, "bold"), fg=TEXT, bg=BG).pack(side="left")
        tk.Label(header, text="FEIRA DE MATEMÁTICA", font=("Arial", 11, "bold"), fg=MUTED, bg=BG).pack(side="right", pady=12)
        body = tk.Frame(self.root, bg=BG)
        body.pack(fill="both", expand=True, padx=22, pady=12)
        board_frame = tk.Frame(body, bg=PANEL, highlightthickness=1, highlightbackground="#2D5C7A")
        board_frame.pack(side="left", fill="both", expand=True, padx=(0, 14))
        self.canvas = tk.Canvas(board_frame, bg="#DDF4EA", highlightthickness=0)
        self.canvas.pack(fill="both", expand=True, padx=12, pady=12)
        self.canvas.bind("<Configure>", lambda event: self.draw_board())
        side = tk.Frame(body, bg=PANEL, width=290)
        side.pack(side="right", fill="y")
        side.pack_propagate(False)
        self.turn_label = tk.Label(side, text="CONFIGURANDO PARTIDA", font=("Arial", 13, "bold"), fg=YELLOW, bg=PANEL)
        self.turn_label.pack(pady=(26, 8))
        self.dice_label = tk.Label(side, text="⚄", font=("Arial", 72, "bold"), fg=TEXT, bg=PANEL)
        self.dice_label.pack(pady=(0, 4))
        self.roll_button = tk.Button(side, text="RODAR O DADO", command=self.roll_dice, font=("Arial", 12, "bold"), fg=BG, bg=YELLOW, activebackground="#FFE29A", relief="flat", padx=18, pady=12, cursor="hand2")
        self.roll_button.pack(padx=25, fill="x")
        self.message_label = tk.Label(side, text="Escolha a quantidade de jogadores.", wraplength=235, justify="center", font=("Arial", 10), fg=MUTED, bg=PANEL)
        self.message_label.pack(padx=22, pady=16)
        tk.Frame(side, height=1, bg="#2D5C7A").pack(fill="x", padx=22, pady=(2, 13))
        tk.Label(side, text="PLACAR", font=("Arial", 12, "bold"), fg=YELLOW, bg=PANEL).pack(anchor="w", padx=24)
        self.score_frame = tk.Frame(side, bg=PANEL)
        self.score_frame.pack(fill="x", padx=24, pady=8)
        self.difficulty_label = tk.Label(side, text="Dificuldade: —", font=("Arial", 10, "bold"), fg=PURPLE, bg=PANEL)
        self.difficulty_label.pack(anchor="w", padx=24, pady=(2, 0))
        tk.Label(side, text="COMO JOGAR", font=("Arial", 12, "bold"), fg=YELLOW, bg=PANEL).pack(anchor="w", padx=24, pady=(9, 0))
        tk.Label(side, text="Na sua vez, rode o dado e veja seu bonequinho avançar casa a casa. Acertar vale +1 ponto. Errar desconta a penalidade indicada na casa.", justify="left", wraplength=235, font=("Arial", 9), fg=MUTED, bg=PANEL).pack(anchor="w", padx=24, pady=7)
        tk.Button(side, text="NOVA PARTIDA", command=self.show_player_selection, font=("Arial", 10, "bold"), fg=TEXT, bg="#2D5C7A", activebackground="#3C7394", relief="flat", padx=10, pady=8, cursor="hand2").pack(side="bottom", padx=24, pady=22, fill="x")

    def show_player_selection(self):
        dialog = tk.Toplevel(self.root)
        dialog.title("Nova partida")
        dialog.geometry("430x430")
        dialog.resizable(False, False)
        dialog.configure(bg=PANEL)
        dialog.transient(self.root)
        dialog.grab_set()
        tk.Label(dialog, text="QUEM VAI JOGAR?", font=("Arial", 20, "bold"), fg=YELLOW, bg=PANEL).pack(pady=(30, 8))
        tk.Label(dialog, text="Escolha a quantidade de jogadores", font=("Arial", 11), fg=MUTED, bg=PANEL).pack(pady=(0, 22))
        selected = tk.IntVar(value=2)
        buttons = tk.Frame(dialog, bg=PANEL)
        buttons.pack()
        for amount, label in [(1, "1 jogador"), (2, "2 jogadores"), (3, "3 jogadores"), (4, "4 jogadores")]:
            tk.Radiobutton(buttons, text=label, variable=selected, value=amount, indicatoron=False, width=16, font=("Arial", 11, "bold"), fg=TEXT, bg="#2D5C7A", selectcolor="#397796", activebackground="#397796", relief="flat", pady=8).pack(pady=3)
        ok_button = tk.Button(dialog, text="OK", command=lambda: (self.choose_difficulty(selected.get()), dialog.destroy()), font=("Arial", 14, "bold"), fg=BG, bg=GREEN, activebackground="#9BE7B5", relief="flat", padx=60, pady=12, cursor="hand2")
        ok_button.pack(pady=(24, 12), fill="x", padx=70)

    def choose_difficulty(self, amount):
        dialog = tk.Toplevel(self.root)
        dialog.title("Escolha a dificuldade")
        dialog.geometry("430x430")
        dialog.resizable(False, False)
        dialog.configure(bg=PANEL)
        dialog.transient(self.root)
        dialog.grab_set()
        tk.Label(dialog, text="QUAL É A DIFICULDADE?", font=("Arial", 19, "bold"), fg=YELLOW, bg=PANEL).pack(pady=(30, 8))
        tk.Label(dialog, text="As perguntas mudarão conforme o nível", font=("Arial", 11), fg=MUTED, bg=PANEL).pack(pady=(0, 22))
        selected = tk.StringVar(value="médio")
        buttons = tk.Frame(dialog, bg=PANEL)
        buttons.pack()
        for value, label in DIFFICULTY_LABELS:
            tk.Radiobutton(buttons, text=label, variable=selected, value=value, indicatoron=False, width=16, font=("Arial", 12, "bold"), fg=TEXT, bg="#2D5C7A", selectcolor="#397796", activebackground="#397796", relief="flat", pady=9).pack(pady=4)
        tk.Button(dialog, text="OK", command=lambda: (self.start_game(amount, selected.get()), dialog.destroy()), font=("Arial", 14, "bold"), fg=BG, bg=GREEN, activebackground="#9BE7B5", relief="flat", padx=60, pady=12, cursor="hand2").pack(pady=(24, 12), fill="x", padx=70)

    def start_game(self, amount, difficulty):
        self.players = [{"name": f"Jogador {i + 1}", "position": 0, "score": 0, "color": COLORS[i]} for i in range(amount)]
        self.difficulty = difficulty
        self.finished = False
        self.skip_next = False
        self.special_effect_active = False
        self.current_player = 0
        self.dice_label.config(text="⚄")
        self.roll_button.config(state="normal")
        self.difficulty_label.config(text=f"Dificuldade: {difficulty.upper()}")
        self.draw_board()
        self.update_turn(f"Dificuldade: {difficulty.upper()}. É a vez do Jogador 1. Rode o dado!")

    def update_scoreboard(self):
        for child in self.score_frame.winfo_children():
            child.destroy()
        for i, player in enumerate(self.players):
            marker = "▶ " if i == self.current_player else "   "
            tk.Label(self.score_frame, text=f"{marker}{player['name']}", font=("Arial", 10, "bold"), fg=player["color"], bg=PANEL, anchor="w").pack(fill="x")
            tk.Label(self.score_frame, text=f"     Casa {player['position'] + 1}  •  {player['score']} ponto(s)", font=("Arial", 9), fg=MUTED, bg=PANEL, anchor="w").pack(fill="x", pady=(0, 4))

    def update_turn(self, message):
        if self.players:
            player = self.players[self.current_player]
            self.turn_label.config(text=f"VEZ DE {player['name'].upper()}", fg=player["color"])
        self.message_label.config(text=message)
        self.update_scoreboard()

    def board_geometry(self):
        width, height = max(self.canvas.winfo_width(), 500), max(self.canvas.winfo_height(), 430)
        cell = min((width - 32) / 10, (height - 32) / 7)
        return (width - 10 * cell) / 2, (height - 7 * cell) / 2, cell

    def draw_board(self):
        if not hasattr(self, "canvas"):
            return
        self.canvas.delete("all")
        width, height = max(self.canvas.winfo_width(), 500), max(self.canvas.winfo_height(), 430)
        ox, oy, cell = self.board_geometry()
        self.canvas.create_text(width / 2, height / 2 - 18, text="BANCO", fill="#28625B", font=("Arial", int(cell * .55), "bold"))
        self.canvas.create_text(width / 2, height / 2 + 30, text="MATEMÁTICO", fill="#28625B", font=("Arial", int(cell * .28), "bold"))
        for i, (col, row) in enumerate(self.cells):
            x1, y1 = ox + col * cell, oy + row * cell
            x2, y2 = x1 + cell - 3, y1 + cell - 3
            if i == 0:
                # Uma única casa, dividida na diagonal: início e chegada.
                self.canvas.create_rectangle(x1, y1, x2, y2, fill="#F59E9E", outline="#21443F", width=2)
                self.canvas.create_polygon(x1, y1, x2, y1, x1, y2, fill="#9EE5B6", outline="")
                self.canvas.create_line(x1, y2, x2, y1, fill="#21443F", width=2)
                self.canvas.create_text(x1 + cell*.30, y1 + cell*.28, text="INÍCIO", fill="#21443F", font=("Arial", max(7, int(cell*.11)), "bold"))
                self.canvas.create_text(x1 + cell*.69, y1 + cell*.73, text="CHEGADA", fill="#21443F", font=("Arial", max(7, int(cell*.10)), "bold"))
            else:
                fill = ["#FFF0B3", "#CBE8FF", "#E5D5FF", "#FFD6C2"][i % 4]
                self.canvas.create_rectangle(x1, y1, x2, y2, fill=fill, outline="#21443F", width=2)
                self.canvas.create_text((x1+x2)/2, y1 + cell*.20, text=str(i + 1), fill="#21443F", font=("Arial", max(8, int(cell*.14)), "bold"))
                rule = HOUSE_RULES.get(i, {"points": 1, "penalty": 1, "effect": "normal"})
                if rule["effect"] != "normal":
                    self.canvas.create_text((x1+x2)/2, (y1+y2)/2 + cell*.03, text=EFFECT_SHORT[rule["effect"]], fill="#28625B", font=("Arial", max(8, int(cell*.13)), "bold"), justify="center")
                else:
                    self.canvas.create_text((x1+x2)/2, y1 + cell*.48, text=["?", "＋", "△", "%", "÷"][i % 5], fill="#28625B", font=("Arial", max(11, int(cell*.20)), "bold"))
                    self.canvas.create_text((x1+x2)/2, y1 + cell*.70, text=f"+{rule['points']} pts", fill="#28625B", font=("Arial", max(7, int(cell*.09)), "bold"))
                    self.canvas.create_text((x1+x2)/2, y1 + cell*.86, text=f"erro: -{rule['penalty']}", fill="#A44747", font=("Arial", max(7, int(cell*.09)), "bold"))
        self.draw_players(ox, oy, cell)

    def draw_players(self, ox, oy, cell):
        # O peão é um pequeno bonequinho: cabeça, corpo e base.
        for p_index, player in enumerate(self.players):
            col, row = self.cells[player["position"]]
            offset_x = ((p_index % 2) - .5) * cell * .28
            offset_y = ((p_index // 2) - .5) * cell * .24
            cx = ox + col * cell + (cell - 3) / 2 + offset_x
            cy = oy + row * cell + (cell - 3) / 2 + cell*.08 + offset_y
            radius = max(6, cell*.10)
            self.canvas.create_oval(cx - radius, cy - radius*2.1, cx + radius, cy, fill="#FFD9B3", outline="#17344F", width=1)
            self.canvas.create_oval(cx - radius*.42, cy - radius*1.48, cx - radius*.18, cy - radius*1.20, fill="#17344F", outline="")
            self.canvas.create_oval(cx + radius*.18, cy - radius*1.48, cx + radius*.42, cy - radius*1.20, fill="#17344F", outline="")
            self.canvas.create_polygon(cx - radius*1.35, cy, cx + radius*1.35, cy, cx + radius*1.05, cy + radius*1.65, cx - radius*1.05, cy + radius*1.65, fill=player["color"], outline="#17344F")
            self.canvas.create_oval(cx - radius*1.45, cy + radius*1.35, cx + radius*1.45, cy + radius*1.85, fill="#17344F", outline="")
            self.canvas.create_text(cx, cy + radius*.65, text=str(p_index + 1), fill=BG, font=("Arial", max(6, int(radius*.85)), "bold"))

    def roll_dice(self):
        if self.finished or self.rolling or self.moving or not self.players:
            return
        self.rolling = True
        self.roll_button.config(state="disabled")
        self.animate_dice(0)

    def animate_dice(self, count):
        self.dice_label.config(text=random.choice(DICE))
        if count < 9:
            self.root.after(80, lambda: self.animate_dice(count + 1))
            return
        result = random.randint(1, 6)
        self.dice_label.config(text=DICE[result - 1])
        self.rolling = False
        self.moving = True
        player = self.players[self.current_player]
        self.message_label.config(text=f"{player['name']} tirou {result}. O bonequinho está andando...")
        self.animate_player_move(self.current_player, result, 0)

    def animate_player_move(self, player_index, total_steps, step):
        player = self.players[player_index]
        if step < total_steps:
            completed = player["position"] == len(self.cells) - 1
            player["position"] = (player["position"] + 1) % len(self.cells)
            self.draw_board()
            if completed:
                self.moving = False
                self.finished = True
                self.roll_button.config(state="disabled")
                self.message_label.config(text=f"{player['name']} completou todo o percurso!")
                self.root.after(350, lambda: self.show_congratulations(player))
                return
            self.root.after(220, lambda: self.animate_player_move(player_index, total_steps, step + 1))
            return
        self.moving = False
        if self.special_effect_active:
            self.special_effect_active = False
            self.roll_button.config(state="normal")
            self.advance_turn(f"Efeito concluído. Nenhum ponto foi contabilizado. Agora é a vez do Jogador {self.current_player + 1}!")
        else:
            self.handle_landing(player_index)

    def handle_landing(self, player_index):
        if self.finished:
            return
        player = self.players[player_index]
        rule = HOUSE_RULES.get(player["position"], {"points": 1, "penalty": 1, "effect": "normal"})
        effect = rule["effect"]
        if effect == "advance":
            self.moving = True
            self.special_effect_active = True
            self.roll_button.config(state="disabled")
            self.message_label.config(text=f"{player['name']} caiu em +2 CASAS. Avançando automaticamente, sem pergunta!")
            self.animate_player_move(player_index, 2, 0)
        elif effect == "back":
            self.moving = True
            self.roll_button.config(state="disabled")
            self.message_label.config(text=f"{player['name']} caiu em -2 CASAS. Voltando automaticamente, sem pergunta!")
            self.animate_backward(player_index, 2, 0, lambda: self.finish_special_effect(player_index))
        elif effect == "skip":
            self.moving = False
            self.roll_button.config(state="normal")
            self.advance_turn(f"{player['name']} caiu em PASSA VEZ. Nenhum ponto foi contabilizado. Agora é a vez do Jogador {self.current_player + 1}!")
        else:
            self.roll_button.config(state="normal")
            self.message_label.config(text=f"{player['name']} chegou à casa {player['position'] + 1}. Resolva a questão!")
            self.root.after(250, self.ask_question)

    def finish_special_effect(self, player_index):
        self.moving = False
        self.roll_button.config(state="normal")
        self.advance_turn(f"Efeito concluído. Nenhum ponto foi contabilizado. Agora é a vez do Jogador {self.current_player + 1}!")

    def advance_turn(self, message=None):
        self.current_player = (self.current_player + 1) % len(self.players)
        self.update_turn(message or f"Agora é a vez do Jogador {self.current_player + 1}!")

    def animate_backward(self, player_index, total_steps, step, callback):
        player = self.players[player_index]
        if step < total_steps:
            player["position"] = (player["position"] - 1) % len(self.cells)
            self.draw_board()
            self.root.after(220, lambda: self.animate_backward(player_index, total_steps, step + 1, callback))
            return
        self.moving = False
        self.roll_button.config(state="normal")
        callback()

    def show_congratulations(self, winner):
        dialog = tk.Toplevel(self.root)
        dialog.title("Parabéns!")
        dialog.geometry("560x390")
        dialog.resizable(False, False)
        dialog.configure(bg="#173B55")
        dialog.transient(self.root)
        dialog.grab_set()
        tk.Label(dialog, text="★  PARABÉNS!  ★", font=("Arial", 28, "bold"), fg=YELLOW, bg="#173B55").pack(pady=(42, 16))
        tk.Label(dialog, text=f"{winner['name']}, parabéns!", font=("Arial", 22, "bold"), fg=winner["color"], bg="#173B55").pack(pady=6)
        tk.Label(dialog, text="Você chegou ao final do percurso!", font=("Arial", 15, "bold"), fg=TEXT, bg="#173B55").pack(pady=8)
        tk.Label(dialog, text=f"Pontuação final: {winner['score']} ponto(s)", font=("Arial", 12), fg=MUTED, bg="#173B55").pack(pady=4)
        def restart():
            dialog.destroy()
            self.players = []
            self.finished = False
            self.show_player_selection()
        tk.Button(dialog, text="NOVA PARTIDA", command=restart, font=("Arial", 13, "bold"), fg=BG, bg=GREEN, activebackground="#9BE7B5", relief="flat", padx=28, pady=12, cursor="hand2").pack(pady=28)
        dialog.protocol("WM_DELETE_WINDOW", restart)

    def ask_question(self):
        self.current_question = random.choice(QUESTIONS_BY_DIFFICULTY[self.difficulty])
        player = self.players[self.current_player]
        house_rule = HOUSE_RULES.get(player["position"], {"points": 1, "penalty": 1, "effect": "normal"})
        house_points = house_rule["points"]
        penalty = house_rule["penalty"]
        dialog = tk.Toplevel(self.root)
        dialog.title(f"Questão de {player['name']}")
        dialog.geometry("540x370")
        dialog.resizable(False, False)
        dialog.configure(bg=PANEL)
        dialog.transient(self.root)
        dialog.grab_set()
        tk.Label(dialog, text=f"{player['name'].upper()} • {self.current_question['tipo']}", font=("Arial", 12, "bold"), fg=player["color"], bg=PANEL).pack(pady=(23, 6))
        effect_text = EFFECT_LABELS[house_rule["effect"]]
        rule_text = f"Acertar: +{house_points} ponto(s)   •   Errar: -{penalty} ponto(s)"
        if effect_text:
            rule_text += f"   •   Efeito: {effect_text}"
        tk.Label(dialog, text=rule_text, font=("Arial", 10, "bold"), fg=YELLOW, bg=PANEL).pack(pady=3)
        tk.Label(dialog, text=self.current_question["pergunta"], wraplength=450, justify="center", font=("Arial", 17, "bold"), fg=TEXT, bg=PANEL).pack(pady=12)
        answer = tk.Entry(dialog, justify="center", font=("Arial", 16), bg="white", fg=BG, relief="flat")
        answer.pack(pady=10, ipadx=8, ipady=7)
        answer.focus_set()
        feedback = tk.Label(dialog, text="", wraplength=460, font=("Arial", 10), fg=MUTED, bg=PANEL)
        feedback.pack()
        answered = {"value": False}
        def next_turn(message=None):
            self.advance_turn(message or f"Turno registrado. Agora é a vez do Jogador {self.current_player + 1}!")
            if dialog.winfo_exists():
                dialog.destroy()


        def submit():
            if answered["value"]:
                return
            if normalize(answer.get()) == normalize(self.current_question["resposta"]):
                player["score"] += house_points
                feedback.config(text=f"Correto! Você ganhou +{house_points} ponto(s).", fg=GREEN)
                self.message_label.config(text=f"{player['name']} acertou! +{house_points} ponto(s).")
            else:
                player["score"] = max(0, player["score"] - penalty)
                feedback.config(text=f"Resposta incorreta. Dica: {self.current_question['dica']}  (-{penalty} ponto(s))", fg=RED)
                self.message_label.config(text=f"{player['name']} errou. Penalidade: -{penalty}.")
            answered["value"] = True
            self.update_scoreboard()
            answer.config(state="disabled")
            button.config(text="PRÓXIMO JOGADOR", command=next_turn, bg=BLUE)
        button = tk.Button(dialog, text="CONFERIR RESPOSTA", command=submit, font=("Arial", 11, "bold"), fg=BG, bg=GREEN, relief="flat", padx=18, pady=10, cursor="hand2")
        button.pack(pady=16)
        answer.bind("<Return>", lambda event: submit())


if __name__ == "__main__":
    root = tk.Tk()
    BancoMatematico(root)
    root.mainloop()
