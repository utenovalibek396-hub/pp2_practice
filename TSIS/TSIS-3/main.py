import sys
import pygame
from persistence import load_settings, save_score
from ui          import MainMenu, UsernameScreen, LeaderboardScreen, SettingsScreen, GameOverScreen
from racer       import RacerGame

SCREEN_W, SCREEN_H = 900, 700

def main():
    pygame.init()
    pygame.display.set_caption("Racer — TSIS 3")
    screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))
    clock  = pygame.time.Clock()

    settings    = load_settings()
    player_name = "Player"

    main_menu   = MainMenu(SCREEN_W, SCREEN_H)
    username_sc = UsernameScreen(SCREEN_W, SCREEN_H)
    leader_sc   = LeaderboardScreen(SCREEN_W, SCREEN_H)
    settings_sc = SettingsScreen(SCREEN_W, SCREEN_H)
    gameover_sc = GameOverScreen(SCREEN_W, SCREEN_H)

    state = "menu"

    while True:
        if state == "menu":
            action = main_menu.run(screen, clock)
            if   action == "play":        state = "username"
            elif action == "leaderboard": state = "leaderboard"
            elif action == "settings":    state = "settings"
            elif action == "quit":        break

        elif state == "username":
            name = username_sc.run(screen, clock)
            if name:
                player_name = name
                state = "play"
            else:
                state = "menu"

        elif state == "play":
            game  = RacerGame(screen, clock, settings, player_name)
            score, distance, coins = game.run()
            save_score(player_name, score, distance, coins)
            state = "gameover"
            last_run = (score, distance, coins)

        elif state == "gameover":
            score, distance, coins = last_run
            action = gameover_sc.run(screen, clock, score, distance, coins)
            if   action == "retry": state = "play"
            else:                   state = "menu"

        elif state == "leaderboard":
            leader_sc.run(screen, clock)
            state = "menu"

        elif state == "settings":
            settings = settings_sc.run(screen, clock)
            state = "menu"

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()