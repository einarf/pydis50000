from pyrr import Matrix44, matrix44, matrix33

import moderngl
from moderngl_window import geometry

from pydis50000.base import Effect


class Milkyway(Effect):
    name = 'milkyway'
    order = 1

    def __init__(self, config):
        super().__init__(config)

        self.prog =self.config.load_program('programs/milkyway.glsl')
        self.sphere = geometry.sphere(radius=200)
        # self.texture = self.config.load_texture_2d('textures/MilkyWayPanorama4K.jpg')
        self.texture = self.config.load_texture_2d('textures/8k_stars_milky_way.jpg')
        self.texture.build_mipmaps()

    def render(self, time=0, frametime=0, projection=None, modelview=None, target=None):
        self.ctx.enable_only(moderngl.NOTHING)
        sky_matrix = matrix44.create_from_matrix33(matrix33.create_from_matrix44(modelview))
        self.prog['m_mv'].write(sky_matrix.astype('f4').tobytes())
        self.prog['m_proj'].write(projection)

        self.texture.use(0)
        self.sphere.render(self.prog)
