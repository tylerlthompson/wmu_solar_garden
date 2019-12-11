"""
author: Tyler Thompson
date: October 26th 2019
"""
from resources.Displays import Display
from abc import abstractmethod
from datetime import datetime
from resources.config import Config


def create_frame(display, config):
    """
    Return a frame based on a frame's config
    :param display: a LEDMatrix object
    :param config: a frame config dictionary
    :return: a Frame object | None
    """
    if config['type'] == 'alert':
        return Alert(display=display, **config)
    elif config['type'] == 'image':
        return Image(display=display, **config)
    elif config['type'] == 'clock':
        return Clock(display=display, **config)
    elif config['type'] == 'single_data_map':
        return SingleDataMap(display=display, **config)
    elif config['type'] == 'double_data_map':
        return DoubleDataMap(display=display, **config)
    else:
        return None


class Frame(Display, Config):

    def __init__(self, display, **kwargs):
        super().__init__()
        self.__dict__.update(kwargs)
        self.display = display
        Config.__init__(self)
        self.lines = []

    @abstractmethod
    def show(self):
        self.logger.error(msg=self.__not_implemented_error__)
        raise NotImplementedError(self.__not_implemented_error__)


class Alert(Frame):

    def __init__(self, display, title, message, message_color, title_color, title_font, message_font, background_color, **kwargs):
        super().__init__(display=display, **kwargs)
        self.title = title
        self.message = message
        self.message_color = message_color
        self.title_color = title_color
        self.title_font = title_font
        self.message_font = message_font
        self.background_color = background_color

        # generate lines
        title_lines, y = self.display.message_to_lines(message=self.title, font=self.title_font, color=self.title_color)
        message_lines, _ = self.display.message_to_lines(message=self.message, font=self.message_font,
                                                         color=self.message_color, y=y)
        self.lines = title_lines + message_lines

    def show(self):
        self.display.matrix.Clear()
        bg_color = self.hex_to_rgb(color=self.background_color)
        self.display.matrix.Fill(bg_color[0], bg_color[1], bg_color[2])
        self.display.show_lines(self.lines)


class Image(Frame):

    def __init__(self, display, image, **kwargs):
        super().__init__(display=display, **kwargs)

        # generate scaled image and position
        from PIL import Image as PIL_Image
        image_path = "{0}/{1}".format(Config().image_dir, image)
        self.image = PIL_Image.open(image_path)
        self.image.thumbnail((display.matrix.width, display.matrix.height), PIL_Image.HAMMING)
        image_width, image_height = self.image.size
        self.x = ((self.config['displays']['led_matrix']['cols'] * self.config['displays']['led_matrix']['chain_length']) - image_width) / 2
        self.y = ((self.config['displays']['led_matrix']['rows'] * self.config['displays']['led_matrix']['parallel']) - image_height) / 2

    def show(self):
        self.display.matrix.Clear()
        self.display.matrix.SetImage(self.image.convert('RGB'), self.x, self.y)


class Clock(Frame):

    def __init__(self, display, color, font, **kwargs):
        super().__init__(display=display, **kwargs)
        self.color = color
        self.font = font
        # self.y = (((self.config['displays']['led_matrix']['rows'] * self.config['displays']['led_matrix']['parallel'])
        #            / 2) + (self.font_to_x_y(font=self.font)[0] / 2))
        now = datetime.now()
        time, y = self.display.message_to_lines(message=now.strftime('%_I:%M %P'),
                                                font=self.font,
                                                color=self.color)
        self.date, _ = self.display.message_to_lines(message=now.strftime('%B %e'),
                                                     font=self.font,
                                                     color=self.color,
                                                     y=y)

    def show(self):
        time, _ = self.display.message_to_lines(message=datetime.now().strftime('%_I:%M %P'),
                                                font=self.font,
                                                color=self.color)
        lines = time + self.date
        self.display.matrix.Clear()
        self.display.show_lines(lines=lines)


class SingleDataMap(Frame):

    def __init__(self, display, data_title, data_title_font, data_title_color, data_point, data_point_font,
                 data_point_color, data_units, location, **kwargs):
        super().__init__(display=display, **kwargs)

        # generate lines
        data = "{0} {1}".format(self.config['data_stores']['data'][location][data_point], data_units)
        title, y = self.display.message_to_lines(message=data_title, font=data_title_font, color=data_title_color)
        point, _ = self.display.message_to_lines(message=data, font=data_point_font, color=data_point_color, y=y+2)
        self.lines = title + point

    def show(self):
        self.display.matrix.Clear()
        self.display.show_lines(lines=self.lines)


class DoubleDataMap(Frame):

    def __init__(self, display,  header, header_font, header_color, data_title_0, data_point_0, data_point_color_0,
                 data_units_0, data_point_font_0, data_title_1, data_point_1, data_point_color_1, data_units_1,
                 data_point_font_1, location, **kwargs):
        super().__init__(display=display, **kwargs)

        # generate lines
        data_0 = "{0} {1} {2}".format(data_title_0,
                                      self.config['data_stores']['data'][location][data_point_0],
                                      data_units_0)
        data_1 = "{0} {1} {2}".format(data_title_1,
                                      self.config['data_stores']['data'][location][data_point_1],
                                      data_units_1)
        header, y0 = self.display.message_to_lines(message=header, font=header_font, color=header_color)
        data_0_line, y1 = self.display.message_to_lines(message=data_0,
                                                        font=data_point_font_0,
                                                        color=data_point_color_0,
                                                        y=y0+2)
        data_1_line, _ = self.display.message_to_lines(message=data_1,
                                                       font=data_point_font_1,
                                                       color=data_point_color_1,
                                                       y=y1+1)
        self.lines = header + data_0_line + data_1_line

    def show(self):
        self.display.matrix.Clear()
        self.display.show_lines(self.lines)
