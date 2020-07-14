import time
from tkinter import *

try:
    from drawable import *
    from VisualizationApp import *
except ModuleNotFoundError:
    from .drawable import *
    from .VisualizationApp import *

class Stack(VisualizationApp):
    nextColor = 0
    MAX_ARG_WIDTH = 8
    MAX_SIZE = 8
    CELL_WIDTH = 20 * MAX_ARG_WIDTH
    CELL_HEIGHT = 40
    CELL_BORDER = 2
    CELL_BORDER_COLOR = 'black'
    STACK_X0 = 300
    STACK_Y0 = 350

    def __init__(self, size=MAX_SIZE, maxArgWidth=MAX_ARG_WIDTH, title="Stack", **kwargs):
        super().__init__(title=title, maxArgWidth=maxArgWidth, **kwargs)
        self.size = size
        self.title = title
        self.list = []
        self.maxArgWidth = maxArgWidth
        self.buttons = self.makeButtons()
        self.display()
        self.indexDisplay = self.createIndex(len(self.list)-1)

    def __str__(self):
        return str(self.list)

    # Create an index arrow to point at an indexed cell with an optional name label
    def createIndex(self, index, name=None):
        cell_coords = self.cellCoords(index)
        cell_center = self.cellCenter(index)
        x0 = self.STACK_X0 - self.CELL_WIDTH * 4 // 5
        x1 = self.STACK_X0 - self.CELL_WIDTH * 3 // 10
        y0 = y1 = cell_coords[1] + self.CELL_HEIGHT // 2
        if not name:
            label = "top" #labels the top of the stack "top" with the pointer arrow
        else:
            label = name

        return self.drawArrow(
            x0, y0, x1, y1, self.VARIABLE_COLOR, self.VARIABLE_FONT, name=label)

    # draw the actual arrow
    def drawArrow(
            self, x0, y0, x1, y1, color, font, name=None):
        arrow = self.canvas.create_line(
            x0, y0, x1, y1, arrow="last", fill=color)
        if name:
            label = self.canvas.create_text(
                x0 - self.CELL_WIDTH / 2, y0 + self.CELL_HEIGHT / 5, text=name, anchor=SW,
                font=font, fill=color)

        return (arrow, label) if name else (arrow,)

    # STACK FUNCTIONALITY

    def push(self, val):

        self.startAnimations()
        callEnviron = self.createCallEnvironment()

        #move arrow up when new cell is inserted
        self.moveItemsBy(self.indexDisplay, (0, - (self.CELL_HEIGHT)))

        cellCoords = self.cellCoords(len(self.list))
        cellCenter = self.cellCenter(len(self.list))

        # create new cell and cell value display objects
        cellCoords = add_vector(cellCoords, (0, 0, 0, self.CELL_BORDER))
        toPositions = (cellCoords, cellCenter)

        # determine the top left and bottom right positions
        startPosition = [self.STACK_X0, 0, self.STACK_X0, 0]
        startPosition = add_vector(startPosition, (0, 0, self.CELL_WIDTH, self.CELL_HEIGHT))
        cellPair = self.createCellValue(startPosition, val)
        callEnviron |= set(cellPair)
        self.moveItemsTo(cellPair, toPositions, steps=self.CELL_HEIGHT, sleepTime=0.01)

        # add a new Drawable with the new value, color, and display objects
        d = drawable(
            val, self.canvas.itemconfigure(cellPair[0], 'fill')[-1], *cellPair)
        self.list.append(d)
        callEnviron ^= set(cellPair)

        # finish the animation
        self.cleanUp(callEnviron)

    def pop(self):

        # pop a Drawable from the list
        if len(self.list) == 0:
            return

        self.startAnimations()
        callEnviron = self.createCallEnvironment()
        n = self.list.pop()

        # delete the associated display objects
        items = (n.display_shape, n.display_val)
        callEnviron |= set(items)

        # self.moveItemsOffCanvas(items, N, sleepTime=0.02) ## alternative method to moveItemsBy
        self.moveItemsBy(items, delta=(0, -max(400, self.canvas.coords(n.display_shape)[3])), steps=self.CELL_HEIGHT, sleepTime=.01)

        # draw an index pointing to the last cell
        self.moveItemsBy(self.indexDisplay, (0, (self.CELL_HEIGHT)))

        # Finish animation
        self.cleanUp(callEnviron)

        return n.val  # returns value displayed in the cell

    # displays the top val of the stack in a small cell on the bottom right of the window
    def peek(self):
        callEnviron = self.createCallEnvironment()
        self.startAnimations()

        # draw output box
        outputBox = self.canvas.create_rectangle(
            self.STACK_X0 + self.CELL_WIDTH * 1.5,
            self.STACK_Y0,
            self.STACK_X0 + self.CELL_WIDTH * 2.5,
            self.STACK_Y0 - self.CELL_HEIGHT,
            fill=self.OPERATIONS_BG)
        callEnviron.add(outputBox)

        pos = len(self.list) - 1

        # calculate where the value will need to move to
        outputBoxCoords = self.canvas.coords(outputBox)
        midOutputBoxY = (outputBoxCoords[3] + outputBoxCoords[1]) // 2
        midOutputBoxX = (outputBoxCoords[0] + outputBoxCoords[2]) // 2

        # create the value to move to output box
        valueOutput = self.copyCanvasItem(self.list[pos].display_val)
        valueList = (valueOutput,)
        callEnviron.add(valueOutput)

        # move value to output box
        toPositions = (midOutputBoxX, midOutputBoxY)
        self.moveItemsTo(valueList, (toPositions,), sleepTime=.02)

        # make the value 25% smaller
        newSize = (self.VALUE_FONT[0], int(self.VALUE_FONT[1] * .75))
        self.canvas.itemconfig(valueOutput, font=newSize)

        # Finish animation
        self.cleanUp(callEnviron)

    # lets user input an int argument that determines max size of the stack
    def newStack(self, size):
        #gets rid of old elements in the list
        del self.list[:]
        self.size = size
        self.display()

        #make a new arrow pointing to the top of the stack
        self.indexDisplay = self.createIndex(len(self.list)-1)

    def cellCoords(self, cell_index):  # Get bounding rectangle for array cell
        return (self.STACK_X0 + self.CELL_BORDER,
                (self.STACK_Y0 - self.CELL_HEIGHT * (cell_index + 1)) + self.CELL_BORDER,
                self.STACK_X0 + self.CELL_WIDTH - self.CELL_BORDER,
                self.STACK_Y0 - self.CELL_HEIGHT * cell_index - self.CELL_BORDER)

    def cellCenter(self, index):  # Center point for array cell at index
        half_cell_x = (self.CELL_WIDTH - self.CELL_BORDER) // 2
        half_cell_y = (self.CELL_HEIGHT - self.CELL_BORDER) // 2

        return add_vector(self.cellCoords(index), (half_cell_x, half_cell_y))

    def createArrayCell(self, index):  # Create a box representing an array cell
        cell_coords = self.cellCoords(index)
        half_border = self.CELL_BORDER // 2
        arrayCoords = add_vector(cell_coords,
                                 (-half_border, -half_border,
                                  self.CELL_BORDER - half_border, self.CELL_BORDER - half_border + 2))
        rect = self.canvas.create_rectangle(arrayCoords,
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
            color = drawable.palette[Stack.nextColor]
            Stack.nextColor = (Stack.nextColor + 1) % len(drawable.palette)
        cell_rect = self.canvas.create_rectangle(
            *rectPos, fill=color, outline='', width=0)
        cell_val = self.canvas.create_text(
            *valPos, text=str(key), font=self.VALUE_FONT, fill=self.VALUE_COLOR)
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
        pushButton = self.addOperation(
            "Push", lambda: self.clickPush(), numArguments=1)
        popButton = self.addOperation(
            "Pop", lambda: self.clickPop())
        peekButton = self.addOperation(
            "Peek", lambda: self.clickPeek())
        newStackButton = self.addOperation(
            "New", lambda: self.clickNewStack(), numArguments=1, validationCmd=vcmd)

        return [pushButton, popButton, peekButton, newStackButton]

    def validArgument(self):
        entered_text = self.getArgument()
        if entered_text:
            if len(entered_text) <= self.maxArgWidth:
                return entered_text
            else:
                self.setMessage("Error! {} value is too long".format(entered_text))

    # Button functions
    def clickPush(self):
        val = self.validArgument()
        if val is None:
            return
        else:
            if len(self.list) >= self.size:
                self.setMessage("Error! Stack is already full.")
            else:
                self.push(val)
                self.setMessage("Value {} pushed!".format(val))
        self.clearArgument()

    def clickPop(self):
        val = self.pop()
        if val is None:
            self.setMessage("Error! Stack is empty.")
        else:
            self.setMessage("Value {} popped!".format(val))

    def clickPeek(self):

        if len(self.list) <= 0:
            self.setMessage("Error! Stack is empty.")
        else:
            val = self.list[-1].val
            self.peek()
            self.setMessage("Value {} is at the top of the stack!".format(val))

    def clickNewStack(self):
        val = self.validArgument()
        if val is None:
            return
        if not val.isdigit():
            self.setMessage("New stack size must be a number")
            return
        val = int(val)
        if 1 > val or val > self.MAX_SIZE:
            self.setMessage("Error! Stack size must be an int between 1 and {}.".format(self.MAX_SIZE))

        else:
            self.newStack(val)
            self.setMessage("New stack created of size {}. ".format(val))
        self.clearArgument()

    def setButtonsStatus(self, state=NORMAL):
        for b in self.buttons:
            b['state'] = state


if __name__ == '__main__':
    # random.seed(3.14159)    # Use fixed seed for testing consistency
    stack = Stack()
    stack.runVisualization()

