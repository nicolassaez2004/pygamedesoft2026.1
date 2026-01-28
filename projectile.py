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
    
    def __init__(self, x, y, target_x, target_y, speed=500, color=(255, 255, 0), radius=5, damage=1, image=None, stun_duration=0):
        self.pos = pygame.Vector2(x, y)
        self.target = pygame.Vector2(target_x, target_y)
        self.speed = speed
        self.radius = radius
        self.color = color
        self.damage = damage
        self.image = image  # opcional: sprite do projétil
        self.stun_duration = stun_duration  # Duração do congelamento causado (0 se não congela)
        
        # Calcula direção
        direction = self.target - self.pos
        if direction.length() > 0:
            self.velocity = direction.normalize() * speed
        else:
            self.velocity = pygame.Vector2(0, 0)
    
    def update(self, dt):
        """Atualiza a posição do projétil"""
        self.pos += self.velocity * dt
    
    def draw(self, window):
        """Desenha o projétil com efeitos visuais melhorados"""
        if self.image is not None:
            angle = -math.degrees(math.atan2(self.velocity.y, self.velocity.x)) if self.velocity.length() > 0 else 0
            rotated = pygame.transform.rotate(self.image, angle)
            rect = rotated.get_rect(center=(self.pos.x, self.pos.y))
            window.blit(rotated, rect)
        else:
            # Efeito de brilho (círculos concêntricos)
            for i in range(3):
                alpha_value = 255 - (i * 80)
                radius = self.radius + i * 2
                glow_color = tuple(max(0, min(255, c - i * 50)) for c in self.color)
                pygame.draw.circle(window, glow_color, self.pos, radius)
            
            # Círculo principal
            pygame.draw.circle(window, self.color, self.pos, self.radius)
            # Brilho central
            pygame.draw.circle(window, (255, 255, 255), self.pos, max(1, self.radius // 2))
    
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
                speed=500,
                color=(255, 255, 0),
                radius=5,
                damage=1
            )
            self.projectiles.append(projectile)
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
                    
                    if projectile not in [p for p, _ in hit_enemies]:
                        hit_enemies.append((projectile, enemy))
                        
                        # Remove o projétil apenas se acertar inimigo NÃO imune
                        if not is_immune and projectile in self.projectiles:
                            self.projectiles.remove(projectile)
                            break
        
        return hit_enemies
    
    def get_projectile_count(self):
        """Retorna quantidade de projéteis ativos"""
        return len(self.projectiles)
