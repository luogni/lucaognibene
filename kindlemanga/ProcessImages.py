__author__="Jeff Byrom"
__date__ ="$Jan 22, 2010 2:07:34 PM$"

import Image
import StringIO
import FileObject

def ProcessAndSave(imageFileList, targetHeight, maxWidth):
    imagecount = 0
    print 'files:'
    for index, file in enumerate(imageFileList):
        if isinstance(file, Image.Image):
            tmpImage = file
        elif (isinstance(file.data, Image.Image)):
            tmpImage = file.data
        else:
            tmpImage = Image.open(StringIO.StringIO(file.data))
            if tmpImage == None:
                print "Can't load", file.filename
                continue
        if tmpImage.getbbox() == None:
            print "Can't load image dimensions..", file.filename
            continue
            
        width = tmpImage.getbbox()[2]
        height = tmpImage.getbbox()[3]

        splitImages = None

        if (height <> targetHeight):
            scalingRatio = float(targetHeight) / height
            newHeight = targetHeight
            newWidth = MultipleOf4(width * scalingRatio)
        else:
            scalingRatio = 1
            newHeight = targetHeight
            newWidth = maxWidth

        try:
            print file.filename + ' (' + str(width) + ', ' + str(height) + ') =>',
        except:
            pass
        #convert to L (8-bit grayscale) for kindle screen:
        if tmpImage.mode != "L":
            tmpImage = tmpImage.convert("L")

        # split the image if it's wider than the maximum
        #     (hopefully it's a cover page or something)
        #     If it's wider than 1.5 pages, split into two pages:
        if (newWidth > (maxWidth * 2) * .75):
            splitImages = SplitImageHoriz(tmpImage, width, height, maxWidth)
            tmpImage = splitImages[0]
            newWidth = newWidth / 2
            #tmpFileObject = FileObject.FileObject(file.filename + '1', splitImages[1], file.size / 2, file.datetime)
            imageFileList.insert(index + 1, splitImages[1])
            splitImages = None

        # if it is bigger than 1 page but less than or equal to
        #     1.5 pages just resize it to 600px wide:
        if (newWidth > maxWidth and newWidth <= (maxWidth * 2) *.75):
            tmpImage = tmpImage.resize(tuple([maxWidth, newHeight]), Image.ANTIALIAS)
        # and if it is less than one page wide, just paste it on a blank
        #     maxWidth white (255) image:
        elif (newWidth < maxWidth):
            tmpImage2 = Image.new("L", tuple([maxWidth, newHeight]), 255)
            left = (maxWidth - newWidth) / 2
            tmpImage2.paste(tmpImage.resize(tuple([newWidth, newHeight]), Image.ANTIALIAS), tuple([left, 0]))
            tmpImage = tmpImage2

        newfilename = '%04d' % imagecount + '.gif'
        print newfilename + ' (' + str(tmpImage.getbbox()[2]) + ', ' + str(tmpImage.getbbox()[3]) + ')'
        tmpImage.save(newfilename)
        imagecount += 1
    #print "done"

def MultipleOf4(input):
    if (input % 4 == 0):
        return int(input)
    else:
        return int((round(input / 4) * 4))

def SplitImageHoriz(image, width, height, maxWidth):
    #print 'width: ' + str(width) + ', height: ' + str(height)
    rightBox = [width / 2, 0, width, height]
    leftBox = [0, 0, width / 2, height]

    imageRight = Image.new("L", tuple([width / 2, height]), 255)
    imageLeft = Image.new("L", tuple([width / 2, height]), 255)

    imageRight.paste(image.crop(rightBox), tuple([0, 0]))
    imageLeft.paste(image.crop(leftBox), tuple([0, 0]))
    
    return [imageRight, imageLeft]
