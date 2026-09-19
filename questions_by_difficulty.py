#Adicione novas questões dentro da lista da dificuldade correspondente.
#Cada questão precisa ter tipo, pergunta, resposta, dica e penalidade.


QUESTIONS_BY_DIFFICULTY = {
    "fácil": [
        {"tipo": "ADIÇÃO", "pergunta": "Quanto é 7 + 5?", "resposta": "12", "dica": "Conte cinco depois do sete.", "penalidade": 1},
        {"tipo": "SUBTRAÇÃO", "pergunta": "Quanto é 20 - 8?", "resposta": "12", "dica": "Retire oito unidades do vinte.", "penalidade": 1},
        {"tipo": "MULTIPLICAÇÃO", "pergunta": "Quanto é 4 × 6?", "resposta": "24", "dica": "Some o 4 seis vezes.", "penalidade": 1},
        {"tipo": "GEOMETRIA", "pergunta": "Quantos lados tem um triângulo?", "resposta": "3", "dica": "Tri significa três.", "penalidade": 1},
        {"tipo": "MEDIDAS", "pergunta": "Quantos centímetros há em 1 metro?", "resposta": "100", "dica": "Um metro possui cem centímetros.", "penalidade": 1},
    ],
    "médio": [
        {"tipo": "FRAÇÕES", "pergunta": "Quanto é 3/4 + 1/4?", "resposta": "1", "dica": "Os denominadores são iguais.", "penalidade": 2},
        {"tipo": "ÁLGEBRA", "pergunta": "Se 2x + 4 = 10, qual é o valor de x?", "resposta": "3", "dica": "Subtraia 4 e depois divida por 2.", "penalidade": 2},
        {"tipo": "PORCENTAGEM", "pergunta": "Quanto é 25% de 80?", "resposta": "20", "dica": "25% é a mesma coisa que 1/4.", "penalidade": 2},
        {"tipo": "EXPRESSÕES", "pergunta": "Resolva: 5 + 2 × 3", "resposta": "11", "dica": "A multiplicação vem antes da adição.", "penalidade": 2},
        {"tipo": "PROBABILIDADE", "pergunta": "Qual a probabilidade de sair 6 em um dado? (fração)", "resposta": "1/6", "dica": "Há um resultado favorável entre seis.", "penalidade": 2},
    ],
    "difícil": [
        {"tipo": "EQUAÇÃO", "pergunta": "Resolva: 3x - 7 = 20.", "resposta": "9", "dica": "Some 7 e depois divida por 3.", "penalidade": 3},
        {"tipo": "ÁREA", "pergunta": "Qual é a área de um retângulo de 12 cm por 5 cm?", "resposta": "60", "dica": "Área é base vezes altura.", "penalidade": 3},
        {"tipo": "RAZÃO", "pergunta": "Se 4 cadernos custam 28 reais, quanto custa cada um?", "resposta": "7", "dica": "Divida 28 por 4.", "penalidade": 3},
        {"tipo": "POTENCIAÇÃO", "pergunta": "Quanto é 2^5?", "resposta": "32", "dica": "Multiplique o 2 cinco vezes.", "penalidade": 3},
        {"tipo": "FRAÇÕES", "pergunta": "Quanto é 2/3 × 9?", "resposta": "6", "dica": "Multiplique 2 por 9 e divida por 3.", "penalidade": 3},
    ],
}

DIFFICULTY_LABELS = [
    ("fácil", "FÁCIL"),
    ("médio", "MÉDIO"),
    ("difícil", "DIFÍCIL"),
]

HOUSE_RULES = {
    1: {"points": 1, "penalty": 1, "effect": "normal"},
    2: {"points": 2, "penalty": 1, "effect": "normal"},
    3: {"points": 3, "penalty": 2, "effect": "normal"},
    4: {"points": 2, "penalty": 1, "effect": "advance"},
    5: {"points": 4, "penalty": 2, "effect": "normal"},
    6: {"points": 1, "penalty": 1, "effect": "normal"},
    7: {"points": 3, "penalty": 2, "effect": "normal"},
    8: {"points": 5, "penalty": 3, "effect": "normal"},
    9: {"points": 2, "penalty": 1, "effect": "back"},
    10: {"points": 4, "penalty": 2, "effect": "normal"},
    11: {"points": 1, "penalty": 1, "effect": "skip"},
    12: {"points": 3, "penalty": 2, "effect": "normal"},
    13: {"points": 5, "penalty": 3, "effect": "normal"},
    14: {"points": 2, "penalty": 1, "effect": "normal"},
    15: {"points": 4, "penalty": 2, "effect": "advance"},
    16: {"points": 1, "penalty": 1, "effect": "normal"},
    17: {"points": 3, "penalty": 2, "effect": "normal"},
    18: {"points": 5, "penalty": 3, "effect": "normal"},
    19: {"points": 2, "penalty": 1, "effect": "back"},
    20: {"points": 4, "penalty": 2, "effect": "normal"},
    21: {"points": 1, "penalty": 1, "effect": "skip"},
    22: {"points": 3, "penalty": 2, "effect": "normal"},
    23: {"points": 5, "penalty": 3, "effect": "normal"},
    24: {"points": 2, "penalty": 1, "effect": "normal"},
    25: {"points": 4, "penalty": 2, "effect": "advance"},
    26: {"points": 1, "penalty": 1, "effect": "normal"},
    27: {"points": 3, "penalty": 2, "effect": "normal"},
    28: {"points": 5, "penalty": 3, "effect": "normal"},
    29: {"points": 2, "penalty": 1, "effect": "back"},
}
