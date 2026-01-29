import pygame
import enemy
import projectile
import player

def inicializa(window_width=1280, window_height=720):
    bg = pygame.image.load('sprite/fundodepedra.jpg')
    bg = pygame.transform.scale(bg, (window_width, window_height))
    plataforma = pygame.image.load('sprite/mapa.jpg')
    plataforma = pygame.transform.scale(plataforma, (480, 400))

    wizard = pygame.image.load('Sprites/MageMicoz.png')
    wizard = pygame.transform.scale(wizard, (80, 80))
    skeleton = pygame.image.load('Sprites/Skellington_gerson.png')
    skeleton = pygame.transform.scale(skeleton, (80, 80))
    
    try:
        bausprite = pygame.image.load('sprite/bausprite.png')
        bausprite = pygame.transform.scale(bausprite, (80, 80))
    except:
        bausprite = pygame.Surface((80, 80))
        bausprite.fill((200, 100, 100))
    
    try:
        kitmedico = pygame.image.load('sprite/kitmedicosprite.png')
        kitmedico = pygame.transform.scale(kitmedico, (80, 80))
    except:
        kitmedico = pygame.Surface((80, 80))
        kitmedico.fill((100, 200, 100))
    
    try:
        arco = pygame.image.load('sprite/arco.png')
        arco = pygame.transform.scale(arco, (80, 80))
    except:
        arco = pygame.Surface((80, 80))
        arco.fill((200, 200, 100))
    
    try:
        espadasprite = pygame.image.load('sprite/espadasprite.png')
        espadasprite = pygame.transform.scale(espadasprite, (80, 80))
    except:
        espadasprite = pygame.Surface((80, 80))
        espadasprite.fill((200, 150, 100))
    
    # Carrega sprites das flechas do jogador
    try:
        flecha_jogador_1 = pygame.image.load('Sprites/FlechaJOGADOR1.png')
        flecha_jogador_1 = pygame.transform.scale(flecha_jogador_1, (50, 50))
    except:
        flecha_jogador_1 = None
    
    try:
        flecha_jogador_2 = pygame.image.load('Sprites/FlechaJOGADOR2.png')
        flecha_jogador_2 = pygame.transform.scale(flecha_jogador_2, (52, 52))
    except:
        flecha_jogador_2 = None
    
    try:
        flecha_jogador_3 = pygame.image.load('Sprites/FlechaJOGADOR3.png')
        flecha_jogador_3 = pygame.transform.scale(flecha_jogador_3, (54, 54))
    except:
        flecha_jogador_3 = None

    assets = {}
    assets['bg'] = bg
    assets['plataforma'] = plataforma
    assets['wizard'] = wizard
    assets['skeleton'] = skeleton
    assets['bausprite'] = bausprite
    assets['kitmedico'] = kitmedico
    assets['arco'] = arco
    assets['espadasprite'] = espadasprite
    assets['flecha_jogador_1'] = flecha_jogador_1
    assets['flecha_jogador_2'] = flecha_jogador_2
    assets['flecha_jogador_3'] = flecha_jogador_3
    
    # Carrega sons
    try:
        assets['som_flecha_acerto'] = pygame.mixer.Sound('sons/FlechaAcertando.mp3')
        assets['som_attack1'] = pygame.mixer.Sound('sons/Attack1Espada.mp3')
        assets['som_soco'] = pygame.mixer.Sound('sons/soco.mp3')
        assets['som_stun'] = pygame.mixer.Sound('sons/StunGeloIce.mp3')
        assets['som_dano'] = pygame.mixer.Sound('sons/TomouDanoPerdeuVida.mp3')
        assets['som_fantasma_morre'] = pygame.mixer.Sound('sons/fantasmamorrendo.mp3')
        assets['som_fantasma_morre'].set_volume(0.15)  # Reduz volume para 15%
        assets['som_disparo'] = pygame.mixer.Sound('sons/disparo.mp3')
    except Exception as e:
        print(f"Aviso: Não foi possível carregar alguns sons: {e}")
        # Cria sons vazios para evitar erros se os arquivos não existirem
        assets['som_flecha_acerto'] = None
        assets['som_attack1'] = None
        assets['som_soco'] = None
        assets['som_stun'] = None
        assets['som_dano'] = None
        assets['som_fantasma_morre'] = None
        assets['som_disparo'] = None

    return assets

def gameplay_loop(window, clock, player_name="Jogador"):
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
    bow_left.ammo = 0  # Começa sem flechas
    
    # Inicia transição de música (fade out do menu, fade in da gameplay)
    pygame.mixer.music.fadeout(1000)  # Fade out de 1 segundo
    try:
        pygame.mixer.music.load('sons/trilha_sonora.mp3')
        pygame.mixer.music.play(-1)  # -1 para loop infinito
        pygame.mixer.music.set_volume(0)  # Começa sem som
        # Fade in gradual
        import time as time_module
        start_time = time_module.time()
        fade_duration = 12  # 12 segundos para fade in
        final_volume = 0.22  
    except Exception as e:
        print(f"Aviso: Não foi possível carregar a música de gameplay: {e}")
        fade_duration = 0
        final_volume = 0.22

    score = 0
    money = 0  # Sistema de dinheiro (começa com 0)
    elapsed_time = 0  # Cronômetro de tempo decorrido no jogo
    dt = 0
    attack_cooldown_right = 0
    attack_cooldown_duration = 0.3
    current_melee_attack = None  # Ataque melee ativo
    time = 0  # Timer para animações
    purchase_cooldown = 0  # Cooldown para compras
    purchase_cooldown_duration = 0.5  # 500ms entre compras
    
    # Sistema de pontuação por tempo
    time_score_timer = 0
    time_score_interval = 2.0  # A cada 2 segundos ganha pontos
    time_score_amount = 10  # Pontos ganhos por intervalo
    
    # Sistema de pausa
    paused = False
    
    # Efeito de dano
    damage_flash_timer = 0
    
    # Efeitos visuais de impacto (lista de efeitos quando soco acerta fantasma)
    impact_effects = []  # Cada item: {'pos': (x, y), 'timer': float, 'particles': [...]}
    
    # Tutorial inicial
    show_tutorial = True
    tutorial_timer = 5.0  # Mostra por 5 segundos
    
    # Transição de música
    music_transition_time = 0
    
    # Custo do kit médico (começa em 2 e dobra a cada compra)
    kitmedico_cost = 2
    
    # Controle de items comprados
    sword_purchased = False
    
    # Controle de upgrades de flecha
    arrow_level = 0  # 0 = sem arco, 1 = FlechaJOGADOR1, 2 = FlechaJOGADOR2, 3 = FlechaJOGADOR3
    bow_purchased = False  # Controle se o arco foi comprado

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "quit", score

            if event.type == pygame.KEYDOWN:
                # Pula o tutorial ao pressionar ESPAÇO
                if event.key == pygame.K_SPACE and show_tutorial:
                    show_tutorial = False
                    
                if event.key == pygame.K_ESCAPE:
                    if player_obj.game_over:
                        return "leaderboard", score
                    else:
                        paused = not paused  # Toggle pause
                if event.key == pygame.K_p:
                    paused = not paused  # Toggle pause com P também

        # Se tutorial estiver ativo, não atualiza o jogo
        if show_tutorial:
            tutorial_timer -= dt
            if tutorial_timer <= 0:
                show_tutorial = False
            
            # Atualiza fade in da música durante o tutorial
            music_transition_time += dt
            if music_transition_time <= fade_duration and fade_duration > 0:
                volume = (music_transition_time / fade_duration) * final_volume
                pygame.mixer.music.set_volume(volume)
            
            # Desenha apenas o fundo, plataforma e tutorial
            window.blit(assets['bg'], (0, 0))
            plataforma_x = (window.get_width() - 480) // 2
            plataforma_y = (window.get_height() - 400) // 2
            window.blit(assets['plataforma'], (plataforma_x, plataforma_y))
            
            # Desenha items na plataforma
            window.blit(assets['bausprite'], (440, 200))
            window.blit(assets['kitmedico'], (760, 200))
            window.blit(assets['arco'], (440, 440))
            # Desenha espada apenas se não foi comprada
            if not sword_purchased:
                window.blit(assets['espadasprite'], (760, 440))
            
            # Desenha o player (parado)
            player_obj.draw(window)
            
            # Desenha HUD básico
            draw_hud(window, score, player_obj, bow_left, enemy_manager, time, elapsed_time, money)
            
            # Desenha tutorial
            draw_tutorial(window, tutorial_timer)
            
            pygame.display.flip()
            dt = clock.tick(60) / 1000
            continue
        
        # Atualiza fade in da música
        music_transition_time += dt
        if music_transition_time <= fade_duration and fade_duration > 0:
            volume = (music_transition_time / fade_duration) * final_volume
            pygame.mixer.music.set_volume(volume)
        elif music_transition_time > fade_duration:
            pygame.mixer.music.set_volume(final_volume)
        
        # Se pausado, mostra menu de pausa
        if paused:
            draw_pause_menu(window)
            pygame.display.flip()
            clock.tick(60)
            continue

        # Atualiza o jogador
        keys = pygame.key.get_pressed()
        mouse_buttons = pygame.mouse.get_pressed()
        player_obj.update(dt, keys, mouse_buttons)
        
        # Incrementa timer para animações
        time += dt
        elapsed_time += dt  # Incrementa cronômetro
        purchase_cooldown = max(0, purchase_cooldown - dt)  # Reduz cooldown de compras
        
        if not player_obj.game_over:
            # Aumenta dificuldade com base no score
            enemy_manager.increase_difficulty(score)
            
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
                # Toca som de ataque baseado na arma do jogador
                if player_obj.weapon in ['nada', 'arco']:
                    # Player sem arma ou só com arco: som de soco
                    if assets['som_soco']:
                        assets['som_soco'].play()
                elif player_obj.weapon in ['espada', 'espada_arco']:
                    # Player com espada ou espada+arco: som de espada
                    if assets['som_attack1']:
                        assets['som_attack1'].play()
            
            # Ataque direito (bola amarela - como o arco)
            attack_cooldown_right -= dt
            if mouse_buttons[2] and attack_cooldown_right <= 0:  # Botão direito
                mouse_x, mouse_y = pygame.mouse.get_pos()
                bow_left.shoot(mouse_x, mouse_y)
                # Toca som de disparo
                if assets['som_disparo']:
                    assets['som_disparo'].play()
                attack_cooldown_right = attack_cooldown_duration

            # Atualiza arco
            bow_left.update(dt, player_obj.pos)
            
            # Atualiza inimigos 
            enemy_manager.update(dt, player_obj.pos, elapsed_time)
            
            # Verifica colisão de ataque melee com inimigos
            if current_melee_attack:
                for enemy_obj in enemy_manager.get_all_enemies():
                    if current_melee_attack.is_colliding_with_enemy(enemy_obj.pos, enemy_obj.radius):
                        if enemy_obj.take_damage(current_melee_attack.damage):
                            # Adiciona efeito visual de impacto
                            import random
                            particles = []
                            
                            if isinstance(enemy_obj, enemy.GhostersonEnemy):
                                # Efeito para fantasma (cinza claro/branco - osso)
                                particle_count = 15
                                base_color = (220, 220, 220)  # Cinza claro/branco representando osso
                                if assets['som_fantasma_morre']:
                                    assets['som_fantasma_morre'].play()
                            elif isinstance(enemy_obj, enemy.SkellingtonEnemy):
                                # Efeito para Skellington (branco - osso)
                                particle_count = 12
                                base_color = (220, 220, 220)  # Branco representando osso
                            else:
                                # Efeito para inimigos normais como Mago (vermelho - sangue)
                                particle_count = 12
                                base_color = (200, 50, 50)  # Vermelho
                            
                            for _ in range(particle_count):
                                angle = random.uniform(0, 360)
                                speed = random.uniform(100, 300)
                                particle = {
                                    'pos': pygame.Vector2(enemy_obj.pos.x, enemy_obj.pos.y),
                                    'vel': pygame.Vector2(speed, 0).rotate(angle),
                                    'life': random.uniform(0.3, 0.6),
                                    'size': random.randint(3, 8),
                                    'color': base_color
                                }
                                particles.append(particle)
                            
                            impact_effects.append({
                                'pos': pygame.Vector2(enemy_obj.pos.x, enemy_obj.pos.y),
                                'timer': 0.6,
                                'particles': particles
                            })
                            
                            enemy_manager.remove_enemy(enemy_obj)
                            score += 100
                            # Ganha 2 dinheiro ao eliminar
                            money += 2
                current_melee_attack = None  # Remove o ataque após checar colisão
            
            # Verifica colisão de projéteis (ataque direito) com inimigos
            hit_enemies = bow_left.check_collisions_with_enemies(enemy_manager.get_all_enemies())
            for proj, hit_enemy in hit_enemies:
                # Verifica se o inimigo é imune a projéteis (como o fantasma)
                if not hasattr(hit_enemy, 'immune_to_projectiles') or not hit_enemy.immune_to_projectiles:
                    # Adiciona efeito de sangue/impacto ao acertar inimigo
                    import random
                    particles = []
                    particle_count = 10 if not isinstance(hit_enemy, enemy.GhostersonEnemy) else 8
                    # Cor baseada no tipo de inimigo
                    if isinstance(hit_enemy, enemy.GhostersonEnemy):
                        base_color = (220, 220, 220)  # Cinza claro/branco para fantasma (seilakkk)
                    elif isinstance(hit_enemy, enemy.SkellingtonEnemy):
                        base_color = (220, 220, 220)  # Branco para Skellington (osso)
                    else:
                        base_color = (200, 50, 50)  # Vermelho para outros (Mago)
                    
                    for _ in range(particle_count):
                        angle = random.uniform(0, 360)
                        speed = random.uniform(80, 200)
                        particles.append({
                            'pos': pygame.Vector2(hit_enemy.pos.x, hit_enemy.pos.y),
                            'vel': pygame.Vector2(speed, 0).rotate(angle),
                            'life': random.uniform(0.2, 0.5),
                            'size': random.randint(2, 5),
                            'color': base_color
                        })
                    impact_effects.append({
                        'pos': pygame.Vector2(hit_enemy.pos.x, hit_enemy.pos.y),
                        'timer': 0.5,
                        'particles': particles
                    })
                    
                    if hit_enemy.take_damage(proj.damage):
                        enemy_manager.remove_enemy(hit_enemy)
                        score += 100
                        # Ganha 2 de dinheiros ao eliminar
                        money += 2
                    # Toca som de acerto
                    if assets['som_flecha_acerto']:
                        assets['som_flecha_acerto'].play()
            
            # Aumenta dificuldade conforme score
            enemy_manager.increase_difficulty(score)
            
            # Variáveis de interação com itens
            near_bausprite = False
            near_bausprite_sem_arco = False
            near_kitmedico = False
            near_espadasprite = False
            near_arco = False
            near_arrow_upgrade_1 = False
            near_arrow_upgrade_2 = False
            bausprite_cost = 5  # Custo para comprar munição
            munition_recovery = 10  # Munição recuperada por compra
            kitmedico_recovery = 1  # Vida recuperada (sempre 1)
            arrow_upgrade_cost_1 = 10  # Custo para upgrade 1 -> 2
            arrow_upgrade_cost_2 = 15  # Custo para upgrade 2 -> 3
            espadasprite_cost = 4  # Preço da espada atualizado
            arco_cost = 6  # Preço do arco
            
            # Verifica colisão com bausprite
            bausprite_rect = assets['bausprite'].get_rect(topleft=(440, 200))
            player_rect = pygame.Rect(player_obj.pos[0] - player_obj.radius, player_obj.pos[1] - player_obj.radius, player_obj.radius * 2, player_obj.radius * 2)
            if bausprite_rect.colliderect(player_rect):
                # Verifica se jogador tem arco
                has_bow = player_obj.weapon in ['arco', 'espada_arco']
                if has_bow:
                    near_bausprite = True
                    # Verifica se pressionou E para comprar
                    keys = pygame.key.get_pressed()
                    if keys[pygame.K_e] and money >= bausprite_cost and purchase_cooldown <= 0:
                        money -= bausprite_cost
                        bow_left.ammo = min(bow_left.ammo + munition_recovery, bow_left.max_ammo)
                        purchase_cooldown = purchase_cooldown_duration  # Ativa cooldown
                else:
                    # Jogador está próximo do baú mas não tem arco
                    near_bausprite = False
                    near_bausprite_sem_arco = True

            
            # Verifica colisão com kitmedico
            kitmedico_rect = assets['kitmedico'].get_rect(topleft=(760, 200))
            if kitmedico_rect.colliderect(player_rect):
                near_kitmedico = True
                # Verifica se pressionou E para recuperar vida
                keys = pygame.key.get_pressed()
                if keys[pygame.K_e] and player_obj.health < player_obj.max_health and money >= kitmedico_cost and purchase_cooldown <= 0:
                    money -= kitmedico_cost
                    player_obj.health = min(player_obj.health + kitmedico_recovery, player_obj.max_health)
                    kitmedico_cost *= 2  # Dobra o custo para a próxima compra
                    purchase_cooldown = purchase_cooldown_duration  # Ativa cooldown
            arco_rect = assets['arco'].get_rect(topleft=(440, 440))
            if arco_rect.colliderect(player_rect):
                has_bow = player_obj.weapon in ['arco', 'espada_arco']
                if not has_bow:
                    near_arco = True
                    keys = pygame.key.get_pressed()
                    if keys[pygame.K_e] and money >= arco_cost and purchase_cooldown <= 0:
                        money -= arco_cost
                        bow_purchased = True
                        arrow_level = 1  # Ativa FlechaJOGADOR1
                        bow_left.set_arrow_level(1, assets['flecha_jogador_1'])
                        # Se já tem espada, combina para espada_arco
                        if player_obj.weapon == 'espada':
                            player_obj.set_weapon('espada_arco')
                        else:
                            player_obj.set_weapon('arco')
                        purchase_cooldown = purchase_cooldown_duration

            espadasprite_rect = assets['espadasprite'].get_rect(topleft=(760, 440))
            if espadasprite_rect.colliderect(player_rect):
                # Verifica se tem uma espada
                has_sword = player_obj.weapon in ['espada', 'espada_arco']
                if not has_sword:
                    near_espadasprite = True
                    # Verifica se pressionou E para comprar
                    keys = pygame.key.get_pressed()
                    if keys[pygame.K_e] and money >= espadasprite_cost and purchase_cooldown <= 0:
                        money -= espadasprite_cost
                        sword_purchased = True  # Marca que a espada foi comprada
                        # Se já tem arco, combina para espada_arco
                        if player_obj.weapon == 'arco':
                            player_obj.set_weapon('espada_arco')
                        else:
                            player_obj.set_weapon('espada')
                        purchase_cooldown = purchase_cooldown_duration

            # Sistema de upgrades de flecha
            # Upgrade 1: FlechaJOGADOR1 -> FlechaJOGADOR2 (aparece no local onde estava o arco após comprar o arco)
            if bow_purchased and arrow_level == 1:
                arrow_upgrade_rect_1 = pygame.Rect(440, 440, 80, 80)
                if arrow_upgrade_rect_1.colliderect(player_rect):
                    near_arrow_upgrade_1 = True
                    keys = pygame.key.get_pressed()
                    if keys[pygame.K_e] and money >= arrow_upgrade_cost_1 and purchase_cooldown <= 0:
                        money -= arrow_upgrade_cost_1
                        arrow_level = 2
                        bow_left.set_arrow_level(2, assets['flecha_jogador_2'])
                        purchase_cooldown = purchase_cooldown_duration
            
            # Upgrade 2: FlechaJOGADOR2 -> FlechaJOGADOR3 (aparece no mesmo local após o primeiro upgrade)
            if bow_purchased and arrow_level == 2:
                arrow_upgrade_rect_2 = pygame.Rect(440, 440, 80, 80)
                if arrow_upgrade_rect_2.colliderect(player_rect):
                    near_arrow_upgrade_2 = True
                    keys = pygame.key.get_pressed()
                    if keys[pygame.K_e] and money >= arrow_upgrade_cost_2 and purchase_cooldown <= 0:
                        money -= arrow_upgrade_cost_2
                        arrow_level = 3
                        bow_left.set_arrow_level(3, assets['flecha_jogador_3'])
                        purchase_cooldown = purchase_cooldown_duration

            # Verifica colisão com inimigos (dano no jogador)
            collision_result = enemy_manager.check_collisions_with_player(player_obj.pos, player_obj.radius)
            if collision_result:
                collision_type, collision_obj = collision_result
                if collision_type == 'enemy':
                    player_obj.take_damage(1)
                    # Toca som de dano
                    if assets['som_dano']:
                        assets['som_dano'].play()
                    # Ativa efeito de flash de dano
                    damage_flash_timer = 0.2
                    # Se for um fantasma (GhostersonEnemy), remove-o após causar dano
                    if isinstance(collision_obj, enemy.GhostersonEnemy):
                        # Toca som de fantasma morrendo
                        if assets['som_fantasma_morre']:
                            assets['som_fantasma_morre'].play()
                        enemy_manager.remove_enemy(collision_obj)
                elif collision_type == 'projectile':
                    # Projétil acertou o jogador
                    player_obj.take_damage(collision_obj.damage)
                    # Toca som de dano
                    if assets['som_dano']:
                        assets['som_dano'].play()
                    # Ativa efeito de flash de dano
                    damage_flash_timer = 0.2
                    # Aplica congelamento se o projétil tiver stun
                    if collision_obj.stun_duration > 0:
                        player_obj.apply_stun(collision_obj.stun_duration)
                        # Toca som de stun
                        if assets['som_stun']:
                            assets['som_stun'].play()
        
        # Atualiza efeito de dano
        if damage_flash_timer > 0:
            damage_flash_timer -= dt
        
        # Atualiza efeitos de impacto (partículas quando soco acerta fantasma)
        for effect in impact_effects[:]:
            effect['timer'] -= dt
            if effect['timer'] <= 0:
                impact_effects.remove(effect)
            else:
                # Atualiza partículas
                for particle in effect['particles'][:]:
                    particle['pos'] += particle['vel'] * dt
                    particle['life'] -= dt
                    if particle['life'] <= 0:
                        effect['particles'].remove(particle)

        # Desenha o jogo
        window.blit(assets['bg'], (0, 0))
        
        # Desenha a plataforma centralizada
        plataforma_x = (window.get_width() - 480) // 2
        plataforma_y = (window.get_height() - 400) // 2
        window.blit(assets['plataforma'], (plataforma_x, plataforma_y))
        
        # Desenha bausprite na posição especificada (antes do jogador)
        window.blit(assets['bausprite'], (440, 200))
        
        # Desenha kitmedico na posição especificada
        window.blit(assets['kitmedico'], (760, 200))

        # Desenha arco e upgrades de flecha
        # Só mostra o arco se ainda não foi comprado OU se foi comprado mas ainda não atingiu nível máximo
        if (not bow_purchased) or (bow_purchased and arrow_level < 3):
            window.blit(assets['arco'], (440, 440))
        # Se arrow_level == 3, não desenha (arco removido após upgrade máximo)

        # Desenha espada apenas se não foi comprada
        if not sword_purchased:
            window.blit(assets['espadasprite'], (760, 440))
        
        # Desenha o player
        player_obj.draw(window)
        
        # Desenha o projétil de ataque melee (debug)
        if current_melee_attack:
            current_melee_attack.draw(window, debug=True)
        
        # Desenha os projéteis
        bow_left.draw(window)
        
        # Desenha os inimigos
        enemy_manager.draw(window)
        
        # Desenha efeitos de impacto (partículas quando acerta inimigos)
        for effect in impact_effects:
            for particle in effect['particles']:
                # Calcula alpha baseado na vida restante
                alpha = int(255 * (particle['life'] / 0.6))
                # Usa cor customizada se definida, senão usa branca/amarela padrão
                if 'color' in particle:
                    r, g, b = particle['color']
                    color = (r, g, b, alpha)
                else:
                    color = (255, 255, 200, alpha)  # Branco/amarelo para fantasmas
                
                particle_surface = pygame.Surface((particle['size'] * 2, particle['size'] * 2), pygame.SRCALPHA)
                pygame.draw.circle(particle_surface, color, (particle['size'], particle['size']), particle['size'])
                window.blit(particle_surface, (particle['pos'].x - particle['size'], particle['pos'].y - particle['size']))
        
        # Efeito de flash quando toma dano
        if damage_flash_timer > 0:
            flash_surface = pygame.Surface((window.get_width(), window.get_height()), pygame.SRCALPHA)
            alpha = int(150 * (damage_flash_timer / 0.2))
            pygame.draw.rect(flash_surface, (255, 0, 0, alpha), flash_surface.get_rect())
            window.blit(flash_surface, (0, 0))
        
        # Desenha prompts de interação
        font_prompt = pygame.font.SysFont('Arial', 25)
        
        if near_bausprite:
            prompt_text = f'Pressione "E" para comprar {munition_recovery} munição ({bausprite_cost}$)'
            if money >= bausprite_cost:
                prompt_color = (100, 255, 100)  # Verde
            else:
                prompt_color = (255, 100, 100)  # Vermelho (sem dinheiro)
            prompt_surface = font_prompt.render(prompt_text, True, prompt_color)
            prompt_x = 640 - prompt_surface.get_width() // 2
            window.blit(prompt_surface, (prompt_x, 600))
        
        if near_bausprite_sem_arco:
            prompt_text = 'Sem arco'
            prompt_color = (255, 100, 100)  # Vermelho
            prompt_surface = font_prompt.render(prompt_text, True, prompt_color)
            prompt_x = 640 - prompt_surface.get_width() // 2
            window.blit(prompt_surface, (prompt_x, 600))
        
        if near_kitmedico:
            # Sempre mostrar o prompt quando próximo; ajustar mensagem se a vida já estiver cheia
            if player_obj.health < player_obj.max_health:
                prompt_text = f'Pressione "E" para recuperar {kitmedico_recovery} vida ({kitmedico_cost}$)'
                if money >= kitmedico_cost:
                    prompt_color = (100, 200, 255)
                else:
                    prompt_color = (255, 100, 100)  # Vermelho (sem dinheiro)
            else:
                prompt_text = 'Vida cheia'
                prompt_color = (180, 180, 180)
            prompt_surface = font_prompt.render(prompt_text, True, prompt_color)
            prompt_x = 640 - prompt_surface.get_width() // 2
            window.blit(prompt_surface, (prompt_x, 600))

        if near_espadasprite:
            prompt_text = f'Pressione "E" para comprar Espada ({espadasprite_cost}$)'
            if money >= espadasprite_cost:
                prompt_color = (100, 255, 100)
            else:
                prompt_color = (255, 100, 100)
            prompt_surface = font_prompt.render(prompt_text, True, prompt_color)
            prompt_x = 640 - prompt_surface.get_width() // 2
            window.blit(prompt_surface, (prompt_x, 600))
        
        if near_arco:
            prompt_text = f'Pressione "E" para comprar Arco ({arco_cost}$)'
            if money >= arco_cost:
                prompt_color = (100, 255, 100)
            else:
                prompt_color = (255, 100, 100)
            prompt_surface = font_prompt.render(prompt_text, True, prompt_color)
            prompt_x = 640 - prompt_surface.get_width() // 2
            window.blit(prompt_surface, (prompt_x, 600))
        
        if near_arrow_upgrade_1:
            prompt_text = f'Pressione "E" para melhorar suas Flechas ({arrow_upgrade_cost_1}$)'
            if money >= arrow_upgrade_cost_1:
                prompt_color = (100, 255, 100)  # Verde
            else:
                prompt_color = (255, 100, 100)
            prompt_surface = font_prompt.render(prompt_text, True, prompt_color)
            prompt_x = 640 - prompt_surface.get_width() // 2
            window.blit(prompt_surface, (prompt_x, 600))
        
        if near_arrow_upgrade_2:
            prompt_text = f'Pressione "E" para melhorar suas Flechas ({arrow_upgrade_cost_2}$)'
            if money >= arrow_upgrade_cost_2:
                prompt_color = (100, 200, 255)  # Azul
            else:
                prompt_color = (255, 100, 100)
            prompt_surface = font_prompt.render(prompt_text, True, prompt_color)
            prompt_x = 640 - prompt_surface.get_width() // 2
            window.blit(prompt_surface, (prompt_x, 600))
        
        # Desenha HUD melhorado
        draw_hud(window, score, player_obj, bow_left, enemy_manager, time, elapsed_time, money)
        
        # Desenha status de game over
        if player_obj.game_over:
            draw_game_over(window, score)

        pygame.display.flip()
        dt = clock.tick(60) / 1000


def draw_health_bar(surface, x, y, width, height, value, max_value, color, bg_color=(50, 50, 50), border_color=(255, 255, 255)):
    """Desenha uma barra de status (vida, munição, etc)"""
    # Fundo
    pygame.draw.rect(surface, bg_color, (x, y, width, height), border_radius=5)
    # Barra preenchida
    fill_width = int((value / max_value) * width)
    if fill_width > 0:
        pygame.draw.rect(surface, color, (x, y, fill_width, height), border_radius=5)
    # Borda
    pygame.draw.rect(surface, border_color, (x, y, width, height), 2, border_radius=5)


def draw_hud(window, score, player_obj, bow_left, enemy_manager, time, elapsed_time=0, money=0):
    """Desenha a HUD melhorada"""
    # Fontes
    font_large = pygame.font.SysFont('Arial', 45, bold=True)
    font_medium = pygame.font.SysFont('Arial', 30, bold=True)
    font_small = pygame.font.SysFont('Arial', 25)
    
    # Cronômetro na esquerda (em cima de VIDA)
    minutes = int(elapsed_time) // 60
    seconds = int(elapsed_time) % 60
    timer_text = font_medium.render(f"{minutes}:{seconds:02d}", True, (255, 255, 255))
    window.blit(timer_text, (20, 20))
    
    # Score centralizado no meio da tela (branco) - sem painel roxo
    score_text = font_large.render(f"SCORE: {score}", True, (255, 255, 255))
    score_shadow = font_large.render(f"SCORE: {score}", True, (0, 0, 0))
    score_x = 640 - score_text.get_width() // 2  # Centraliza horizontalmente
    
    window.blit(score_shadow, (score_x + 2, 12))
    window.blit(score_text, (score_x, 10))
    
    # Dinheiro abaixo do score (centralizado)
    money_text = font_medium.render(f"${money}", True, (255, 215, 0))
    money_x = 640 - money_text.get_width() // 2
    window.blit(money_text, (money_x, 55))
    
    # Vida (abaixo do cronômetro)
    health_label = font_medium.render("VIDA", True, (255, 255, 255))
    window.blit(health_label, (20, 75))
    draw_health_bar(window, 100, 80, 200, 25, player_obj.health, player_obj.max_health, 
                   (0, 255, 0) if player_obj.health > 2 else (255, 100, 0))
    health_text = font_small.render(f"{player_obj.health}/{player_obj.max_health}", True, (255, 255, 255))
    window.blit(health_text, (310, 80))
    
    # Munição (movida para a direita)
    ammo_label = font_medium.render("FLECHAS", True, (255, 255, 255))
    window.blit(ammo_label, (900, 75))
    draw_health_bar(window, 1020, 80, 200, 25, bow_left.ammo, bow_left.max_ammo, 
                   (255, 215, 0) if bow_left.ammo > 10 else (255, 50, 50))
    ammo_text = font_small.render(f"{bow_left.ammo}/{bow_left.max_ammo}", True, (255, 255, 255))
    window.blit(ammo_text, (1230, 80))
    
    # Status de Stun - embaixo do score
    if player_obj.stun_timer > 0:
        stun_bg = pygame.Surface((250, 60), pygame.SRCALPHA)
        pygame.draw.rect(stun_bg, (0, 100, 200, 200), stun_bg.get_rect(), border_radius=10)
        stun_bg_x = 640 - 125  # Centraliza embaixo do score
        window.blit(stun_bg, (stun_bg_x, 65))
        
        stun_label = font_medium.render("❄️ CONGELADO!", True, (150, 220, 255))
        window.blit(stun_label, (stun_bg_x + 10, 70))
        stun_time = font_small.render(f"{player_obj.stun_timer:.1f}s", True, (255, 255, 255))
        window.blit(stun_time, (stun_bg_x + 10, 100))



def draw_game_over(window, score):
    """Desenha tela de game over"""
    # Overlay escuro
    overlay = pygame.Surface((1280, 720), pygame.SRCALPHA)
    pygame.draw.rect(overlay, (0, 0, 0, 180), overlay.get_rect())
    window.blit(overlay, (0, 0))
    
    # Textos
    font_gameover = pygame.font.SysFont('Arial', 120, bold=True)
    font_score = pygame.font.SysFont('Arial', 60, bold=True)
    font_instruction = pygame.font.SysFont('Arial', 40)
    
    # Game Over com efeito de sombra
    gameover_shadow = font_gameover.render("GAME OVER", True, (0, 0, 0))
    gameover_text = font_gameover.render("GAME OVER", True, (255, 50, 50))
    window.blit(gameover_shadow, (640 - gameover_text.get_width() // 2 + 5, 205))
    window.blit(gameover_text, (640 - gameover_text.get_width() // 2, 200))
    
    # Score final
    final_score = font_score.render(f"Score Final: {score}", True, (255, 215, 0))
    window.blit(final_score, (640 - final_score.get_width() // 2, 350))
    
    # Instruções
    instruction = font_instruction.render("Pressione ESC para voltar ao menu", True, (200, 200, 200))
    window.blit(instruction, (640 - instruction.get_width() // 2, 500))


def draw_pause_menu(window):
    """Desenha menu de pausa"""
    # Overlay semi-transparente
    overlay = pygame.Surface((1280, 720), pygame.SRCALPHA)
    pygame.draw.rect(overlay, (0, 0, 0, 150), overlay.get_rect())
    window.blit(overlay, (0, 0))
    
    # Painel central
    panel_width, panel_height = 600, 400
    panel_x = (1280 - panel_width) // 2
    panel_y = (720 - panel_height) // 2
    
    panel = pygame.Surface((panel_width, panel_height), pygame.SRCALPHA)
    pygame.draw.rect(panel, (40, 40, 60, 230), panel.get_rect(), border_radius=20)
    pygame.draw.rect(panel, (100, 100, 150), panel.get_rect(), 3, border_radius=20)
    window.blit(panel, (panel_x, panel_y))
    
    # Textos
    font_title = pygame.font.SysFont('Arial', 80, bold=True)
    font_option = pygame.font.SysFont('Arial', 40)
    
    # Título
    pause_text = font_title.render("PAUSADO", True, (255, 215, 0))
    window.blit(pause_text, (640 - pause_text.get_width() // 2, panel_y + 60))
    
    # Instruções
    instructions = [
        "ESC ou P - Continuar",
        "",
        "Controles:",
        "WASD - Mover",
        "Mouse Esquerdo - Ataque Melee",
        "Mouse Direito - Ataque Ranged"
    ]
    
    y_offset = panel_y + 140
    for instruction in instructions:
        if instruction == "":
            y_offset += 20
            continue
        text = font_option.render(instruction, True, (200, 200, 200))
        window.blit(text, (640 - text.get_width() // 2, y_offset))
        y_offset += 40


def draw_tutorial(window, time_remaining):
    """Desenha tutorial inicial"""
    # Painel semi-transparente
    panel_width, panel_height = 700, 500
    panel_x = (1280 - panel_width) // 2
    panel_y = (720 - panel_height) // 2
    
    panel = pygame.Surface((panel_width, panel_height), pygame.SRCALPHA)
    pygame.draw.rect(panel, (0, 30, 60, 220), panel.get_rect(), border_radius=20)
    pygame.draw.rect(panel, (100, 150, 255), panel.get_rect(), 4, border_radius=20)
    window.blit(panel, (panel_x, panel_y))
    
    # Textos
    font_title = pygame.font.SysFont('Arial', 60, bold=True)
    font_text = pygame.font.SysFont('Arial', 35)
    font_small = pygame.font.SysFont('Arial', 25, italic=True)
    
    # Título
    title = font_title.render("COMO JOGAR", True, (255, 215, 0))
    window.blit(title, (640 - title.get_width() // 2, panel_y + 30))
    
    # Controles
    controls = [
        ("WASD", "Mover o personagem"),
        ("Mouse Esquerdo", "Ataque corpo a corpo"),
        ("Mouse Direito", "Ataque à distância"),
        ("ESC / P", "Pausar o jogo"),
    ]
    
    y_offset = panel_y + 120
    for key, description in controls:
        key_text = font_text.render(key, True, (100, 200, 255))
        desc_text = font_text.render(f"- {description}", True, (220, 220, 220))
        window.blit(key_text, (panel_x + 50, y_offset))
        window.blit(desc_text, (panel_x + 280, y_offset))
        y_offset += 60
    
    # Objetivo
    objective = font_text.render("Objetivo: Sobreviva e derrote os inimigos!", True, (255, 180, 100))
    window.blit(objective, (640 - objective.get_width() // 2, panel_y + 400))
    
    # Timer
    skip_text = font_small.render(f"Pressione ESPAÇO para pular ({time_remaining:.0f}s)", True, (180, 180, 200))
    window.blit(skip_text, (640 - skip_text.get_width() // 2, panel_y + 450))
