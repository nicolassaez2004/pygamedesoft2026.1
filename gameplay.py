import pygame
import enemy
import projectile
import player

def inicializa(window_width=1280, window_height=720):
    bg = pygame.image.load('sprite/fundodepedra.jpg')
    bg = pygame.transform.scale(bg, (window_width, window_height))
    plataforma = pygame.image.load('sprite/mapa.jpg')
    plataforma = pygame.transform.scale(plataforma, (480, 400))

    player = pygame.image.load('sprite/player.jpg')
    player = pygame.transform.scale(player, (80, 80))
    wizard = pygame.image.load('Sprites/MageMicoz.png')
    wizard = pygame.transform.scale(wizard, (80, 80))
    skeleton = pygame.image.load('Sprites/Skellington_gerson.png')
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

def gameplay_loop(window, clock):
    # Carrega os assets
    assets = inicializa(window.get_width(), window.get_height())
    
    # Cria o jogador
    player_obj = player.Player(
        window.get_width() / 2,
        window.get_height() / 2,
        window.get_width(),
        window.get_height()
    )
    
    # Inicializa o gerenciador de inimigos
    enemy_manager = enemy.EnemyManager(window.get_width(), window.get_height())
    
    # Inicializa o arco do player (ataque direito - bola amarela)
    bow_left = projectile.Bow(player_obj.pos, max_ammo=30)  # Bola amarela

    score = 0
    dt = 0
    attack_cooldown_right = 0
    attack_cooldown_duration = 0.3
    current_melee_attack = None  # Ataque melee ativo
    
    # Sistema de pontuação por tempo
    time_score_timer = 0
    time_score_interval = 2.0  # A cada 2 segundos ganha pontos
    time_score_amount = 10  # Pontos ganhos por intervalo

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "quit"

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return "leaderboard"

        # Atualiza o jogador
        keys = pygame.key.get_pressed()
        mouse_buttons = pygame.mouse.get_pressed()
        player_obj.update(dt, keys, mouse_buttons)
        
        if not player_obj.game_over:
            # Sistema de pontuação por tempo
            time_score_timer += dt
            if time_score_timer >= time_score_interval:
                score += time_score_amount
                time_score_timer = 0
            
            # Aplicar colisão com a plataforma
            plataforma_x = (window.get_width() - 480) // 2
            plataforma_y = (window.get_height() - 400) // 2
            player_obj.check_plataforma_collision(plataforma_x, plataforma_y)

            # Ataque esquerdo (melee - hitbox do ATTACK 1)
            # Sempre verifica se há um ataque melee ativo
            attack_melee = player_obj.get_melee_attack()
            if attack_melee:
                current_melee_attack = attack_melee
            
            # Ataque direito (bola amarela - como o arco)
            attack_cooldown_right -= dt
            if mouse_buttons[2] and attack_cooldown_right <= 0:  # Botão direito
                mouse_x, mouse_y = pygame.mouse.get_pos()
                bow_left.shoot(mouse_x, mouse_y)
                attack_cooldown_right = attack_cooldown_duration

            # Atualiza arco
            bow_left.update(dt, player_obj.pos)
            
            # Atualiza inimigos (ISSO ESTAVA FALTANDO!)
            enemy_manager.update(dt, player_obj.pos)
            
            # Verifica colisão de ataque melee com inimigos
            if current_melee_attack:
                for enemy_obj in enemy_manager.get_all_enemies():
                    if current_melee_attack.is_colliding_with_enemy(enemy_obj.pos, enemy_obj.radius):
                        if enemy_obj.take_damage(current_melee_attack.damage):
                            enemy_manager.remove_enemy(enemy_obj)
                            score += 100
                current_melee_attack = None  # Remove o ataque após checar colisão
            
            # Verifica colisão de projéteis (ataque direito) com inimigos
            hit_enemies = bow_left.check_collisions_with_enemies(enemy_manager.get_all_enemies())
            for proj, hit_enemy in hit_enemies:
                # Verifica se o inimigo é imune a projéteis (como o fantasma)
                if not hasattr(hit_enemy, 'immune_to_projectiles') or not hit_enemy.immune_to_projectiles:
                    if hit_enemy.take_damage(proj.damage):
                        enemy_manager.remove_enemy(hit_enemy)
                        score += 100
            
            # Aumenta dificuldade conforme score
            enemy_manager.increase_difficulty(score)

            # Verifica colisão com inimigos (dano no jogador)
            collision_result = enemy_manager.check_collisions_with_player(player_obj.pos, player_obj.radius)
            if collision_result:
                collision_type, collision_obj = collision_result
                if collision_type == 'enemy':
                    player_obj.take_damage(1)
                    # Se for um fantasma (GhostersonEnemy), remove-o após causar dano
                    if isinstance(collision_obj, enemy.GhostersonEnemy):
                        enemy_manager.remove_enemy(collision_obj)
                elif collision_type == 'projectile':
                    # Projétil acertou o jogador
                    player_obj.take_damage(collision_obj.damage)
                    # Aplica congelamento se o projétil tiver stun
                    if collision_obj.stun_duration > 0:
                        player_obj.apply_stun(collision_obj.stun_duration)

        # Desenha o jogo
        window.blit(assets['bg'], (0, 0))
        
        # Desenha a plataforma centralizada
        plataforma_x = (window.get_width() - 480) // 2
        plataforma_y = (window.get_height() - 400) // 2
        window.blit(assets['plataforma'], (plataforma_x, plataforma_y))
        
        # Desenha o player
        player_obj.draw(window)
        
        # Desenha o projétil de ataque melee (debug)
        if current_melee_attack:
            current_melee_attack.draw(window, debug=True)
        
        # Desenha os projéteis
        bow_left.draw(window)
        
        # Desenha os inimigos
        enemy_manager.draw(window)
        
        # Desenha HUD (Score e Munição)
        font_hud = pygame.font.SysFont(None, 40)
        score_text = font_hud.render(f"Score: {score}", True, (255, 255, 255))
        ammo_text = font_hud.render(f"Ammo: {bow_left.ammo}/{bow_left.max_ammo}", True, (255, 255, 0))
        enemies_text = font_hud.render(f"Enemies: {len(enemy_manager.get_all_enemies())}", True, (255, 100, 100))
        health_text = font_hud.render(f"Health: {player_obj.health}/{player_obj.max_health}", True, (0, 255, 0))
        state_text = font_hud.render(f"State: {player_obj.state}", True, (200, 200, 255))
        
        # Texto de congelamento se estiver ativo
        stun_color = (0, 255, 255) if player_obj.stun_timer > 0 else (200, 200, 200)
        stun_text = font_hud.render(f"Stun: {player_obj.stun_timer:.2f}s" if player_obj.stun_timer > 0 else "Stun: Ready", True, stun_color)
        
        window.blit(score_text, (10, 10))
        window.blit(ammo_text, (10, 50))
        window.blit(enemies_text, (10, 90))
        window.blit(health_text, (10, 130))
        window.blit(state_text, (10, 170))
        window.blit(stun_text, (10, 210))
        
        # Desenha status de game over
        if player_obj.game_over:
            font_gameover = pygame.font.SysFont(None, 80)
            gameover_text = font_gameover.render("GAME OVER", True, (255, 0, 0))
            window.blit(gameover_text, (window.get_width() // 2 - gameover_text.get_width() // 2, 
                                       window.get_height() // 2 - gameover_text.get_height() // 2))

        pygame.display.flip()
        dt = clock.tick(60) / 1000
