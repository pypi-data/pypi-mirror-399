from abc import abstractmethod

import pygame.display as display
from pygame import FULLSCREEN, Color, Surface
from pygame.time import Clock

ColorType = str | tuple[int, int, int] | Color


class ScreenSettings:
    """defines information needed to udpate the screen"""

    def __init__(
        self,
        *,
        width: float = 0.0,
        height: float = 0.0,
        frames_per_second: int = 60,
        bg_color: ColorType | None = None,
        bg_image: Surface | None = None,
    ):
        self.clock = Clock()
        self.bg_image = bg_image
        self.bg_color = bg_color
        self.frames_per_second = frames_per_second
        self.width = width
        self.height = height
        if self.width == 0.0 and self.height == 0.0:
            self.screen = display.set_mode((0, 0), FULLSCREEN)
            self.width = self.screen.get_width()
            self.height = self.screen.get_height()
        else:
            self.screen = display.set_mode((self.width, self.height))

    def resize_screen(self, width: float, height: float):
        """resizes to fullscreen by default"""
        self.width = width
        self.height = height
        self.screen = display.set_mode((self.width, self.height))

    def get_delta_time(self, units: int = 1000) -> float:
        return self.clock.tick(self.frames_per_second) / units

    @abstractmethod
    def update_screen(self):
        """Define logic for screen activity.  Required"""
        raise NotImplementedError()
