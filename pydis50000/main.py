from pathlib import Path

import moderngl
from moderngl_window.conf import settings

from pydis50000.base import CameraWindow
from pydis50000.milkyway import Milkyway
from pydis50000.clouds import AvatarCloud, MorphCloud

from pydis50000.timers import RocketMusicTimer as Timer
from pydis50000.tracks import tracks
import pyglet

RESOURCE_ROOT = Path(__file__).parent.resolve() / 'resources'
settings.ROCKET = {
    'mode': 'editor',
    'rps': 28,  # BPM: 112 / 4 = 28
    'project': None,
    'files': None,
}
settings.MUSIC = str(RESOURCE_ROOT / 'audio' / 'Scott_Holmes_Together_We_Stand.wav')


class PyDis50000(CameraWindow):
    title = "PyDis 50000"
    window_size = 1280, 720
    resizable = True
    resource_dir = RESOURCE_ROOT
    # samples = 16

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # self.wnd.mouse_exclusivity = True
        self.camera.mouse_sensitivity = 0.1
        self.camera.velocity = 100.0
        self.camera.projection.update(near=0.01, far=1000)
        self.camera_enabled = False

        # --- Initialize effects
        self.avatar_cloud = AvatarCloud(self)
        self.milkyway = Milkyway(self)
        # self.earth = Earth(self)
        self.morph_cloud = MorphCloud(self)

        # --- All timer and track related here
        self.track1 = tracks.get('test_1')
        self.track2 = tracks.get('test_2')
        self.track3 = tracks.get('test_3')

        self.timer = Timer()
        self.timer.start()
        # self.timer.start()
        self.frame_time = 60.0 / 1000.0
        self.prev_time = 0

    def render(self, time, frame_time):
        pyglet.clock.tick()
        # Let's hack around the the timer system for now using custom ones
        # frame_time = time - self.prev_time
        # self.prev_time = time
        time = self.timer.get_time()
        # print('render', time)

        # self.ctx.blend_func = moderngl.ONE, moderngl.ONE, moderngl.SRC_ALPHA, moderngl.ONE_MINUS_SRC_ALPHA 

        projection = self.camera.projection.matrix
        modelview = self.camera.matrix

        self.ctx.enable_only(moderngl.NOTHING)
        self.milkyway.render(projection, modelview)

        self.ctx.enable(moderngl.DEPTH_TEST)
        # self.earth.render(projection, modelview, time=time)

        # self.ctx.enable(moderngl.BLEND)
        # self.avatar_cloud.render(projection, modelview)
        self.morph_cloud.render(projection, modelview, time=time)

    def key_event(self, key, action, modifiers):
        super().key_event(key, action, modifiers)
        if action == self.wnd.keys.ACTION_PRESS:
            if key == self.wnd.keys.R:
                self.timer.time = 0


if __name__ == '__main__':
    PyDis50000.run()
