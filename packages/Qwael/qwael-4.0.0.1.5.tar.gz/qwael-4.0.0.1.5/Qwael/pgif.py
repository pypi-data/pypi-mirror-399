from kivy.uix.image import Image
from kivy.clock import Clock
from kivy.properties import ListProperty, NumericProperty

class gif(Image):
    source_list = ListProperty([])
    time = NumericProperty(0.1)
    umit = NumericProperty(0)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.index = 0
        self.turn = 0
        self._event = None

        Clock.schedule_once(self._start)

    def _start(self, dt):
        if not self.source_list:
            return

        self.source = self.source_list[0]
        self._event = Clock.schedule_interval(
            self._update,
            self.time
        )

    def _update(self, dt):
        self.index += 1

        if self.index >= len(self.source_list):
            self.index = 0
            self.turn += 1

            if self.umit != 0 and self.turn >= self.umit:
                self.stop()
                return

        self.source = self.source_list[self.index]

    def stop(self):
        if self._event:
            self._event.cancel()
            self._event = None

    def play(self):
        if not self._event:
            self._event = Clock.schedule_interval(
                self._update,
                self.time
            )