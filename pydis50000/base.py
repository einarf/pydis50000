import moderngl
import moderngl_window
from moderngl_window.scene import KeyboardCamera


class CameraWindow(moderngl_window.WindowConfig):
    """Base class with built in 3D camera support"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.camera = KeyboardCamera(self.wnd.keys, aspect_ratio=self.wnd.aspect_ratio)
        self.camera_enabled = True

    def key_event(self, key, action, modifiers):
        keys = self.wnd.keys

        if self.camera_enabled:
            self.camera.key_input(key, action, modifiers)

        if action == keys.ACTION_PRESS:
            if key == keys.C:
                self.camera_enabled = not self.camera_enabled
                self.wnd.mouse_exclusivity = self.camera_enabled
                self.wnd.cursor = not self.camera_enabled
            if key == keys.SPACE:
                self.timer.toggle_pause()

    def mouse_position_event(self, x: int, y: int, dx, dy):
        if self.camera_enabled:
            self.camera.rot_state(-dx, -dy)

    def resize(self, width: int, height: int):
        self.camera.projection.update(aspect_ratio=self.wnd.aspect_ratio)


class Effect:

    def __init__(self, config: moderngl_window.WindowConfig):
        self._ctx = config.ctx
        self._config = config

    @property
    def ctx(self) -> moderngl.Context:
        return self._ctx

    @property
    def config(self) -> moderngl_window.WindowConfig:
        return self._config

    def render(self, time, frame_time, **kwargs):
        raise NotImplementedError()

    def get_track(self, name: str):
        pass
