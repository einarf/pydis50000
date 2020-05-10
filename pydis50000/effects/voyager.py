from pyrr import Matrix44, matrix44, matrix33

import moderngl
from moderngl_window import geometry

from pydis50000.base import Effect


class Voyager(Effect):
    name = 'voyager'
    order = 100

    def __init__(self, config):
        super().__init__(config)

        self.scene = self.config.load_scene('scenes/Voyager_17.glb')

    def render(self, time=0, frametime=0, projection=None, modelview=None, target=None):
        self.ctx.enable_only(moderngl.DEPTH_TEST)
        self.scene.draw(projection, modelview)
