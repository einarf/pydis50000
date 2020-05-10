"""
This is just hacking in all the old timers from demosys-py.
Ugly as hell, but it works in minutes.
"""
from rocket import Rocket
from rocket.controllers import TimeController

from moderngl_window.conf import settings
from pyglet.media import Player, StaticSource, load

from pydis50000.tracks import tracks


class BaseTimer:
    """
    The base class guiding the implementation of timers.
    All methods must be implemented.
    """
    def __init__(self, **kwargs):
        pass

    def start(self):
        """
        Start the timer initially or resume after pause
        Raises:
            NotImplementedError
        """
        raise NotImplementedError()

    def pause(self):
        """
        Pause the timer
        Raises:
            NotImplementedError
        """
        raise NotImplementedError()

    def toggle_pause(self):
        """
        Toggle pause state
        Raises:
            NotImplementedError
        """
        raise NotImplementedError()

    def stop(self) -> float:
        """
        Stop the timer. Should only be called once when stopping the timer.
        Returns:
            The time the timer was stopped
        Raises:
            NotImplementedError
        """
        raise NotImplementedError()

    def get_time(self) -> float:
        """
        Get the current time in seconds
        Returns:
            The current time in seconds
        Raises:
            NotImplementedError
        """
        raise NotImplementedError()

    def set_time(self, value: float):
        """
        Set the current time in seconds.
        Args:
            value (float): The new time
        Raises:
            NotImplementedError
        """
        raise NotImplementedError()


class RocketTimer(BaseTimer):
    """
    Basic rocket timer.
    Sets up rocket using values in ``settings.ROCKET``.
    The current time is translated internally in rocket
    to row positions based on the configured rows per second (RPS).
    """
    def __init__(self, **kwargs):
        """Initialize the rocket timer using values from settings"""
        config = getattr(settings, 'ROCKET', None)
        if config is None:
            config = {}

        self.mode = config.get('mode') or 'editor'
        self.files = config.get('files') or './tracks'
        self.project = config.get('project') or 'project.xml'
        self.rps = config.get('rps', 24)
        self.start_paused = False

        self.controller = TimeController(self.rps)
        if self.mode == 'editor':
            self.rocket = Rocket.from_socket(self.controller, track_path=self.files)
            self.start_paused = True
        elif self.mode == 'project':
            self.rocket = Rocket.from_project_file(self.controller, self.project)
        elif self.mode == 'files':
            self.rocket = Rocket.from_files(self.controller, self.files)
        else:
            raise ValueError("Unknown rocket mode: '{}'".format(self.mode))

        # Register tracks in the editor
        # Ninja in pre-created track objects
        for track in tracks.tacks:
            self.rocket.tracks.add(track)

        # Tell the editor about these tracks
        for track in tracks.tacks:
            self.rocket.track(track.name)

        self.rocket.update()
        super().__init__(**kwargs)

    def start(self):
        """Start the timer"""
        if not self.start_paused:
            self.rocket.start()

    def get_time(self) -> float:
        """
        Get the current time in seconds
        Returns:
            The current time in seconds
        """
        self.rocket.update()
        return self.rocket.time

    def set_time(self, value: float):
        """
        Set the current time jumping in the timeline.
        Args:
            value (float): The new time
        """
        if value < 0:
            value = 0

        self.controller.row = self.rps * value

    def pause(self):
        """Pause the timer"""
        self.controller.playing = False

    def toggle_pause(self):
        """Toggle pause mode"""
        self.controller.playing = not self.controller.playing

    def stop(self) -> float:
        """
        Stop the timer
        Returns:
            The current time.
        """
        return self.rocket.time


class MusicTimer(BaseTimer):
    """
    Timer based on the current position in a wav, ogg or mp3 using pygame.mixer.
    Path to the music file is configured in ``settings.MUSIC``.
    """
    def __init__(self, **kwargs):
        self.source = StaticSource(load(settings.MUSIC))
        self.player = Player()
        self.player.queue(self.source)

        self.paused = True
        self.initialized = False
        super().__init__(**kwargs)

    def start(self):
        """Play the music"""
        if self.initialized:
            self.player.play()
        else:
            self.player.play()
            self.initialized = True

        self.paused = False

    def pause(self):
        """Pause the music"""
        self.player.pause()
        self.paused = True

    def toggle_pause(self):
        """Toggle pause mode"""
        if self.paused:
            self.start()
        else:
            self.pause()

    def stop(self) -> float:
        """
        Stop the music
        Returns:
            The current location in the music
        """
        t = self.player.time
        self.player.stop()
        return t

    def get_time(self) -> float:
        """
        Get the current position in the music in seconds
        """
        return self.player.time

    def set_time(self, value: float):
        """
        Set the current time in the music in seconds causing the player
        to seek to this location in the file.
        """
        if value < 0:
            value = 0

        self.player.seek(value)


class RocketMusicTimer(RocketTimer):
    """
    Combines music.Timer and rocket.Timer
    """
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.music = MusicTimer(start_paused=self.start_paused)

    def start(self):
        """Start the timer"""
        self.music.start()
        if not self.start_paused:
            self.music.pause()
            self.rocket.start()

        self.music.set_time(self.controller.time)

    def get_time(self) -> float:
        """
        Get the current time in seconds
        Returns:
            The current time in seconds
        """
        # if the controller is playing we must play the music if paused
        if self.controller.playing and self.music.paused:
            self.music.set_time(self.controller.time)
            self.music.start()
            return self.controller.time

        # If the controller is not playing and music is not paused, we need to pause music
        if not self.controller.playing and not self.music.paused:
            self.music.pause()
            self.music.set_time(self.controller.time)
            return self.controller.time

        rt = super().get_time()
        t = self.music.get_time()

        if abs(rt - t) > 0.1:
            # print("Music out of sync!!!", t, rt)
            self.music.set_time(rt)
            return rt

        # print(self.music.paused, self.controller.playing)
        return t

    def set_time(self, value: float):
        """
        Set the current time jumping in the timeline
        Args:
            value (float): The new time value
        """
        # print('set_time', value)
        self.music.set_time(value)

    def pause(self):
        """Pause the timer"""
        self.controller.playing = False
        self.music.pause()

    def toggle_pause(self):
        """Toggle pause mode"""
        self.controller.playing = not self.controller.playing
        self.music.toggle_pause()

    def stop(self) -> float:
        """
        Stop the timer
        Returns:
            The current time
        """
        return self.rocket.time