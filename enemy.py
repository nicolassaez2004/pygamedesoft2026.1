import pygame
import random
import math


class Enemy:
    """Classe que representa um inimigo no jogo"""
    
    def __init__(self, x, y, speed=150, radius=20):
        self.pos = pygame.Vector2(x, y)
        self.speed = speed
        self.radius = radius
        self.color = (255, 0, 0)
        self.health = 1
        self.max_health = 1
        
    def update(self, dt, player_pos, window_width, window_height):
        """Atualiza a posição do inimigo em direção ao player"""
        direction = player_pos - self.pos
        
        if direction.length() > 0:
            direction = direction.normalize()
            self.pos += direction * self.speed * dt
        
        # Mantém o inimigo dentro da tela
        self.pos.x = max(self.radius, min(self.pos.x, window_width - self.radius))
        self.pos.y = max(self.radius, min(self.pos.y, window_height - self.radius))
    
    def draw(self, window):
        """Desenha o inimigo"""
        pygame.draw.circle(window, self.color, self.pos, self.radius)
        
    def is_colliding_with_player(self, player_pos, player_radius):
        """Verifica colisão com o player"""
        distance = self.pos.distance_to(player_pos)
        return distance < (self.radius + player_radius)
    
    def take_damage(self, damage):
        """Aplica dano ao inimigo"""
        self.health -= damage
        return self.health <= 0


class EnemyManager:
    """Gerencia os inimigos do jogo"""
    
    def __init__(self, window_width, window_height, spawn_margin=50):
        self.enemies = []
        self.window_width = window_width
        self.window_height = window_height
        self.spawn_margin = spawn_margin
        
        self.spawn_timer = 0
        self.spawn_interval = 1.0  # segundos entre spawns
        self.max_enemies = 5
        self.difficulty = 1.0  # multiplicador de dificuldade
        
    def spawn_enemy(self):
        """Spawna um novo inimigo em um local aleatório nas bordas"""
        side = random.choice(['top', 'bottom', 'left', 'right'])
        
        if side == 'top':
            x = random.randint(0, self.window_width)
            y = -self.spawn_margin
        elif side == 'bottom':
            x = random.randint(0, self.window_width)
            y = self.window_height + self.spawn_margin
        elif side == 'left':
            x = -self.spawn_margin
            y = random.randint(0, self.window_height)
        else:  # right
            x = self.window_width + self.spawn_margin
            y = random.randint(0, self.window_height)
        
        speed = 150 * self.difficulty
        enemy = Enemy(x, y, speed=speed)
        self.enemies.append(enemy)
    
    def update(self, dt, player_pos):
        """Atualiza todos os inimigos"""
        # Spawna novos inimigos se houver espaço
        self.spawn_timer += dt
        if self.spawn_timer >= self.spawn_interval and len(self.enemies) < self.max_enemies:
            self.spawn_enemy()
            self.spawn_timer = 0
        
        # Atualiza cada inimigo
        for enemy in self.enemies:
            enemy.update(dt, player_pos, self.window_width, self.window_height)
    
    def draw(self, window):
        """Desenha todos os inimigos"""
        for enemy in self.enemies:
            enemy.draw(window)
    
    def check_collisions_with_player(self, player_pos, player_radius):
        """Verifica colisões com o player, retorna True se há colisão"""
        for enemy in self.enemies:
            if enemy.is_colliding_with_player(player_pos, player_radius):
                return True
        return False
    
    def remove_enemy(self, enemy):
        """Remove um inimigo da lista"""
        if enemy in self.enemies:
            self.enemies.remove(enemy)
    
    def get_all_enemies(self):
        """Retorna lista de todos os inimigos"""
        return self.enemies
    
    def increase_difficulty(self, score):
        """Aumenta a dificuldade baseado no score"""
        self.difficulty = 1.0 + (score // 1000) * 0.1
        self.max_enemies = 5 + (score // 2000)
        self.spawn_interval = max(0.5, 1.0 - (score // 5000) * 0.1)
    
    def clear(self):
        """Limpa todos os inimigos"""
        self.enemies.clear()
