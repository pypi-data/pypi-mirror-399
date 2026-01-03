#!/usr/bin/python
# -*- coding: utf-8 -*-

import qrcode

class UtilityQR:

    def generate(text, filename):
        #qrcode_graphics = qrcode.make(text)
        qr = qrcode.QRCode(border=2, box_size=10)
        qr.add_data(text)
        qrcode_graphics = qr.make_image(
            fill_color="#404040",
            back_color="#f2f2f2")
        qrcode_graphics.save(filename)

    def ascii(text):
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=1, # Set box size to 1 for ASCII representation
            border=0,
        )
        qr.add_data(text)
        qr.make(fit=True)
        qr_matrix = qr.get_matrix()
        ascii_qr = ""
        for row in qr_matrix:
            for cell in row:
                if cell:
                    ascii_qr += "██"
                else:
                    ascii_qr += "  "
            ascii_qr += "\n"
        return ascii_qr

    def graphical(text, filename, kind):
        qrcode = segno.make_qr(text)
        qrcode.save(
            filename,
            border=0,
            dark="#404040",
            light="#f2f2f2",
            scale=13,
            kind=kind,)

    def text(text, filename):
        qrcode = segno.make_qr(text)
        qrcode.save(
            filename,
            border=0,
            kind="txt")

    def ansi(text, filename):
        qrcode = segno.make_qr(text)
        qrcode.save(
            filename,
            border=0,
            kind="ans")
