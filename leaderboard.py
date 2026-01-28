import pygame

def leaderboard_loop(window, clock):
    """Tela de leaderboard que permite voltar ao menu"""
    
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "quit"

            if event.type == pygame.KEYDOWN:
                # ESC ou ENTER volta ao menu
                if event.key == pygame.K_RETURN or event.key == pygame.K_ESCAPE:
                    return "menu"

        # Preenche com fundo preto para evitar tela preta vazia
        window.fill((20, 20, 40))
        
        # Título
        font_title = pygame.font.SysFont('Arial', 80, bold=True)
        title = font_title.render("PLACAR", True, (255, 215, 0))
        window.blit(title, (640 - title.get_width() // 2, 100))
        
        # Mensagem
        font_text = pygame.font.SysFont('Arial', 40)
        text = font_text.render("Placar em breve...", True, (200, 200, 200))
        window.blit(text, (640 - text.get_width() // 2, 350))
        
        # Instrução
        font_small = pygame.font.SysFont('Arial', 30)
        instruction = font_small.render("Pressione ENTER ou ESC para voltar ao menu", True, (150, 150, 170))
        window.blit(instruction, (640 - instruction.get_width() // 2, 600))

        pygame.display.flip()
        clock.tick(60)
