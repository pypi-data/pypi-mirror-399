from abc import abstractmethod
from typing import Generic, TypeVar

import pygame

from .screen import ScreenSettings
from .sprites import GameSprite


class Game:
    """Game class defines high-level game logic. This class includes a run method, which controls the game loop.
    User is required to implement abstract methods self.update() and self.events(), which is invoked within self.run()
    """

    def __init__(self, screen_settings: ScreenSettings | None = None):
        """High level game orchestrations

        Args:
            screen_settings (ScreenSettings): Any screen settings
        """
        self.dt = 0
        self.running = False
        self.screen_settings = screen_settings

    def run(self):
        """Runs and maintains the game loop and clock. Updates the screen and invokes any handlers
        Invokes pygame.init(), pygame.quit() when pygame.QUIT event is reached
        """
        pygame.init()
        self.running = True
        while self.running:
            self.update()
            if self.screen_settings is not None:
                self.screen_settings.update_screen()
                self.dt = self.screen_settings.get_delta_time()
                pygame.display.flip()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                self.events(event)

        pygame.quit()

    def events(self, event: pygame.event.Event, *args, **kwargs):
        """Define custom event handlers.  Optional.  Called once per game loop

        Args:
            event (pygame.event.Event): The event passed from run() method
            *args/**kwargs
        """
        pass

    @abstractmethod
    def update(self, *args, **kwargs):
        """Required implentation of game logic. Called once per game loop.

        Raises:
            NotImplementedError: Required implementation
        """
        raise NotImplementedError()


class SpriteGame(Game):
    def __init__(
        self,
        screen_settings: ScreenSettings,
        player_sprite: GameSprite,
        *other_sprites: GameSprite,
    ):
        """Create new instance of SpriteGame object.  Invokes pygame.init().  Must
        implement update_sprites()

        Args:
            settings (ScreenSettings): Information needed to update the screen
            player_sprite (GameSprite): The sprite to be used for the player
            *other_sprites (GameSprite): Any other sprites needed for the game
        """
        super().__init__(screen_settings=screen_settings)
        self.player_sprite: GameSprite = player_sprite
        self.other_sprites_group = pygame.sprite.Group(other_sprites)

    @abstractmethod
    def update_sprites(self):
        """Defines behavior for all GameSprite objects over time.  Called once per game loop

        Args:
            dt (float): change in time
        """
        raise NotImplementedError
