import pygame
import math
import numpy as np

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

# ── Configurações dos objetos ──────────────────────────────────────────────────
tamanho_bola = 15
tamanho_jogador = 100

qtde_blocos_linha = 8
qtde_linhas_blocos = 5
qtde_total_blocos = qtde_blocos_linha * qtde_linhas_blocos

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

bola = pygame.Rect(100, 500, tamanho_bola, tamanho_bola)
jogador = pygame.Rect(350, 750, tamanho_jogador, 15)
blocos = []
movimento_bola = [3.0, -3.0]
velocidade_jogador = 5
ultima_pontuacao_acelerada = 0
vidas = 3


# ── Funções de criação ─────────────────────────────────────────────────────────
def criar_blocos(qtde_blocos_linha, qtde_linhas_blocos):
    largura_tela = tamanho_tela[0]
    distancia_entre_blocos = 5
    largura_bloco = largura_tela / 8 - distancia_entre_blocos
    altura_bloco = 15
    distancia_entre_linhas = altura_bloco + 10

    blocos = []
    for j in range(qtde_linhas_blocos):
        cor_da_linha = cores_blocos[j % len(cores_blocos)]
        for i in range(qtde_blocos_linha):
            bloco = pygame.Rect(
                i * (largura_bloco + distancia_entre_blocos),
                j * distancia_entre_linhas,
                largura_bloco,
                altura_bloco
            )
            blocos.append((bloco, cor_da_linha))
    return blocos


def reiniciar_jogo():
    global bola, jogador, blocos, movimento_bola, velocidade_jogador, ultima_pontuacao_acelerada, vidas
    bola = pygame.Rect(100, 500, tamanho_bola, tamanho_bola)
    jogador = pygame.Rect(350, 750, tamanho_jogador, 15)
    blocos = criar_blocos(qtde_blocos_linha, qtde_linhas_blocos)
    movimento_bola = [3.0, -3.0]
    velocidade_jogador = 5
    ultima_pontuacao_acelerada = 0
    vidas = 3


# ── Funções de desenho ─────────────────────────────────────────────────────────
def desenhar_tela_inicio():
    tela.fill(cores["preta"])

    fonte_titulo = pygame.font.Font(None, 80)
    fonte_sub = pygame.font.Font(None, 36)

    titulo = fonte_titulo.render("BRICK BREAKER", True, cores["amarela"])
    sub = fonte_sub.render("Pressione ENTER para jogar", True, cores["cinza"])
    teclas = fonte_sub.render("< > para mover a prancha", True, cores["cinza"])

    tela.blit(titulo, titulo.get_rect(center=(tamanho_tela[0] // 2, 320)))
    tela.blit(sub,    sub.get_rect(center=(tamanho_tela[0] // 2, 430)))
    tela.blit(teclas, teclas.get_rect(center=(tamanho_tela[0] // 2, 475)))


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
        som_raquete.play()

    for item in blocos:
        bloco, cor = item
        if bloco.colliderect(bola):
            blocos.remove(item)
            som_bloco.play()
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


def atualizar_pontuacao(pontuacao):
    fonte = pygame.font.Font(None, 30)
    texto = fonte.render(f"Pontuação: {pontuacao}", True, cores["amarela"])
    tela.blit(texto, (0, 770))


def atualizar_vidas(vidas):
    fonte = pygame.font.Font(None, 30)
    texto = fonte.render(f"Vidas: {vidas}", True, cores["vermelho"])
    tela.blit(texto, (700, 770))


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

    # ── Jogando ──
    elif estado == "jogando":
        pontuacao_atual = qtde_total_blocos - len(blocos)

        desenhar_jogo()
        desenhar_blocos(blocos)
        atualizar_pontuacao(pontuacao_atual)
        atualizar_vidas(vidas)
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
            som_vitoria.play()
            motivo_fim = "vitoria"
            estado = "fim"

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
