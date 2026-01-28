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
        self.health = 10
        self.max_health = 10
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

    def __init__(self, x, y, sprite, speed=160, radius=None, scale_factor=1.0, speed_multiplier=1.0):
        # Aplica o scale_factor ao sprite
        if scale_factor != 1.0:
            new_width = int(sprite.get_width() * scale_factor)
            new_height = int(sprite.get_height() * scale_factor)
            sprite = pygame.transform.smoothscale(sprite, (new_width, new_height))
        
        # Ajusta velocidade
        adjusted_speed = speed * speed_multiplier
        
        super().__init__(x, y, sprite, adjusted_speed, radius)
        
        # Ajusta o radius baseado no scale_factor
        if radius is None:
            self.radius = int((sprite.get_width() // 2) * scale_factor)
        
        self.immune_to_projectiles = True  # Só pode ser morto por ataques melee
        self.scale_factor = scale_factor
        self.speed_multiplier = speed_multiplier


class SkellingtonEnemy(RangedEnemy):
    """Skellington: fica à distância e atira flechas aleatórias"""

    def __init__(self, x, y, sprite, speed=140, radius=None):
        super().__init__(x, y, sprite, speed, radius, preferred_min=260, preferred_max=420)
        self.shoot_interval = 2.5  # Reduzido de 1.8 para começar mais devagar

    def maybe_shoot(self, player_pos):
        if not self.can_shoot():
            return None

        # Escalação de flechas por dificuldade
        difficulty_level = max(1.0, self.manager_ref.difficulty)
        
        if difficulty_level < 1.3:
            # Apenas flecha tipo 0 (fraca)
            arrow_idx = 0
        elif difficulty_level < 1.6:
            # Pode usar tipo 0 ou 1 (chance de tipo forte)
            arrow_idx = random.choice([0, 0, 1])  # 2/3 fraca, 1/3 média
        else:
            # Todos os tipos disponíveis
            arrow_idx = random.randint(0, 2)
        
        # Reduzir intervalo conforme dificuldade aumenta
        base_interval = 2.5
        difficulty_multiplier = max(1.0, 1.0 - (difficulty_level - 1.0) * 0.15)  # Reduz até 15% conforme dificuldade
        adjusted_interval = base_interval * difficulty_multiplier
        self.shoot_interval = adjusted_interval
        
        # Definição com escalação
        arrow_types = [
            {"sprite": 0, "speed": 315, "damage": 1, "radius": 18, "stun": 0},  # Flecha 1: 1 dano, -25%
            {"sprite": 1, "speed": 428, "damage": 2, "radius": 18, "stun": 0},  # Flecha 2: 2 dano, -5%
            {"sprite": 2, "speed": 460, "damage": 1, "radius": 20, "stun": 0.5},  # Flecha 3: 1 dano, congela 0.5s, +15%
        ]
        choice = arrow_types[arrow_idx]
        
        # Calcula velocidade escalada (apos 2 minutos)
        scaled_speed = self.manager_ref.get_scaled_projectile_speed(choice["speed"])
        
        # Calcula congelamento escalado (apenas para Flecha 3)
        if arrow_idx == 2:  # Apenas Flecha 3 congela
            scaled_stun = self.manager_ref.get_scaled_stun_duration(choice["stun"])
        else:
            scaled_stun = choice["stun"]
        
        self.reset_cooldown()
        return projectile.Projectile(
            self.pos.x,
            self.pos.y,
            player_pos.x,
            player_pos.y,
            speed=scaled_speed,
            color=(255, 255, 255),
            radius=choice["radius"],
            damage=choice["damage"],
            image=self.manager_ref.arrow_sprites[choice["sprite"]],
            stun_duration=scaled_stun
        )


class MageEnemy(RangedEnemy):
    """Mago: fica longe e lança magias aleatórias"""

    def __init__(self, x, y, sprite, speed=130, radius=None):
        super().__init__(x, y, sprite, speed, radius, preferred_min=260, preferred_max=420)
        self.shoot_interval = 2.8  # Reduzido de 2.1 para começar mais devagar

    def maybe_shoot(self, player_pos):
        if not self.can_shoot():
            return None

        # Escalação de magias por dificuldade
        difficulty_level = max(1.0, self.manager_ref.difficulty)
        
        if difficulty_level < 1.3:
            # Apenas magia tipo 0 (fraca)
            spell_idx = 0
        elif difficulty_level < 1.6:
            # Pode usar tipo 0 ou 1
            spell_idx = random.choice([0, 0, 1])  # 2/3 fraca, 1/3 média
        else:
            # Todos os tipos disponíveis
            spell_idx = random.randint(0, 2)
        
        # Reduzir intervalo conforme dificuldade aumenta
        base_interval = 2.8
        difficulty_multiplier = max(1.0, 1.0 - (difficulty_level - 1.0) * 0.15)  # Reduz até 15% conforme dificuldade
        adjusted_interval = base_interval * difficulty_multiplier
        self.shoot_interval = adjusted_interval
        
        # Definição com escalação
        spells = [
            {"sprite": 0, "speed": 255, "damage": 1, "radius": 16, "stun": 0},  # Magia 1: 1 dano,
            {"sprite": 1, "speed": 355, "damage": 2, "radius": 17, "stun": 0},  # Magia 2: 2 dano
            {"sprite": 2, "speed": 455, "damage": 1, "radius": 18, "stun": 0.5},  # Magia 3: 1 dano, congela 0.5s, +15%
        ]
        choice = spells[spell_idx]
        
        # Calcula velocidade escalada (apos 2 minutos)
        scaled_speed = self.manager_ref.get_scaled_projectile_speed(choice["speed"])
        
        # Calcula congelamento escalado (apenas para Magia 3)
        if spell_idx == 2:  # Apenas Magia 3 congela
            scaled_stun = self.manager_ref.get_scaled_stun_duration(choice["stun"])
        else:
            scaled_stun = choice["stun"]
        
        self.reset_cooldown()
        return projectile.Projectile(
            self.pos.x,
            self.pos.y,
            player_pos.x,
            player_pos.y,
            speed=scaled_speed,
            color=(255, 255, 255),
            radius=choice["radius"],
            damage=choice["damage"],
            image=self.manager_ref.magic_sprites[choice["sprite"]],
            stun_duration=scaled_stun
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
        self.spawn_interval = 2.0  # segundos entre spawns (aumentado para começar mais fácil)
        self.max_enemies = 3  # reduzido de 5 para 3
        self.difficulty = 1.0  # multiplicador de dificuldade
        self.enemy_projectiles = []
        self.current_score = 0  # Rastreia o score para ajustar dificuldade
        self.elapsed_time = 0  # Rastreia tempo decorrido para scaling de velocidade

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

        # Garantir que exista pelo menos um Ghosterson quando possível:
        # se atualmente não há nenhum Ghosterson e ainda há espaço para spawn
        # dentro do limite `max_enemies`, forçamos o próximo spawn a ser 'ghost'.
        if not any(isinstance(e, GhostersonEnemy) for e in self.enemies):
            enemy_type = 'ghost'

        # Variação leve de velocidade por spawn para aleatoriedade
        base_speed = 120 * self.difficulty 
        speed_variation = random.uniform(0.8, 1.1)  # Reduzido o range de variação
        speed = base_speed * speed_variation

        if enemy_type == 'ghost':
            # Fantasma com tamanho variável (0.4 a 1.0) e velocidade variável (1.0 a 1.4)
            ghost_scale = random.uniform(0.4, 1.0)
            ghost_speed_mult = random.uniform(1.0, 1.4)
            enemy_obj = GhostersonEnemy(
                x, y, 
                sprite=self.ghost_sprite, 
                speed=speed,
                scale_factor=ghost_scale,
                speed_multiplier=ghost_speed_mult
            )
        elif enemy_type == 'mage':
            enemy_obj = MageEnemy(x, y, sprite=self.mage_sprite, speed=speed)
        else:
            enemy_obj = SkellingtonEnemy(x, y, sprite=self.skell_sprite, speed=speed)

        # referência para acessar sprites de projéteis
        enemy_obj.manager_ref = self
        self.enemies.append(enemy_obj)

    def update(self, dt, player_pos, elapsed_time):
        """Atualiza todos os inimigos"""
        # Atualiza tempo decorrido para escalação de dificuldade
        self.elapsed_time = elapsed_time
        
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
        """Verifica colisões com o player, retorna tupla (tipo, objeto) ou None"""
        for enemy in self.enemies[:]:
            if enemy.is_colliding_with_player(player_pos, player_radius):
                return ('enemy', enemy)
        # Checa projéteis inimigos
        for proj in self.enemy_projectiles[:]:
            if proj.is_colliding_with_enemy(player_pos, player_radius):
                self.enemy_projectiles.remove(proj)
                return ('projectile', proj)  # Retorna projétil para aplicar stun
        return None

    def remove_enemy(self, enemy):
        """Remove um inimigo da lista"""
        if enemy in self.enemies:
            self.enemies.remove(enemy)

    def get_all_enemies(self):
        """Retorna lista de todos os inimigos"""
        return self.enemies[:]

    def increase_difficulty(self, score):
        """Aumenta dificuldade com base no score - progressão lenta"""
        self.current_score = score
        
        # Limitar máximo de inimigos conforme score (progressão mais lenta)
        if score < 1500:
            self.max_enemies = 3
        elif score < 3500:
            self.max_enemies = 4
        elif score < 6000:
            self.max_enemies = 5
        else:
            self.max_enemies = 6
        
        # Aumentar dificuldade muito mais gradualmente (reduzido de 1/5000 para 1/8000)
        self.difficulty = 1.0 + (score / 8000.0)
        
        # Spawn interval reduz bem lentamente
        self.spawn_interval = max(0.8, 2.0 - (score / 10000.0))
    
    def get_scaled_projectile_speed(self, base_speed):
        """Calcula velocidade do projétil baseado no tempo decorrido (a partir de 2 minutos)"""
        time_after_2min = max(0, self.elapsed_time - 120)  # 120 segundos = 2 minutos
        
        if time_after_2min <= 0:
            return base_speed
        
        # A cada segundo após 2 minutos, aumenta 2% de velocidade
        speed_multiplier = 1.0 + (time_after_2min * 0.02)
        return int(base_speed * speed_multiplier)
    
    def get_scaled_stun_duration(self, base_stun):
        """Calcula duração do congelamento baseado no tempo decorrido (a partir de 2 minutos)"""
        if base_stun == 0:
            return 0  # Sem congelamento base
        
        time_after_2min = max(0, self.elapsed_time - 120)  # 120 segundos = 2 minutos
        
        if time_after_2min <= 0:
            return 0.5  # Até 2 minutos, sempre 0.5s
        elif time_after_2min <= 600:  # 2:00 até 2:10 (10 segundos)
            return 0.6
        elif time_after_2min <= 1200:  # 2:11 até 2:20 (10 segundos)
            return 0.75
        elif time_after_2min <= 1800:  # 2:21 até 2:30 (10 segundos)
            return 0.9
        else:  # 2:31 em diante
            return 1.0

    def clear(self):
        """Limpa todos os inimigos"""
        self.enemies.clear()
        self.enemy_projectiles.clear()
