from moderngl_window import geometry
from pydis50000.base import Effect

from pyrr import Matrix44

class BlueBall(Effect):
    name = "blue_ball"
    order = 50

    def __init__(self, config):
        super().__init__(config)
        self.sphere = geometry.sphere(radius=100, sectors=256, rings=128)
        self.program = self.config.load_program("programs/blueball.glsl")

    def render(self, time=0, frametime=0, projection=None, modelview=None, target=None):
        self.ctx.enable(self.ctx.DEPTH_TEST | self.ctx.CULL_FACE)
        self.ctx.wireframe = True
        try:
            self.program['time'] = time
        except KeyError:
            pass
        self.program['m_proj'].write(projection)
        self.program['m_cam'].write(modelview)
        self.program['m_model'].write(Matrix44.identity(dtype="f4"))
        self.sphere.render(self.program)

        self.ctx.wireframe = False
