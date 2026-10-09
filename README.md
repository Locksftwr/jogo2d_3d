# 🎲 Banco Matemático 3D

Um jogo de tabuleiro 3D interativo e cinematográfico de perguntas e respostas matemáticas, desenvolvido em **Python** utilizando a engine de jogos **Ursina**. Criado para feiras de matemática e competições pedagógicas.

---

## 📋 Pré-requisitos

Antes de começar, certifique-se de ter o **Python** instalado em seu computador (versão **3.10** ou superior).

Para verificar se o Python e o gerenciador de pacotes `pip` estão instalados, abra o terminal (PowerShell ou CMD) e digite:

```bash
python --version
pip --version
```

> **Dica:** Ao instalar o Python no Windows, certifique-se de marcar a caixa **"Add Python to PATH"** na primeira tela do instalador.

---

## 🚀 Como Baixar e Instalar as Bibliotecas Necessárias

O jogo utiliza a biblioteca **Ursina Engine** (que já inclui internamente as dependências 3D como Panda3D, Pillow e suporte a áudio OpenAL).

### Método 1: Instalação Rápida (Direta)

Abra o terminal na pasta onde o jogo está localizado e execute o seguinte comando:

```bash
pip install -r requirements.txt
```

Ou instale a biblioteca diretamente:

```bash
pip install ursina
```

---

### Método 2: Usando Ambiente Virtual (Recomendado)

Criar um ambiente virtual isola as bibliotecas deste projeto e evita conflitos com outras instalações do seu sistema:

#### 1. Criar o ambiente virtual:
```bash
python -m venv .venv
```

#### 2. Ativar o ambiente virtual:

- **No Windows (PowerShell):**
  ```powershell
  .venv\Scripts\Activate.ps1
  ```
  *(Se aparecer erro de permissão no PowerShell, execute antes: `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned`)*

- **No Windows (Prompt de Comando / CMD):**
  ```cmd
  .venv\Scripts\activate.bat
  ```

- **No Linux / macOS:**
  ```bash
  source .venv/bin/activate
  ```

#### 3. Instalar as bibliotecas no ambiente ativado:
```bash
pip install -r requirements.txt
```

---

## 🎮 Como Iniciar o Jogo

Com as bibliotecas instaladas, inicie o jogo com o comando:

```bash
python banco_matematico_3d.py
```

---

## ⌨️ Controles e Atalhos

| Comando | Ação |
| :--- | :--- |
| <kbd>Espaço</kbd> | Rola o dado 3D / Gira a Roleta da Sorte |
| <kbd>Enter</kbd> | Confere a resposta digitada / Avança para a vez do próximo jogador |
| <kbd>W</kbd>, <kbd>A</kbd>, <kbd>S</kbd>, <kbd>D</kbd> ou <kbd>Setas</kbd> | Gira e orbita a câmera 3D ao redor do tabuleiro |
| <kbd>Scroll do Mouse</kbd> | Aproxima e afasta o zoom da câmera |
| <kbd>C</kbd> | Liga / Desliga a Câmera Cinematográfica Dinâmica |
| <kbd>R</kbd> | Restaura a câmera para a posição padrão de visão geral |
| <kbd>Clique com o Mouse</kbd> | Clica nos botões da interface ou inspeciona qualquer casa do tabuleiro |

---

## ✨ Recursos Especiais do Jogo

- 🏆 **Peões Metálicos Nobres:** Acabamento em Ouro, Prata, Cobre e Bronze dependendo da quantidade de competidores.
- 🔥 **Modo Overdrive (Combo x3):** Ao acertar 3 perguntas seguidas e atingir o multiplicador máximo de pontos, o tabuleiro escurece suavemente e a casa do jogador passa a piscar intensamente em chamas neon.
- 🎰 **Casas de "Roleta da Sorte" (Douradas):** Casas especiais onde o jogador gira o dado em busca de sorte: tirar de 1 a 3 perde 5 pontos, tirar de 4 a 6 fatura 10 pontos instantâneos com comemoração.
- 🔊 **Feedback Sonoro Completo (SFX):** Sons de rolagem de pedra do dado, salto elástico ("boing") do peão, alarme sonoro na contagem regressiva dos últimos 5 segundos vermelhos e moeda retro de vitória nos acertos.
- 🥇 **Grande Troféu 3D:** Ergue-se no centro do tabuleiro ao lado do logotipo comemorativo da UESPI quando um jogador vence a partida.
- ⏱️ **Tempo de Resposta Dinâmico:** 30 segundos nos níveis Fácil e Médio, e 45 segundos no nível Difícil, com barra de progresso gradiente (Verde ➔ Amarelo ➔ Vermelho) posicionada abaixo do campo de resposta.
- 📜 **Placar de Recordes:** Salva a pontuação de todos os participantes no arquivo `leaderboard.json`.

---

## ❓ Solução de Dúvidas e Problemas

1. **`'pip' não é reconhecido como comando interno ou externo`**:
   - Reinstale o Python marcando a opção **"Add Python to PATH"** ou adicione o caminho do Python manualmente nas Variáveis de Ambiente do Windows.
2. **`Script de ativação do PowerShell bloqueado`**:
   - Abra o PowerShell como Administrador ou usuário atual e rode:
     ```powershell
     Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
     ```
3. **Sem som ou som baixo**:
   - O jogo utiliza a biblioteca nativa OpenAL do Panda3D/Ursina. Verifique se o volume de saída do seu sistema e caixas de som/fones estão ativos.

