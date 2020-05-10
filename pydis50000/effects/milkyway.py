from pyrr import Matrix44, matrix44, matrix33

from moderngl_window import geometry

from pydis50000.base import Effect


class Milkyway(Effect):

    def __init__(self, config):
        super().__init__(config)

        self.prog =self.config.load_program('programs/milkyway.glsl')
        self.sphere = geometry.sphere(radius=200)
        self.texture = self.config.load_texture_2d('textures/MilkyWayPanorama4K.jpg')

    def render(self, projection, modelview):
        sky_matrix = matrix44.create_from_matrix33(matrix33.create_from_matrix44(modelview))
        self.prog['m_mv'].write(sky_matrix.astype('f4').tobytes())
        self.prog['m_proj'].write(projection)

        self.texture.use(0)
        self.sphere.render(self.prog)
