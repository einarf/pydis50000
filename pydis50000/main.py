import math
from pathlib import Path

import moderngl
from moderngl_window.conf import settings
from moderngl_window import geometry
from pyrr import matrix44

from pydis50000.base import CameraWindow
from pydis50000.effects import (
    Milkyway,
    AvatarCloud, 
    MorphCloud,
    Voyager,
)

from pydis50000.timers import RocketMusicTimer, RocketTimer
from pydis50000.tracks import tracks
import pyglet

RESOURCE_ROOT = Path(__file__).parent.resolve() / 'resources'
settings.ROCKET = {
    'mode': 'editor',  # Connect to external editor
    #'mode': 'project',  # Load the project file
    'rps': 28,  # BPM: 112 / 4 = 28
    'project': RESOURCE_ROOT / 'tracks.xml',
    'files': None,  # For remote export. We don't use this
}
settings.MUSIC = str(RESOURCE_ROOT / 'audio' / 'Scott_Holmes_Together_We_Stand.wav')


class PyDis50000(CameraWindow):
    title = "PyDis 50000"
    window_size = 1280, 720
    resizable = True
    resource_dir = RESOURCE_ROOT
    # samples = 16

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # self.wnd.mouse_exclusivity = True
        self.camera.mouse_sensitivity = 0.1
        self.camera.velocity = 10.0
        self.camera.projection.update(near=0.01, far=1000)
        self.camera_enabled = False

        # Framebuffers & Postprocessing stuff
        self.screen_quad = geometry.quad_fs()
        self.screen_quad_prog = self.load_program('programs/screen_quad.glsl')
        self.offscreen = self.ctx.framebuffer(
            color_attachments=[self.ctx.texture(self.wnd.size, 4)]
        )

        # --- Initialize effects
        self.router = EffecRouter(self)

        # --- All timer and track related here
        self.track_cam_x = tracks.get('camera:pos_x')
        self.track_cam_y = tracks.get('camera:pos_y')
        self.track_cam_z = tracks.get('camera:pos_z')
        self.track_cam_rot_x = tracks.get('camera:rot_x')
        self.track_cam_rot_z = tracks.get('camera:rot_y')
        self.track_cam_rot_tilt = tracks.get('camera:tilt')
        self.track_fade = tracks.get('camera:fade')

        # self.timer = RocketTimer()
        self.timer = RocketMusicTimer()
        self.timer.start()
        self.frame_time = 60.0 / 1000.0
        self.prev_time = 0

    def render(self, time, frame_time):
        pyglet.clock.tick()
        time = self.timer.get_time()

        # Prepare camera matrix
        translation = matrix44.create_from_translation((
            self.track_cam_x.time_value(time),
            self.track_cam_y.time_value(time),
            self.track_cam_z.time_value(time),
        ), dtype='f4')
        rotation = matrix44.create_from_eulers((
            math.radians(self.track_cam_rot_x.time_value(time)),
            math.radians(self.track_cam_rot_tilt.time_value(time)),
            math.radians(self.track_cam_rot_z.time_value(time)),
        ), dtype='f4')

        projection = self.camera.projection.matrix
        modelview = matrix44.multiply(matrix44.multiply(translation, rotation), self.camera.matrix)

        # Render active effects
        self.offscreen.use()
        self.offscreen.clear()
        for effect in self.router.gen_active_effects(time):
            effect.render(time=time, projection=projection, modelview=modelview)

        # # Postprocessing
        self.wnd.use()
        self.offscreen.color_attachments[0].use()
        self.screen_quad_prog['fade'].value = self.track_fade.time_value(time)
        self.screen_quad.render(self.screen_quad_prog)

    def resize(self, width, height):
        super().resize(width, height)
        if self.offscreen:
            self.offscreen.color_attachments[0].release()
            self.offscreen.release()
        self.offscreen = self.ctx.framebuffer(
            color_attachments=[self.ctx.texture((width, height), 4)]
        )

    def key_event(self, key, action, modifiers):
        super().key_event(key, action, modifiers)
        keys = self.wnd.keys

        if action == keys.ACTION_PRESS:
            if key == keys.R:
                self.timer.time = 0
            elif key == keys.LEFT:
                self.timer.set_time(self.timer.get_time() - 10)
            elif key == keys.RIGHT:
                self.timer.set_time(self.timer.get_time() + 10)


class EffecRouter:
    """Decides what effects are active at a given point in time"""
    def __init__(self, config):
        self.effects = []
        # Create the effect instances
        self.effects.append(AvatarCloud(config))
        self.effects.append(Milkyway(config))
        self.effects.append(MorphCloud(config))
        self.effects.append(Voyager(config))
        # self.earth = Earth(self)

        # Sort by order
        self.effects.sort(key=lambda x: x.order)

    def gen_active_effects(self, time):
        for effect in self.effects:
            value = effect.rocket_timeline_track.time_value(time)
            if value > 0.5:
                yield effect


if __name__ == '__main__':
    PyDis50000.run()
