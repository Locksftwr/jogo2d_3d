# jogo2d_3d
# Banco Matemático 3D

Jogo de tabuleiro educativo de matemática em 3D, feito em Python com a [Ursina Engine](https://www.ursinaengine.org/). De 1 a 4 jogadores rodam o dado, andam pelo tabuleiro e resolvem perguntas para ganhar pontos.

> **Nota:** este é um protótipo com visual simples (cubos, esferas e botões). Ele é a versão 3D de um jogo que originalmente foi feito em tkinter.

## Como jogar

1. Escolha a quantidade de jogadores (1 a 4).
2. Escolha a dificuldade das perguntas.
3. Na sua vez, clique em **RODAR O DADO**. O peão anda casa a casa.
4. Ao parar em uma casa normal, responda a pergunta:
   - **Acertou:** ganha os pontos da casa.
   - **Errou:** perde a penalidade da casa (a pontuação nunca fica abaixo de 0) e vê uma dica.
5. Quem completar todo o percurso e voltar à casa de **INÍCIO/CHEGADA** vence a partida.

### Casas especiais

| Efeito | O que acontece |
|--------|----------------|
| `advance` (+2) | O peão avança 2 casas automaticamente, sem pergunta |
| `back` (-2) | O peão volta 2 casas automaticamente, sem pergunta |
| `skip` (PASSA) | Passa a vez, sem pergunta |

### Controles

- **Mouse:** botões de menu, dado e resposta.
- **Enter:** confere a resposta e avança para o próximo jogador.

## Requisitos

- Python 3.8 ou superior
- [Ursina](https://www.ursinaengine.org/)

```bash
pip install ursina
```

## Como executar

```bash
python banco_matematico_3d.py
```

O arquivo `questions_by_difficulty.py` precisa estar na mesma pasta do jogo.

## Estrutura do projeto

```
.
├── banco_matematico_3d.py   # o jogo
├── questions_by_difficulty.py    # perguntas, dificuldades e regras das casas
└── README.md
```

## Personalizando perguntas e regras

Tudo fica no `questions_by_difficulty.py`, que precisa definir três coisas:

```python
# Lista de (valor, texto do botão)
DIFFICULTY_LABELS = [("fácil", "Fácil"), ("médio", "Médio"), ("difícil", "Difícil")]

# Perguntas por dificuldade (as chaves são os valores acima)
QUESTIONS_BY_DIFFICULTY = {
    "fácil": [
        {"tipo": "Soma", "pergunta": "Quanto é 2 + 2?", "resposta": "4", "dica": "É um número par."},
    ],
    "médio": [...],
    "difícil": [...],
}

# Regras por casa (índice começa em 0). Casas não listadas usam +1 ponto / -1 de penalidade
HOUSE_RULES = {
    5:  {"points": 2, "penalty": 1, "effect": "normal"},
    8:  {"points": 0, "penalty": 0, "effect": "advance"},   # normal | advance | back | skip
}
```

As respostas são comparadas ignorando maiúsculas, minúsculas e espaços.

## Sobre o tabuleiro

O tabuleiro tem 30 casas em formato de retângulo. A casa 0 é ao mesmo tempo o **INÍCIO** e a **CHEGADA**.

## Limitações conhecidas

- Visual simples, por ser um protótipo.
- Não há tela para digitar o nome dos jogadores (eles se chamam Jogador 1, 2, 3 e 4).
- Não há sons nem efeitos além do giro do dado e do movimento dos peões.
