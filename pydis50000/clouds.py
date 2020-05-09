import random
from array import array

import moderngl

from pydis50000.base import Effect


class AvatarCloud(Effect):

    def __init__(self, config):
        super().__init__(config)

        avatar_size = 256
        avatar_count = 22
        data = self.config.load_binary('avatars.bin')
        self.texture = self.ctx.texture_array((avatar_size, avatar_size, avatar_count), 4, data=data)
        self.texture.build_mipmaps()

        self.prog = self.config.load_program('programs/points.glsl')
        self.buffer = self.ctx.buffer(array('f', self.gen_points(50_000)))
        self.vao = self.ctx.vertex_array(
            self.prog,
            [(self.buffer, '3f', 'in_pos')]
        )
        self.prog['num_layers'] = avatar_count

    def render(self, projection, modelview):
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

    def __init__(self, config):
        super().__init__(config)

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
        # print(self.num_points)

        # copy paste from AvatarCloud
        avatar_size = 256
        avatar_count = 22
        data = self.config.load_binary('avatars.bin')
        self.avatar_texture = self.ctx.texture_array((avatar_size, avatar_size, avatar_count), 4, data=data)
        self.avatar_texture.build_mipmaps()

        self.morph_prog = self.config.load_program('programs/points_morph.glsl')
        self.start_buffer = self.ctx.buffer(array('f', self.gen_points(self.num_points)))
        self.morph_vao = self.ctx.vertex_array(
            self.morph_prog,
            [
                (self.start_buffer, '3f', 'in_pos'),
                (self.dest_buffer, '3f 3f', 'in_dest', 'in_color'),
            ]
        )
        self.morph_prog['num_layers'] = avatar_count

    def render(self, projection, modelview, time=0):
        self.morph_prog['m_mv'].write(modelview)
        self.morph_prog['m_proj'].write(projection)
        self.morph_prog['interpolate'] = min(1 - pow(time / 10.0, 2), 1.0)
        self.avatar_texture.use(0)
        self.morph_vao.render(mode=moderngl.POINTS, vertices=self.num_points)

    def gen_points(self, n: int, size=250):
        for i in range(n):
            yield random.uniform(-size, size)
            yield random.uniform(-size, size)
            yield random.uniform(-size, size)
