import pygame


def gameplay_loop(window, clock):
    player_pos = pygame.Vector2(
        window.get_width() / 2,
        window.get_height() / 2
    )

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

        window.fill((0, 40, 0))
        pygame.draw.circle(window, (255, 255, 255), player_pos, 40) #trocar pelo sprite do player no futuro

        pygame.display.flip()
        dt = clock.tick(60) / 1000
