from pyrr import Matrix44, matrix44, matrix33

from moderngl_window import geometry

from pydis50000.base import Effect


class Voyager(Effect):

    def __init__(self, config):
        super().__init__(config)

        self.scene = self.config.load_scene('scenes/Voyager_17.glb')

    def render(self, projection, modelview):
        self.scene.draw(projection, modelview)
