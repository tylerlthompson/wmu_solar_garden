"""
author: Tyler Thompson
date: October 26th 2019
"""
from rgbmatrix import RGBMatrix, RGBMatrixOptions, graphics
from resources.Displays import Display
from resources.config import Config


class LEDMatrix(Config, Display):

    def __init__(self):
        super().__init__()
        self.font = graphics.Font()
        self.font.LoadFont(self.font_to_file_path(self.config['displays']['led_matrix']['default_font']))
        self.graphics = graphics
        self.options = RGBMatrixOptions()
        self.options.rows = self.config['displays']['led_matrix']['rows']
        self.options.cols = self.config['displays']['led_matrix']['cols']
        self.options.chain_length = self.config['displays']['led_matrix']['chain_length']
        self.options.parallel = self.config['displays']['led_matrix']['parallel']
        self.options.pwm_bits = self.config['displays']['led_matrix']['pwm_bits']
        self.options.brightness = self.config['displays']['led_matrix']['brightness']
        self.options.hardware_mapping = self.config['displays']['led_matrix']['hardware_mapping']
        self.options.multiplexing = self.config['displays']['led_matrix']['multiplexing']
        self.options.row_address_type = self.config['displays']['led_matrix']['row_address_type']
        self.options.pwm_lsb_nanoseconds = self.config['displays']['led_matrix']['pwn_lsb_nanoseconds']
        self.options.led_rgb_sequence = self.config['displays']['led_matrix']['led_rgb_sequence']
        self.options.disable_hardware_pulsing = self.config['displays']['led_matrix']['disable_hardware_pulsing']
        self.options.show_refresh_rate = self.config['displays']['led_matrix']['show_refresh_rate']
        self.options.gpio_slowdown = self.config['displays']['led_matrix']['gpio_slowdown']
        self.matrix = RGBMatrix(options=self.options)
        self.y = 0
        self.lines = None

    def update_brightness(self, value=False):
        """
        Set the brightness based on the config settings
        :param value: override the config settings
        :return: None
        """

        """
        Pyranometer 
        max: 55.41 
        min: -1.661 
        avg: 7.026
        """
        if not value:
            self.read_config()
            self.matrix.brightness = self.config['displays']['led_matrix']['brightness']
        else:
            self.matrix.brightness = value

    def show_lines(self, lines):
        for line in lines:
            self.graphics.DrawText(self.matrix, line.font, line.x, line.y, line.color, line.text)

    def show_text(self, text, x=False, y=False, color='FFFFFF', font='4x6'):
        self.font.LoadFont(self.font_to_file_path(font=font))
        color = color.replace('#', '')
        rgb = tuple(int(color[i:i + 2], 16) for i in (0, 2, 4))
        text_color = graphics.Color(rgb[0], rgb[1], rgb[2])
        words = str(text).split(' ')
        lines = []
        line = ""
        font_dim = self.font_to_x_y(font=font)
        if not y:
            y = font_dim[1]
        for word in words:
            if ((len(line) + len(word)) < int((self.config['displays']['led_matrix']['cols'] * self.config['displays']['led_matrix']['chain_length']) / font_dim[0])) and line:
                line = '{0} {1}'.format(line, word)
            else:
                if line:
                    lines.append(line)
                line = word
        lines.append(line)

        for line in lines:
            if not x:
                new_x = int(round(((((self.config['displays']['led_matrix']['cols'] * self.config['displays']['led_matrix']['chain_length']) / font_dim[0]) - len(line)) / 2) * font_dim[0]))
            else:
                new_x = x
            self.graphics.DrawText(self.matrix, self.font, new_x, y, text_color, line)
            y += font_dim[1]
        return y

    def show_simple_text(self, message, font, color, x, y):
        self.graphics.DrawText(self.matrix, font, x, y, color, message)

    def message_to_lines(self, message, font, color, y=False):
        line = ""
        lines = []
        font_dim = self.font_to_x_y(font=font)
        font_load = self.graphics.Font()
        font_load.LoadFont(self.font_to_file_path(font=font))
        hex_color = self.hex_to_rgb(color=color)
        color = graphics.Color(hex_color[0], hex_color[1], hex_color[2])
        words = message.split(' ')
        max_y = int(self.config['displays']['led_matrix']['rows'] * self.config['displays']['led_matrix']['parallel'])

        if not y:
            y = font_dim[1]

        for word in words:
            next_line_length = (len(line) + len(word))
            max_line_length = int((self.config['displays']['led_matrix']['cols'] * self.config['displays']['led_matrix']['chain_length']) / font_dim[0])

            if (next_line_length < max_line_length) and line:
                line = '{0} {1}'.format(line, word)
            else:
                if line and y < max_y:
                    x = self.get_x_offset(line=line, font_width=font_dim[0])
                    new_line = Line(text=line, color=color, font=font_load, x=x, y=y)
                    lines.append(new_line)
                    y += font_dim[1]
                line = word

        if y < max_y:
            x = self.get_x_offset(line=line, font_width=font_dim[0])
            new_line = Line(text=line, color=color, font=font_load, x=x, y=y)
            lines.append(new_line)
            y += font_dim[1]

        return lines, y

    def get_x_offset(self, line, font_width):
        return int(((((self.config['displays']['led_matrix']['cols'] * self.config['displays']['led_matrix']['chain_length']) / font_width) - len(line)) / 2) * font_width)


class Line(object):

    def __init__(self, text, color, font, x, y):
        self.text = text
        self.color = color
        self.font = font
        self.x = x
        self.y = y
