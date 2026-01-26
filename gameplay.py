import pygame
import enemy
import projectile

def inicializa(window_width=1280, window_height=720):
    bg = pygame.image.load('sprite/fundodepedra.jpg')
    bg = pygame.transform.scale(bg, (window_width, window_height))
    plataforma = pygame.image.load('sprite/plataforma.png')
    plataforma = pygame.transform.scale(plataforma, (480, 400))

    player = pygame.image.load('sprite/player.jpg')
    player = pygame.transform.scale(player, (80, 80))
    wizard = pygame.image.load('sprite/wizard.jpg')
    wizard = pygame.transform.scale(wizard, (80, 80))
    skeleton = pygame.image.load('sprite/skeleton.jpg')
    skeleton = pygame.transform.scale(skeleton, (80, 80))
    knight = pygame.image.load('sprite/knight.jpg')
    knight = pygame.transform.scale(knight, (80, 80))

    assets = {}
    assets['bg'] = bg
    assets['plataforma'] = plataforma
    assets['player'] = player
    assets['wizard'] = wizard
    assets['skeleton'] = skeleton
    assets['knight'] = knight

    return assets

def desenha(window, assets):
    window.fill((0, 0, 0))
    window.blit(assets['bg'], (0, 0))
    window.blit(assets['player'], (640, 360))

def check_plataforma_collision(player_pos, player_radius, plataforma_x, plataforma_y, plataforma_width=480, plataforma_height=400):
    """Verifica colisão com a plataforma e ajusta a posição do player"""
    # Cria rect do player
    player_rect = pygame.Rect(player_pos.x - player_radius, player_pos.y - player_radius, player_radius * 2, player_radius * 2)
    
    # Define os 4 retângulos dos quadrados dos cantos (35x35 cada)
    corner_size = 35
    corner_rects = [
        pygame.Rect(plataforma_x, plataforma_y, corner_size, corner_size),  # Top-left
        pygame.Rect(plataforma_x + plataforma_width - corner_size, plataforma_y, corner_size, corner_size),  # Top-right
        pygame.Rect(plataforma_x, plataforma_y + plataforma_height - corner_size, corner_size, corner_size),  # Bottom-left
        pygame.Rect(plataforma_x + plataforma_width - corner_size, plataforma_y + plataforma_height - corner_size, corner_size, corner_size)  # Bottom-right
    ]
    
    # Verifica colisão com os 4 quadrados dos cantos
    for corner_rect in corner_rects:
        if player_rect.colliderect(corner_rect):
            # Calcula a direção para afastar o player
            corner_center_x = corner_rect.centerx
            corner_center_y = corner_rect.centery
            
            dx = player_pos.x - corner_center_x
            dy = player_pos.y - corner_center_y
            distance = (dx**2 + dy**2)**0.5
            
            if distance > 0:
                # Normaliza e afasta
                dx_norm = dx / distance
                dy_norm = dy / distance
                player_pos.x = corner_center_x + dx_norm * (corner_size // 2 + player_radius + 5)
                player_pos.y = corner_center_y + dy_norm * (corner_size // 2 + player_radius + 5)
            else:
                # Se estiver exatamente no centro, empurra para a direita
                player_pos.x = corner_rect.right + player_radius + 5
    
    # Bordas internas da plataforma (linhas vermelhas - com margem)
    margin = 35  # Margem interna da plataforma
    plat_left = plataforma_x + margin
    plat_right = plataforma_x + plataforma_width - margin
    plat_top = plataforma_y + margin
    plat_bottom = plataforma_y + plataforma_height - margin
    
    # Ajusta a posição do player para não ultrapassar as bordas internas
    player_pos.x = max(plat_left + player_radius, min(player_pos.x, plat_right - player_radius))
    player_pos.y = max(plat_top + player_radius, min(player_pos.y, plat_bottom - player_radius))
    
    return player_pos

def gameplay_loop(window, clock):
    # Carrega os assets
    assets = inicializa(window.get_width(), window.get_height())
    
    player_pos = pygame.Vector2(
        window.get_width() / 2,
        window.get_height() / 2
    )
    player_radius = 40
    player_speed = 300

    # Inicializa o gerenciador de inimigos
    enemy_manager = enemy.EnemyManager(window.get_width(), window.get_height())
    
    # Inicializa o arco do player
    bow = projectile.Bow(player_pos, max_ammo=30)

    score = 0
    game_over = False
    dt = 0

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "quit"

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return "leaderboard"

        if not game_over:
            # Movimento do player
            keys = pygame.key.get_pressed()

            if keys[pygame.K_w]:
                player_pos.y -= player_speed * dt
            if keys[pygame.K_s]:
                player_pos.y += player_speed * dt
            if keys[pygame.K_a]:
                player_pos.x -= player_speed * dt
            if keys[pygame.K_d]:
                player_pos.x += player_speed * dt

            # Mantém o player dentro da tela
            player_pos.x = max(player_radius, min(player_pos.x, window.get_width() - player_radius))
            player_pos.y = max(player_radius, min(player_pos.y, window.get_height() - player_radius))
            
            # Aplicar colisão com a plataforma
            plataforma_x = (window.get_width() - 480) // 2
            plataforma_y = (window.get_height() - 400) // 2
            player_pos = check_plataforma_collision(player_pos, player_radius, plataforma_x, plataforma_y)

            # Dispara em direção ao mouse
            mouse_x, mouse_y = pygame.mouse.get_pos()
            if pygame.mouse.get_pressed()[0]:  # Clique esquerdo
                bow.shoot(mouse_x, mouse_y)

            # Atualiza o arco
            bow.update(dt, player_pos)
            
            # Atualiza inimigos
            enemy_manager.update(dt, player_pos)
            
            # Verifica colisão de projéteis com inimigos
            hit_enemies = bow.check_collisions_with_enemies(enemy_manager.get_all_enemies())
            for proj, hit_enemy in hit_enemies:
                if hit_enemy.take_damage(proj.damage):
                    enemy_manager.remove_enemy(hit_enemy)
                    score += 100
            
            # Aumenta dificuldade conforme score
            enemy_manager.increase_difficulty(score)

            # Verifica colisão com inimigos
            if enemy_manager.check_collisions_with_player(player_pos, player_radius):
                game_over = True

        # Desenha o jogo
        window.blit(assets['bg'], (0, 0))
        
        # Desenha a plataforma centralizada
        plataforma_x = (window.get_width() - 480) // 2
        plataforma_y = (window.get_height() - 400) // 2
        window.blit(assets['plataforma'], (plataforma_x, plataforma_y))
        
        # Desenha o player
        player_rect = assets['player'].get_rect(center=(int(player_pos.x), int(player_pos.y)))
        window.blit(assets['player'], player_rect)
        
        # Desenha os projéteis
        bow.draw(window)
        
        # Desenha os inimigos
        enemy_manager.draw(window)
        
        # Desenha HUD (Score e Munição)
        font_hud = pygame.font.SysFont(None, 40)
        score_text = font_hud.render(f"Score: {score}", True, (255, 255, 255))
        ammo_text = font_hud.render(f"Ammo: {bow.ammo}/{bow.max_ammo}", True, (255, 255, 0))
        enemies_text = font_hud.render(f"Enemies: {len(enemy_manager.get_all_enemies())}", True, (255, 100, 100))
        
        window.blit(score_text, (10, 10))
        window.blit(ammo_text, (10, 50))
        window.blit(enemies_text, (10, 90))
        
        # Desenha status de game over
        if game_over:
            font_gameover = pygame.font.SysFont(None, 80)
            gameover_text = font_gameover.render("GAME OVER", True, (255, 0, 0))
            window.blit(gameover_text, (window.get_width() // 2 - gameover_text.get_width() // 2, 
                                       window.get_height() // 2 - gameover_text.get_height() // 2))

        pygame.display.flip()
        dt = clock.tick(60) / 1000
