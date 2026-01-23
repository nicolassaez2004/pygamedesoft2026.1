import pygame

#nada aqui ainda
def leaderboard_loop(window, clock):

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "quit"

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    return "menu"
                if event.key == pygame.K_ESCAPE:
                    return "quit"

        window.fill((0, 0, 0))

        pygame.display.flip()
        clock.tick(60)
