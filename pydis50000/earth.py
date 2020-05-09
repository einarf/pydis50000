from pydis50000.base import Effect


class Earth(Effect):

    def __init__(self, config):
        super().__init__(config)

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


