#!/usr/bin/env python3
"""Script de teste para validar o player.py"""

import pygame
import sys

pygame.init()

try:
    from player import Player, assets
    print("✓ Player importado com sucesso")
    print(f"✓ Assets carregados: {len(assets)} itens")
    print(f"  Assets disponíveis: {list(assets.keys())}")
    
    # Teste básico de inicialização
    window = pygame.display.set_mode((1280, 720))
    p = Player(640, 360, 1280, 720)
    print(f"✓ Player instanciado com sucesso")
    print(f"  - Posição: {p.pos}")
    print(f"  - Arma inicial: {p.weapon}")
    print(f"  - Estado: {p.state}")
    print(f"  - Sprite atual: {p.current_sprite}")
    
    # Testa mudança de arma
    p.set_weapon("espada")
    print(f"✓ Arma trocada para: {p.weapon}")
    print(f"  - Dano melee: {p.melee_damage}")
    
    # Testa ataque
    p.trigger_attack()
    print(f"✓ Ataque disparado")
    print(f"  - Attack timer: {p.attack_timer}")
    
    pygame.quit()
    print("\n✓ Todos os testes passaram!")
    
except Exception as e:
    print(f"✗ Erro: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
