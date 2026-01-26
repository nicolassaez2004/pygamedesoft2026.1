import pygame

def inicializa():
    bg = pygame.image.load('sprite/fundodepedra.jpg')
    plataforma = pygame.image.load('sprite/plataforma.jpg')

    player = pygame.image.load('sprite/player.jpg')
    wizard = pygame.image.load('sprite/wizard.jpg')
    skeleton = pygame.image.load('sprite/skeleton.jpg')
    knight = pygame.image.load('sprite/knight.jpg')

    assets = {}
    assets = ['bg'] = bg
    assets = ['plataforma'] = plataforma
    assets = ['player'] = player
    assets = ['wizard'] = wizard
    assets = ['skeleton'] = skeleton
    assets = ['knight'] = knight

    return assets

def desenha(window, assets):
    window.fill((0, 0, 0))
    window.blit(assets['bg'], (0, 0))
    window.blit(assets['player'], (640, 360))

def gameplay_loop(window, clock, player):
    player_pos = player

    dt = 0

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "quit"

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return "leaderboard"  # fim do jogo por enquanto / vamo mudar isso depois

        #wasd mov básica e sem alma
        keys = pygame.key.get_pressed()

        if keys[pygame.K_w]:
            player_pos.y -= 300 * dt
        if keys[pygame.K_s]:
            player_pos.y += 300 * dt
        if keys[pygame.K_a]:
            player_pos.x -= 300 * dt
        if keys[pygame.K_d]:
            player_pos.x += 300 * dt

        pygame.display.flip()
        dt = clock.tick(60) / 1000
