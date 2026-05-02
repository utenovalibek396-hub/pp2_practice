import sys  # Import the system-specific parameters and functions module
import pygame  # Import the Pygame library for game development
from persistence import load_settings, save_score  # Import functions for data persistence (saving/loading)
from ui          import MainMenu, UsernameScreen, LeaderboardScreen, SettingsScreen, GameOverScreen  # Import UI screen classes
from racer       import RacerGame  # Import the main game logic class

SCREEN_W, SCREEN_H = 900, 700  # Define global constants for the screen width and height

def main():  # Define the main function where the execution starts
    pygame.init()  # Initialize all imported pygame modules
    pygame.display.set_caption("Racer — TSIS 3")  # Set the text that appears in the window title bar
    screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))  # Create the graphical window with specified dimensions
    clock  = pygame.time.Clock()  # Create a clock object to manage the frame rate (FPS)

    settings    = load_settings()  # Load saved user settings from a file or database
    player_name = "Player"  # Set a default name for the player character

    main_menu   = MainMenu(SCREEN_W, SCREEN_H)  # Initialize the main menu interface
    username_sc = UsernameScreen(SCREEN_W, SCREEN_H)  # Initialize the screen for entering the player's name
    leader_sc   = LeaderboardScreen(SCREEN_W, SCREEN_H)  # Initialize the leaderboard display screen
    settings_sc = SettingsScreen(SCREEN_W, SCREEN_H)  # Initialize the settings configuration screen
    gameover_sc = GameOverScreen(SCREEN_W, SCREEN_H)  # Initialize the game over summary screen

    state = "menu"  # Set the initial state of the application to the main menu

    while True:  # Start the infinite main loop of the application
        if state == "menu":  # Check if the current state is the main menu
            action = main_menu.run(screen, clock)  # Run the menu logic and get the user's selected action
            if   action == "play":        state = "username"  # Transition to name entry if "play" is chosen
            elif action == "leaderboard": state = "leaderboard"  # Transition to high scores if selected
            elif action == "settings":    state = "settings"  # Transition to the settings menu
            elif action == "quit":        break  # Exit the main loop to close the application

        elif state == "username":  # Check if the state is for entering the username
            name = username_sc.run(screen, clock)  # Run the username screen and capture the returned name
            if name:  # If a valid name was entered
                player_name = name  # Update the current player's name
                state = "play"  # Transition to the actual gameplay state
            else:  # If the user cancelled or provided no name
                state = "menu"  # Return to the main menu

        elif state == "play":  # Check if the state is set to active gameplay
            game  = RacerGame(screen, clock, settings, player_name)  # Create a new instance of the racing game
            score, distance, coins = game.run()  # Start the game loop and receive results upon completion
            save_score(player_name, score, distance, coins)  # Save the game results to the persistence layer
            state = "gameover"  # Transition to the game over screen
            last_run = (score, distance, coins)  # Temporarily store results for the game over display

        elif state == "gameover":  # Check if the state is game over
            score, distance, coins = last_run  # Unpack the results of the most recent game run
            action = gameover_sc.run(screen, clock, score, distance, coins)  # Display the results to the user
            if   action == "retry": state = "play"  # Restart the game immediately if "retry" is selected
            else:                   state = "menu"  # Return to the main menu otherwise

        elif state == "leaderboard":  # Check if the state is to view rankings
            leader_sc.run(screen, clock)  # Run the leaderboard display logic
            state = "menu"  # Automatically return to the main menu after closing the leaderboard

        elif state == "settings":  # Check if the state is for configuration
            settings = settings_sc.run(screen, clock)  # Run the settings screen and update the settings variable
            state = "menu"  # Return to the main menu after adjusting settings

    pygame.quit()  # Uninitialize all pygame modules and close the window
    sys.exit()  # Terminate the Python script completely

if __name__ == "__main__":  # Check if this script is being run directly (not imported)
    main()  # Call the main function to start the program