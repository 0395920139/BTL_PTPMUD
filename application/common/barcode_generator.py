# -*- coding: utf-8 -*-
import barcode
from barcode.writer import ImageWriter

from application.config import Config

config = Config()

EAN = barcode.get_barcode_class(config.BARCODE_TYPE)


def get_barcode_svg(code, path):
    ean = EAN(u''+ code)
    file_fullname = ean.save(path)
    
    return file_fullname


#
# generate barcode as png image file
#
def get_barcode_png(code, path):
    ean = EAN(u'' + code, writer=ImageWriter())
    file_fullname = ean.save(path)
    print ('>>>> ', file_fullname)
    return file_fullname
    