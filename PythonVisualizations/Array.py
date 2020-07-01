import random
from tkinter import *

try:
    from drawable import *
    from VisualizationApp import *
except ModuleNotFoundError:
    from .drawable import *
    from .VisualizationApp import *


class Array(VisualizationApp):
    CELL_SIZE = 50
    CELL_BORDER = 2
    CELL_BORDER_COLOR = 'black'
    ARRAY_X0 = 100
    ARRAY_Y0 = 100
    FOUND_COLOR = 'brown4'
    nextColor = 0

    def __init__(self, size=10, title="Array", **kwargs):
        super().__init__(title=title, **kwargs)
        self.size = size
        self.title = title
        self.list = []
        self.buttons = self.makeButtons()

        # Fill in initial array values with random integers
        # The display items representing these array cells are created later
        for i in range(size - 1):
            self.list.append(drawable(random.randrange(90)))
        self.display()

    def __str__(self):
        return str(self.list)

    # ARRAY FUNCTIONALITY

    def createIndex(  # Create an index arrow to point at an indexed
            self, index,  # cell
            name=None,  # with an optional name label
            level=1,  # at a particular level away from the cells
            color=None):  # (negative are below)
        if not color: color = self.VARIABLE_COLOR

        cell_coords = self.cellCoords(index)
        cell_center = self.cellCenter(index)
        level_spacing = self.VARIABLE_FONT[1]
        x = cell_center[0]
        if level > 0:
            y0 = cell_coords[1] - self.CELL_SIZE * 3 // 5 - level * level_spacing
            y1 = cell_coords[1] - self.CELL_SIZE * 3 // 10
        else:
            y0 = cell_coords[3] + self.CELL_SIZE * 3 // 5 - level * level_spacing
            y1 = cell_coords[3] + self.CELL_SIZE * 3 // 10
        arrow = self.canvas.create_line(
            x, y0, x, y1, arrow="last", fill=color)
        if name:
            label = self.canvas.create_text(
                x + 2, y0, text=name, anchor=SW if level > 0 else NW,
                font=self.VARIABLE_FONT, fill=color)
        return (arrow, label) if name else (arrow,)

    def insert(self, val):
        callEnviron = self.createCallEnvironment()
        self.startAnimations()

        # draw an index pointing to the last item in the list
        indexDisplay = self.createIndex(len(self.list)-1, "nItems", level = -1, color = 'black')
        callEnviron |= set(indexDisplay)

        # create new cell and cell value display objects
        toPositions = (self.cellCoords(len(self.list)),
                       self.cellCenter(len(self.list)))

        # Animate arrival of new value from operations panel area
        canvasDimensions = self.widgetDimensions(self.canvas)
        startPosition = add_vector(
            [canvasDimensions[0]//2 - self.CELL_SIZE, canvasDimensions[1]] * 2,
            (0, 0) + (self.CELL_SIZE - self.CELL_BORDER,) * 2)
        cellPair = self.createCellValue(startPosition, val)
        callEnviron |= set(cellPair)
        self.moveItemsTo(cellPair, toPositions, steps=self.CELL_SIZE, sleepTime=0.01)

        # add a new Drawable with the new value, color, and display objects
        self.list.append(drawable(
            val, self.canvas.itemconfigure(cellPair[0], 'fill'), *cellPair))
        callEnviron ^= set(cellPair) # Remove new cell from temp call environ

        # move nItems pointer 
        self.moveItemsBy(indexDisplay, (self.CELL_SIZE, 0))
        self.cleanUp(callEnviron)

    def removeFromEnd(self):
        callEnviron = self.createCallEnvironment()
        
        #draw an index pointing to the last item in the list 
        indexDisplay = self.createIndex(len(self.list)-1, 'nItems', level = -1, color = 'black')
        callEnviron |= set(indexDisplay)         
        
        # pop a Drawable from the list
        if len(self.list) == 0:
            self.setMessage('Array is empty!')
            return
        self.startAnimations() 
        n = self.list.pop()  

        # delete the associated display objects
        self.canvas.delete(n.display_shape)
        self.canvas.delete(n.display_val)
        # advance index for next insert
        self.moveItemsBy(indexDisplay, (-self.CELL_SIZE, 0))              

        # update window
        self.window.update()
        self.cleanUp(callEnviron)

    def assignElement(
            self, fromIndex, toIndex, callEnviron,
            steps=CELL_SIZE // 2, sleepTime=0.01):
        fromDrawable = self.list[fromIndex]

        # get positions of "to" cell in array
        toPositions = (self.cellCoords(toIndex), self.cellCenter(toIndex))

        # create new display objects as copies of the "from" cell and value
        newCell = self.copyCanvasItem(fromDrawable.display_shape)
        newCellVal = self.copyCanvasItem(fromDrawable.display_val)
        callEnviron |= set([newCell, newCellVal])

        # Move copies to the desired location
        self.moveItemsTo((newCell, newCellVal), toPositions, steps=steps,
                         sleepTime=sleepTime)

        # delete the original "to" display value and the new display shape
        self.canvas.delete(self.list[toIndex].display_val)
        self.canvas.delete(self.list[toIndex].display_shape)

        # update value and display value in "to" position in the list
        self.list[toIndex].display_val = newCellVal
        self.list[toIndex].val = self.list[fromIndex].val
        self.list[toIndex].display_shape = newCell
        self.list[toIndex].color = self.list[fromIndex].color
        callEnviron ^= set([newCell, newCellVal])

        # update the window
        self.window.update()

    def cellCoords(self, cell_index):  # Get bounding rectangle for array cell
        return (self.ARRAY_X0 + self.CELL_SIZE * cell_index, self.ARRAY_Y0,  # at index
                self.ARRAY_X0 + self.CELL_SIZE * (cell_index + 1) - self.CELL_BORDER,
                self.ARRAY_Y0 + self.CELL_SIZE - self.CELL_BORDER)

    def cellCenter(self, index):  # Center point for array cell at index
        half_cell = (self.CELL_SIZE - self.CELL_BORDER) // 2
        return add_vector(self.cellCoords(index), (half_cell, half_cell))

    def createArrayCell(self, index):  # Create a box representing an array cell
        cell_coords = self.cellCoords(index)
        half_border = self.CELL_BORDER // 2
        rect = self.canvas.create_rectangle(
            *add_vector(cell_coords,
                        (-half_border, -half_border,
                         self.CELL_BORDER - half_border, self.CELL_BORDER - half_border)),
            fill=None, outline=self.CELL_BORDER_COLOR, width=self.CELL_BORDER)
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
            color = drawable.palette[Array.nextColor]
            Array.nextColor = (Array.nextColor + 1) % len(drawable.palette)

        cell_rect = self.canvas.create_rectangle(
            *rectPos, fill=color, outline='', width=0)
        cell_val = self.canvas.create_text(
            *valPos, text=str(key), font=self.VALUE_FONT, fill=self.VALUE_COLOR)
        handler = lambda e: self.setArgument(str(key))
        for item in (cell_rect, cell_val):
            self.canvas.tag_bind(item, '<Button>', handler)

        return cell_rect, cell_val

    def display(self):
        callEnviron = self.createCallEnvironment()
        self.canvas.delete("all")

        for i in range(self.size):  # Draw grid of cells
            self.createArrayCell(i)
            
        # draw an index pointing to the last item in the list
        indexDisplay = self.createIndex(len(self.list)-1, "nItems", level = -1, color = 'black')
        callEnviron |= set(indexDisplay)        

        # go through each Drawable in the list
        for i, n in enumerate(self.list):
            # create display objects for the associated Drawables
            n.display_shape, n.display_val = self.createCellValue(
                i, n.val, n.color)
            n.color = self.canvas.itemconfigure(n.display_shape, 'fill')    
        
        self.window.update()
        self.cleanUp(callEnviron)

    def find(self, val):
        callEnviron = self.createCallEnvironment()
        self.startAnimations()
        
        # draw an index pointing to the last item in the list
        indexDisplay = self.createIndex(len(self.list)-1, 'nItems', level = -1, color = 'black')
        callEnviron |= set(indexDisplay)        

        # draw an index for variable j pointing to the first cell
        indexDisplay = self.createIndex(0, 'j')
        callEnviron |= set(indexDisplay)

        # go through each Drawable in the list
        for i in range(len(self.list)):
            self.window.update()

            n = self.list[i]

            # Pause for comparison
            self.wait(0.2)
            
            # if the value is found
            if n.val == val:
                # get the position of the displayed cell
                posShape = self.canvas.coords(n.display_shape)

                # Highlight the found element with a circle
                callEnviron.add(self.canvas.create_oval(
                    *add_vector(
                        posShape,
                        multiply_vector((1, 1, -1, -1), self.CELL_BORDER)),
                    outline=self.FOUND_COLOR))
                self.wait(0.2)
                
                self.cleanUp(callEnviron)
                return i

            # if not found, then move the index over one cell
            self.moveItemsBy(indexDisplay, (self.CELL_SIZE, 0), sleepTime=0.01)

        self.cleanUp(callEnviron)
        return None

    def remove(self, val):
        callEnviron = self.createCallEnvironment()
        self.startAnimations()
        
        # draw an index pointing to the last item in the list
        indexDisplay = self.createIndex(len(self.list)-1, 'nItems',level = -1, color = 'black')
        callEnviron |= set(indexDisplay)         
        
        index = self.find(val)
        found = index != None    # Record if value was found
        if found:
            self.wait(0.3)

            n = self.list[index]         

            # Slide value rectangle up and off screen
            items = (n.display_shape, n.display_val)
            self.moveItemsOffCanvas(items, N, sleepTime=0.02)

            # Create an index for shifting the cells
            kIndex = self.createIndex(index, 'k')
            callEnviron |= set(kIndex)
            
            # Slide values from right to left to fill gap
            for i in range(index+1, len(self.list)):
                self.assignElement(i, i - 1, callEnviron)
                self.moveItemsBy(kIndex, (self.CELL_SIZE, 0), sleepTime=0.01)
            self.moveItemsBy(indexDisplay, (-self.CELL_SIZE, 0), sleepTime=0.01)

            # delete the last cell from the list and as a drawable 
            n = self.list.pop()  
            self.canvas.delete(n.display_shape)
            self.canvas.delete(n.display_val)
            
        self.cleanUp(callEnviron)
        return found
        
    def fixCells(self):       # Move canvas display items to exact cell coords
        for i, drawItem in enumerate(self.list):
            self.canvas.coords(drawItem.display_shape, *self.cellCoords(i))
            self.canvas.coords(drawItem.display_val, *self.cellCenter(i))
        self.window.update()

    def cleanUp(self, *args, **kwargs): # Customize clean up for sorting
        super().cleanUp(*args, **kwargs) # Do the VisualizationApp clean up
        self.fixCells()       # Restore cells to their coordinates in array

    def traverse(self):
        callEnviron = self.createCallEnvironment()
        self.startAnimations()
        
        #draw an index pointing to the last item in the list 
        indexDisplay = self.createIndex(len(self.list)-1, 'nItems', level = -1, color = 'black')
        callEnviron |= set(indexDisplay) 
        
        # draw an index pointing to the first cell
        indexDisplay = self.createIndex(0, 'j')
        callEnviron |= set(indexDisplay)

        # draw output box
        canvasDimensions = self.widgetDimensions(self.canvas)
        spacing = self.CELL_SIZE * 3 // 4
        padding = 10
        outputBox = self.canvas.create_rectangle(
            (canvasDimensions[0] - len(self.list) * spacing - padding) // 2,
            canvasDimensions[1] - self.CELL_SIZE - padding,
            (canvasDimensions[0] + len(self.list) * spacing + padding) // 2,
            canvasDimensions[1] - padding,
            fill = self.OPERATIONS_BG)
        callEnviron.add(outputBox)

        for j in range(len(self.list)):
            # calculate where the value will need to move to
            outputBoxCoords = self.canvas.coords(outputBox)
            midOutputBox = (outputBoxCoords[3] + outputBoxCoords[1]) // 2

            # create the value to move to output box
            valueOutput = self.copyCanvasItem(self.list[j].display_val)
            valueList = (valueOutput,)
            callEnviron.add(valueOutput)

            # move value to output box
            toPositions = (outputBoxCoords[0] + padding/2 + (j + 1/2)*spacing, 
                           midOutputBox)
            self.moveItemsTo(valueList, (toPositions,), sleepTime=.02)

            # make the value 25% smaller
            newSize = (self.VALUE_FONT[0], int(self.VALUE_FONT[1] * .75))
            self.canvas.itemconfig(valueOutput, font=newSize)
            self.window.update()

            # wait and then move the index pointer over
            self.wait(0.2)
            self.moveItemsBy(indexDisplay, (self.CELL_SIZE, 0), sleepTime=0.03)

        self.cleanUp(callEnviron)

    def makeButtons(self):
        vcmd = (self.window.register(numericValidate),
                '%d', '%i', '%P', '%s', '%S', '%v', '%V', '%W')
        traverseButton = self.addOperation(
            "Traverse", lambda: self.traverse())
        findButton = self.addOperation(
            "Find", lambda: self.clickFind(), numArguments=1,
            validationCmd=vcmd)
        insertButton = self.addOperation(
            "Insert", lambda: self.clickInsert(), numArguments=1,
            validationCmd=vcmd)
        deleteValueButton = self.addOperation(
            "Delete", lambda: self.clickDelete(), numArguments=1,
            validationCmd=vcmd)
        deleteRightmostButton = self.addOperation(
            "Delete Rightmost", lambda: self.removeFromEnd())
        #this makes the pause, play and stop buttons 
        self.addAnimationButtons()
        return [findButton, insertButton, deleteValueButton,
                deleteRightmostButton, traverseButton]

    def validArgument(self):
        entered_text = self.getArgument()
        if entered_text and entered_text.isdigit():
            val = int(entered_text)
            if val < 100:
                return val

    # Button functions
    def clickFind(self):
        val = self.validArgument()
        if val is None:
            self.setMessage("Input value must be an integer from 0 to 99.")
        else:
            result = self.find(val)
            if result != None:
                msg = "Found {}!".format(val)
            else:
                msg = "Value {} not found".format(val)
            self.setMessage(msg)
        self.clearArgument()

    def clickInsert(self):
        val = self.validArgument()
        if val is None:
            self.setMessage("Input value must be an integer from 0 to 99.")
        else:
            if len(self.list) >= self.size:
                self.setMessage("Error! Array is already full.")
            else:
                self.insert(val)
                self.setMessage("Value {} inserted".format(val))
        self.clearArgument()

    def clickDelete(self):
        val = self.validArgument()
        if val is None:
            self.setMessage("Input value must be an integer from 0 to 99.")
        else:
            result = self.remove(val)
            if result:
                msg = "Value {} deleted!".format(val)
            else:
                msg = "Value {} not found".format(val)
            self.setMessage(msg)
        self.clearArgument()

if __name__ == '__main__':
    random.seed(3.14159)  # Use fixed seed for testing consistency
    array = Array()

    array.runVisualization()
