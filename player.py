import pygame
import math

#animações jogador parado
player_parado_nada = pygame.image.load('jogador/player-parado-nada.png') #player sem item na mão (não consegue atirar e seu golpe dá apenas 1 de dano)
player_parado_espada = pygame.image.load('jogador/player-parado-espada.png')
player_parado_arco = pygame.image.load('jogador/player-parado-arco.png')
player_parado_espada_arco = pygame.image.load('jogador/player-parado-espada-arco.png')

#animações jogador caminhando
player_andas_nada = pygame.image.load('jogador/player-andas-nada.png') #player sem item na mão (não consegue atirar e seu golpe dá apenas 1 de dano)
player_andas_espada = pygame.image.load('jogador/player-andas-espada.png')
player_andas_arco = pygame.image.load('jogador/player-andas-arco.png')
player_andas_espada_arco = pygame.image.load('jogador/player-parado-espada-arco.png')

#animações jogador golpeando

player_golpe_nada = pygame.image.load('jogador/player-golpe-nada.png') #player sem item na mão (não consegue atirar e seu golpe dá apenas 1 de dano)
player_golpe_espada = pygame.image.load('jogador/player-golpe-espada.png')
player_golpe_arco = pygame.image.load('jogador/player-golpe-arco.png')
player_golpe_espada_arco = pygame.image.load('jogador/player-parado-espada-arco.png')

assets = {}

#animações jogador parado
assets['player_parado_nada'] = player_parado_nada #player sem item na mão (não consegue atirar e seu golpe dá apenas 1 de dano)
assets['player_parado_espada'] = player_parado_espada
assets['player_parado_arco'] = player_parado_arco
assets['player_parado_espada_arco'] = player_parado_espada_arco

#animações jogador caminhando
assets['player_andas_nada'] = player_andas_nada #player sem item na mão (não consegue atirar e seu golpe dá apenas 1 de dano)
assets['player_andas_espada'] = player_andas_espada
assets['player_andas_arco'] = player_andas_arco
assets['player_andas_espada_arco'] = player_andas_espada_arco

#animações jogador golpeando
assets['player_golpe_nada'] = player_golpe_nada #player sem item na mão (não consegue atirar e seu golpe dá apenas 1 de dano)
assets['player_golpe_espada'] = player_golpe_espada
assets['player_golpe_arco'] = player_golpe_arco
assets['player_golpe_espada_arco'] = player_golpe_espada_arco

class Player:
    """Classe que representa o jogador com animações baseadas em assets"""
    
    def __init__(self, x, y, window_width, window_height):
        self.pos = pygame.Vector2(x, y)
        self.window_width = window_width
        self.window_height = window_height
        self.radius = 40
        self.speed = 300
        self.max_health = 5
        self.health = 5
        self.game_over = False
        
        # Estado da animação
        self.state = "idle"  # idle, walk, attack, hurt, death
        self.facing_direction = pygame.Vector2(1, 0)
        self.animation_frame = 0  # Frame atual da animação
        self.animation_timer = 0  # Timer para controlar velocidade da animação
        self.animation_speed = 8  # frames por segundo
        
        # Sistema de armas (começa sem armas)
        self.weapon = "nada"  # nada, espada, arco, espada_arco
        self.melee_damage = 1  # Dano padrão sem armas
        
        # Armazena frames de cada estado
        self.animation_frames = {}  # Chave: estado, valor: lista de frames
        
        # Carregar sprites como assets
        self._load_sprites()
        # Tenta usar o primeiro frame de idle, ou fallback
        if "idle" in self.animation_frames and len(self.animation_frames["idle"]) > 0:
            self.current_sprite = self.animation_frames["idle"][0]
        else:
            self.current_sprite = self._get_sprite_for_state("idle")
        
        # Dano temporário
        self.hurt_timer = 0
        self.hurt_duration = 0.3  # segundos
        
        # Congelamento por projéteis
        self.stun_timer = 0
        self.stun_duration = 0  # duração do congelamento
        
        # Ataque melee
        self.attack_timer = 0
        self.attack_duration = 0.42  # Duração mais curta para ataque ficar ágil
        self.melee_spawned = False  # Controle para gerar hitbox apenas no timing
    
    def _load_sprites(self):
        """Carrega os sprites dos assets como spritesheets e divide em frames"""
        # Dicionário que mapeia asset_key para (num_frames esperados)
        # Se a spritesheet tem 2 colunas e 2 linhas, são 4 frames, etc.
        frame_configs = {
            'player_parado_nada': None,      # Auto-detectar
            'player_parado_espada': None,
            'player_parado_arco': None,
            'player_parado_espada_arco': None,
            'player_andas_nada': None,
            'player_andas_espada': None,
            'player_andas_arco': None,
            'player_andas_espada_arco': None,
            'player_golpe_nada': None,
            'player_golpe_espada': None,
            'player_golpe_arco': None,
            'player_golpe_espada_arco': None,
        }
        
        # Carrega e divide cada asset em frames
        for asset_key in frame_configs:
            if asset_key not in assets:
                print(f"Aviso: Asset '{asset_key}' não encontrado")
                continue
            
            try:
                spritesheet = assets[asset_key].copy()
                width = spritesheet.get_width()
                height = spritesheet.get_height()
                
                # Frame size é 32x32 pixels
                frame_size = 32
                
                # Calcula quantos frames há na spritesheet
                frames_per_row = width // frame_size
                frames_per_col = height // frame_size
                total_frames = frames_per_row * frames_per_col
                
                print(f"Carregando '{asset_key}': {width}x{height}, "
                      f"{frames_per_row}x{frames_per_col} = {total_frames} frames")
                
                frames = []
                
                # Percorre de cima para baixo, esquerda para direita
                for row in range(frames_per_col):
                    for col in range(frames_per_row):
                        x = col * frame_size
                        y = row * frame_size
                        
                        # Extrai o frame (subsurface)
                        try:
                            frame = spritesheet.subsurface(
                                pygame.Rect(x, y, frame_size, frame_size)
                            )
                            # Copia para evitar problemas com subsurfaces
                            frame = frame.copy()
                            # Redimensiona para 80x80
                            frame = pygame.transform.scale(frame, (80, 80))
                            frames.append(frame)
                        except ValueError as e:
                            print(f"  Erro ao extrair frame ({col}, {row}): {e}")
                
                # Armazena os frames nomeados por estado + arma
                if asset_key.startswith('player_parado'):
                    state_key = 'idle'
                elif asset_key.startswith('player_andas'):
                    state_key = 'walk'
                elif asset_key.startswith('player_golpe'):
                    state_key = 'attack1'
                else:
                    state_key = 'idle'
                
                # Cria chave composta: estado + arma
                composite_key = (state_key, self.weapon)
                
                # Também armazena com chave simples (fallback para idle/walk/attack1 genérico)
                if state_key not in self.animation_frames or len(self.animation_frames[state_key]) < len(frames):
                    self.animation_frames[state_key] = frames
                    print(f"  ✓ {state_key} carregado com {len(frames)} frames")
                    
            except Exception as e:
                print(f"Erro ao processar '{asset_key}': {e}")
    
    def _get_sprite_for_state(self, state):
        """Retorna o sprite apropriado para um estado e arma atuais"""
        weapon_suffix = self.weapon
        state_prefix = ""
        
        if state == "idle":
            state_prefix = "player_parado"
        elif state == "walk":
            state_prefix = "player_andas"
        elif state == "attack1":
            state_prefix = "player_golpe"
        else:
            # Para hurt e death, tentar carregar de assets ou usar padrão
            asset_key = f"{state}_{self.weapon}"
            if asset_key in assets:
                img = assets[asset_key].copy()
                img = pygame.transform.scale(img, (80, 80))
                return img
            # Fallback
            dummy = pygame.Surface((80, 80))
            dummy.fill((100, 100, 100))
            return dummy
        
        # Constrói a chave do asset baseado em estado + arma
        asset_key = f"{state_prefix}_{weapon_suffix}"
        
        if asset_key in assets:
            img = assets[asset_key].copy()
            img = pygame.transform.scale(img, (80, 80))
            return img
        
        # Se não encontrar, tenta sem arma
        asset_key_fallback = f"{state_prefix}_nada"
        if asset_key_fallback in assets:
            img = assets[asset_key_fallback].copy()
            img = pygame.transform.scale(img, (80, 80))
            return img
        
        # Fallback final
        dummy = pygame.Surface((80, 80))
        dummy.fill((100, 100, 100))
        return dummy
    
    def update(self, dt, keys, mouse_buttons):
        """Atualiza o estado do jogador"""
        if self.game_over:
            self.state = "death"
            return
        
        # Atualiza timer de dano
        if self.hurt_timer > 0:
            self.hurt_timer -= dt
        
        # Atualiza timer de congelamento
        if self.stun_timer > 0:
            self.stun_timer -= dt
        
        # Atualiza timer de ataque
        if self.attack_timer > 0:
            self.attack_timer -= dt
        
        # Movimento (pode acontecer em qualquer momento, até durante dano)
        # Mas não pode se congelado
        is_moving = False
        if self.stun_timer <= 0:  # Só se não estiver congelado
            if keys[pygame.K_w]:
                self.pos.y -= self.speed * dt
                is_moving = True
            if keys[pygame.K_s]:
                self.pos.y += self.speed * dt
                is_moving = True
            if keys[pygame.K_a]:
                self.pos.x -= self.speed * dt
                is_moving = True
            if keys[pygame.K_d]:
                self.pos.x += self.speed * dt
                is_moving = True
        
        # Verifica ataque esquerdo - inicia o ataque
        if mouse_buttons[0]:  # Botão esquerdo
            self.trigger_attack()
        
        # Determina o estado de animação (ordem de prioridade)
        # 1. Ataque tem prioridade máxima
        if self.attack_timer > 0:
            self.state = "attack1"
        # 2. Dano (mas pode andar)
        elif self.hurt_timer > 0:
            self.state = "hurt"
        # 3. Movimento
        elif is_moving:
            self.state = "walk"
        # 4. Idle padrão
        else:
            self.state = "idle"
        
        # Atualiza direção para o mouse
        mouse_x, mouse_y = pygame.mouse.get_pos()
        direction = pygame.Vector2(mouse_x - self.pos.x, mouse_y - self.pos.y)
        if direction.length() > 0:
            self.facing_direction = direction.normalize()
        
        # Atualiza animação de frames
        self.animation_timer += dt
        frame_duration = 1.0 / self.animation_speed
        
        if self.animation_timer >= frame_duration:
            self.animation_timer = 0
            self.animation_frame += 1
            
            # Reseta para o primeiro frame se chegou ao final
            if self.state in self.animation_frames:
                total_frames = len(self.animation_frames[self.state])
                if self.animation_frame >= total_frames:
                    self.animation_frame = 0
        
        # Obtém o sprite atual baseado no estado e frame
        if self.state in self.animation_frames:
            frame_idx = min(self.animation_frame, len(self.animation_frames[self.state]) - 1)
            self.current_sprite = self.animation_frames[self.state][frame_idx]
        else:
            # Fallback se não houver frames carregados
            self.current_sprite = self._get_sprite_for_state(self.state)
        
        # Mantém o player dentro da tela
        self.pos.x = max(self.radius, min(self.pos.x, self.window_width - self.radius))
        self.pos.y = max(self.radius, min(self.pos.y, self.window_height - self.radius))
    
    def check_plataforma_collision(self, plataforma_x, plataforma_y, plataforma_width=480, plataforma_height=400):
        """Verifica colisão com a plataforma"""
        player_rect = pygame.Rect(self.pos.x - self.radius, self.pos.y - self.radius, self.radius * 2, self.radius * 2)
        
        # Define os 4 retângulos dos quadrados dos cantos
        corner_size = 35
        corner_rects = [
            pygame.Rect(plataforma_x, plataforma_y, corner_size, corner_size),
            pygame.Rect(plataforma_x + plataforma_width - corner_size, plataforma_y, corner_size, corner_size),
            pygame.Rect(plataforma_x, plataforma_y + plataforma_height - corner_size, corner_size, corner_size),
            pygame.Rect(plataforma_x + plataforma_width - corner_size, plataforma_y + plataforma_height - corner_size, corner_size, corner_size)
        ]
        
        # Verifica colisão com os 4 quadrados dos cantos
        for corner_rect in corner_rects:
            if player_rect.colliderect(corner_rect):
                corner_center_x = corner_rect.centerx
                corner_center_y = corner_rect.centery
                
                dx = self.pos.x - corner_center_x
                dy = self.pos.y - corner_center_y
                distance = (dx**2 + dy**2)**0.5
                
                if distance > 0:
                    dx_norm = dx / distance
                    dy_norm = dy / distance
                    self.pos.x = corner_center_x + dx_norm * (corner_size // 2 + self.radius + 5)
                    self.pos.y = corner_center_y + dy_norm * (corner_size // 2 + self.radius + 5)
                else:
                    self.pos.x = corner_rect.right + self.radius + 5
        
        # Bordas internas da plataforma
        margin = 35
        plat_left = plataforma_x + margin
        plat_right = plataforma_x + plataforma_width - margin
        plat_top = plataforma_y + margin
        plat_bottom = plataforma_y + plataforma_height - margin
        
        self.pos.x = max(plat_left + self.radius, min(self.pos.x, plat_right - self.radius))
        self.pos.y = max(plat_top + self.radius, min(self.pos.y, plat_bottom - self.radius))
    
    def take_damage(self, damage=1):
        """O jogador recebe dano"""
        if not self.game_over:
            self.health -= damage
            self.hurt_timer = self.hurt_duration
            if self.health <= 0:
                self.game_over = True
                self.health = 0
    
    def apply_stun(self, stun_duration):
        """Aplica congelamento ao jogador"""
        if stun_duration > 0:
            self.stun_timer = stun_duration
    
    def trigger_attack(self):
        """Inicia o ataque melee"""
        if self.attack_timer <= 0:  # Só permite novo ataque se não estiver em ataque
            self.attack_timer = self.attack_duration
            self.melee_spawned = False
            return True
        return False
    
    def set_weapon(self, weapon_type):
        """Define o tipo de arma do jogador (nada, espada, arco, espada_arco)"""
        if weapon_type in ["nada", "espada", "arco", "espada_arco"]:
            self.weapon = weapon_type
            # Ajusta dano do ataque baseado na arma
            if weapon_type == "nada":
                # Sem arma, dano mais baixo
                self.melee_damage = 1
            elif weapon_type == "espada":
                self.melee_damage = 3
            elif weapon_type == "arco":
                self.melee_damage = 1  # Arco é para disparar, não para melee
            elif weapon_type == "espada_arco":
                self.melee_damage = 2
    
    def get_melee_attack(self):
        """Retorna um ataque melee se estiver ativo (apenas uma vez por ataque)"""
        # Cria o ataque apenas quando o timer está ativo
        if self.attack_timer > 0:
            # attack_timer começa em attack_duration e diminui
            elapsed_time = self.attack_duration - self.attack_timer
            # Ataque ocorre na segunda metade da animação
            damage_start = 0.5 * self.attack_duration
            if not self.melee_spawned and elapsed_time >= damage_start:
                self.melee_spawned = True
                damage = getattr(self, 'melee_damage', 1)
                return MeleeAttack(self.pos, self.facing_direction, damage=damage)
        return None
    
    def draw(self, window):
        """Desenha o jogador"""
        if self.current_sprite is None:
            return
            
        # Inverte sprite se estiver olhando para esquerda
        sprite_to_draw = self.current_sprite
        if self.facing_direction.x < 0:
            sprite_to_draw = pygame.transform.flip(self.current_sprite, True, False)
        
        player_rect = sprite_to_draw.get_rect(center=(int(self.pos.x), int(self.pos.y)))
        window.blit(sprite_to_draw, player_rect)


class MeleeAttack:
    """Representa o ataque melee do jogador (hitbox do ATTACK 1)"""
    
    def __init__(self, player_pos, facing_direction, damage=2):
        self.player_pos = pygame.Vector2(player_pos)
        self.facing_direction = facing_direction.normalize() if facing_direction.length() > 0 else pygame.Vector2(1, 0)
        self.damage = damage
        
        # Tamanho da hitbox 
        self.width = 70
        self.height = 60
        
        # Posição da hitbox (à frente do jogador)
        offset_distance = 100
        self.pos = self.player_pos + self.facing_direction * offset_distance
    
    def get_rect(self):
        """Retorna o rect da hitbox"""
        return pygame.Rect(
            self.pos.x - self.width // 2,
            self.pos.y - self.height // 2,
            self.width,
            self.height
        )
    
    def is_colliding_with_enemy(self, enemy_pos, enemy_radius):
        """Verifica colisão com um inimigo"""
        distance = self.pos.distance_to(enemy_pos)
        return distance < (self.width // 2 + enemy_radius)
    
    def draw(self, window, debug=False):
        """Desenha a hitbox (apenas para debug)"""
        if debug:
            rect = self.get_rect()
            pygame.draw.rect(window, (255, 0, 0), rect, 2)
