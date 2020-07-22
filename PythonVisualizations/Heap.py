import time
import random
from tkinter import *

try:
    from drawable import *
    from VisualizationApp import *
except ModuleNotFoundError:
    from .drawable import *
    from .VisualizationApp import *


class Heap(VisualizationApp):
    nextColor = 0
    MAX_ARG_WIDTH = 8
    MAX_SIZE = 31
    CELL_WIDTH = 25
    CELL_HEIGHT = 12
    CELL_BORDER = 1
    CELL_BORDER_COLOR = 'black'
    HEAP_X0 = 50
    HEAP_Y0 = 30

    def __init__(self, size=2, maxArgWidth=MAX_ARG_WIDTH, title="Heap", **kwargs):
        super().__init__(title=title, maxArgWidth=maxArgWidth, **kwargs)
        self.size = size
        self.title = title
        self.list = []
        self.maxArgWidth = maxArgWidth
        self.buttons = self.makeButtons()
        self.display()
        self.indexDisplay = self.createIndex(len(self.list))

    def __str__(self):
        return str(self.list)

    # Create an index arrow to point at an indexed cell with an optional name label
    def createIndex(self, index, name=None):
        cell_coords = self.cellCoords(index)
        cell_center = self.cellCenter(index)
        x0 = self.HEAP_X0 - self.CELL_WIDTH - 5
        x1 = self.HEAP_X0 - self.CELL_WIDTH * 3 // 10
        y0 = y1 = cell_coords[-1] + self.CELL_HEIGHT // 2
        if not name:
            label = "nItems"  # labels the top of the Heap "top" with the pointer arrow
        else:
            label = name
        return self.drawArrow(
            x0, y0, x1, y1, self.VARIABLE_COLOR, self.SMALL_FONT, name=label)

        # draw the actual arrow

    def drawArrow(
            self, x0, y0, x1, y1, color, font, name=None):
        arrow = self.canvas.create_line(
            x0, y0, x1, y1, arrow="last", fill=color)
        if name:
            label = self.canvas.create_text(
                x0 - self.CELL_WIDTH / 2, y0 + (self.CELL_HEIGHT / 16) - 3, text=name, anchor=SW,
                font=font, fill=color)
        return (arrow, label) if name else (arrow,)

    def swap(self, a, b, aCellObjects=[], bCellObjects=[]):
        itemsA = [self.list[a].display_shape,
                  self.list[a].display_val] + aCellObjects
        itemsB = [self.list[b].display_shape,
                  self.list[b].display_val] + bCellObjects
        upDelta = (0, - self.CELL_HEIGHT * 4 // 3)
        downDelta = multiply_vector(upDelta, -1)
        if a == b:  # Swapping with self - just move up & down
            self.moveItemsBy(itemsA, upDelta, sleepTime=0.02)
            self.moveItemsBy(itemsA, downDelta, sleepTime=0.02)
            return
        # make a and b cells plus their associated items switch places
        self.moveItemsOnCurve(
            itemsA + itemsB, [self.canvas.coords(i) for i in itemsB + itemsA],
            sleepTime=0.05, startAngle=90 * 11 / (10 + abs(a - b)))
        # perform the actual cell swap operation in the list
        self.list[a], self.list[b] = self.list[b], self.list[a]
        # HEAP FUNCTIONALITY

    def insert(self, val):
        callEnviron = self.createCallEnvironment()
        self.startAnimations()

        # If array needs to grow, add cells:
        if self.size < len(self.list) + 1:
            # making a tag for the array
            arrayList = self.canvas.find_withtag("arrayCell")
            # making a tag for the copy of the array
            for cell in arrayList:
                item = self.copyCanvasItem(cell)
                self.canvas.itemconfig(item, tags="newArrayCell")
            newArrayList = self.canvas.find_withtag("newArrayCell")
            newArrayList = list(newArrayList)
            boxes = list(newArrayList)
            callEnviron |= set(boxes)
            # adding the values to the list of the copy of the array
            for i in range(len(self.list)):
                newArrayList += [self.list[i].display_shape, self.list[i].display_val]
            self.moveItemsBy(newArrayList, (2 * self.CELL_WIDTH, 0))  # moving the whole array over

            # Growing the the array
            for i in range(self.size * 2):
                self.createArrayCell(i)
            self.size *= 2
            # copying the values back into the larger array
            copyVals = []
            for i in range(len(self.list)):
                copyVals += [self.list[i].display_shape, self.list[i].display_val]
            self.moveItemsBy(copyVals, (-2 * self.CELL_WIDTH, 0))
            # getting rid of the smaller array
        # don't move arrow up if the first cell is being filled because it is already pointing there
        if len(self.list) >= 1:
            self.moveItemsBy(self.indexDisplay, (0, + self.CELL_HEIGHT))
        cellCoords = self.cellCoords2(len(self.list))  # Color box
        cellCenter = self.cellCenter2(len(self.list))  # Number in box
        # create new cell and cell value display objects
        cellCoords = add_vector(cellCoords, (0, 0, 0, self.CELL_BORDER))
        toPositions = (cellCoords, cellCenter)
        # determine the top left and bottom right positions
        startPosition = [self.HEAP_X0, 0, self.HEAP_X0, 0]  # Color
        startPosition = add_vector(startPosition, (0, 0, self.CELL_WIDTH, self.CELL_HEIGHT))  # color`
        cellPair = self.createCellValue(startPosition, val)
        callEnviron.add(cellPair)
        self.moveItemsTo(cellPair, toPositions, steps=self.CELL_HEIGHT, sleepTime=0.01)

        # add a new Drawable with the new value, color, and display objects
        d = drawable(
            val, self.canvas.itemconfigure(cellPair[0], 'fill')[-1], *cellPair)
        self.list.append(d)  # store item at the end of the list

        if len(self.list) <= 0:  # heap condition.  The root node, i = 0,
            return

        for i in range(len(self.list) - 1, 0, -1):
            if self.list[i] > self.list[(i - 1) // 2]:  # if i is less than its parent
                self.swap(i, (i - 1) // 2)

        callEnviron.discard(cellPair)
        # finish the animation
        self.cleanUp(callEnviron)

    # makes a new heap of size 2
    def newArray(self):
        # gets rid of old elements in the list
        del self.list[:]
        self.size = 2
        self.display()
        # make a new arrow pointing to the top of the Heap
        self.indexDisplay = self.createIndex(len(self.list))

    def peek(self):
        self.startAnimations()
        callEnviron = self.createCallEnvironment()

        # draw output box
        canvasDimensions = self.widgetDimensions(self.canvas)
        spacing = self.CELL_WIDTH * 3 // 4
        padding = 10
        boxSize = 1
        peekIndex = 0
        # changed the values that were added to the variables to get the output box in a desirable location
        outputBox = self.canvas.create_rectangle(
            (self.HEAP_X0 * 2 + padding),
            canvasDimensions[1] - self.CELL_WIDTH - padding,
            (self.HEAP_X0 * 2 + boxSize * spacing + padding * 2),
            canvasDimensions[1] - padding,
            fill=self.OPERATIONS_BG)
        callEnviron.add(outputBox)

        outputBoxCoords = self.canvas.coords(outputBox)
        midOutputBox = (outputBoxCoords[3] + outputBoxCoords[1]) // 2
        # create the value to move to output box
        valueOutput = self.copyCanvasItem(self.list[peekIndex].display_val)
        valueList = (valueOutput,)
        callEnviron.add(valueOutput)
        # move value to output box
        # self.highlightCodeTags('print', callEnviron)
        toPositions = (outputBoxCoords[0] + padding / 2 + (peekIndex + 1 / 2) * spacing,
                        midOutputBox)
        self.moveItemsTo(valueList, (toPositions,), sleepTime=.02)
        # make the value 25% smaller
        newSize = (self.VALUE_FONT[0], int(self.VALUE_FONT[1] * .75))
        self.canvas.itemconfig(valueOutput, font=newSize)

        # add label to output box
        labelX = self.HEAP_X0 * 2 + boxSize * spacing + padding * 5
        labelY = canvasDimensions[1] - padding * 2

        boxLabel = self.canvas.create_text(
            labelX, labelY, text="root", font=self.VARIABLE_FONT)
        callEnviron.add(boxLabel)
        self.highlightCodeTags([], callEnviron)
        # finish animation
        self.cleanUp(callEnviron)


    def removeMax(self):
        self.startAnimations()
        callEnviron = self.createCallEnvironment()

        # remove first element from list
        n = self.list[0]
        self.list[0] = None
        self.size -= 1
        # if the array is now empty, delete the NoneType place holder from the array
        if self.size < 1: del self.list[:]
        # Slide value rectangle up and off screen
        items = (n.display_shape, n.display_val)
        toPositions = (100, -100, 100, -50)
        callEnviron |= set(items)
        self.moveItemsBy(items, delta=(0, -max(400, self.canvas.coords(n.display_shape)[3])), steps=self.CELL_HEIGHT,
                        sleepTime=.05)

        if self.size < 1:
            self.setMessage("Heap requirement satisfied")

        # move bottom cell to top, and heapify
        else:
            self.swapRoot()
            self.heapify()

        # Finish animation
        self.cleanUp(callEnviron)


    def isHeap(self):
        cur = 0
        size = len(self.list)

        while cur < size // 2:
            leftChild = 2 * cur + 1
            rightChild = leftChild + 1

            top = self.list[cur]
            if self.list[leftChild] > top or (rightChild < size and self.list[rightChild] > top):
                return False  # return false if a child is larger than a parent
            else:
                cur += 1

        return True


    def heapify(self):
        # trickle down until heap is in order
        while not self.isHeap():
            self.trickleDown()


    def swapRoot(self):
        self.startAnimations()
        callEnviron = self.createCallEnvironment()
        n = self.list[-1]
        items = (n.display_shape, n.display_val)

        # move the last cell to the front of the heap
        cellCoords = self.cellCoords2(0)
        cellCenter = self.cellCenter2(0)
        toPositions = (cellCoords, cellCenter)
        # self.moveItemsOffCanvas(items, N, sleepTime=0.02) ## alternative method to moveItemsBy
        self.moveItemsTo(items, toPositions)
        self.list[0] = n
        # delete the last element from the list
        del self.list[-1]


    def trickleDown(self, cur=0, size=-1):
        self.startAnimations()
        callEnviron = self.createCallEnvironment()

        if size == -1: size = len(self.list)
        top = self.list[cur]  # save the Node at the root

        # while the current Node has at least one child...
        while cur < size // 2:
            leftChild = 2 * cur + 1
            rightChild = leftChild + 1
            largerChild = leftChild
            top = self.list[cur]
            # find smaller child (right child might not exist)
            if rightChild < size and \
                    self.list[leftChild] < self.list[rightChild]:
                largerChild = rightChild
            # done trickling if top's key is >= the key of larger child
            if top >= self.list[largerChild]:
                cur += 1

            else:
                # shift child up
                self.swap(cur, largerChild)
                cur += 1

        self.cleanUp(callEnviron)


    def randomFill(self, val):
        callEnviron = self.createCallEnvironment()
        self.startAnimations()

        self.size = val
        del self.list[:]
        self.display()

        # adding the values to the list
        for i in range(val):
            num = random.randint(1, 99)

            # don't move arrow up if the first cell is being filled because it is already pointing there
            if len(self.list) >= 1:
                self.moveItemsBy(self.indexDisplay, (0, + self.CELL_HEIGHT))

            cellCoords = self.cellCoords2(len(self.list))  # Color box
            cellCenter = self.cellCenter2(len(self.list))  # Number in box

            # create new cell and cell value display objects
            cellCoords = add_vector(cellCoords, (0, 0, 0, self.CELL_BORDER))
            toPositions = (cellCoords, cellCenter)

            # determine the top left and bottom right positions
            startPosition = [self.HEAP_X0, 0, self.HEAP_X0, 0]  # Color
            startPosition = add_vector(startPosition, (0, 0, self.CELL_WIDTH, self.CELL_HEIGHT))  # color`
            cellPair = self.createCellValue(startPosition, num)
            callEnviron.add(cellPair)
            self.moveItemsTo(cellPair, toPositions, steps=self.CELL_HEIGHT, sleepTime=0.01)

            # add a new Drawable with the new value, color, and display objects
            d = drawable(
                num, self.canvas.itemconfigure(cellPair[0], 'fill')[-1], *cellPair)
            self.list.append(d)  # store item at the end of the list

        # finish the animation
        self.cleanUp(callEnviron)


    def cellCoords(self, cell_index):  # Get bounding rectangle for array cell
        return (self.HEAP_X0 + self.CELL_BORDER,  # width
                (self.HEAP_Y0 + self.CELL_HEIGHT * (cell_index + 1)) + self.CELL_BORDER,  # height
                self.HEAP_X0 + self.CELL_WIDTH - self.CELL_BORDER,
                self.HEAP_Y0 + self.CELL_HEIGHT * cell_index - self.CELL_BORDER)


    def cellCoords2(self, cell_index):  # Get bounding rectangle for array cell
        return (self.HEAP_X0 + self.CELL_BORDER,  # width
                (self.HEAP_Y0 + self.CELL_HEIGHT * (cell_index + 1)),  # height
                self.HEAP_X0 + self.CELL_WIDTH - self.CELL_BORDER,
                self.HEAP_Y0 + self.CELL_HEIGHT * cell_index)


    def cellCenter(self, index):  # Center point for array cell at index
        half_cell_x = (self.CELL_WIDTH - self.CELL_BORDER) // 2
        half_cell_y = (self.CELL_HEIGHT - self.CELL_BORDER) // 2
        return subtract_vector(self.cellCoords(index), (half_cell_x, half_cell_y))


    def cellCenter2(self, index):  # Center point for array cell at index
        half_cell_x = (self.CELL_WIDTH + self.CELL_BORDER) // 2
        half_cell_y = (self.CELL_HEIGHT - self.CELL_BORDER) // 2

        return add_vector(subtract_vector(self.cellCoords(index), (0, half_cell_y)), (half_cell_x, 0))


    def createArrayCell(self, index):  # Create a box representing an array cell
        cell_coords = self.cellCoords(index)
        half_border = self.CELL_BORDER // 2
        arrayCoords = add_vector(cell_coords,
                                (half_border - 1, half_border - 1,
                                self.CELL_BORDER - half_border - 1, self.CELL_BORDER - half_border))
        rect = self.canvas.create_rectangle(arrayCoords,
                                            fill=None, outline=self.CELL_BORDER_COLOR, width=self.CELL_BORDER,
                                            tags="arrayCell")
        self.canvas.lower(rect)
        return rect


    def createCellValue(self, indexOrCoords, key, color=None):
        """Create new canvas items to represent a cell value.  A square
        is created filled with a particular color with an text key centered
        inside.  The position of the cell can either be an integer index in
        the Array or the bounding box coordinates of the square.  If color
        is not supplied, the next color in the palette is used.
        An event handler is set up to update the VisualizationApp argument
        with the cell's value if clicked with any button.
        Returns the tuple, (square, text), of canvas items
        """
        # Determine position and color of cell
        if isinstance(indexOrCoords, int):
            rectPos = self.cellCoords(indexOrCoords)
            valPos = self.cellCenter(indexOrCoords)
        else:
            rectPos = indexOrCoords
            valPos = divide_vector(add_vector(rectPos[:2], rectPos[2:]), 2)
        if color is None:
            # Take the next color from the palette
            color = drawable.palette[Heap.nextColor]
            Heap.nextColor = (Heap.nextColor + 1) % len(drawable.palette)
        cell_rect = self.canvas.create_rectangle(
            *rectPos, fill=color, outline='', width=0)
        cell_val = self.canvas.create_text(
            *valPos, text=str(key), font=self.SMALL_FONT, fill=self.VALUE_COLOR)
        handler = lambda e: self.setArgument(str(key))
        for item in (cell_rect, cell_val):
            self.canvas.tag_bind(item, '<Button>', handler)
        return cell_rect, cell_val


    def display(self):
        self.canvas.delete("all")
        for i in range(self.size):  # Draw grid of cells
            self.createArrayCell(i)
        # go through each Drawable in the list
        for i, n in enumerate(self.list):
            # create display objects for the associated Drawables
            n.display_shape, n.display_val = self.createCellValue(
                i, n.val, n.color)
            n.color = self.canvas.itemconfigure(n.display_shape, 'fill')
        self.window.update()

    def makeButtons(self):
        vcmd = (self.window.register(numericValidate),
                '%d', '%i', '%P', '%s', '%S', '%v', '%V', '%W')
        # numArguments decides the side where the button appears in the operations grid
        insertButton = self.addOperation(
            "Insert", lambda: self.clickInsert(), numArguments=1, validationCmd=vcmd)
        newHeapButton = self.addOperation(
            "New", lambda: self.clickNewArray())
        peekButton = self.addOperation(
            "Peek", lambda: self.clickPeek())
        randomFillButton = self.addOperation(
            "Random Fill ", lambda: self.clickRandomFill(), numArguments=1,
            validationCmd=vcmd)
        removeMaxButton = self.addOperation(
            "Remove Max", lambda: self.clickRemoveMax())
        heapifyButton = self.addOperation(
            "Heapify", lambda: self.clickHeapify())
        return [insertButton, newHeapButton, peekButton, randomFillButton, removeMaxButton, heapifyButton]


    def validArgument(self):
        entered_text = self.getArgument()
        if entered_text and entered_text.isdigit():
            val = int(entered_text)
            if val < 100:
                return val

    # Button functions
    def clickInsert(self):
        val = self.validArgument()
        if val is None:
            self.setMessage("Input value must be an integer from 0 to 99.")
        else:
            if len(self.list) == self.MAX_SIZE:
                self.setMessage("Error! Heap is already full.")
            else:
                self.insert(val)
                self.setMessage("Value {} inserted!".format(val))
        self.clearArgument()

    def clickPeek(self):
        if len(self.list) <= 0:
            self.setMessage("Error! Heap is empty.")
        else:
            val = self.list[0].val
            self.peek()
            self.setMessage("{} is the root value!".format(val))


    def clickNewArray(self):
        self.newArray()

    def clickRemoveMax(self):
        if len(self.list) == 0:
            self.setMessage('Heap is empty!')

        else:
            val = self.list[0].val
            self.removeMax()
            self.setMessage("{} was removed!".format(val))

        self.setButtonsStatus()


    def clickRandomFill(self):
        # if the animation is not stopped (it is running or paused):
        if self.animationState != self.STOPPED:
            # error message appears and insert will not take place
            self.setMessage("Unable to insert at the moment")
        else:
            val = self.validArgument()
            if val is None:
                self.setMessage("Input value must be an integer from 1 to {}.".format(self.MAX_SIZE))
            elif self.window.winfo_width() <= self.HEAP_X0 + (
                    (len(self.list) + 1) * self.CELL_WIDTH):
                self.setMessage("Error! No room to display")
            elif 0 < val < 32:
                self.randomFill(val)


    def clickHeapify(self):
        self.heapify()
        self.setButtonsStatus()

        # if no button is specified to change its state, all buttons will be set to default state NORMAL, unless a different state is specified


    def setButtonsStatus(self, state=NORMAL, buttonName=None):
        if not buttonName:
            for b in self.buttons:
                b['state'] = state
        else:
            for b in self.buttons:
                if b["text"] == buttonName: b['state'] = state


if __name__ == '__main__':
    # random.seed(3.14159)    # Use fixed seed for testing consistency
    HEAP = Heap()
    HEAP.runVisualization()