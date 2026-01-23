import pygame

def menu_loop(window, clock):
    #fonte qualquer
    font_titulo = pygame.font.SysFont(None, 80)
    font_opcao = pygame.font.SysFont(None, 45)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "quit"

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    return "gameplay"
                if event.key == pygame.K_ESCAPE:
                    return "quit"


        #mudar depois obviamente, sem design aqui ainda
        window.fill((0, 0, 0))

        titulo = font_titulo.render("PITAGORAS OPS", True, (255, 255, 255))
        jogar = font_opcao.render("ENTER - Jogar", True, (200, 200, 200))
        sair = font_opcao.render("ESC - Sair", True, (200, 200, 200))

        window.blit(titulo, (640 - titulo.get_width() // 2, 220))
        window.blit(jogar, (640 - jogar.get_width() // 2, 360))
        window.blit(sair, (640 - sair.get_width() // 2, 420))

        pygame.display.flip()
        clock.tick(60)
