import cv2
import numpy as np
from argparse import ArgumentParser

def parse_args():

	parser = ArgumentParser()
	parser.add_argument('src_txt')
	parser.add_argument('dst_img')

	args = parser.parse_args()
	return args.src_txt, args.dst_img

def main():
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