import pygame
import math

class Player:
    """Classe que representa o jogador com animações de spritesheet"""
    
    def __init__(self, x, y, window_width, window_height):
        self.pos = pygame.Vector2(x, y)
        self.window_width = window_width
        self.window_height = window_height
        self.radius = 41
        self.speed = 300
        self.max_health = 5
        self.health = 5
        self.game_over = False
        
        # Estado da animação
        self.state = "idle"  # idle, walk, attack, hurt, death
        self.facing_direction = pygame.Vector2(1, 0)
        self.animation_frame = 0
        self.animation_timer = 0
        self.animation_speed = 8  # frames por segundo (ataque mais rápido)
        
        # Carregar spritesheets
        self.spritesheets = {}
        self.animation_frames = {}  # Armazena frames extraídos dos spritesheets
        self._load_sprites()
        self.current_sprite = self.animation_frames["idle"][0] if "idle" in self.animation_frames else None
        
        # Dano temporário
        self.hurt_timer = 0
        self.hurt_duration = 0.3  # segundos
        
        # Ataque melee
        self.attack_timer = 0
        self.attack_duration = 0.42  # Duração mais curta para ataque ficar ágil
        self.melee_spawned = False  # Controle para gerar hitbox apenas no timing
    
    def _load_sprites(self):
        """Carrega todos os spritesheets do jogador"""
        # Cada spritesheet tem uma quantidade diferente de frames
        sprite_info = {
            "idle": ("jogador/IDLE.png", 7, 96),      # 7 frames, 96px cada
            "walk": ("jogador/WALK.png", 8, 96),      # 8 frames, 96px cada
            "attack1": ("jogador/ATTACK 1.png", 6, 96),  # 6 frames, 96px cada
            "hurt": ("jogador/HURT.png", 4, 96),      # 4 frames, 96px cada
            "death": ("jogador/DEATH.png", 12, 96)     # 12 frames, 96px cada
        }
        
        try:
            for state, (path, num_frames, frame_width) in sprite_info.items():
                spritesheet = pygame.image.load(path)
                self.spritesheets[state] = spritesheet
                
                # Extrai frames do spritesheet
                frames = []
                sheet_height = spritesheet.get_height()
                
                for i in range(num_frames):
                    x = i * frame_width
                    # Cria um subsurface (referência, não cópia)
                    try:
                        frame = spritesheet.subsurface(
                            pygame.Rect(x, 0, frame_width, sheet_height)
                        )
                        # Faz uma cópia para garantir que funcione
                        frame = frame.copy()
                        # Redimensiona para tamanho apropriado (225x225 = 150×1.5)
                        frame = pygame.transform.scale(frame, (225, 225))
                        frames.append(frame)
                    except ValueError as e:
                        print(f"Erro ao extrair frame {i} de {state}: {e}")
                        # Cria frame padrão
                        dummy = pygame.Surface((225, 225))
                        dummy.fill((0, 255, 0))
                        frames.append(dummy)
                
                self.animation_frames[state] = frames
                
        except Exception as e:
            print(f"Erro ao carregar sprites: {e}")
            # Se não conseguir carregar, cria sprites padrão
            dummy_surface = pygame.Surface((150, 150))
            dummy_surface.fill((0, 255, 0))
            sprite_info_keys = ["idle", "walk", "attack1", "hurt", "death"]
            for state in sprite_info_keys:
                self.animation_frames[state] = [dummy_surface]
    
    def update(self, dt, keys, mouse_buttons):
        """Atualiza o estado do jogador"""
        if self.game_over:
            self.state = "death"
            return
        
        # Atualiza timer de dano
        if self.hurt_timer > 0:
            self.hurt_timer -= dt
        
        # Atualiza timer de ataque
        if self.attack_timer > 0:
            self.attack_timer -= dt
        
        # Movimento (pode acontecer em qualquer momento, até durante dano)
        is_moving = False
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
        # 1. Ataque tem prioridade máxima (usa spritesheet "attack1")
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
        
        # Atualiza animação
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
    
    def trigger_attack(self):
        """Inicia o ataque melee"""
        if self.attack_timer <= 0:  # Só permite novo ataque se não estiver em ataque
            self.attack_timer = self.attack_duration
            self.animation_frame = 0  # Reinicia a animação
            self.melee_spawned = False
            return True
        return False
    
    def get_melee_attack(self):
        """Retorna um ataque melee se estiver ativo (apenas uma vez por ataque)"""
        # Cria o ataque apenas quando o timer está ativo
        if self.attack_timer > 0:
            # attack_timer começa em attack_duration e diminui
            elapsed_time = self.attack_duration - self.attack_timer
            # A animação attack1 tem 6 frames; últimos 3 frames são a segunda metade
            damage_start = 0.5 * self.attack_duration  # a partir do frame 3 (de 6)
            if not self.melee_spawned and elapsed_time >= damage_start:
                self.melee_spawned = True
                return MeleeAttack(self.pos, self.facing_direction, damage=2)
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
        
        # Desenha barra de vida
        bar_width = 60
        bar_height = 8
        bar_x = int(self.pos.x) - bar_width // 2
        bar_y = int(self.pos.y) - 50
        
        # Fundo da barra (vermelho)
        pygame.draw.rect(window, (255, 0, 0), (bar_x, bar_y, bar_width, bar_height))
        
        
        # Barra de vida (verde)
        health_percentage = max(0, self.health / self.max_health)
        pygame.draw.rect(window, (0, 255, 0), (bar_x, bar_y, bar_width * health_percentage, bar_height))
        
        # Borda da barra
        pygame.draw.rect(window, (255, 255, 255), (bar_x, bar_y, bar_width, bar_height), 1)


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
