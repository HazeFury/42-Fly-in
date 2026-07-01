import arcade
import sys
from views.menu_view import MenuView
from utils.errors import CustomError


def main() -> None:
    print("--- STARTING THE PROGRAM ---")
    print("Please select a card in the Arcade window...")

    try:
        window = arcade.Window(1680, 1050, "Fly-in Simulation")

        window.show_view(MenuView())

        arcade.run()

        print("\n--- PROGRAM CLOSING ---")

    except KeyboardInterrupt:
        print("\n\033[93m[INFO] User interrupt "
              "(Ctrl+C). Program closing...\033[0m", file=sys.stderr)

        if arcade.get_window():
            arcade.close_window()
        sys.exit(0)

    except CustomError as e:
        print(f"\n\033[91m{e}\033[0m")
        if arcade.get_window():
            arcade.close_window()
        sys.exit(1)

    except Exception as e:
        print(f"\033[91m[FATAL ERROR]\033[0m {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
