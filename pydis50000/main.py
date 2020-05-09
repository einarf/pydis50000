from pathlib import Path

import moderngl

from pydis50000.base import CameraWindow
from pydis50000.milkyway import Milkyway
from pydis50000.clouds import AvatarCloud, MorphCloud


class Test(CameraWindow):
    title = "PyDis 50000"
    window_size = 1280, 720
    resizable = True
    resource_dir = Path(__file__).parent.resolve() / 'resources'
    # samples = 16

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.wnd.mouse_exclusivity = True
        self.camera.mouse_sensitivity = 0.1
        self.camera.velocity = 100.0
        self.camera.projection.update(near=0.01, far=1000)
        # self.timer.pause()

        self.avatar_cloud = AvatarCloud(self)
        self.milkyway = Milkyway(self)
        # self.earth = Earth(self)
        self.morph_cloud = MorphCloud(self)

    def render(self, time, frame_time):
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
    Test.run()
