import pygame
import math
import numpy as np
import random

pygame.init()
pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)

# ── Sons sintéticos ────────────────────────────────────────────────────────────


def gerar_som(frequencia, duracao, volume=0.3):
    sample_rate = 44100
    frames = int(duracao * sample_rate)
    t = np.linspace(0, duracao, frames)
    onda = np.sin(2 * np.pi * frequencia * t)
    fade = int(frames * 0.1)
    onda[-fade:] *= np.linspace(1, 0, fade)
    onda = (onda * volume * 32767).astype(np.int16)
    onda_stereo = np.column_stack([onda, onda])
    return pygame.sndarray.make_sound(onda_stereo)


som_raquete = gerar_som(frequencia=300, duracao=0.08)
som_bloco = gerar_som(frequencia=600, duracao=0.06)
som_vida = gerar_som(frequencia=120, duracao=0.4)
som_vitoria = gerar_som(frequencia=900, duracao=0.5,
                        volume=0.4)


# ── Configurações da tela ──────────────────────────────────────────────────────
tamanho_tela = (800, 800)
tela = pygame.display.set_mode(tamanho_tela)
pygame.display.set_caption("Brick Breaker")
clock = pygame.time.Clock()

# Configurações dos objetos ──────────────────────────────────────────────────
tamanho_bola = 15
tamanho_jogador = 100
qtde_total_blocos = 40

cores = {
    "branca":  (255, 255, 255),
    "preta":   (0,   0,   0),
    "amarela": (255, 255, 0),
    "azul":    (0,   0,   255),
    "verde":   (0,   255, 0),
    "cinza":   (180, 180, 180),
    "vermelho": (220, 50,  50),
}

cores_blocos = [
    cores["vermelho"],
    cores["amarela"],
    cores["verde"],
    cores["azul"],
    cores["branca"],
]

# ── Estado global do jogo ──────────────────────────────────────────────────────
estado = "inicio"
motivo_fim = ""
nivel = 1
blocos_do_nivel = 0

config = {
    "som":        True,
    "dificuldade": "normal"
}

opcao_selecionada = 0

bola = pygame.Rect(100, 500, tamanho_bola, tamanho_bola)
jogador = pygame.Rect(350, 750, tamanho_jogador, 15)
blocos = []
movimento_bola = [3.0, -3.0]
velocidade_jogador = 5
ultima_pontuacao_acelerada = 0
vidas = 3


# ── Funções de criação ─────────────────────────────────────────────────────────
def criar_blocos(nivel):
    largura_tela = tamanho_tela[0]
    distancia_entre_blocos = 5
    largura_bloco = largura_tela / 8 - distancia_entre_blocos
    altura_bloco = 15
    distancia_entre_linhas = altura_bloco + 10
    qtde_colunas = 8
    qtde_linhas = 5

    chance = min(0.30 + (nivel - 1) * 0.15, 1.0)

    def fazer_bloco(i, j):
        cor = cores_blocos[j % len(cores_blocos)]
        bloco = pygame.Rect(
            i * (largura_bloco + distancia_entre_blocos),
            j * distancia_entre_linhas,
            largura_bloco,
            altura_bloco
        )
        return (bloco, cor)

    blocos = []
    for j in range(qtde_linhas):
        for i in range(qtde_colunas // 2):
            if random.random() < chance:
                blocos.append(fazer_bloco(i, j))
                blocos.append(fazer_bloco(qtde_colunas - 1 - i, j))

    while len(blocos) < 4:
        j = random.randint(0, qtde_linhas - 1)
        i = random.randint(0, qtde_colunas // 2 - 1)
        blocos.append(fazer_bloco(i, j))
        blocos.append(fazer_bloco(qtde_colunas - 1 - i, j))

    return blocos


def reiniciar_jogo():
    global bola, jogador, blocos, movimento_bola, velocidade_jogador, ultima_pontuacao_acelerada, vidas, nivel, blocos_do_nivel

    velocidades = {"facil": 2.0, "normal": 3.0, "dificil": 4.0}
    niveis_inicio = {"facil": 1, "normal": 1, "dificil": 3}
    vel = velocidades[config["dificuldade"]]

    nivel = niveis_inicio[config["dificuldade"]]
    bola = pygame.Rect(100, 500, tamanho_bola, tamanho_bola)
    jogador = pygame.Rect(350, 750, tamanho_jogador, 15)
    blocos = criar_blocos(nivel)
    blocos_do_nivel = len(blocos)
    movimento_bola = [vel, -vel]
    velocidade_jogador = 5
    ultima_pontuacao_acelerada = 0
    vidas = 3


def avancar_nivel():
    global bola, blocos, nivel, ultima_pontuacao_acelerada, blocos_do_nivel
    nivel += 1
    bola = pygame.Rect(100, 500, tamanho_bola, tamanho_bola)
    blocos = criar_blocos(nivel)
    blocos_do_nivel = len(blocos)
    ultima_pontuacao_acelerada = 0


# ── Funções de desenho ─────────────────────────────────────────────────────────
def desenhar_tela_inicio():
    tela.fill(cores["preta"])

    fonte_titulo = pygame.font.Font(None, 80)
    fonte_sub = pygame.font.Font(None, 36)

    titulo = fonte_titulo.render("BRICK BREAKER", True, cores["amarela"])
    sub = fonte_sub.render("Pressione ENTER para jogar", True, cores["cinza"])
    teclas = fonte_sub.render("< > para mover a prancha", True, cores["cinza"])
    config_hint = fonte_sub.render(
        "C  para configurações", True, cores["cinza"])

    tela.blit(titulo,      titulo.get_rect(center=(tamanho_tela[0] // 2, 280)))
    tela.blit(sub,         sub.get_rect(center=(tamanho_tela[0] // 2, 390)))
    tela.blit(teclas,      teclas.get_rect(center=(tamanho_tela[0] // 2, 435)))
    tela.blit(config_hint, config_hint.get_rect(
        center=(tamanho_tela[0] // 2, 480)))


def desenhar_tela_fim(motivo):
    tela.fill(cores["preta"])

    fonte_titulo = pygame.font.Font(None, 80)
    fonte_sub = pygame.font.Font(None, 36)

    if motivo == "vitoria":
        msg = "VOCÊ GANHOU!"
        cor = cores["verde"]
    else:
        msg = "GAME OVER"
        cor = cores["vermelho"]

    titulo = fonte_titulo.render(msg, True, cor)
    reinicia = fonte_sub.render(
        "Pressione ENTER para jogar de novo", True, cores["cinza"])
    sair = fonte_sub.render("Pressione ESC para sair", True, cores["cinza"])

    tela.blit(titulo,   titulo.get_rect(center=(tamanho_tela[0] // 2, 320)))
    tela.blit(reinicia, reinicia.get_rect(center=(tamanho_tela[0] // 2, 430)))
    tela.blit(sair,     sair.get_rect(center=(tamanho_tela[0] // 2, 475)))


def desenhar_tela_config():
    tela.fill(cores["preta"])

    fonte_titulo = pygame.font.Font(None, 60)
    fonte_opcao = pygame.font.Font(None, 40)
    fonte_dica = pygame.font.Font(None, 28)

    titulo = fonte_titulo.render("CONFIGURAÇÕES", True, cores["amarela"])
    tela.blit(titulo, titulo.get_rect(center=(tamanho_tela[0] // 2, 200)))

    opcoes = [
        ("Som", "Ligado" if config["som"] else "Desligado"),
        ("Dificuldade", config["dificuldade"].capitalize()),
    ]

    for idx, (label, valor) in enumerate(opcoes):
        cor_texto = cores["amarela"] if idx == opcao_selecionada else cores["cinza"]
        prefixo = ">>  " if idx == opcao_selecionada else "    "
        linha = fonte_opcao.render(
            f"{prefixo}{label}:  {valor}", True, cor_texto)
        tela.blit(linha, linha.get_rect(
            center=(tamanho_tela[0] // 2, 340 + idx * 80)))

    dica = fonte_dica.render(
        "W S navegar   <> ou ENTER alterar   ESC voltar", True, cores["cinza"])
    tela.blit(dica, dica.get_rect(center=(tamanho_tela[0] // 2, 580)))


def processar_input_config(evento):
    global opcao_selecionada
    dificuldades = ["facil", "normal", "dificil"]

    if evento.type == pygame.KEYDOWN:
        if evento.key == pygame.K_UP:
            opcao_selecionada = (opcao_selecionada - 1) % 2
        if evento.key == pygame.K_DOWN:
            opcao_selecionada = (opcao_selecionada + 1) % 2

        if evento.key in (pygame.K_RETURN, pygame.K_LEFT, pygame.K_RIGHT):
            if opcao_selecionada == 0:
                config["som"] = not config["som"]
            elif opcao_selecionada == 1:
                idx_atual = dificuldades.index(config["dificuldade"])
                if evento.key == pygame.K_LEFT:
                    config["dificuldade"] = dificuldades[(
                        idx_atual - 1) % len(dificuldades)]
                else:
                    config["dificuldade"] = dificuldades[(
                        idx_atual + 1) % len(dificuldades)]


def tocar_som(som):
    if config["som"]:
        som.play()


def desenhar_jogo():
    tela.fill(cores["preta"])
    pygame.draw.rect(tela, cores["azul"],   jogador)
    pygame.draw.rect(tela, cores["branca"], bola)


def desenhar_blocos(blocos):
    for bloco, cor in blocos:
        pygame.draw.rect(tela, cor, bloco)


# ── Funções de lógica ──────────────────────────────────────────────────────────
def movimentar_jogador():
    teclas = pygame.key.get_pressed()
    if teclas[pygame.K_RIGHT]:
        if (jogador.x + tamanho_jogador) < tamanho_tela[0]:
            jogador.x += int(velocidade_jogador)
    if teclas[pygame.K_LEFT]:
        if jogador.x > 0:
            jogador.x -= int(velocidade_jogador)


def movimentar_bola(bola):
    movimento = movimento_bola
    bola.x += int(movimento[0])
    bola.y += int(movimento[1])

    if bola.x <= 0:
        movimento[0] = abs(movimento[0])
    if bola.x + tamanho_bola >= tamanho_tela[0]:
        movimento[0] = -abs(movimento[0])
    if bola.y <= 0:
        movimento[1] = abs(movimento[1])
    if bola.y + tamanho_bola >= tamanho_tela[1]:
        global vidas
        vidas -= 1
        som_vida.play()
        if vidas <= 0:
            return None
        bola.x, bola.y = 100, 500
        movimento[0] = abs(movimento[0])
        movimento[1] = -abs(movimento[1])
        return movimento

    if jogador.colliderect(bola):
        movimento[1] = -abs(movimento[1])
        tocar_som(som_raquete)

    for item in blocos:
        bloco, cor = item
        if bloco.colliderect(bola):
            blocos.remove(item)
            tocar_som(som_bloco)
            overlap_x = min(bola.right, bloco.right) - \
                max(bola.left, bloco.left)
            overlap_y = min(bola.bottom, bloco.bottom) - \
                max(bola.top, bloco.top)
            if overlap_x < overlap_y:
                movimento[0] = -movimento[0]
            else:
                movimento[1] = -movimento[1]
            break

    return movimento


def atualizar_hud(pontuacao, vidas, nivel):
    fonte = pygame.font.Font(None, 30)
    texto_pont = fonte.render(
        f"Pontuação: {pontuacao}", True, cores["amarela"])
    texto_vidas = fonte.render(f"Vidas: {vidas}", True, cores["vermelho"])
    texto_nivel = fonte.render(f"Nível: {nivel}", True, cores["cinza"])
    tela.blit(texto_pont,  (0, 770))
    tela.blit(texto_nivel, (360, 770))
    tela.blit(texto_vidas, (680, 770))


def aumentar_velocidade(pontuacao):
    global velocidade_jogador, ultima_pontuacao_acelerada
    VELOCIDADE_MAXIMA = 7.0
    if pontuacao % 5 == 0 and pontuacao > 0 and pontuacao != ultima_pontuacao_acelerada:
        if abs(movimento_bola[0]) < VELOCIDADE_MAXIMA:
            movimento_bola[0] = math.copysign(
                abs(movimento_bola[0]) + 0.4, movimento_bola[0])
            movimento_bola[1] = math.copysign(
                abs(movimento_bola[1]) + 0.4, movimento_bola[1])
            velocidade_jogador += 0.4
        ultima_pontuacao_acelerada = pontuacao


# ── Loop principal ─────────────────────────────────────────────────────────────
reiniciar_jogo()

while True:
    # ── Tela de início ──
    if estado == "inicio":
        desenhar_tela_inicio()
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                exit()
            if evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_RETURN:
                    estado = "jogando"
                if evento.key == pygame.K_c:
                    estado = "config"

    # ── Configurações ──
    elif estado == "config":
        desenhar_tela_config()
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                exit()
            if evento.type == pygame.KEYDOWN and evento.key == pygame.K_ESCAPE:
                estado = "inicio"
            else:
                processar_input_config(evento)

    # ── Jogando ──
    elif estado == "jogando":
        pontuacao_atual = blocos_do_nivel - len(blocos)

        desenhar_jogo()
        desenhar_blocos(blocos)
        atualizar_hud(pontuacao_atual, vidas, nivel)
        aumentar_velocidade(pontuacao_atual)

        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                exit()

        movimentar_jogador()
        movimento_bola = movimentar_bola(bola)

        if not movimento_bola:
            motivo_fim = "derrota"
            estado = "fim"
        elif len(blocos) == 0:
            tocar_som(som_vitoria)
            avancar_nivel()

    # ── Tela de fim ──
    elif estado == "fim":
        desenhar_tela_fim(motivo_fim)
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                exit()
            if evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_RETURN:
                    reiniciar_jogo()
                    estado = "jogando"
                if evento.key == pygame.K_ESCAPE:
                    pygame.quit()
                    exit()

    clock.tick(60)
    pygame.display.flip()
