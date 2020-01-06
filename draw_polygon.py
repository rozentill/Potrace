import cv2
import numpy as np
from argparse import ArgumentParser

def parse_args():

	parser = ArgumentParser()
	parser.add_argument('src_txt')

	args = parser.parse_args()
	return args.src_txt

def main():

	src = parse_args()
	img = np.zeros((17,17,3), np.uint8)
	with open(src, 'r') as f:
		
		lines = f.readlines()
		
		for line in lines:

			point = line.split(" ")
			x = int(float(point[0]))
			y = int(float(point[1]))
			print(y, x)
			img[y, x, 2] = 255
			# img = img*255
			cv2.circle(img, (x, y), 1, (0,0,255), -1)

	cv2.imwrite('tmp.png', img)


if __name__ == '__main__':
	
	main()