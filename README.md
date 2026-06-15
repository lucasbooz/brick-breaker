# 🎮 Brick Breaker

Um jogo clássico de Brick Breaker (quebra-blocos) feito em Python com Pygame, desenvolvido como projeto de aprendizado.

![Status](https://img.shields.io/badge/status-em%20desenvolvimento-yellow)
![Python](https://img.shields.io/badge/python-3.x-blue)
![Pygame](https://img.shields.io/badge/pygame-2.x-green)

## 📋 Sobre o projeto

Este é meu primeiro projeto de jogo em Python, criado com o objetivo de aprender e praticar conceitos fundamentais de programação: estruturas de dados, lógica condicional, máquinas de estado, detecção de colisão e desenvolvimento incremental.

O projeto começou a partir de um tutorial e está sendo evoluído continuamente com novas mecânicas e melhorias.

## 🕹️ Como jogar

- **Setas (← →)**: move a prancha
- **ENTER**: inicia o jogo / joga novamente após o fim
- **ESC**: sai do jogo (na tela de fim)

**Objetivo**: destrua todos os blocos rebatendo a bola com a prancha, sem deixá-la cair. Você tem 3 vidas.

## ✨ Funcionalidades

- [x] Tela de início e tela de fim (vitória/derrota)
- [x] Sistema de vidas
- [x] Pontuação em tempo real
- [x] Dificuldade progressiva (a bola acelera conforme você avança)
- [x] Blocos coloridos por linha
- [x] Colisões precisas com detecção de lado (cima/baixo/lateral)
- [x] Controle de FPS consistente (60 FPS)
- [ ] Power-ups (bola múltipla, prancha grande/pequena, bola de fogo)
- [ ] Níveis com disposição aleatória de blocos
- [ ] Efeitos sonoros
- [ ] Menu de configurações

## 🔧 Tecnologias

- [Python 3](https://www.python.org/)
- [Pygame](https://www.pygame.org/)

## 🚀 Como executar

### Pré-requisitos

- Python 3 instalado ([python.org](https://www.python.org/downloads/))

### Passo a passo

```bash
# Clone o repositório
git clone https://github.com/lucasbooz/brick-breaker.git
cd brick-breaker

# Instale o Pygame
pip install pygame

# Execute o jogo
python brick_breaker.py
```

## 🧠 O que eu aprendi com este projeto

- Estruturas de dados em Python: listas, tuplas, dicionários e quando usar cada uma
- Máquinas de estado para organizar diferentes telas/fases de um programa
- Diferença entre eventos (`KEYDOWN`) e estado contínuo (`get_pressed()`) no Pygame
- Detecção de colisão entre retângulos (`colliderect`) e como determinar o lado da colisão
- Controle de frame rate com `pygame.time.Clock`
- Boas práticas de organização de código e versionamento com Git

## 📝 Licença

Este projeto está sob a licença MIT — sinta-se livre para usar, estudar e modificar.

## 🙋 Sobre

Projeto desenvolvido como parte do meu aprendizado em programação.

---

Feito com 💙 e bastante curiosidade.
