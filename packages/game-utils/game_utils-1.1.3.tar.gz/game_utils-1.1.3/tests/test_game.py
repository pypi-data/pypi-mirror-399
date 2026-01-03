import logging

import pygame.event
from pygame.locals import K_ESCAPE, QUIT, USEREVENT

from game_utils.game import Game
from game_utils.screen import ScreenSettings

logger = logging.getLogger(__name__)
logger.setLevel(logging.WARNING)

TESTEVENT = USEREVENT


class MockGame(Game):
    def __init__(self):
        super().__init__()
        self.state = 0
        self.event = False

    def update(self):
        self.state += 1
        if self.state == 1:
            pygame.event.post(pygame.event.Event(TESTEVENT))
        if self.state == 3:
            self.running = False

    def events(self, event, *args, **kwargs):
        if event.type == TESTEVENT:
            self.event = True


def test_run():
    tg = MockGame()
    tg.run()
    assert tg.state == 3
    assert tg.event == True
