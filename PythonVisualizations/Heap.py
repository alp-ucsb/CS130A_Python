import time
from tkinter import *
import random 

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
    CELL_BORDER = 2
    CELL_BORDER_COLOR = 'black'
    HEAP_X0 = 80
    HEAP_Y0 = 18

    def __init__(self, size=2, maxArgWidth=MAX_ARG_WIDTH, title="Heap", **kwargs):
        super().__init__(title=title, maxArgWidth=maxArgWidth, **kwargs)
        self.size = size
        self.title = title
        self.list = []
        self.maxArgWidth = maxArgWidth
        self.buttons = self.makeButtons()
        
        self.display()

    def __str__(self):
        return str(self.list)
    
    # Create an index arrow to point at an indexed cell with an optional name label
    def createIndex(self, index, level=1, name='nItems'):
        cell_coords = self.cellCoords(index)
        cell_center = self.cellCenter(index)
        level_spacing = self.SMALL_FONT[1]
        if level > 0:
            x0 = self.HEAP_X0 - self.CELL_WIDTH * 0.8 - level * level_spacing
            x1 = self.HEAP_X0 - self.CELL_WIDTH * 0.3
        else:
            x0 = self.HEAP_X0 + 1.8 * self.CELL_WIDTH - level * level_spacing
            x1 = self.HEAP_X0 + self.CELL_WIDTH * 1.3
        y0 = y1 = cell_center[1]
        return self.drawArrow(
            x0, y0, x1, y1, self.VARIABLE_COLOR, self.SMALL_FONT, name=name)
    
    # draw the actual arrow 
    def drawArrow(
            self, x0, y0, x1, y1, color, font, name=None):
        arrow = self.canvas.create_line(
            x0, y0, x1, y1, arrow="last", fill=color)
        leftPointing = x1 < x0
        separation = 3 if leftPointing else -3
        if name:
            label = self.canvas.create_text(
                x0 + separation, y0, text=name, anchor=W if leftPointing else E,
                font=font, fill=color)

        return (arrow, label) if name else (arrow,) 

    # HEAP FUNCTIONALITY

    def insert(self, val):
        callEnviron = self.createCallEnvironment() 
        self.startAnimations()       
        
        #If array needs to grow, add cells:
        if self.size <= len(self.list):
            shift_delta = (2 * self.CELL_WIDTH, 0)
            cells = self.canvas.find_withtag("arrayCell")
            cells_and_values = list(cells)
            for v in self.list: # move current array cells and values over
                
                cells_and_values.append(v.display_shape)
                cells_and_values.append(v.display_val)
            self.moveItemsBy(cells_and_values, shift_delta, sleepTime=0.02)
          
            # Grow the the array 
            for i in range(self.size): 
                callEnviron.add(self.createArrayCell(i)) # Temporary
                self.createArrayCell(i + self.size) # Lasting
            self.size *= 2
            
            #copying the values back into the larger array 
            for v in self.list:
                newValue = (self.copyCanvasItem(v.display_shape),
                            self.copyCanvasItem(v.display_val))
                callEnviron |= set(newValue)
                self.moveItemsBy(newValue, multiply_vector(shift_delta, -1),
                                 sleepTime=0.01)

            # Move old cells back to original positions in one step
            # These are lasting and overlap the temporary ones just created
            self.moveItemsBy(cells_and_values, multiply_vector(shift_delta, -1),
                             steps=1)

        cellCoords = self.cellCoords(len(self.list)) # Color box
        cellCenter = self.cellCenter(len(self.list)) # Number in box

        # create new cell and cell value display objects
        toPositions = (cellCoords, cellCenter)

        # determine the top left and bottom right positions
        startPosition = [self.HEAP_X0, 0, self.HEAP_X0, 0] #Color 
        startPosition = add_vector(startPosition, (0, 0, self.CELL_WIDTH, self.CELL_HEIGHT)) #color`
        cellPair = self.createCellValue(startPosition, val)
        callEnviron |= set(cellPair)
        self.moveItemsTo(cellPair, toPositions, steps=self.CELL_HEIGHT, sleepTime=0.01)
    
        # add a new Drawable with the new value, color, and display objects
        d = drawable(
            val, self.canvas.itemconfigure(cellPair[0], 'fill')[-1], *cellPair)
        self.list.append(d)    #store item at the end of the list     
        callEnviron -= set(cellPair)
        
        # Move nItems index to one past inserted item
        y = self.cellCenter(len(self.list))[1]
        # Use x coord from nItemsIndex but y value from target location
        coords = [[y if i % 2 == 1 else c
                   for i, c in enumerate(self.canvas.coords(i))]
                  for i in self.nItemsIndex]
        self.moveItemsTo(self.nItemsIndex, coords, sleepTime=0.01)
            
        self.siftUp(len(self.list) - 1)  # Sift up new item
                    
        # finish the animation
        self.cleanUp(callEnviron)

    def siftUp(self, i):
        if i <= 0:
            return
        callEnviron = self.createCallEnvironment()
        item = self.list[i].copy()
        copyItem = (self.copyCanvasItem(item.display_shape),
                    self.copyCanvasItem(item.display_val))
        callEnviron |= set(copyItem)
        itemDelta = (3 * self.CELL_WIDTH, 0)
        self.moveItemsBy(copyItem, itemDelta, sleepTime=0.02)
        iIndex = self.createIndex(i, name='i', level=-1)
        parentIndex = self.createIndex((i - 1) // 2, name='parent', level=-2)
        callEnviron |= set(iIndex + parentIndex)
        while 0 < i:
            parent = (i - 1) // 2
            delta = self.cellCenter(parent)[1] - self.canvas.coords(
                parentIndex[0])[1]
            if delta != 0:      # Move parent index pointer
                self.moveItemsBy(parentIndex, (0, delta), sleepTime=0.01)

            self.wait(0.2)      # Pause for comparison
            if self.list[parent] < item: # if parent less than item sifting up
                # move a copy of the parent down to node i
                copyVal = (self.copyCanvasItem(self.list[parent].display_shape),
                           self.copyCanvasItem(self.list[parent].display_val))
                callEnviron |= set(copyVal)
                self.moveItemsOnCurve(
                    copyVal, (self.cellCoords(i), self.cellCenter(i)),
                    startAngle=-90 * 11 / (10 + i - parent),
                    sleepTime=0.02)
                self.list[i].val = self.list[parent].val
                self.list[i].color = self.list[parent].color
                self.canvas.delete(self.list[i].display_shape)
                self.canvas.delete(self.list[i].display_val)
                self.list[i].display_shape, self.list[i].display_val = copyVal
                callEnviron -= set(copyVal)
            else:
                break

            # Advance i to parent, move original item along with i Index
            delta = self.cellCenter(parent)[1] - self.cellCenter(i)[1]
            self.moveItemsBy(iIndex + copyItem, (0, delta), sleepTime=0.01)
            i = parent

        # Move copied item into appropriate location
        self.moveItemsBy(copyItem, multiply_vector(itemDelta, -1),
                         sleepTime=0.01)
        self.canvas.delete(self.list[i].display_shape)
        self.canvas.delete(self.list[i].display_val)
        self.list[i].val, self.list[i].color = item.val, item.color
        self.list[i].display_shape, self.list[i].display_val = copyItem
        callEnviron -= set(copyItem)
        self.cleanUp(callEnviron)
        
    
     
       
    def siftDown(self, i=0):  # Sift item i down to preserve heap cond. default start at root node index
        
        firstLeaf = len(self.list)//2 # Get index of first leaf
        if i >= firstLeaf: 
            return # If item i is at or below leaf level, it cannot be moved down
        self.startAnimations()
        callEnviron = self.createCallEnvironment()
        
        item = self.list[i].copy()   # Store item at cell i
        copyItem = (self.copyCanvasItem(item.display_shape),
                            self.copyCanvasItem(item.display_val))
        callEnviron |= set(copyItem)
        itemDelta = (3 * self.CELL_WIDTH, 0)
        self.moveItemsBy(copyItem, itemDelta, sleepTime=0.02)
        
        # arrows
        iIndex = self.createIndex(i, name='i', level=-1)
        maxChildIndex = self.createIndex(2 * i + 1, name='maxChild', level=-2)
        callEnviron |= set(iIndex + maxChildIndex)
           
        itemkey = item.val # key
        while i < firstLeaf:  # While i above leaf level, find children
            left = (2*i)+1
            right = (2*i)+2
            maxi = left        # Assume left child has larger key
           
            if (right < len(self.list) and # If both children are present, and
                self.list[left].val < # left child has smaller key
                self.list[right].val): 
                maxi = right    # then use right child

            delta = self.cellCenter(maxi)[1] - self.canvas.coords(maxChildIndex[0])[1]  
            if delta != 0:      # Move child index pointer
                self.moveItemsBy(maxChildIndex, (0, delta), sleepTime=0.01) 
                self.wait(0.2)      # Pause for comparison
            
            if (itemkey <      # If item i's key is less
                self.list[maxi].val): # than max child's key,

                # move a copy of the child down to node i
                copyVal = (self.copyCanvasItem(self.list[maxi].display_shape),
                           self.copyCanvasItem(self.list[maxi].display_val))
                callEnviron |= set(copyVal)
                self.moveItemsOnCurve(
                    copyVal, (self.cellCoords(i), self.cellCenter(i)),
                    sleepTime=0.02)
                self.canvas.delete(self.list[i].display_shape)
                self.canvas.delete(self.list[i].display_val)
                self.list[i].val = self.list[maxi].val # then move max child up
                self.list[i].color = self.list[maxi].color
                self.list[i].display_shape, self.list[i].display_val = copyVal
                callEnviron -= set(copyVal)    # retain copied value
                
                # Advance i to child, move original item along with i Index
                delta = self.cellCenter(maxi)[1] - self.cellCenter(i)[1]
                self.moveItemsBy(iIndex + copyItem, (0, delta), sleepTime=0.01)
                i = maxi
                 
            else:              # If item i's key is greater than or equal
                break           # to larger child, then found position

        # Move copied item into appropriate location
        self.moveItemsBy(copyItem, multiply_vector(itemDelta, -1),
                         sleepTime=0.01)
        self.canvas.delete(self.list[i].display_shape)
        self.canvas.delete(self.list[i].display_val)
        self.list[i].val, self.list[i].color = item.val, item.color
        self.list[i].display_shape, self.list[i].display_val = copyItem

        callEnviron -= set(copyItem)
        self.cleanUp(callEnviron)        

    def heapify(self, N = None):  # Organize an array of N items to satisfy the heap condition using keys extracted from the items by the key function
        callEnviron = self.createCallEnvironment()
        if N is None:            # If N is not supplied,
            N = len(self.list)   # then use number of items in list
        heapLo = N // 2          # The heap lies in the range [heapLo, N)
        while heapLo > 0:        # Heapify until the entire array is a heap
            heapLo -= 1           # Decrement heap's lower boundary
            self.siftDown(heapLo) # Sift down item at heapLo

        self.cleanUp(callEnviron)
              
    # lets user input an int argument that determines max size of the Heap
    def newArray(self):
        #gets rid of old elements in the list
        del self.list[:]
        self.size = 2
        self.display()
    

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
        newFont = (self.VALUE_FONT[0], int(self.VALUE_FONT[1] * .75))
        self.canvas.itemconfig(valueOutput, font=newFont)

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
        self.moveItemsBy(items, delta=(0, -self.canvas.coords(n.display_shape)[3]), steps=self.CELL_HEIGHT,
                        sleepTime=.05)
        self.canvas.delete(items)

        if self.size < 1:
            self.setMessage("Heap requirement satisfied")

        # move bottom cell to top, and heapify
        else:
            self.swapRoot()
            self.siftDown()
        
        # Finish animation
        self.cleanUp(callEnviron)
    
    def swapRoot(self):
        self.startAnimations()
        callEnviron = self.createCallEnvironment()
        n = self.list[-1]
        items = (n.display_shape, n.display_val)

        # move the last cell to the front of the heap
        cellCoords = self.cellCoords(0)
        cellCenter = self.cellCenter(0)
        toPositions = (cellCoords, cellCenter)
        # self.moveItemsOffCanvas(items, N, sleepTime=0.02) ## alternative method to moveItemsBy
        self.moveItemsTo(items, toPositions)
        self.list[0] = n
        # delete the last element from the list
        del self.list[-1]
        
        # finish the animation
        self.cleanUp(callEnviron)
        
    
    def randomFill(self, val):
        callEnviron = self.createCallEnvironment()
        self.startAnimations()

        self.size = val
        del self.list[:]
        self.display()
        
        for i in range(val):
            num = random.randrange(99)
            self.list.append(drawable(num))

        self.display()
            

        # finish the animation
        self.cleanUp(callEnviron)
        
    def cellCoords(self, cell_index):  # Get bounding rectangle for array cell
        return (self.HEAP_X0, 
                self.HEAP_Y0 + self.CELL_HEIGHT * cell_index,
                self.HEAP_X0 + self.CELL_WIDTH - self.CELL_BORDER,
                self.HEAP_Y0 + self.CELL_HEIGHT * (cell_index + 1) - self.CELL_BORDER) 

    def cellCenter(self, index):  # Center point for array cell at index
        half_cell_x = (self.CELL_WIDTH - self.CELL_BORDER) // 2
        half_cell_y = (self.CELL_HEIGHT - self.CELL_BORDER) // 2
        return add_vector(self.cellCoords(index), (half_cell_x, half_cell_y))

    def arrayCellCoords(self, index):
        cell_coords = self.cellCoords(index)
        half_border = self.CELL_BORDER // 2
        other_half = self.CELL_BORDER - half_border
        return add_vector(cell_coords,
                          (-half_border, -half_border, other_half, other_half))
        
    def createArrayCell(self, index):  # Create a box representing an array cell
        rect = self.canvas.create_rectangle(
            self.arrayCellCoords(index), fill=None, tags= "arrayCell",
            outline=self.CELL_BORDER_COLOR, width=self.CELL_BORDER)
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

        #make a new arrow pointing to the top of the Heap
        self.nItemsIndex = self.createIndex(len(self.list))

        # go through each Drawable in the list
        for i, n in enumerate(self.list):
            # create display objects for the associated Drawables
            n.display_shape, n.display_val = self.createCellValue(
                i, n.val, n.color)
            n.color = self.canvas.itemconfigure(n.display_shape, 'fill')[-1]

    def fixPositions(self):  # Move canvas display items to exact cell coords
        for i, drawItem in enumerate(self.list):
            self.canvas.coords(drawItem.display_shape, *self.cellCoords(i))
            self.canvas.coords(drawItem.display_val, *self.cellCenter(i))
            
        # Restore array cell borders in case they were moved
        for i, item in enumerate(self.canvas.find_withtag('arrayCell')):
            if i >= self.size: # Delete any extra cell borders
                self.canvas.delete(item)
            else:
                self.canvas.coords(item, *self.arrayCellCoords(i))
            
        # Move nItems index to one past end of array
        y = self.cellCenter(len(self.list))[1]
        # Use x coord from nItemsIndex but y value from target location
        for item in self.nItemsIndex:
            coords = [y if i % 2 == 1 else c
                      for i, c in enumerate(self.canvas.coords(item))]
            self.canvas.coords(item, *coords)

    def cleanUp(self, *args, **kwargs): # Customize clean up for sorting
        super().cleanUp(*args, **kwargs) # Do the VisualizationApp clean up
        if ((len(args) == 0 or args[0] is None) and # When cleaning up entire 
            kwargs.get('callEnviron', None) is None): # call stack,
            self.fixPositions()       # restore positions of all structures

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
        self.addAnimationButtons()
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
            if len(self.list) >= self.MAX_SIZE:
                self.setMessage("Error! Heap is already full.")
            else:
                self.insert(val)
                self.setMessage("Value {} inserted".format(val))
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


    def clickRandomFill(self):
        # if the animation is not stopped (it is running or paused):
        if self.animationState != self.STOPPED:
            # error message appears and insert will not take place
            self.setMessage("Unable to insert at the moment")
        else:
            val = self.validArgument()
            if val is None:
                self.setMessage("Input value must be an integer from 1 to {}.".format(self.MAX_SIZE))
            elif self.window.winfo_height() <= self.HEAP_Y0 + (
                    val * self.CELL_HEIGHT):
                self.setMessage("Error! No room to display")
            elif 0 < val < 32:
                self.randomFill(val)


    def clickHeapify(self):
        self.heapify()


if __name__ == '__main__':
    # random.seed(3.14159)    # Use fixed seed for testing consistency
    HEAP = Heap()
    HEAP.runVisualization()
