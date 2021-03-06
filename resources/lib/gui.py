import time

import xbmc
import xbmcgui

import utils

class Button(xbmcgui.ControlButton):
    WIDTH = HEIGHT = 32

    def __new__(cls, parent, action, x, y, scaling=1.0):
        focusTexture = utils.TEXTURE_FMT.format(action + '-focus')
        noFocusTexture = utils.TEXTURE_FMT.format(action)
        width = int(round(cls.WIDTH * scaling))
        height = int(round(cls.HEIGHT * scaling))
        self = super(Button, cls).__new__(cls, x, y, width, height, "", focusTexture, noFocusTexture)

        parent.buttons.append(self)
        return self


class ToggleButton(xbmcgui.ControlRadioButton):
    WIDTH = 110
    HEIGHT = 40

    def __new__(cls, parent, action, x, y):
        focusOnTexture = utils.TEXTURE_FMT.format('radio-on')
        noFocusOnTexture = utils.TEXTURE_FMT.format('radio-on')
        focusOffTexture = utils.TEXTURE_FMT.format('radio-off')
        noFocusOffTexture = utils.TEXTURE_FMT.format('radio-off')
        focusTexture = utils.TEXTURE_FMT.format('back')
        noFocusTexture = utils.TEXTURE_FMT.format('trans')
        textOffsetX = 12

        self = super(ToggleButton, cls).__new__(cls, x, y, cls.WIDTH, cls.HEIGHT, action.title(),
                                                focusOnTexture, noFocusOnTexture,
                                                focusOffTexture, noFocusOffTexture,
                                                focusTexture, noFocusTexture,
                                                textOffsetX)

        self.action = action
        
        parent.buttons.append(self)
        return self

    def send_cmd(self, control):
        return self.cmd.set_enabled(control.isSelected())


class CameraPreview(xbmcgui.WindowDialog):
    def __init__(self, duration, path, scaling, position, mjpeg_stream):
        utils.log_normal("Showing preview")
        
        self.buttons = []
        
        self.duration = duration
        self.path = path
        self.mjpeg_stream = mjpeg_stream
        
        self.setProperty('zorder', "99")
        
        WIDTH = 320
        HEIGHT = 180

        width = int(WIDTH * scaling)
        height = int(HEIGHT * scaling)

        if "bottom" in position:
            y = 720 - height
        else:
            y = 0

        if "left" in position:
            x = 0
            start = - width
        else:
            x = 1280 - width
            start = width

        animations = [('WindowOpen',
                       "effect=slide start={0:d} time=2000 tween=cubic easing=out".format(start)),
                      ('WindowClose',
                       "effect=slide end={0:d} time=2000 tween=cubic easing=in".format(start))]

        self.image = xbmcgui.ControlImage(x, y, width, height, utils.TEXTURE_FMT.format('black'))
        self.addControl(self.image)
        self.image.setAnimations(animations)
            
        trans = utils.TEXTURE_FMT.format('trans')
        self.select_button = xbmcgui.ControlButton(x, y, width, height, "", trans, trans)
        self.addControl(self.select_button)
        self.select_button.setAnimations(animations)

        button_scaling = 0.5 * scaling
        button_width = int(round(Button.WIDTH * button_scaling))
        self.close_button = Button(self, 'close', x + width - button_width - 10, y + 10, scaling=button_scaling)
        self.addControl(self.close_button)
        self.close_button.setAnimations(animations)

    def start(self):
        with utils.ExtractMJPEGFrames(self.path, self.duration, self.mjpeg_stream,
                                      self.image.setImage, False) as self.extract_mjpeg:
            duration = self.extract_mjpeg.start()
        return duration

    def onControl(self, control):
        if control == self.close_button:
            self.stop()
        elif control == self.select_button:
            self.run()
            
    def onAction(self, action):
        if action in (utils.ACTION_PREVIOUS_MENU, utils.ACTION_BACKSPACE, utils.ACTION_NAV_BACK):
            self.stop()
        elif action == utils.ACTION_SELECT_ITEM:
            self.run()
            
    def run(self):
        xbmc.executebuiltin("RunAddon({0})".format(utils.addon_info('id')))
        self.stop()
            
    def stop(self):
        utils.log_normal("Closing preview")
        self.removeControl(self.close_button)
        self.extract_mjpeg.stop()
        self.close()

