import pygame
import menu
import gameplay
import leaderboard

#controla as telas (a leaderboard ainda não tem nada)
def main():
    pygame.init()
    window = pygame.display.set_mode((1280, 720))
    pygame.display.set_caption("Pitagoras Ops")
    clock = pygame.time.Clock()

    estado = "menu"

    while estado != "quit":
        if estado == "menu":
            estado = menu.menu_loop(window, clock)

        elif estado == "gameplay":
            estado = gameplay.gameplay_loop(window, clock)

        elif estado == "leaderboard":
            estado = leaderboard.leaderboard_loop(window, clock)

    pygame.quit()


if __name__ == "__main__":
    main()
