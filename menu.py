import pygame
import math

def input_name_screen(window, clock):
    """Tela para o jogador inserir seu nome antes de começar o jogo"""
    
    # Carrega e toca a música do menu se não estiver tocando
    try:
        if not pygame.mixer.music.get_busy():
            pygame.mixer.music.load('sons/menu.mp3')
            pygame.mixer.music.play(-1)
            pygame.mixer.music.set_volume(0.22)
    except Exception as e:
        print(f"Aviso: Não foi possível carregar a música do menu: {e}")
    
    # Fontes
    font_title = pygame.font.SysFont('Arial', 70, bold=True)
    font_text = pygame.font.SysFont('Arial', 40)
    font_input = pygame.font.SysFont('Arial', 50)
    font_button = pygame.font.SysFont('Arial', 45)
    
    player_name = ""
    max_name_length = 15
    cursor_visible = True
    cursor_timer = 0
    cursor_blink_speed = 0.5  # segundos
    time = 0
    
    while True:
        dt = clock.tick(60) / 1000.0
        time += dt
        cursor_timer += dt
        
        # Pisca o cursor
        if cursor_timer >= cursor_blink_speed:
            cursor_visible = not cursor_visible
            cursor_timer = 0
        
        mouse_clicked = False
        mouse_pos = pygame.mouse.get_pos()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "quit", ""
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return "menu", ""
                
                elif event.key == pygame.K_RETURN:
                    # Se o nome não estiver vazio, continua para o jogo
                    if player_name.strip():
                        return "gameplay", player_name.strip()
                
                elif event.key == pygame.K_BACKSPACE:
                    player_name = player_name[:-1]
                
                else:
                    # Adiciona caractere se for letra, número ou espaço
                    if len(player_name) < max_name_length:
                        if event.unicode.isprintable():
                            player_name += event.unicode
            
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mouse_clicked = True
        
        # Background com gradiente
        draw_gradient_rect(window, (20, 20, 40), (60, 20, 80), pygame.Rect(0, 0, 1280, 720))
        
        # Efeito de partículas no fundo
        for i in range(30):
            x = (100 + i * 40 + math.sin(time + i) * 50) % 1280
            y = (100 + i * 20 + math.cos(time + i * 0.5) * 30) % 720
            alpha = int(100 + 100 * math.sin(time + i))
            size = 2 + int(2 * math.sin(time + i))
            color = (100 + alpha // 2, 50 + alpha // 3, 150 + alpha // 2)
            pygame.draw.circle(window, color, (int(x), int(y)), size)
        
        # Título
        title_offset = math.sin(time) * 5
        title = font_title.render("DIGITE SEU NOME", True, (255, 215, 0))
        title_shadow = font_title.render("DIGITE SEU NOME", True, (0, 0, 0))
        window.blit(title_shadow, (640 - title.get_width() // 2 + 3, 120 + title_offset + 3))
        window.blit(title, (640 - title.get_width() // 2, 120 + title_offset))
        
        # Caixa de entrada
        input_box_rect = pygame.Rect(340, 300, 600, 80)
        
        # Fundo da caixa com transparência
        box_surface = pygame.Surface((input_box_rect.width, input_box_rect.height), pygame.SRCALPHA)
        pygame.draw.rect(box_surface, (50, 30, 80, 180), box_surface.get_rect(), border_radius=10)
        window.blit(box_surface, (input_box_rect.x, input_box_rect.y))
        
        # Borda da caixa
        pygame.draw.rect(window, (255, 215, 0), input_box_rect, 3, border_radius=10)
        
        # Texto digitado
        display_text = player_name
        if cursor_visible:
            display_text += "|"
        
        text_surface = font_input.render(display_text, True, (255, 255, 255))
        text_x = input_box_rect.centerx - text_surface.get_width() // 2
        text_y = input_box_rect.centery - text_surface.get_height() // 2
        window.blit(text_surface, (text_x, text_y))
        
        # Instruções
        instruction1 = font_text.render(f"Máximo {max_name_length} caracteres", True, (180, 180, 200))
        window.blit(instruction1, (640 - instruction1.get_width() // 2, 420))
        
        # Botão "Continuar" (só aparece se tiver nome)
        if player_name.strip():
            button_rect = pygame.Rect(490, 520, 300, 70)
            is_hovered = button_rect.collidepoint(mouse_pos)
            
            # Cor do botão
            button_color = (120, 70, 180, 200) if is_hovered else (100, 50, 150, 180)
            border_color = (255, 215, 0)
            
            # Fundo do botão
            button_surface = pygame.Surface((button_rect.width, button_rect.height), pygame.SRCALPHA)
            pygame.draw.rect(button_surface, button_color, button_surface.get_rect(), border_radius=10)
            window.blit(button_surface, (button_rect.x, button_rect.y))
            
            # Borda do botão
            pygame.draw.rect(window, border_color, button_rect, 3, border_radius=10)
            
            # Texto do botão
            button_text = font_button.render("CONTINUAR", True, (255, 215, 0))
            button_text_x = button_rect.centerx - button_text.get_width() // 2
            button_text_y = button_rect.centery - button_text.get_height() // 2
            window.blit(button_text, (button_text_x, button_text_y))
            
            # Verifica clique no botão
            if mouse_clicked and button_rect.collidepoint(mouse_pos):
                return "gameplay", player_name.strip()
        
        # Instrução para pressionar ENTER
        instruction2_text = "Pressione ENTER para continuar" if player_name.strip() else "Digite seu nome para começar"
        instruction2 = font_text.render(instruction2_text, True, (150, 150, 170))
        window.blit(instruction2, (640 - instruction2.get_width() // 2, 630))
        
        # Instrução ESC
        instruction3 = font_text.render("ESC - Voltar ao menu", True, (130, 130, 150))
        window.blit(instruction3, (640 - instruction3.get_width() // 2, 680))
        
        pygame.display.flip()

def draw_gradient_rect(surface, color1, color2, rect):
    """Desenha um retângulo com gradiente vertical"""
    for y in range(rect.height):
        ratio = y / rect.height
        r = int(color1[0] * (1 - ratio) + color2[0] * ratio)
        g = int(color1[1] * (1 - ratio) + color2[1] * ratio)
        b = int(color1[2] * (1 - ratio) + color2[2] * ratio)
        pygame.draw.line(surface, (r, g, b), (rect.x, rect.y + y), (rect.x + rect.width, rect.y + y))

def menu_loop(window, clock):
    # Carrega e toca a música do menu
    try:
        pygame.mixer.music.load('sons/menu.mp3')
        pygame.mixer.music.play(-1)  # -1 para loop infinito
        pygame.mixer.music.set_volume(0.22)
    except Exception as e:
        print(f"Aviso: Não foi possível carregar a música do menu: {e}")
    
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
                        return "input_name"
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
                        return "input_name"
                    elif i == 1:
                        return "quit"

        # Instruções na parte inferior
        font_instrucoes = pygame.font.SysFont('Arial', 25)
        instrucoes = font_instrucoes.render("Use ↑↓ ou W/S para navegar | ENTER ou CLIQUE para selecionar", True, (150, 150, 170))
        window.blit(instrucoes, (640 - instrucoes.get_width() // 2, 650))

        pygame.display.flip()
        clock.tick(60)
