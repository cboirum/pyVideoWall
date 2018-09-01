import pyglet
#import GLU
from pyglet.gl import GL_MAX_TEXTURE_SIZE
from PIL import Image
#v=GLint()
#glGetIntegerv(GL_MAX_TEXTURE_SIZE,v)
#print 'texture size max:',GL_MAX_TEXTURE_SIZE
#print 'Max texture size:',v
window = pyglet.window.Window(resizable=True)
#image = pyglet.resource.image('galaxie.JPG')
#image = pyglet.image.load('world.jpg').get_region(1000,1000,1000,1000)
path = 'galaxie.JPG'
temp_image = Image.open(path)
width = temp_image.
raw_image = temp_image.tostring()
pitch = -
MainImage = pyglet.image.ImageData(width,height, 'RGB',raw_image, pitch= -resized_x * 3)
MainImage = pyglet.image.load(path)#.get_region(0,0,200,200)
profile = False

def chopImage(path='world.jpg',col_row=(False,False),border = False,batching=False):
	'''
	Checks to see if an image is too large and chops it into 
	pieces if so
	'''
	imWidth = pyglet.image.load(path).width
	imHeight = pyglet.image.load(path).height
	imageGrid = []
	subWidth = imWidth
	if not col_row[0] or not col_row[1]:
		x = 1
		y = 1
		while subWidth >= GL_MAX_TEXTURE_SIZE:
			subWidth = subWidth/2
			x +=1
		subHeight = imHeight
		while subHeight >= GL_MAX_TEXTURE_SIZE:
			subHeight = subHeight/2
			y +=1
	else:
		x, y = col_row
		subWidth = subWidth / x
		subHeight = imHeight / y
		
	print 'original H/W :',imHeight,imWidth
	print 'sub H/W	    :',subHeight,subWidth
	print 'grid size H/W:',y,x
	images = []
	iGrid = {}
	if batching:
		batch = pyglet.graphics.Batch()
		sprites = []
	for rows in range(y):
		#row = []
		for col in range(x):
			
			startX = col*subWidth
			startY = rows*subHeight
			#subImage = pyglet.image.load(path).get_region(startX,startY,subWidth,subHeight)
			if border:
				drawX = startX + col * border
				drawY = startY + rows * border
			else:
				drawX = startX
				drawY = startY
			#image = pyglet.image.load(path).get_region(startX,startY,subWidth,subHeight)
			size = subHeight,subWidth
			images.append([size,(drawX,drawY,)])
			iGrid[str(drawX)+str(drawY)] = [(rows,col),None]
		
#			if batching:
#				sprites.append(pyglet.sprite.Sprite(image,x=drawX,y=drawY,batch=batch))
			#subImage = back2ImageData(subImage)
			#row.append(subImage)
		#imageGrid.append(row)
	iGrid['nRows'] = x
	iGrid['nCols'] = y
	
	if not batching:
		sprites = []
		batch = None
	return images,sprites,batch,iGrid#, subHeight,subWidth, x,y

def visible(size,coords,winOffset=False):
	'''
	determines if an image is visible given it's coordinates
	'''
	x,y = coords
	winSizeX, winSizeY = window.get_size()
	winPosX, winPosY = window.get_location()
	iH,iW = size

	if winOffset:
		winPosX += winOffset
		winPosY += winOffset
		winSizeY -= winOffset*2
		winSizeX -= winOffset*2

	iB = y
	iT = y + iH
	iL = x
	iR = x + iW
	wB = 0#winPosY
	wT = winSizeY #+ winPosY 
	wL = 0#winPosX
	wR = winSizeX #+ winPosX 
	outLeft = iR < wL
	outRight = iL > wR
	outAbove = iB > wT
	outBelow = iT < wB
	inWindow = not outLeft | outRight | outAbove | outBelow
	
	return inWindow

def makeBatch(images,iGrid):
	'''
	makes a batch of sprites out of images depending on if they are
	visible or not
	'''
	if profile:
		import pycallgraph
		pycallgraph.start_trace()
	batch = pyglet.graphics.Batch()
	sprites = []
	tiles = []
	xS = []
	yS = []
	#print"Making sprite batch"
	i = 0
	for size,coords in images:
		i+=1
		#print"image",i,"of",len(images)
		x,y = coords
		h,w = size
		key = str(x) + str(y)
		if visible(size,coords):
			iGrid[key][1] = True
			image = MainImage.get_region(x,y,w,h)
			print"x,y",x,y
			print"size",image.width,image.height
			try:
				sprites.append(pyglet.sprite.Sprite(image,x=x,y=y,batch=batch))
			except:
				print"error"
		else:
			iGrid[key][1] = False
	if profile:
		pycallgraph.make_dot_graph(r'C:\C9\test.png')
		print "callgraph saved"
		sys.exit()
	return batch,sprites,iGrid
	
def back2ImageData(imageDataRegion):
	'''
	returns adraw-able image data from image region data
	'''
	idr = imageDataRegion
	format = idr.format
	width = idr.width
	height = idr.height
	data = idr
	image1a = pyglet.image.ImageData(width, height, format, data, pitch=idr.pitch)
	return image1a

def drawImages(imageGrid,cols,rows):
	'''
	draws a 2d array of images in a grid as one image
	'''
	pX = 0
	pY = 0
	subWidth = imageGrid[0][0].width
	subHeight = imageGrid[0][0].height
	for y,row in enumerate(imageGrid[:rows]):
		for x,subImage in enumerate(row[:cols]):
			subImage.blit(pX,pY)
			pX += x * subWidth
		pY += y * subHeight
		
def saveGrid(imageGrid):
	'''
	saves each grid pic to file to save ram
	'''
	for y,row in enumerate(imageGrid):
		for x,subImage in enumerate(row):
			#dir = 'subImages'
			name = 'sub_'+str(x)+'_'+str(y)+'.jpg' #dir + '\'+'
			subImage.save(filename=name)
#	if imWidth >= GL_MAX_TEXTURE_SIZE:
#		subWidth = imWidth/2
#	if imHeight >= GL_MAX_TEXTURE_SIZE:
#		subHeight = imHeight/2

#print GLU_MAX_TEXTURE_SIZE
#print 'totalWidth:',totalSize
#def drawImageGrid():
#	imageGrid, subHeight,subWidth,
#	
#	imY = -subHeight
#	for imRow in imageGrid:
#		imY += subHeight
#		imX = -subWidth
#		for image in imRow:
#			imX += subWidth
			#image.blit(imX,imY)
def insideWindow(x,y,image,winSizeX,winSizeY,winPosX,winPosY,winOffset=False):
	'''
	determines if an image is inside of the current window
	'''
	iH = image.height
	iW = image.width
#	corners = []
#	iBL = x,y
#	iBR = x + iW, y
#	iTL = x, y + iH
#	iTR = x + iW, y + iH
	if winOffset:
		winPosX += winOffset
		winPosY += winOffset
		winSizeY -= winOffset*2
		winSizeX -= winOffset*2

	iB = y
	iT = y + iH
	iL = x
	iR = x + iW
	wB = 0#winPosY
	wT = winSizeY #+ winPosY 
	wL = 0#winPosX
	wR = winSizeX #+ winPosX 
	outLeft = iR < wL
	outRight = iL > wR
	outAbove = iB > wT
	outBelow = iT < wB
	inside = not outLeft | outRight | outAbove | outBelow
#	if x == 0 and y == 0:
#		print"window BL corner:",wL,wB
#		print"Image  BL corner:",iL,iB
#		print"Window TR corner:",wR,wT
#		print"Image  TR corner:",iR,iT
#		print"	Is inside	  :",inside
	
	return inside
#	corners.append(iBL)
#	corners.append(iBR)
#	corners.append(iTL)
#	corners.append(iTR)
#	inBounds = False
#	for corner in corners:
#		cX, cY = corner
#		
def batchTest(sprites,winSizeX,winSizeY,winPosX,winPosY,winOffset=False):
	'''
	determines which sprites need to be drawn based on their location
	'''
	

#	corners = []
#	iBL = x,y
#	iBR = x + iW, y
#	iTL = x, y + iH
#	iTR = x + iW, y + iH
	if winOffset:
		winPosX += winOffset
		winPosY += winOffset
		winSizeY -= winOffset*2
		winSizeX -= winOffset*2
	
	wB = 0#winPosY
	wT = winSizeY #+ winPosY 
	wL = 0#winPosX
	wR = winSizeX #+ winPosX 	
	batch = pyglet.graphics.Batch()
	for sprite in sprites:
		iH = sprite.height
		iW = sprite.width
		x = sprite.x
		y = sprite.y

		iB = y
		iT = y + iH
		iL = x
		iR = x + iW
		
		outLeft = iR < wL
		outRight = iL > wR
		outAbove = iB > wT
		outBelow = iT < wB
		inside = not outLeft | outRight | outAbove | outBelow
		if inside:
			batch.add(sprite,1,pyglet.gl.GL_TRIANGLES,None)
#	if x == 0 and y == 0:
#		print"window BL corner:",wL,wB
#		print"Image  BL corner:",iL,iB
#		print"Window TR corner:",wR,wT
#		print"Image  TR corner:",iR,iT
#		print"	Is inside	  :",inside
	
	return batch

def printGrid(iGrid):
	'''
	Prints a dictionary grid to show visible tiles
	'''
	nRows = iGrid['nRows']
	nCols = iGrid['nCols']
	vGrid = []
	for row in range(nRows):
		Row = []
		for col in range(nCols):
			Row.append(False)
		vGrid.append(Row)
	for key in iGrid.keys():
		if key not in ['nRows','nCols']:
			pos,vis = iGrid[key]
			col,row = pos
			vGrid[row][col]=vis
	for row in reversed(vGrid):
		for col in row:
			print "["+'*'*col+' '*(not col)+']',
		print
	print
@window.event
def on_draw():
	global iGrid
	window.clear()
	pass
	#winSizeX, winSizeY = window.get_size()
	#winPosX, winPosY = window.get_location()
	#batch = batchTest(sprites,winSizeX,winSizeY,winPosX,winPosY,winOffset=5)
	batch,sprites,iGrid = makeBatch(images,iGrid)
	printGrid(iGrid)
	batch.draw()
	#drawImageGrid()
	#window.clear()
	#drawImages(imageGrid,1,1)
#	image1 = imageGrid[0][0].get_image_data()
#	image1_data = image1.get_data(image1.format, image1.pitch)
#	format = image1.format
#	width = image1.width
#	height = image1.height
#	data = image1_data
#	image1a = pyglet.image.ImageData(width, height, format, data, pitch=image1.pitch)
#	print 'image1a:',image1a
#	print "iGrid:",imageGrid[0][0]#.blit(0,0)
#	print "iGrid:",image1
#	print "image:",image
	#image2 = parts[0]
	#image2.blit(0,0)
	
def gridDraw():	
	winSizeX, winSizeY = window.get_size()
	winPosX, winPosY = window.get_location()
	count = 0
	for image,coords in images:
		x,y = coords
		count +=1
		if insideWindow(x,y,image,winSizeX,winSizeY,winPosX,winPosY,winOffset=5):
			image.blit(x,y)
		#print"Drawing image",count, 'at position:',x,y
		
	#imageGrid[0][0].blit(0,0)	
		
	#image.blit(0,0)

import sys
print 'maxInt:',sys.maxint
#sys.exit()
#imageGrid, subHeight,subWidth, x,y = chopImage('galaxie.jpg',col_row = (2,2))

#path = 'world.jpg'
images,sprites,batch,iGrid = chopImage(path,col_row = (2,2),border = 5)
#images,sprites,batch = chopImage('galaxie.JPG',col_row = (2,2),border = 5,batching=True)
#batch = makeBatch(images)

print"Starting app"
pyglet.app.run()