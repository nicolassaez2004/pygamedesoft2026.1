#!/usr/bin/env python3
"""Script de teste para validar a integração com gameplay.py"""

import pygame
import sys

pygame.init()

try:
    import gameplay
    import player
    
    print("✓ Módulos importados com sucesso")
    
    # Testa inicializa()
    window = pygame.display.set_mode((1280, 720))
    assets = gameplay.inicializa(1280, 720)
    print(f"✓ Assets carregados pela gameplay: {len(assets)} itens")
    
    # Testa criação do player
    p = player.Player(640, 360, 1280, 720)
    print(f"✓ Player instanciado: {p.weapon=}")
    
    # Simula alguns updates para testar animação idle
    keys = {pygame.K_w: False, pygame.K_s: False, pygame.K_a: False, pygame.K_d: False}
    print(f"Total de frames idle: {len(p.animation_frames.get('idle', []))}")
    for i in range(6):
        p.update(0.016, keys, (False, False, False))
        print(f"  Frame {i+1}: state={p.state}, frame_idx={p.animation_frame}, "
              f"sprite_size={p.current_sprite.get_size() if p.current_sprite else 'None'}")
    
    # Testa transição de estado
    p.pos.x += 100  # Simula movimento
    keys = {pygame.K_w: True, pygame.K_s: False, pygame.K_a: False, pygame.K_d: False}
    print(f"\nTotal de frames walk: {len(p.animation_frames.get('walk', []))}")
    for i in range(6):
        p.update(0.016, keys, (False, False, False))
        print(f"  Frame {i+1}: state={p.state}, frame_idx={p.animation_frame}")
    
    # Testa ataque
    keys = {pygame.K_w: False, pygame.K_s: False, pygame.K_a: False, pygame.K_d: False}
    print(f"\nTotal de frames attack1: {len(p.animation_frames.get('attack1', []))}")
    p.update(0.016, keys, (True, False, False))  # Mouse button down
    print(f"✓ Após ataque: state={p.state}, attack_timer={p.attack_timer:.3f}, frame_idx={p.animation_frame}")
    
    pygame.quit()
    print("\n✓ Testes de integração passaram!")
    
except Exception as e:
    print(f"✗ Erro: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
