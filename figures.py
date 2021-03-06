#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
#  demo_window.py
#
#  Copyright 2020 John Coppens <john@jcoppens.com>
#
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#  MA 02110-1301, USA.
#
#
from gi.repository import Gdk, Gtk, GooCanvas, GdkPixbuf
import gi
import math
gi.require_version('Gdk', '3.0')
gi.require_version('Gtk', '3.0')
gi.require_version('GooCanvas', '2.0')


def to_rgba(color):
    """ Conversion de formato Gdk.RGBA (r, g, b y a en valores de 0 a 1.0)
        resultado de get_rgba) a integer para GooCanvas.
    """
    return ((int(color.red * 255) << 24) +
            (int(color.green * 255) << 16) +
            (int(color.blue * 255) << 8) +
            int(color.alpha * 255))


class Marker():
    def __init__(self, layer, x, y, radius=8, color="White", callback=None):
        self.x, self.y = x, y
        self.radius = radius
        self.color = color
        self.position = None
        self.callback = callback

        self.marker = GooCanvas.CanvasEllipse(
            parent=layer,
            center_x=x, center_y=y,
            radius_x=radius, radius_y=radius,
            stroke_color=color,
            fill_color_rgba=0xffffff20,
            line_width=2)

        self.marker.connect("button-press-event", self.button_pressed)
        layer.connect("button-release-event", self.button_released)
        layer.connect("motion-notify-event", self.button_moved)

    def button_pressed(self, src, tgt, event):
        self.position = event.x, event.y
        return True

    def button_released(self, src, tgt, event):
        self.position = None

    def moveto(self, x, y):
        self.marker.set_property("center-x", x)
        self.marker.set_property("center-y", y)

    def get_position(self):
        return(self.marker.get_property("center-x"), self.marker.get_property("center-y"))

    def button_moved(self, src, tgt, event):
        if self.position is None:
            return

        dx = event.x - self.position[0]
        dy = event.y - self.position[1]

        new_x = self.marker.get_property("center-x") + dx
        new_y = self.marker.get_property("center-y") + dy

        self.moveto(new_x, new_y)

        self.position = new_x, new_y
        if self.callback is not None:
            self.callback(new_x, new_y)


class Figure():
    def __init__(self, tbox):
        """ Tarea comun: Buscar colores, y ancho del trazo actualmente
            seleccionados.
        """
        self.tbox = tbox

        self.stroke_color = to_rgba(self.tbox.stroke_colbtn.get_rgba())
        self.fill_color = to_rgba(self.tbox.fill_colbtn.get_rgba())
        self.line_width = self.tbox.spbtn.get_value()


class Rectangle(Figure):
    def __init__(self, tbox, x, y):
        super(Rectangle, self).__init__(tbox)
        self.origin = x, y
        self.cuadranteNegX = False
        self.cuadranteNegY = False
        self.marker1 = Marker(self.tbox.layer, x, y, color="Red",
                              callback=self.moveto)

        self.rect = GooCanvas.CanvasRect(       # TODO
            parent=tbox.layer,
            x=x, y=y,
            width=0, height=0,
            fill_color_rgba=self.fill_color,
            stroke_color_rgba=self.stroke_color,
            line_width=self.line_width)

        self.id_release = tbox.layer.connect("button-release-event",
                                             self.button_released)
        self.id_motion = tbox.layer.connect("motion-notify-event",
                                            self.button_moved)

    def set_x_y(self, x, y):
        self.rect.set_property('x', x)
        self.rect.set_property('y', y)

    def get_x_y(self):
        return (self.rect.get_property('x'),
                self.rect.get_property('y'))

    def set_w_h(self, w, h):
        x, y = self.get_x_y()
        self.width = w
        self.height = h
        x, y = self.origin[0], self.origin[1]
        self.cuadranteNegX = self.cuadranteNegY = False
        if w < 0:
            x += w
            w = -w
            self.cuadranteNegX = True
        if h < 0:
            y += h
            h = -h
            self.cuadranteNegY = True

        self.set_x_y(x, y)
        self.rect.set_property('width', w)
        self.rect.set_property('height', h)

    def button_released(self, src, tgt, event):
        w = event.x - self.origin[0]
        h = event.y - self.origin[1]
        self.set_w_h(w, h)
        self.tbox.layer.disconnect(self.id_release)
        self.tbox.layer.disconnect(self.id_motion)
        self.marker2 = Marker(self.tbox.layer, event.x, event.y,
                              color="Yellow",
                              callback=self.resize)

    def moveto(self, x, y):
        w = self.rect.get_property('width')
        h = self.rect.get_property('height')
        self.origin = x, y
        x1 = x + w
        y1 = y + h
        if self.cuadranteNegX:
            x -= w
            x1 = x
        if self.cuadranteNegY:
            y -= h
            y1 = y
        self.set_x_y(x, y)
        self.marker2.moveto(x1, y1)

    def resize(self, xnew, ynew):
        x, y = self.get_x_y()
        self.set_w_h(xnew - x, ynew - y)

    def button_moved(self, src, tgt, event):
        w = event.x - self.origin[0]
        h = event.y - self.origin[1]
        self.set_w_h(w, h)


class Ellipse(Figure):
    def __init__(self, tbox, x, y):
        super(Ellipse, self).__init__(tbox)
        self.origin = x, y
        self.cuadranteNegX = False
        self.cuadranteNegY = False
        self.marker1 = Marker(self.tbox.layer, x, y, color="Red",
                              callback=self.moveto)

        self.ellipse = GooCanvas.CanvasEllipse(
            parent=tbox.layer,
            x=x, y=y,
            width=0, height=0,
            fill_color_rgba=self.fill_color,
            stroke_color_rgba=self.stroke_color,
            line_width=self.line_width)

        self.id_release = tbox.layer.connect("button-release-event",
                                             self.button_released)
        self.id_motion = tbox.layer.connect("motion-notify-event",
                                            self.button_moved)

    def set_x_y(self, x, y):
        self.ellipse.set_property('x', x)
        self.ellipse.set_property('y', y)

    def get_x_y(self):
        return (self.ellipse.get_property('x'),
                self.ellipse.get_property('y'))

    def set_w_h(self, w, h):
        x, y = self.origin[0], self.origin[1]
        self.cuadranteNegX = self.cuadranteNegY = False
        if w < 0:
            x += w
            w = -w
            self.cuadranteNegX = True
        if h < 0:
            y += h
            h = -h
            self.cuadranteNegY = True
        self.set_x_y(x, y)
        self.ellipse.set_property('width', w)
        self.ellipse.set_property('height', h)

    def button_released(self, src, tgt, event):
        w = event.x - self.origin[0]
        h = event.y - self.origin[1]
        self.set_w_h(w, h)
        self.tbox.layer.disconnect(self.id_release)
        self.tbox.layer.disconnect(self.id_motion)

        self.marker2 = Marker(self.tbox.layer, event.x, event.y,
                              color="Yellow",
                              callback=self.resize)

    def moveto(self, x, y):
        w = self.ellipse.get_property('width')
        h = self.ellipse.get_property('height')
        self.origin = x, y
        x1 = x + w
        y1 = y + h
        if self.cuadranteNegX:
            x -= w
            x1 = x
        if self.cuadranteNegY:
            y -= h
            y1 = y
        self.set_x_y(x, y)
        self.marker2.moveto(x1, y1)

    def resize(self, xnew, ynew):
        x, y = self.origin[0], self.origin[1]
        self.set_w_h(xnew - x, ynew - y)

    def button_moved(self, src, tgt, event):
        w = event.x - self.origin[0]
        h = event.y - self.origin[1]
        self.set_w_h(w, h)


class ArcoEllipse(Figure):
    def __init__(self, tbox, x, y):
        super(ArcoEllipse, self).__init__(tbox)
        self.origin = x, y
        self.moved = False
        self.rx = 0
        self.ry = 0
        self.up = 1
        self.marker1 = Marker(self.tbox.layer, x, y, color="Red",
                              callback=self.moveto)

        self.aEllipse = GooCanvas.CanvasPath(
            parent=tbox.layer,
            data="",
            x=x, y=y,
            width=0, height=0,
            stroke_color_rgba=self.stroke_color,
            fill_color_rgba=self.fill_color,
            line_width=self.line_width,
        )

        self.id_release = tbox.layer.connect("button-release-event",
                                             self.button_released)
        self.id_motion = tbox.layer.connect("motion-notify-event",
                                            self.button_moved)

    def set_data(self, x, y, w, h):
        if not self.moved:
            self.rx = w / 2
            self.ry = 100
        self.aEllipse.set_property(
            'data', "M{},{} A{},{} 0 0 {} {},{}".format(
                x, y, self.rx, self.ry, self.up, x + w, y + h)
        )

    def button_released(self, src, tgt, event):
        x = event.x
        y = event.y
        h = self.aEllipse.get_property('height')
        if x > self.origin[0]:
            if y > self.origin[1]:
                y3 = y - h
            else:
                y3 = self.origin[1]-h
        else:
            if y > self.origin[1]:
                y3 = self.origin[1] + h
            else:
                y3 = y+h
        self.set_data(self.origin[0], self.origin[1],
                      x-self.origin[0], y-self.origin[1])
        self.tbox.layer.disconnect(self.id_release)
        self.tbox.layer.disconnect(self.id_motion)
        self.marker2 = Marker(self.tbox.layer, x, y,
                              color="Yellow",
                              callback=self.resize)
        self.marker3 = Marker(self.tbox.layer, x-((x-self.origin[0])/2), y3,
                              color="Blue",
                              callback=self.panza
                              )

    def panza(self, x, y):
        self.moved = True
        x1, y1 = self.marker1.get_position()
        x2, y2 = self.marker2.get_position()
        h = self.aEllipse.get_property('height')
        self.rx = math.hypot(y2 - y1, x2 - x1) / 2
        self.ry = y2 - y
        if (y > y1+(h/2)):
            self.up = 0
        else:
            self.up = 1
        self.set_data(x1, y1,
                      x2 - x1, y2 - y1)

    def moveto(self, x, y):
        x2, y2 = self.marker2.get_position()
        x3, y3 = self.marker3.get_position()
        x2 += x - self.origin[0]
        y2 += y - self.origin[1]
        x3 += x - self.origin[0]
        y3 += y - self.origin[1]
        self.origin = x, y
        self.marker2.moveto(x2, y2)
        self.marker3.moveto(x3, y3)
        self.set_data(x, y, x2-x, y2-y)

    def resize(self, xnew, ynew):
        x, y = self.origin[0], self.origin[1]
        w = xnew - x
        h = ynew - y
        self.set_data(x, y, w, h)

    def button_moved(self, src, tgt, event):
        x1, y1 = self.marker1.get_position()
        w = event.x - x1
        h = event.y - y1
        self.set_data(x1, y1, w, h)


class Curve(Figure):
    def __init__(self, tbox, x, y):
        super(Curve, self).__init__(tbox)
        self.origin = x, y
        self.moved = False
        self.bx = 0
        self.by = 0
        self.marker1 = Marker(self.tbox.layer, x, y, color="Red",
                              callback=self.moveto)

        self.curve = GooCanvas.CanvasPath(
            parent=tbox.layer,
            data="",
            x=x, y=y,
            width=0, height=0,
            stroke_color_rgba=self.stroke_color,
            fill_color_rgba=self.fill_color,
            line_width=self.line_width,
        )

        self.id_release = tbox.layer.connect("button-release-event",
                                             self.button_released)
        self.id_motion = tbox.layer.connect("motion-notify-event",
                                            self.button_moved)

    def set_data(self, x, y, w, h):
        if not self.moved:
            self.bx = x + (w / 2)
            self.by = y + h
        self.curve.set_property(
            'data', "M{},{} Q{},{} {},{}".format(
                x, y, self.bx, self.by, x + w, y + h)
        )

    def set_x_y(self, x, y):
        self.curve.set_property('x', x)
        self.curve.set_property('y', y)

    def set_w_h(self, w, h):
        self.width = w
        self.height = h
        x, y = self.origin[0], self.origin[1]
        if w < 0:
            x += w
            w = -w
        if h < 0:
            y += h
            h = -h
        self.set_x_y(x, y)
        self.curve.set_property('width', w)
        self.curve.set_property('height', h)

    def button_released(self, src, tgt, event):
        x = event.x
        y = event.y
        w = x - self.origin[0]
        h = y - self.origin[1]
        self.set_data(self.origin[0], self.origin[1], w, h)
        self.set_w_h(w, h)
        self.tbox.layer.disconnect(self.id_release)
        self.tbox.layer.disconnect(self.id_motion)
        self.marker2 = Marker(self.tbox.layer, x, y,
                              color="Yellow",
                              callback=self.resize)
        self.marker3 = Marker(self.tbox.layer, self.bx, self.by,
                              color="Blue",
                              callback=self.panza
                              )

    def panza(self, x, y):
        self.moved = True
        self.bx = x
        self.by = y
        w, h = self.marker2.get_position()
        self.set_data(self.origin[0], self.origin[1],
                      w-self.origin[0], h-self.origin[1])

    def moveto(self, x, y):
        x2, y2 = self.marker2.get_position()
        x3, y3 = self.marker3.get_position()
        x2 += x - self.origin[0]
        y2 += y - self.origin[1]
        x3 += x - self.origin[0]
        y3 += y - self.origin[1]
        self.origin = x, y
        self.marker2.moveto(x2, y2)
        self.marker3.moveto(x3, y3)
        self.set_data(x, y, x2 - x, y2 - y)
        self.bx = x3
        self.by = y3

    def resize(self, xnew, ynew):
        x, y = self.origin[0], self.origin[1]
        self.set_w_h(xnew - x, ynew - y)
        self.set_data(x, y, xnew - x, ynew - y)
        self.marker3.moveto(self.bx, self.by)

    def button_moved(self, src, tgt, event):
        x, y = self.origin[0], self.origin[1]
        w = event.x - x
        h = event.y - y
        self.set_data(x, y, w, h)
        self.set_w_h(w, h)
