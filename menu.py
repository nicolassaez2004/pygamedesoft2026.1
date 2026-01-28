import pygame
import math

def draw_gradient_rect(surface, color1, color2, rect):
    """Desenha um retângulo com gradiente vertical"""
    for y in range(rect.height):
        ratio = y / rect.height
        r = int(color1[0] * (1 - ratio) + color2[0] * ratio)
        g = int(color1[1] * (1 - ratio) + color2[1] * ratio)
        b = int(color1[2] * (1 - ratio) + color2[2] * ratio)
        pygame.draw.line(surface, (r, g, b), (rect.x, rect.y + y), (rect.x + rect.width, rect.y + y))

def menu_loop(window, clock):
    # Fontes melhoradas
    font_titulo = pygame.font.SysFont('Arial', 100, bold=True)
    font_opcao = pygame.font.SysFont('Arial', 50)
    font_subtitle = pygame.font.SysFont('Arial', 30, italic=True)

    # Animação do título
    titulo_offset = 0
    time = 0
    
    # Índice da opção selecionada
    selected_option = 0
    options = ["JOGAR", "SAIR"]
    
    # Lista para guardar os retângulos dos botões (para detecção de clique)
    button_rects = []

    while True:
        mouse_pos = pygame.mouse.get_pos()
        button_rects = []  # Limpa a cada frame
        mouse_clicked = False
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "quit"

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    if selected_option == 0:
                        return "gameplay"
                    elif selected_option == 1:
                        return "quit"
                if event.key == pygame.K_ESCAPE:
                    return "quit"
                if event.key == pygame.K_UP or event.key == pygame.K_w:
                    selected_option = (selected_option - 1) % len(options)
                if event.key == pygame.K_DOWN or event.key == pygame.K_s:
                    selected_option = (selected_option + 1) % len(options)
            
            # Marca que houve clique (verifica depois de desenhar os botões)
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Botão esquerdo
                    mouse_clicked = True

        # Background com gradiente
        draw_gradient_rect(window, (20, 20, 40), (60, 20, 80), pygame.Rect(0, 0, 1280, 720))
        
        # Efeito de partículas no fundo
        time += 0.05
        for i in range(30):
            x = (100 + i * 40 + math.sin(time + i) * 50) % 1280
            y = (100 + i * 20 + math.cos(time + i * 0.5) * 30) % 720
            alpha = int(100 + 100 * math.sin(time + i))
            size = 2 + int(2 * math.sin(time + i))
            color = (100 + alpha // 2, 50 + alpha // 3, 150 + alpha // 2)
            pygame.draw.circle(window, color, (int(x), int(y)), size)

        # Animação do título (efeito de flutuação)
        titulo_offset = math.sin(time) * 10

        # Título com borda/sombra
        titulo_text = "PITAGORAS OPS"
        # Sombra
        titulo_shadow = font_titulo.render(titulo_text, True, (0, 0, 0))
        window.blit(titulo_shadow, (640 - titulo_shadow.get_width() // 2 + 5, 150 + titulo_offset + 5))
        # Título principal com gradiente simulado
        titulo = font_titulo.render(titulo_text, True, (255, 215, 0))
        window.blit(titulo, (640 - titulo.get_width() // 2, 150 + titulo_offset))
        
        # Subtítulo
        subtitle = font_subtitle.render("Sobreviva às ondas de inimigos!", True, (200, 200, 255))
        window.blit(subtitle, (640 - subtitle.get_width() // 2, 250 + titulo_offset))

        # Opções do menu com retângulos
        menu_y_start = 380
        menu_spacing = 100

        for i, option in enumerate(options):
            # Verifica hover do mouse
            is_hovered = False
            
            # Cor e tamanho baseado na seleção ou hover
            if i == selected_option:
                color = (255, 215, 0)
                bg_color = (100, 50, 150, 180)
                # Pulso que aumenta e diminui (não só horizontal)
                pulse = 1.0 + math.sin(time * 2) * 0.05  # Varia entre 0.95 e 1.05, mais lento
            else:
                color = (180, 180, 200)
                bg_color = (50, 30, 80, 100)
                # Pulso sutil mesmo quando não selecionado
                pulse = 1.0 + math.sin(time * 1.5 + i) * 0.02

            # Renderiza texto
            text = font_opcao.render(option, True, color)
            text_width = text.get_width()
            text_height = text.get_height()
            
            # Posição
            y_pos = menu_y_start + i * menu_spacing
            x_pos = 640 - text_width // 2
            
            # Desenha retângulo de fundo com escala de pulso
            padding = 20
            scaled_width = (text_width + padding * 2) * pulse
            scaled_height = (text_height + padding * 2) * pulse
            
            rect = pygame.Rect(
                640 - scaled_width // 2,
                y_pos + text_height // 2 - scaled_height // 2,
                scaled_width,
                scaled_height
            )
            
            # Verifica se o mouse está sobre o botão
            if rect.collidepoint(mouse_pos):
                is_hovered = True
                selected_option = i  # Atualiza seleção ao passar o mouse
                bg_color = (120, 70, 180, 200)  # Cor mais intensa no hover
            
            # Guarda o retângulo para detecção de clique
            button_rects.append(rect)
            
            # Fundo semi-transparente
            s = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
            pygame.draw.rect(s, bg_color, s.get_rect(), border_radius=10)
            window.blit(s, (rect.x, rect.y))
            
            # Borda se selecionado ou hover
            if i == selected_option or is_hovered:
                pygame.draw.rect(window, color, rect, 3, border_radius=10)
            
            # Escala e centraliza o texto
            if pulse != 1.0:
                # Escala o texto junto com o botão
                scaled_text = pygame.transform.scale(
                    text,
                    (int(text_width * pulse), int(text_height * pulse))
                )
                text_x = 640 - scaled_text.get_width() // 2
                text_y = y_pos + text_height // 2 - scaled_text.get_height() // 2
                window.blit(scaled_text, (text_x, text_y))
            else:
                window.blit(text, (x_pos, y_pos))

        # Verifica clique do mouse após desenhar os botões
        if mouse_clicked:
            for i, rect in enumerate(button_rects):
                if rect.collidepoint(mouse_pos):
                    if i == 0:
                        return "gameplay"
                    elif i == 1:
                        return "quit"

        # Instruções na parte inferior
        font_instrucoes = pygame.font.SysFont('Arial', 25)
        instrucoes = font_instrucoes.render("Use ↑↓ ou W/S para navegar | ENTER ou CLIQUE para selecionar", True, (150, 150, 170))
        window.blit(instrucoes, (640 - instrucoes.get_width() // 2, 650))

        pygame.display.flip()
        clock.tick(60)
