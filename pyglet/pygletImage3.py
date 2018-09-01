import pyglet
#import GLU
from pyglet.gl import GL_MAX_TEXTURE_SIZE
#import pyglet

#
#v=GLint()
#glGetIntegerv(GL_MAX_TEXTURE_SIZE,v)
#print 'texture size max:',GL_MAX_TEXTURE_SIZE
#print 'Max texture size:',v
window = pyglet.window.Window(resizable=True)

display = pyglet.window.get_platform().get_default_display()
screens = display.get_screens()
for i,screen in enumerate(screens):
	print"Screen",i,"Resolution:",screen.width,screen.height
	print"Screen",i,"Position  :",screen.x,screen.y
screen = screens[2]
sH = screen.height
sW = screen.width
#image = pyglet.resource.image('galaxie.JPG')
#image = pyglet.image.load('world.jpg').get_region(1000,1000,1000,1000)


def chopImage(path='world.jpg',col_row=(False,False),border = False):
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
			images.append([pyglet.image.load(path).get_region(startX,startY,subWidth,subHeight),(drawX,drawY,)])
			#subImage = back2ImageData(subImage)
			#row.append(subImage)
		#imageGrid.append(row)
	return images#, subHeight,subWidth, x,y

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
	if x == 0 and y == 0:
		print"window BL corner:",wL,wB
		print"Image  BL corner:",iL,iB
		print"Window TR corner:",wR,wT
		print"Image  TR corner:",iR,iT
		print"	Is inside	  :",inside
	
	return inside
#	corners.append(iBL)
#	corners.append(iBR)
#	corners.append(iTL)
#	corners.append(iTR)
#	inBounds = False
#	for corner in corners:
#		cX, cY = corner
#		
def getWinBounds():
	'''
	Returns L,R,B,T
	'''
	W, H = window.get_size()
	L, T = window.get_location()
	R = W + L
	B = T + H
	return L,R,B,T

@window.event
def on_draw():
	L,R,B,T = getWinBounds()
	#sW screen width 
	#sH screen height
	#wB window bottom (wrt screen) y up
	#wL window left (wrt screen) x right
	wL = L
	wB = sH - B
	wT = sH - T
	wR = R
	print"wL", wL
	print"wR", wR
	print"wB", wB
	print"wT", wT
#	print"L",L
#	print"R",R
#	print"B",B
#	print"T",T
	startX = wL
	startY = wR
	subWidth = wR-wL
	subHeight = wT-wB
	path = picPath
	#image = pyglet.image.load(path).get_region(startX,startY,subWidth,subHeight)
	image = pyglet.image.load(path).get_region(0,0,subWidth,subHeight)
	image.blit(0,0)
	pass
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
#	winSizeX, winSizeY = window.get_size()
#	winPosX, winPosY = window.get_location()
#	count = 0
#	for image,coords in images:
#		x,y = coords
#		count +=1
#		if insideWindow(x,y,image,winSizeX,winSizeY,winPosX,winPosY,winOffset=5):
#			image.blit(x,y)
		#print"Drawing image",count, 'at position:',x,y
		
	#imageGrid[0][0].blit(0,0)	
		
	#image.blit(0,0)

import sys
print 'maxInt:',sys.maxint
#sys.exit()
#imageGrid, subHeight,subWidth, x,y = chopImage('galaxie.jpg',col_row = (2,2))
#images = chopImage('galaxie.JPG',col_row = (12,12),border = 5)
picPath = 'galaxie.jpg'
print"Starting app"
pyglet.app.run()