from skimage import io
import sys

def process(inputname, outputname):
    im = io.imread(inputname)
    for i in range(100):
        for j in range(100):
            im[i, j, :] = 0
            im[i, j, 2] = 255
    io.imsave(outputname, im)

if __name__ == "__main__":
    process(sys.argv[1], './output/test.png')
