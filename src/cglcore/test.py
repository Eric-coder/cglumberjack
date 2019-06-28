import path
import subprocess
import logging
import os
from cglcore.config import app_config
from cglcore.convert import create_mov

# C:\ProgramData\chocolatey\lib\ffmpeg\tools\ffmpeg\bin\ffmpeg.exe -start_number 01866954 -framerate 24 -gamma 1 -i \\Mac\Home\Documents\cglumberjack\temp\dpx2\A180C006_171113_R2XD.%08d.jpg -s:v 1920x1080 -b:v 50M -c:v libx264 -profile:v high -crf 24 -pix_fmt yuv420p -r 24  -filter:v "scale=iw*min(1920/iw\,1080/ih):ih*min(1920/iw\,1080/ih), pad=1920:1080:(1920-iw*min(1920/iw\,1080/ih))/2:(1080-ih*min(1920/iw\,1080/ih))/2"  \\Mac\Home\Documents\cglumberjack\temp\dpx2\A180C006_171113_R2XD.mov



def _execute(command):
    print 'executing command: %s' % command
    p = subprocess.Popen(command,
                         stdout=subprocess.PIPE,
                         stderr=subprocess.STDOUT)
    for each in p.stdout:
        each = each.strip()
        try:
            if "ERROR" in each:
                logging.error(each)
        except TypeError:
            pass


def create_proxy_jpg(input_folder, output_folder):
    for f in os.listdir(input_folder):
        jpeg_name = '%s.jpg' % os.path.splitext(f)[0]
        in_file = os.path.join(input_folder, f)
        out_file = os.path.join(output_folder, jpeg_name)
        command = '%s %s %s' % (config['magick'], in_file, out_file)
        _execute(command)

config = app_config()['paths']
sequence = r'\\Mac\Home\Documents\cglumberjack\temp\exr'
output_folder = r'\\Mac\Home\Documents\cglumberjack\temp\exr2'
# os.makedirs(output_folder)

# create_proxy_jpg(sequence, output_folder)

image_seq = path.lj_list_dir(output_folder, hashes=True)[0].split()[0]
image_seq = os.path.join(output_folder, image_seq)




# create_mov(sequence, output_folder)




