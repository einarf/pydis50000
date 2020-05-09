import random
from pathlib import Path
from array import array

from pyrr import Matrix44, matrix44, matrix33

import moderngl
import moderngl_window
from moderngl_window import geometry

from pydis50000.base import CameraWindow


class Test(CameraWindow):
    title = "PyDis 50000"
    window_size = 1280, 720
    resizable = True
    resource_dir = Path(__file__).parent.resolve() / 'pydis50000/resources'
    samples = 16

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



class Milkyway:

    def __init__(self, config):
        self.ctx = config.ctx
        self.config = config

        self.prog =self.config.load_program('programs/milkyway.glsl')
        self.sphere = geometry.sphere(radius=200)
        self.texture = self.config.load_texture_2d('textures/MilkyWayPanorama4K.jpg')

    def render(self, projection, modelview):
        sky_matrix = matrix44.create_from_matrix33(matrix33.create_from_matrix44(modelview))
        self.prog['m_mv'].write(sky_matrix.astype('f4').tobytes())
        self.prog['m_proj'].write(projection)

        self.texture.use(0)
        self.sphere.render(self.prog)


class MorphCloud:

    def __init__(self, config):
        self.config = config
        self.ctx = config.ctx

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
        print(self.num_points)

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


class AvatarCloud:

    def __init__(self, config):
        self.ctx = config.ctx
        self.config = config

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


class Earth:

    def __init__(self, config):
        self.ctx = config.ctx
        self.config = config

        self.sphere = geometry.sphere(radius=100, sectors=64, rings=64)
        self.prog = self.config.load_program('programs/earth.glsl')

        self.texture_day = self.config.load_texture_2d('textures/8k_earth_daymap.jpg')
        self.texture_day.build_mipmaps()

        self.texture_night = self.config.load_texture_2d('textures/8k_earth_nightmap.jpg')
        self.texture_night.build_mipmaps()

        self.texture_clouds = self.config.load_texture_2d('textures/8k_earth_nightmap.jpg')
        self.texture_clouds.build_mipmaps()

        self.texture_clouds = self.config.load_texture_2d('textures/8k_earth_nightmap.jpg')
        self.texture_clouds.build_mipmaps()

        # self.texture_specular = self.config.load_texture_2d('textures/8k_earth_specular_map.tif')
        # self.texture_specular.build_mipmaps()

        # self.quad = geometry.quad_fs()
        # self.texture_prog = self.config.load_program("programs/texture.glsl")

        self.prog['texture_day'] = 0
        self.prog['texture_night'] = 1
        self.prog['texture_clouds'] = 2
        # self.prog['texture_specular'] = 3

    def render(self, projection, modelview, time=0):
        rot =  matrix44.create_from_eulers([0.0, 0.0, -time / 5.0], dtype='f4'),
        earth_matrix = matrix44.multiply(rot, modelview)
        
        self.prog['m_mv'].write(earth_matrix)
        self.prog['m_proj'].write(projection)
        self.prog['sun_pos'].write(matrix44.apply_to_vector(modelview, (1000, 0, 0)).astype('f4'))

        self.texture_day.use(0)
        self.texture_night.use(1)
        self.texture_clouds.use(2)
        # self.texture_specular.use(3)

        self.sphere.render(self.prog)

        # self.texture_specular.use(0)
        # self.quad.render(self.texture_prog)


if __name__ == '__main__':
    Test.run()
