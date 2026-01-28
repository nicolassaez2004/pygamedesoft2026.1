import pygame
import math


class Coin:
    """Classe que representa uma moeda caída"""
    
    def __init__(self, x, y, value=10):
        self.pos = pygame.Vector2(x, y)
        self.value = value
        self.radius = 6
        self.collected = False
    
    def draw(self, window):
        """Desenha a moeda"""
        # Moeda dourada
        pygame.draw.circle(window, (255, 215, 0), self.pos, self.radius)
        pygame.draw.circle(window, (184, 134, 11), self.pos, self.radius, 2)
        # Brilho
        pygame.draw.circle(window, (255, 255, 100), self.pos, self.radius // 2)
    
    def is_colliding_with_player(self, player_pos, player_radius):
        """Verifica colisão com o jogador"""
        distance = self.pos.distance_to(player_pos)
        return distance < (self.radius + player_radius + 20)  # Hitbox maior para coleta automática


class Projectile:
    """Classe que representa um projétil (player ou inimigo)"""
    
    def __init__(self, x, y, target_x, target_y, speed=500, color=(255, 255, 0), radius=5, damage=1, image=None, stun_duration=0, penetration=0, no_ammo_consume_chance=0, trail_color=(255, 255, 150), enable_trail=True):
        self.pos = pygame.Vector2(x, y)
        self.target = pygame.Vector2(target_x, target_y)
        self.speed = speed
        self.radius = radius
        self.color = color
        self.damage = damage
        self.image = image  # opcional: sprite do projétil
        self.stun_duration = stun_duration  # Duração do congelamento causado (0 se não congela)
        self.penetration = penetration  # Número de inimigos que pode atravessar
        self.enemies_hit = set()  # Conjunto de inimigos já atingidos (para penetração)
        self.no_ammo_consume_chance = no_ammo_consume_chance  # Chance (0-1) de não consumir munição
        
        # Sistema de trail (rastro)
        self.trail = []  # Lista de posições anteriores para criar rastro
        self.trail_max_length = 8  # Comprimento máximo do trail
        self.trail_color = trail_color  # Cor do trail
        self.enable_trail = enable_trail  # Se deve ou não ter trail
        
        # Calcula direção
        direction = self.target - self.pos
        if direction.length() > 0:
            self.velocity = direction.normalize() * speed
        else:
            self.velocity = pygame.Vector2(0, 0)
    
    def update(self, dt):
        """Atualiza a posição do projétil"""
        # Adiciona posição atual ao trail antes de mover (só se enable_trail estiver ativo)
        if self.image is not None and self.enable_trail:
            self.trail.append(pygame.Vector2(self.pos.x, self.pos.y))
            if len(self.trail) > self.trail_max_length:
                self.trail.pop(0)
        
        self.pos += self.velocity * dt
    
    def draw(self, window):
        """Desenha o projétil com efeitos visuais melhorados"""
        if self.image is not None:
            # Desenha trail (rastro) antes do projétil (só se enable_trail estiver ativo)
            if self.enable_trail:
                for i, trail_pos in enumerate(self.trail):
                    alpha = int(255 * (i / max(1, len(self.trail))))
                    size = max(2, int(6 * (i / max(1, len(self.trail)))))
                    r, g, b = self.trail_color
                    trail_color = (r, g, b, alpha)  # Usa a cor do trail definida
                    trail_surface = pygame.Surface((size * 2, size * 2), pygame.SRCALPHA)
                    pygame.draw.circle(trail_surface, trail_color, (size, size), size)
                    window.blit(trail_surface, (trail_pos.x - size, trail_pos.y - size))
            
            angle = -math.degrees(math.atan2(self.velocity.y, self.velocity.x)) if self.velocity.length() > 0 else 0
            rotated = pygame.transform.rotate(self.image, angle)
            rect = rotated.get_rect(center=(self.pos.x, self.pos.y))
            window.blit(rotated, rect)
        else:
            # Projéteis de inimigos - desenho simples sem efeitos
            pygame.draw.circle(window, self.color, self.pos, self.radius)
    
    def is_out_of_bounds(self, window_width, window_height, margin=50):
        """Verifica se o projétil saiu da tela"""
        return (self.pos.x < -margin or self.pos.x > window_width + margin or
                self.pos.y < -margin or self.pos.y > window_height + margin)
    
    def is_colliding_with_enemy(self, enemy_pos, enemy_radius):
        """Verifica colisão com um inimigo"""
        distance = self.pos.distance_to(enemy_pos)
        return distance < (self.radius + enemy_radius)


class Bow:
    """Classe que representa o arco do player"""
    
    def __init__(self, player_pos, max_ammo=30):
        self.player_pos = player_pos
        self.max_ammo = max_ammo
        self.ammo = max_ammo
        self.projectiles = []
        
        self.reload_rate = 0.2  # segundos entre disparos
        self.shoot_cooldown = 0
        
        # Sistema de upgrade de flecha
        self.arrow_level = 0  # 0 = nada, 1 = FlechaJOGADOR1, 2 = FlechaJOGADOR2, 3 = FlechaJOGADOR3
        self.arrow_image = None  # Sprite da flecha
        self.arrow_speed = 500
        self.arrow_penetration = 0
        self.arrow_no_ammo_consume_chance = 0.0
        self.arrow_trail_color = (200, 200, 200)  # Cor do trail da flecha
        
    def set_arrow_level(self, level, image=None):
        """Define o nível de upgrade da flecha"""
        self.arrow_level = level
        self.arrow_image = image
        
        if level == 1:
            # FlechaJOGADOR1: propriedades normais, trail cinza/branco (ar)
            self.arrow_speed = 500
            self.arrow_penetration = 0
            self.arrow_no_ammo_consume_chance = 0.0
            self.arrow_trail_color = (200, 200, 200)  # Cinza/branco representando ar
        elif level == 2:
            # FlechaJOGADOR2: atravessa 1 inimigo (acerta 2 no máximo), mais rápida, trail verde (veneno)
            self.arrow_speed = 600
            self.arrow_penetration = 1
            self.arrow_no_ammo_consume_chance = 0.0
            self.arrow_trail_color = (100, 255, 100)  # Verde representando veneno
        elif level == 3:
            # FlechaJOGADOR3: atravessa 2 inimigos (acerta 3 no máximo), ainda mais rápida, 12.5% chance de não consumir munição, trail azul claro (gelo)
            # FlechaJOGADOR3: atravessa 2 inimigos (acerta 3 no máximo), ainda mais rápida, 12.5% chance de não consumir munição, trail azul claro (gelo)
            self.arrow_speed = 700
            self.arrow_penetration = 2
            self.arrow_no_ammo_consume_chance = 0.125
            self.arrow_trail_color = (150, 200, 255)  # Azul claro representando gelo
        
    def update(self, dt, player_pos):
        """Atualiza o arco e projéteis"""
        self.player_pos = player_pos
        self.shoot_cooldown = max(0, self.shoot_cooldown - dt)
        
        # Atualiza projéteis
        for projectile in self.projectiles[:]:
            projectile.update(dt)
            # Remove projéteis fora da tela
            if projectile.is_out_of_bounds(1280, 720):
                self.projectiles.remove(projectile)
    
    def shoot(self, target_x, target_y):
        """Dispara um projétil em direção ao alvo"""
        if self.ammo > 0 and self.shoot_cooldown <= 0:
            projectile = Projectile(
                self.player_pos.x,
                self.player_pos.y,
                target_x,
                target_y,
                speed=self.arrow_speed,
                color=(255, 255, 0),
                radius=5,
                damage=10,
                image=self.arrow_image,
                penetration=self.arrow_penetration,
                no_ammo_consume_chance=self.arrow_no_ammo_consume_chance,
                trail_color=self.arrow_trail_color
            )
            self.projectiles.append(projectile)
            
            # Verifica se deve consumir munição
            import random
            if random.random() > self.arrow_no_ammo_consume_chance:
                self.ammo -= 1
            
            self.shoot_cooldown = self.reload_rate
            return True
        return False
    
    def add_ammo(self, amount):
        """Adiciona munição, respeitando o máximo"""
        self.ammo = min(self.ammo + amount, self.max_ammo)
    
    def set_max_ammo(self, new_max):
        """Define o máximo de munição"""
        self.max_ammo = new_max
        self.ammo = min(self.ammo, self.max_ammo)
    
    def draw(self, window):
        """Desenha todos os projéteis"""
        for projectile in self.projectiles:
            projectile.draw(window)
    
    def check_collisions_with_enemies(self, enemies):
        """Verifica colisões com inimigos e retorna lista de inimigos atingidos"""
        hit_enemies = []
        
        for projectile in self.projectiles[:]:
            for enemy in enemies:
                if projectile.is_colliding_with_enemy(enemy.pos, enemy.radius):
                    # Verifica se o inimigo é imune a projéteis (como fantasma)
                    is_immune = hasattr(enemy, 'immune_to_projectiles') and enemy.immune_to_projectiles
                    
                    # Verifica se já acertou esse inimigo (para penetração)
                    enemy_id = id(enemy)
                    if enemy_id not in projectile.enemies_hit:
                        hit_enemies.append((projectile, enemy))
                        projectile.enemies_hit.add(enemy_id)
                        
                        # Remove o projétil se não tiver penetração ou já atingiu limite
                        if not is_immune:
                            hits_remaining = projectile.penetration - len(projectile.enemies_hit) + 1
                            if hits_remaining <= 0 and projectile in self.projectiles:
                                self.projectiles.remove(projectile)
                                break
        
        return hit_enemies
    
    def get_projectile_count(self):
        """Retorna quantidade de projéteis ativos"""
        return len(self.projectiles)
