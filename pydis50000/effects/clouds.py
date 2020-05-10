import random
from array import array

import moderngl
from moderngl_window import WindowConfig

from pydis50000.base import Effect


class AvatarCloud(Effect):
    name = 'avatar_cloud'
    order = 5

    def __init__(self, config):
        super().__init__(config)

        self.texture = self.config.avatar_texture
        self.prog = self.config.load_program('programs/points.glsl')
        self.buffer = self.ctx.buffer(array('f', self.gen_points(5000)))
        self.vao = self.ctx.vertex_array(
            self.prog,
            [(self.buffer, '3f', 'in_pos')]
        )
        self.prog['num_layers'] = self.texture.layers

    def render(self, time=0, frametime=0, projection=None, modelview=None, target=None):
        self.ctx.enable_only(moderngl.DEPTH_TEST)
        self.prog['m_mv'].write(modelview)
        self.prog['m_proj'].write(projection)
        self.texture.use(0)
        self.vao.render(mode=moderngl.POINTS)

    def gen_points(self, n: int, size=250):
        for i in range(n):
            yield random.uniform(-size, size)
            yield random.uniform(-size, size)
            yield random.uniform(-size, size)


class MorphCloud(Effect):
    name = 'morph_cloud'
    order = 5

    def __init__(self, config: WindowConfig):
        super().__init__(config)

        self.track_morph = self.get_track("morph")
        self.logo_texture = self.config.load_texture_2d('textures/logo_full_512.png')

        # Generate destination data from texture
        self.gen_texture_points_prog = self.config.load_program('programs/gen_points_from_texture.glsl')
        self.dest_buffer = self.ctx.buffer(reserve=512 * 512 * 24)  # Room for vec3 x 2 for all texture positions
        self.gen_vao = self.ctx.vertex_array(self.gen_texture_points_prog, [])
        self.query = self.ctx.query()

        with self.query:
            self.logo_texture.use(0)
            self.gen_vao.transform(self.dest_buffer, vertices=512 * 512)

        self.num_points = self.query.primitives

        self.avatar_texture = self.texture = self.config.avatar_texture
        self.morph_prog = self.config.load_program('programs/points_morph.glsl')
        self.start_buffer = self.ctx.buffer(array('f', self.gen_points(self.num_points, size=1000)))
        self.morph_vao = self.ctx.vertex_array(
            self.morph_prog,
            [
                (self.start_buffer, '3f', 'in_pos'),
                (self.dest_buffer, '3f 3f', 'in_dest', 'in_color'),
            ]
        )
        self.morph_prog['num_layers'] = self.avatar_texture.layers

    def render(self, time=0, frametime=0, projection=None, modelview=None, target=None):
        self.ctx.enable_only(moderngl.DEPTH_TEST)
        self.morph_prog['m_mv'].write(modelview)
        self.morph_prog['m_proj'].write(projection)
        self.morph_prog['interpolate'] = self.track_morph.time_value(time)
        self.avatar_texture.use(0)
        self.morph_vao.render(mode=moderngl.POINTS, vertices=self.num_points)

    def gen_points(self, n: int, size=250):
        for i in range(n):
            yield random.uniform(-size, size)
            yield random.uniform(-size, size)
            yield random.uniform(-size, size)
