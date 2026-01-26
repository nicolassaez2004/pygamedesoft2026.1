import pygame
import enemy
import projectile

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
def gameplay_loop(window, clock):
    player_pos = pygame.Vector2(
        window.get_width() / 2,
        window.get_height() / 2
    )
    player_radius = 20
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
        window.fill((0, 40, 0))
        
        # Desenha o player
        pygame.draw.circle(window, (255, 255, 255), player_pos, player_radius)
        
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
