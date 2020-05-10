from pyrr import Matrix44, matrix44, matrix33

import moderngl
from moderngl_window import geometry

from pydis50000.base import Effect


class PydisLogo(Effect):
    name = 'logo'
    order = 1000

    def __init__(self, config):
        super().__init__(config)
        self.track_fade = self.get_track('fade')
        size = 1024 / 1920 * 2, 315 / 1080 * 2
        self.quad_2d = geometry.quad_2d(size=size)
        self.texture = self.config.load_texture_2d('textures/logo_site_banner_1024.png')
        self.prog = self.config.load_program('programs/logo.glsl')

    def render(self, time=0, frametime=0, projection=None, modelview=None, target=None):
        self.ctx.enable_only(moderngl.BLEND)
        self.texture.use(0)
        self.prog['fade'] = self.track_fade.time_value(time)
        self.quad_2d.render(self.prog)
