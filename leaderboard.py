import pygame
import json
import os

def load_leaderboard():
    """Carrega o leaderboard do arquivo JSON"""
    if os.path.exists('leaderboard.json'):
        try:
            with open('leaderboard.json', 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return []
    return []

def save_leaderboard(leaderboard):
    """Salva o leaderboard no arquivo JSON"""
    try:
        with open('leaderboard.json', 'w', encoding='utf-8') as f:
            json.dump(leaderboard, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"Erro ao salvar leaderboard: {e}")

def add_score(player_name, score):
    """Adiciona uma nova pontuação ao leaderboard"""
    leaderboard = load_leaderboard()
    leaderboard.append({
        'name': player_name,
        'score': score
    })
    # Ordena por pontuação decrescente
    leaderboard.sort(key=lambda x: x['score'], reverse=True)
    # Mantém apenas os top 10
    leaderboard = leaderboard[:10]
    save_leaderboard(leaderboard)
    return leaderboard

def leaderboard_loop(window, clock, player_name="", final_score=0):
    """Tela de leaderboard que exibe as pontuações e permite voltar ao menu"""
    
    # Se houver pontuação, salva no leaderboard
    if final_score > 0 and player_name:
        leaderboard = add_score(player_name, final_score)
    else:
        leaderboard = load_leaderboard()
    
    # Carrega e toca a música do menu
    try:
        pygame.mixer.music.load('sons/menu.mp3')
        pygame.mixer.music.play(-1)  # -1 para loop infinito
        pygame.mixer.music.set_volume(0.22) 
    except Exception as e:
        print(f"Aviso: Não foi possível carregar a música do menu: {e}")
    
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "quit"

            if event.type == pygame.KEYDOWN:
                # ESC ou ENTER volta ao menu
                if event.key == pygame.K_RETURN or event.key == pygame.K_ESCAPE:
                    return "menu"

        # Preenche com fundo escuro gradiente
        window.fill((20, 20, 40))
        
        # Título
        font_title = pygame.font.SysFont('Arial', 80, bold=True)
        title = font_title.render("PLACAR", True, (255, 215, 0))
        title_shadow = font_title.render("PLACAR", True, (0, 0, 0))
        window.blit(title_shadow, (640 - title.get_width() // 2 + 3, 53))
        window.blit(title, (640 - title.get_width() // 2, 50))
        
        # Se houver pontuação atual do jogador, mostra em destaque
        if final_score > 0 and player_name:
            font_current = pygame.font.SysFont('Arial', 35)
            current_text = f"Sua pontuação: {player_name} - {final_score} pontos"
            current_surface = font_current.render(current_text, True, (100, 255, 100))
            window.blit(current_surface, (640 - current_surface.get_width() // 2, 140))
        
        # Top 10 leaderboard
        if leaderboard:
            start_y = 200 if (final_score > 0 and player_name) else 160
            font_header = pygame.font.SysFont('Arial', 40, bold=True)
            header = font_header.render("TOP 10", True, (255, 255, 255))
            window.blit(header, (640 - header.get_width() // 2, start_y))
            
            font_entry = pygame.font.SysFont('Arial', 32)
            y_offset = start_y + 60
            
            for i, entry in enumerate(leaderboard[:10], 1):
                # Cor especial para o top 3
                if i == 1:
                    color = (255, 215, 0)  # Ouro
                elif i == 2:
                    color = (192, 192, 192)  # Prata
                elif i == 3:
                    color = (205, 127, 50)  # Bronze
                else:
                    color = (200, 200, 200)  # Branco
                
                # Destaca se for a pontuação atual
                if entry['name'] == player_name and entry['score'] == final_score and final_score > 0:
                    color = (100, 255, 100)
                    entry_text = f"► {i}. {entry['name']} - {entry['score']} pontos ◄"
                else:
                    entry_text = f"{i}. {entry['name']} - {entry['score']} pontos"
                
                entry_surface = font_entry.render(entry_text, True, color)
                window.blit(entry_surface, (640 - entry_surface.get_width() // 2, y_offset))
                y_offset += 45
        else:
            # Nenhuma pontuação ainda
            font_text = pygame.font.SysFont('Arial', 40)
            text = font_text.render("Nenhuma pontuação registrada ainda", True, (200, 200, 200))
            window.blit(text, (640 - text.get_width() // 2, 300))
        
        # Instrução
        font_small = pygame.font.SysFont('Arial', 30)
        instruction = font_small.render("Pressione ENTER ou ESC para voltar ao menu", True, (150, 150, 170))
        window.blit(instruction, (640 - instruction.get_width() // 2, 660))

        pygame.display.flip()
        clock.tick(60)
