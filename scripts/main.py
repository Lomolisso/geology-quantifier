import sampleExtraction
import tube

def gen_percent():
	img = sampleExtraction.extract_sample()
	# TODO Some ML Stuff

def gen_texture_tube():
	img = sampleExtraction.extract_sample()
	tube.fill_tube(img)


gen_texture_tube()