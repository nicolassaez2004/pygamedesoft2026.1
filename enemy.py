import pygame
import random
import math
import os
import projectile


class Enemy:
    """Classe base de inimigo"""

    def __init__(self, x, y, sprite, speed=150, radius=None):
        self.pos = pygame.Vector2(x, y)
        self.speed = speed
        self.sprite = sprite
        self.sprite_flipped = pygame.transform.flip(self.sprite, True, False)
        self.radius = radius if radius is not None else self.sprite.get_width() // 2
        self.health = 1
        self.max_health = 1
        self.flipped = False

    def move_towards(self, target_pos, dt):
        direction = target_pos - self.pos
        if direction.length() > 0:
            direction = direction.normalize()
            self.pos += direction * self.speed * dt

    def clamp_inside(self, window_width, window_height):
        self.pos.x = max(self.radius, min(self.pos.x, window_width - self.radius))
        self.pos.y = max(self.radius, min(self.pos.y, window_height - self.radius))

    def update(self, dt, player_pos, window_width, window_height):
        # Por padrão segue o player
        self.move_towards(player_pos, dt)
        self.clamp_inside(window_width, window_height)
        self.flipped = self.pos.x > player_pos.x

    def draw(self, window):
        surface = self.sprite_flipped if self.flipped else self.sprite
        rect = surface.get_rect(center=(self.pos.x, self.pos.y))
        window.blit(surface, rect)

    def is_colliding_with_player(self, player_pos, player_radius):
        return self.pos.distance_to(player_pos) < (self.radius + player_radius)

    def take_damage(self, damage):
        self.health -= damage
        return self.health <= 0


class RangedEnemy(Enemy):
    """Inimigo que prefere manter distância e atira projéteis"""

    def __init__(self, x, y, sprite, speed=140, radius=None, preferred_min=250, preferred_max=400):
        super().__init__(x, y, sprite, speed, radius)
        self.preferred_min = preferred_min
        self.preferred_max = preferred_max
        self.shoot_cooldown = 0
        self.shoot_interval = 1.8

    def update(self, dt, player_pos, window_width, window_height):
        direction = player_pos - self.pos
        dist = direction.length()

        if dist > 0:
            direction = direction.normalize()

        # Move para longe se muito perto, aproxima levemente se muito longe
        if dist < self.preferred_min:
            self.pos -= direction * self.speed * dt
        elif dist > self.preferred_max:
            self.pos += direction * (self.speed * 0.4) * dt
        # caso contrário, permanece parado (kiting)

        self.clamp_inside(window_width, window_height)
        self.flipped = self.pos.x > player_pos.x
        self.shoot_cooldown = max(0, self.shoot_cooldown - dt)

    def can_shoot(self):
        return self.shoot_cooldown <= 0

    def reset_cooldown(self):
        self.shoot_cooldown = self.shoot_interval


class GhostersonEnemy(Enemy):
    """Inimigo do tipo Ghosterson - imune a projéteis, só leva dano de espada"""

    def __init__(self, x, y, sprite, speed=160, radius=None):
        super().__init__(x, y, sprite, speed, radius)
        self.immune_to_projectiles = True  # Só pode ser morto por ataques melee


class SkellingtonEnemy(RangedEnemy):
    """Skellington: fica à distância e atira flechas aleatórias"""

    def __init__(self, x, y, sprite, speed=140, radius=None):
        super().__init__(x, y, sprite, speed, radius, preferred_min=260, preferred_max=420)

    def maybe_shoot(self, player_pos):
        if not self.can_shoot():
            return None

        # Radii ajustados para sprite 100x100
        arrow_types = [
            {"sprite": 0, "speed": 520, "damage": 1, "radius": 18},
            {"sprite": 1, "speed": 560, "damage": 1, "radius": 18},
            {"sprite": 2, "speed": 500, "damage": 2, "radius": 20},
        ]
        choice = random.choice(arrow_types)
        self.reset_cooldown()
        return projectile.Projectile(
            self.pos.x,
            self.pos.y,
            player_pos.x,
            player_pos.y,
            speed=choice["speed"],
            color=(255, 255, 255),
            radius=choice["radius"],
            damage=choice["damage"],
            image=self.manager_ref.arrow_sprites[choice["sprite"]]
        )


class MageEnemy(RangedEnemy):
    """Mago: fica longe e lança magias aleatórias"""

    def __init__(self, x, y, sprite, speed=130, radius=None):
        super().__init__(x, y, sprite, speed, radius, preferred_min=260, preferred_max=420)
        self.shoot_interval = 2.1

    def maybe_shoot(self, player_pos):
        if not self.can_shoot():
            return None

        # Radii ajustados para sprite 100x100
        spells = [
            {"sprite": 0, "speed": 420, "damage": 2, "radius": 20},
            {"sprite": 1, "speed": 480, "damage": 1, "radius": 18},
            {"sprite": 2, "speed": 380, "damage": 3, "radius": 22},
        ]
        choice = random.choice(spells)
        self.reset_cooldown()
        return projectile.Projectile(
            self.pos.x,
            self.pos.y,
            player_pos.x,
            player_pos.y,
            speed=choice["speed"],
            color=(255, 255, 255),
            radius=choice["radius"],
            damage=choice["damage"],
            image=self.manager_ref.magic_sprites[choice["sprite"]]
        )


class EnemyManager:
    """Gerencia os inimigos do jogo"""

    def __init__(self, window_width, window_height, spawn_margin=50):
        self.enemies = []
        self.window_width = window_width
        self.window_height = window_height
        self.spawn_margin = spawn_margin

        # Carrega os sprites dos inimigos uma vez
        ghost_path = os.path.join("Sprites", "Ghosterson_light.png")
        skell_path = os.path.join("Sprites", "Skellington_gerson.png")
        mage_path = os.path.join("Sprites", "MageMicoz.png")
        arrow_paths = [
            os.path.join("Sprites", "Flecha1.png"),
            os.path.join("Sprites", "Flecha2.png"),
            os.path.join("Sprites", "Flecha3.png"),
        ]
        magic_paths = [
            os.path.join("Sprites", "Magia1.png"),
            os.path.join("Sprites", "Magia2.png"),
            os.path.join("Sprites", "Magia3.png"),
        ]

        # Função utilitária para carregar e escalar
        def load_and_scale(path, size, fallback_color):
            try:
                img = pygame.image.load(path).convert_alpha()
            except Exception:
                img = pygame.Surface((size, size), pygame.SRCALPHA)
                img.fill(fallback_color)
            return pygame.transform.smoothscale(img, (size, size))

        desired_size = 80
        proj_size = 100  # projéteis um pouco maiores
        self.ghost_sprite = load_and_scale(ghost_path, desired_size, (255, 0, 0))
        self.skell_sprite = load_and_scale(skell_path, desired_size, (0, 255, 0))
        self.mage_sprite = load_and_scale(mage_path, desired_size, (150, 0, 255))
        self.arrow_sprites = [load_and_scale(p, proj_size, (255, 255, 0)) for p in arrow_paths]
        self.magic_sprites = [load_and_scale(p, proj_size, (255, 0, 255)) for p in magic_paths]

        self.spawn_timer = 0
        self.spawn_interval = 1.0  # segundos entre spawns
        self.max_enemies = 5
        self.difficulty = 1.0  # multiplicador de dificuldade
        self.enemy_projectiles = []

    def spawn_enemy(self):
        """Spawna um novo inimigo em um local aleatório nas bordas e tipo aleatório"""
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

        # Tipo aleatório de inimigo (inclui mago)
        enemy_type = random.choice(['ghost', 'skell', 'mage'])

        # Variação leve de velocidade por spawn para aleatoriedade
        base_speed = 150 * self.difficulty
        speed_variation = random.uniform(0.9, 1.2)
        speed = base_speed * speed_variation

        if enemy_type == 'ghost':
            enemy_obj = GhostersonEnemy(x, y, sprite=self.ghost_sprite, speed=speed)
        elif enemy_type == 'mage':
            enemy_obj = MageEnemy(x, y, sprite=self.mage_sprite, speed=speed)
        else:
            enemy_obj = SkellingtonEnemy(x, y, sprite=self.skell_sprite, speed=speed)

        # referência para acessar sprites de projéteis
        enemy_obj.manager_ref = self
        self.enemies.append(enemy_obj)

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

            # Disparo para inimigos à distância
            if isinstance(enemy, (SkellingtonEnemy, MageEnemy)):
                proj = enemy.maybe_shoot(player_pos)
                if proj:
                    self.enemy_projectiles.append(proj)

        # Atualiza projéteis de inimigos
        for proj in self.enemy_projectiles[:]:
            proj.update(dt)
            if proj.is_out_of_bounds(self.window_width, self.window_height):
                self.enemy_projectiles.remove(proj)

    def draw(self, window):
        """Desenha todos os inimigos"""
        for enemy in self.enemies:
            enemy.draw(window)
        # Desenha projéteis inimigos
        for proj in self.enemy_projectiles:
            proj.draw(window)

    def check_collisions_with_player(self, player_pos, player_radius):
        """Verifica colisões com o player, retorna inimigo que colidiu ou None"""
        for enemy in self.enemies[:]:
            if enemy.is_colliding_with_player(player_pos, player_radius):
                return enemy
        # Checa projéteis inimigos
        for proj in self.enemy_projectiles[:]:
            if proj.is_colliding_with_enemy(player_pos, player_radius):
                self.enemy_projectiles.remove(proj)
                return 'projectile'  # Retorna string para indicar que foi projétil
        return None

    def remove_enemy(self, enemy):
        """Remove um inimigo da lista"""
        if enemy in self.enemies:
            self.enemies.remove(enemy)

    def get_all_enemies(self):
        """Retorna lista de todos os inimigos"""
        return self.enemies

    def increase_difficulty(self, score):
        """Aumenta a dificuldade baseado no score"""
        # A cada 500 pontos, aumenta a velocidade em 15%
        self.difficulty = 1.0 + (score // 500) * 0.15
        # A cada 1000 pontos, adiciona mais 1 inimigo (máximo)
        self.max_enemies = 5 + (score // 1000)
        # A cada 2000 pontos, reduz o tempo entre spawns
        self.spawn_interval = max(0.3, 1.0 - (score // 2000) * 0.15)

    def clear(self):
        """Limpa todos os inimigos"""
        self.enemies.clear()
        self.enemy_projectiles.clear()
