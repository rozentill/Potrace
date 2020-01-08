import cv2
import os
import numpy as np
import subprocess
import shutil
from os.path import join
from argparse import ArgumentParser

def parse_args():

	parser = ArgumentParser()
	parser.add_argument('src_dir')
	parser.add_argument('dst_dir')

	args = parser.parse_args()
	return args.src_dir, args.dst_dir

def verbose(*args, level=1):
	if VERBOSITY_LEVEL >= level:
		print(*args)

def process_command(command, stdinput=None, stdout_=False, stderr_=False):
	"""run command in invisible shell, return stdout and/or stderr as specified

	Returns stdout, stderr, or a tuple (stdout, stderr) depending on which of
	stdout_ and stderr_ is True. Raises an exception if the command encounters
	an error.

	command: command with arguments to send to command line
	stdinput: data (bytes) to send to command's stdin, or None
	stdout_: True to receive command's stdout in the return value
	stderr_: True to receive command's stderr in the return value
"""
	verbose(command)
	stdin_pipe   = (subprocess.PIPE if stdinput  is not None else None)
	stdout_pipe  = (subprocess.PIPE if stdout_ is True else None)
	stderr_pipe  = subprocess.PIPE
	process = subprocess.Popen(command, stdin=stdin_pipe, stderr=stderr_pipe, stdout=stdout_pipe,
		shell=True)
	stdoutput, stderror = process.communicate(stdinput)
	returncode = process.wait()
	if returncode != 0:
		Exception(stderror.decode())
	if stdout_ and not stderr_:
		return stdoutput
	elif stderr_ and not stdout_:
		return stderr
	elif stdout_ and stderr_:
		return (stdoutput, stderror)
	elif not stdout_ and not stderr_:
		return None

#run and draw
def main():

	POTRACE_PATH = "./potrace-1.16/src/potrace"

	src, dst = parse_args()

	subdir_list = os.listdir(src)

	for subdir in subdir_list:

		f_img_src = join(src, subdir, "raster.png")
		
		img_src = cv2.imread(f_img_src, cv2.IMREAD_UNCHANGED)

		height = img_src.shape[0]
		width = img_src.shape[1]

		# run potrace

		f_ppm = join(dst, subdir, "raster~tmp_layer.ppm")
		f_svg = join(dst, subdir, "raster_polygon.svg")

		command = ('"{potrace}" --svg -o "{dest}" -C "{outcolor}" -t {despeckle} '
		'-a {smoothcorners} -O {optimizepaths} "{src}"').format(
		potrace = POTRACE_PATH, dest=f_svg, outcolor="#ffffff",
		despeckle=0, smoothcorners=1, optimizepaths=0.2, src=f_ppm)
		process_command(command)
		# check polygon
		f_tmp = "tmp.txt"
		if os.path.isfile(f_tmp):
			pass
		else:
			print("Not found tmp file!")

		#copy polygon
		f_dst_polygon = join(dst, subdir, "raster_polygon.txt")
		shutil.copy(f_tmp, f_dst_polygon)
		os.remove(f_tmp)

		#draw polygon

		with open(f_dst_polygon, 'r') as f:
			scale = 10
			img_polygon = np.ones(((width+2)*scale,(height+2)*scale, 3), np.uint8)
			img_polygon = img_polygon*255
			img_polygon[1*scale:height*scale+1*scale, 1*scale:width*scale+1*scale] = cv2.resize(img_src, (width*scale, height*scale), interpolation=cv2.INTER_NEAREST)
			start_x = -1
			start_y = -1
			prev_x = -1
			prev_y = -1
			num = 0
			lines = f.readlines() 
			for line in lines:
				if "split" in line:
					num = 0
					cv2.line(img_polygon, (prev_x, prev_y), (start_x, start_y), (120, 120, 120), 1) # draw back to start point
					continue
				else: #there are numbers
					point = line.split(" ")
					x = (float(point[0]))
					y = (float(point[1]))
					x = int((x+1)*scale)
					y = int((16-y+1)*scale)
					cv2.circle(img, (x, y), 2, (0, 0, 255), -1)
					num += 1
					if num == 1:
						start_y = y
						start_x = x
					else:
						cv2.line(img, (prev_x, prev_y), (x, y), (0, 0, 0), 2)

					prev_y = y
					prev_x = x

			cv2.imwrite(f_dst_polygon_img, img_polygon)



#only draw
def main_test_single():

	scale = 10
	
	src, dst = parse_args()
	img_dst = cv2.imread(dst)
	width = img_dst.shape[1]
	height = img_dst.shape[0]
	img_dst = cv2.resize(img_dst, (width*scale, height*scale), interpolation=cv2.INTER_NEAREST)
	img = np.ones(((width+2)*scale,(height+2)*scale, 3), np.uint8)
	img = img*255
	img[1*scale:height*scale+1*scale, 1*scale:width*scale+1*scale] = img_dst

	x = 0
	y = 0
	prev_x = 0
	prev_y = 0
	start_x = 0 
	start_y = 0
	num = 0
	with open(src, 'r') as f:
		
		lines = f.readlines()
		
		for line in lines:

			point = line.split(" ")
			x = (float(point[0]))
			y = (float(point[1]))
			x = int((x+1)*scale)
			y = int((16-y+1)*scale)
			cv2.circle(img, (x, y), 2, (0, 0, 255), -1)
			if num == 0:
			
				start_y = y
				start_x = x
			else:
				cv2.line(img, (prev_x, prev_y), (x, y), (255, 255, 0), 1)

			prev_x = x
			prev_y = y
			num+=1

	cv2.line(img, (prev_x, prev_y), (start_x, start_y), (255, 255, 0), 1)
	cv2.imwrite('tmp.png', img)


if __name__ == '__main__':
	
	main()
