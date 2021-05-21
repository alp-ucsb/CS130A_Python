from tkinter import *
import re, math
try:
    from drawnValue import *
    from HashTableOpenAddressing import *
except ModuleNotFoundError:
    from .drawnValue import *
    from .HashTableOpenAddressing import *

# Regular expression for max load factor
maxLoadFactorPattern = re.compile(r'[01](\.\d*)?')

class HashTableChaining(HashTableOpenAddressing):
    MIN_LOAD_FACTOR = 0.5
    MAX_LOAD_FACTOR = 2.0
    CELL_INDEX_COLOR = 'gray60'
    
    def __init__(self, title="Hash Table - Open Chaining", **kwargs):
        self.initialRect = (
            0, 0, kwargs.get('canvasWidth', self.DEFAULT_CANVAS_WIDTH),
            kwargs.get('canvasHeight', self.DEFAULT_CANVAS_HEIGHT))
        super().__init__(title=title, canvasBounds=self.initialRect, **kwargs)
        self.probeChoiceButtons = ()

    def newHashTable(self, nCells=2, maxLoadFactor=1.0):
        self.table = [None] * max(1, nCells)
        self.nItems = 0
        self.maxLoadFactor = maxLoadFactor
        self.display()
        
    insertCode = '''
def insert(self, key={key}, value):
   i = self.hash(key)
   flag = self.insert(self.__table[i], key, value)
   if flag:
      self.__nItems += 1
      if self.loadFactor() > self.__maxLoadFactor:
         self.__growTable()
   return flag
'''
    
    def insert(self, key, nodeItems=None, inputText=None,
               code=insertCode, start=True):
        '''Insert a user provided key or the link node items from the old table
        during growTable.  Animate operation if code is provided,
        starting in the specified animation mode.  The inputText can
        be a text item that is moved into the input of the hasher.  It
        will be deleted and replaced by the hashed address for hashing
        animation.
        '''
        wait = 0.1 if code else 0
        callEnviron = self.createCallEnvironment(
            code=code.format(**locals()) if code else '',
            startAnimations=code and start)

        if code:
            self.highlightCode('i = self.hash(key)', callEnviron)
        addressCharsAndArrow, i = self.hashAndGetIndex(
            key, animate=code and self.showHashing.get(), sleepTime=wait / 10,
            textItem=inputText)
        callEnviron |= set(addressCharsAndArrow)
        localVars = set(addressCharsAndArrow)

        if code:
            iArrow = self.createArrayIndex(i, 'i')
            callEnviron |= set(iArrow)
            localVars |= set(iArrow)
            self.dispose(callEnviron, addressCharsAndArrow[-1])
            localVars.discard(addressCharsAndArrow[-1])
            self.highlightCode(
                'flag = self.insert(self.__table[i], key, value)', callEnviron)

        flag = self.insertIntoList(i, key, nodeItems, callEnviron, wait)
        
        if code:
            outputBoxCoords = self.outputBoxCoords()
            gap = 4
            flagText = self.canvas.create_text(
                *(V(self.canvas.coords(self.nItemsText)) - 
                  V(0, self.VARIABLE_FONT[1])), anchor=SW,
                text='flag = {}'.format(flag), font=self.VARIABLE_FONT,
                fill=self.VARIABLE_COLOR)
            callEnviron.add(flagText)
            localVars.add(flagText)
            self.highlightCode(('flag', 2), callEnviron, wait=wait)

        if flag:
            if code:
                self.highlightCode('self.__nItems += 1', callEnviron, wait=wait)
            self.nItems += 1
            self.updateNItems()

            if code:
                self.highlightCode('self.loadFactor() > self.__maxLoadFactor',
                                   callEnviron, wait=wait)
                if self.loadFactor() > self.maxLoadFactor:
                    self.highlightCode('self.__growTable()', callEnviron)
                    colors = self.fadeNonLocalItems(localVars)

            if self.loadFactor() > self.maxLoadFactor:
                self.__growTable(code=self._growTableCode if code else '')
                if code:
                    self.restoreLocalItems(localVars, colors)

        if code:
            self.highlightCode('return flag', callEnviron)
        self.cleanUp(callEnviron)
        return flag

    def insertIntoList(self, cell, key, nodeItems, callEnviron, wait):
        linkedList = self.table[cell].val if self.table[cell] else []
        listIndex = 0
        while listIndex < len(linkedList):
            if linkedList[listIndex].val == key:
                break
            listIndex += 1
        updateExisting = listIndex < len(linkedList)
        linkCoords = ([self.canvas.coords(item) 
                       for item in linkedList[listIndex].items]
                      if updateExisting else 
                      self.findSpaceForLink(cell, key=key))
        newItems = nodeItems or self.createLinkItems(
            self.newItemCoords()[:2] if wait else linkCoords, key)
        callEnviron |= set(newItems)
        if wait:
            linkIndex = self.createLinkIndex(cell)
            callEnviron |= set(linkIndex)
            for j in range(listIndex):
                self.moveItemsTo(linkIndex, self.linkIndexCoords(linkedList[j]),
                                 sleepTime=wait / 10)
                self.wait(wait / 2)
            self.moveItemsTo(linkIndex, self.linkIndexCoords(linkCoords),
                             sleepTime=wait / 10)
            if updateExisting:
                self.canvas.tag_lower(
                    newItems[0], linkedList[listIndex].items[1])
                self.moveItemsTo(newItems[0], linkCoords[0],
                                 sleepTime=wait / 10)
            else:
                self.moveItemsLinearly(
                    newItems, linkCoords, sleepTime=wait / 10)
        else:
            if not updateExisting:
                for item, coords in zip(newItems, linkCoords):
                    self.canvas.coords(item, coords)
                self.expandCanvasFor(*newItems)
                
        if updateExisting:
            self.copyItemAttributes(newItems[0], linkedList[listIndex].items[0],
                                    'fill')
            self.dispose(callEnviron, *newitems)
        else:
            linkedList.append(drawnValue(key, *newItems))
            if self.table[cell] is None:
                self.table[cell] = drawnValue(
                    linkedList, *self.createInitialLink(cell, linkedList[0]))
            else:
                self.table[cell].val = linkedList
                self.linkNodes(linkedList[-2], linkedList[-1])
            callEnviron -= set(newItems)
        if wait:
            self.dispose(callEnviron, *linkIndex)
        return not updateExisting

    def findSpaceForLink(self, cell, key=' '):
        cellCoords = self.cellCenter(cell)
        linkCoords = self.newLinkCoords(key=key)
        rowGap = self.linkHeight * 5 // 2
        widthNeeded = linkCoords[2][2] - linkCoords[2][0]
        pad = self.linkHeight
        bboxes = [self.canvas.bbox(n.items[2])
                  for d in self.table if d for n in d.val]
        y0 = self.array_y0 + self.cellHeight
        used = []
        for bbox in bboxes:
            level = (bbox[1] + 5 - y0) // rowGap
            while level >= len(used):
                used.append([])
            used[level].append((bbox[0], bbox[2]))
        level = 1 if self.table[cell] is None else (
            (self.canvas.bbox(self.table[cell].val[-1].items[2])[1] + 1 - y0) //
            rowGap) + 1
        bounds = ()
        x = cellCoords[0]
        while level < len(used) and used[level]:
            used[level].sort()
            blocks = used[level]
            j = 0
            while j < len(blocks) and blocks[j][0] < x:
                j += 1
            # blocks[j - 1][0] < x <= blocks[j][0]
            if j >= len(blocks) and blocks[j - 1][1] < x:
                bounds = (blocks[j - 1][1], math.inf)
                break
            if j > 0:
                if (x <= blocks[j - 1][1] or
                    blocks[j][0] - blocks[j - 1][1] < widthNeeded + 2 * pad):
                    level += 1
                else:
                    bounds = (blocks[j - 1][1], blocks[j][0])
                    break
            else:
                bounds = (-math.inf, blocks[j][0])
                break

        offset = self.linkHeight // 2
        y = y0 + level * rowGap
        x -= offset
        if bounds:
            x = max(bounds[0] + pad, min(bounds[1] - pad - widthNeeded, x))
        return self.linkCoords((x, y), key=key)
    
    _growTableCode = '''
def __growTable(self):
   oldTable = self.__table
   size = len(oldTable) * 2 + 1
   while not is_prime(size):
      size += 2
   self.__table = [None] * size
   self.__nItems = 0
   for i in range(len(oldTable)):
      if oldTable[i]:
         for item in oldTable[i].traverse():
             self.insert(*item)
 '''
    
    def __growTable(self, code=_growTableCode):
        wait = 0.1 if code else 0
        callEnviron = self.createCallEnvironment(code=code)
        
        localVars = set()
        oldTable = self.table
        oldTableColor = 'blue2'
        tagsToMove = ('arrayBox', 'cell', 'link', 'sizeLabel')
        if code:
            self.highlightCode('oldTable = self.__table', callEnviron)
            oldTableCells = self.arrayCells
            cell0 = self.canvas.coords(oldTableCells[0])
            delta = (self.cellWidth * 2 * (len(self.table) + 2),
                     2 * self.cellHeight)
            callEnviron.add(self.canvas.create_text(
                cell0[0] - self.cellWidth // 2 + delta[0],
                (cell0[1] + cell0[3]) // 2 + delta[1], anchor=E,
                text='oldTable', font=self.cellIndexFont, fill=oldTableColor))
            self.moveItemsBy(tagsToMove, delta, sleepTime=wait / 10)
            self.canvas_itemConfig('arrayBox', outline=oldTableColor)
            for tag in ('linkArrow', 'cellArrow'):
                self.canvas_itemConfig(tag, fill=oldTableColor)

        size = min(len(oldTable) * 2 + 1, self.MAX_CELLS)
        if code:
            self.highlightCode('size = len(oldTable) * 2 + 1', callEnviron,
                               wait=wait)
            sizeText = self.canvas.create_text(
                *(V(self.canvas.coords(self.nItemsText)) - 
                  V(0, self.VARIABLE_FONT[1])), anchor=SW,
                text='size = {}'.format(size), font=self.VARIABLE_FONT,
                fill=self.VARIABLE_COLOR)
            callEnviron.add(sizeText)
            localVars.add(sizeText)
            if len(oldTable) * 2 + 1 > size:
                self.setMessage('Reached maximum number of cells {}'.format(
                    self.MAX_CELLS))
                self.wait(5 * wait)
                
            self.highlightCode('not is_prime(size)', callEnviron, wait=wait)

        while not is_prime(size) and size < self.MAX_CELLS:
            size += 2
            if code:
                self.highlightCode('size += 2', callEnviron, wait=wait)
                self.canvas_itemConfig(sizeText, text='size = {}'.format(size))
                self.highlightCode('not is_prime(size)', callEnviron, wait=wait)

        if size == self.MAX_CELLS and len(oldTable) == self.MAX_CELLS:
            if code:
                self.moveItemsBy(tagsToMove, V(delta) * -1, sleepTime=0)
                self.canvas_itemConfig('arrayBox', outline='black')
            self.cleanUp(callEnviron)
            return
            
        if code:
            self.highlightCode('self.__table = [None] * size', callEnviron,
                               wait=wait)
        callEnviron |= set(
            self.arrayCells + list(flat(*(
                self.canvas.find_withtag(tag) for tag in ('sizeLabel', 'link')))))
        self.table = [None] * size
        self.arrayCells = [
            self.createArrayCell(j) for j in range(len(self.table))]
        self.arrayLabels += [
            self.createArrayIndexLabel(j) for j in range(len(oldTable), size)]
        self.createArraySizeLabel()
        self.nItems = 0
        if code:
            self.highlightCode('self.__nItems = 0', callEnviron, wait=wait)
        self.updateNItems()

        if code:
            self.highlightCode('i in range(len(oldTable))', callEnviron)
            iArrow, itemArrow = None, None
        for i in range(len(oldTable)):
            if code:
                if iArrow is None:
                    iArrow = self.createArrayIndex(
                        self.canvas.coords(oldTableCells[i]), 'i')
                    callEnviron |= set(iArrow)
                    localVars |= set(iArrow)
                else:
                    self.moveItemsTo(
                        iArrow, self.arrayIndexCoords(
                            self.canvas.coords(oldTableCells[i])),
                        sleepTime=wait / 10)
                self.highlightCode('oldTable[i]', callEnviron, wait=wait)

            if oldTable[i] and oldTable[i].val:
                keyCopy = None
                if code:
                    self.highlightCode('item in oldTable[i].traverse()',
                                       callEnviron, wait=wait)
                linkedList = oldTable[i].val
                self.dispose(callEnviron, *oldTable[i].items)
                for linkIndex in range(len(linkedList)):
                    if code:
                        if itemArrow is None:
                            itemArrow = self.createLinkIndex(
                                linkedList[linkIndex], 'item')
                            callEnviron |= set(itemArrow)
                            localVars |= set(itemArrow)
                        else:
                            self.moveItemsTo(itemArrow, self.linkIndexCoords(
                                linkedList[linkIndex]), sleepTime=wait / 10)
                            
                        self.highlightCode('self.insert(*item)',
                                           callEnviron)
                        if self.showHashing.get():
                            keyCopy = self.copyCanvasItem(
                                linkedList[linkIndex].items[1])
                            callEnviron.add(keyCopy)
                        colors = self.fadeNonLocalItems(localVars)
                    self.insert(
                        linkedList[linkIndex].val, 
                        nodeItems=linkedList[linkIndex].items,
                        inputText=keyCopy, code=self.insertCode if code else '')
                    callEnviron -= set(linkedList[linkIndex].items)
                    if code:
                        self.restoreLocalItems(localVars, colors)
                        self.highlightCode('item in oldTable[i].traverse()',
                                           callEnviron, wait=wait)
                if code:
                    self.dispose(callEnviron, *itemArrow)
                    localVars -= set(itemArrow)
                    itemArrow = None
            if code:
                self.highlightCode('i in range(len(oldTable))', callEnviron)
                    
        self.cleanUp(callEnviron)
        
    searchCode = '''
def search(self, key={key}):
   i = self.hash(key)
   return (None if self.__table[i] is None else
           self.__table[i].search(key))
'''
    
    def search(self, key, inputText=None, code=searchCode, start=True):
        wait = 0.1 if code else 0
        callEnviron = self.createCallEnvironment(
            code=code.format(**locals()) if code else '',
            startAnimations=code and start)

        pad = 5
        outBox = self.outputBoxCoords(nLines=2, pad=pad)
        outBox = (outBox[0], outBox[1], 
                  outBox[0] + self.linkWidth + 2 * pad, outBox[3])
        outBoxCenter = BBoxCenter(outBox)
        outputBox = self.createOutputBox(coords=outBox)
        callEnviron.add(outputBox)
        
        if code:
            self.highlightCode('i = self.hash(key)', callEnviron)
        addressCharsAndArrow, i = self.hashAndGetIndex(
            key, animate=code and self.showHashing.get(), sleepTime=wait / 10)
        callEnviron |= set(addressCharsAndArrow)
        localVars = set(addressCharsAndArrow)

        if code:
            iArrow = self.createArrayIndex(i, 'i')
            callEnviron |= set(iArrow)
            self.dispose(callEnviron, addressCharsAndArrow[-1])
            localVars.discard(addressCharsAndArrow[-1])
            self.highlightCode('self.__table[i] is None', callEnviron)

        if self.table[i] is None or len(self.table[i].val) == 0:
            if code:
                self.highlightCode(('return', 'None'), callEnviron)
            self.cleanUp(callEnviron)
            return None
        
        if code:
            self.highlightCode('self.__table[i].search(key)', callEnviron)
            
        linkedList = self.table[i].val
        itemArrow = self.createLinkIndex(i)
        callEnviron |= set(itemArrow)
        linkIndex = 0
        while linkIndex < len(linkedList):
            if code:
                self.moveItemsTo(itemArrow, self.linkIndexCoords(
                    linkedList[linkIndex]), sleepTime=wait / 10)
                self.wait(wait / 2)
            if linkedList[linkIndex].val == key:
                break
            linkIndex += 1

        found = linkIndex < len(linkedList)
        if found:
            items = [self.copyCanvasItem(item)
                     for item in linkedList[linkIndex].items[0:2]]
            callEnviron |= set(items)
            self.canvas.tag_lower(items[0])
            delta = V(BBoxCenter(outBox)) - V(self.canvas.coords(items[1])) 
            self.moveItemsBy(
                items, delta, sleepTime=wait / 10,
                startFont=self.getItemFont(items[1]), endFont=self.outputFont)
            self.copyItemAttributes(items[0], outputBox, 'fill')
            self.dispose(callEnviron, items[0])
        else:
            if itemArrow:
                self.moveItemsTo(itemArrow, self.linkIndexCoords(i),
                                 sleepTime=wait / 10)
                
        self.cleanUp(callEnviron)
        return self.table[i] if found else None
    
    deleteCode = '''
def delete(self, key={key}, ignoreMissing={ignoreMissing}):
   i = self.hash(key)
   if self.__table[i] is not None:
      if self.__table[i].delete(key):
         self.__nItems -= 1
         return True
   if ignoreMissing:
      return False
   raise Exception(
      'Hash table does not contain key {brackets} so cannot delete'
      .format(key))
'''
    
    def delete(self, key, ignoreMissing=False, code=deleteCode, start=True):
        wait = 0.1 if code else 0
        brackets = '{}'
        callEnviron = self.createCallEnvironment(
            code=code.format(**locals()) if code else '',
            startAnimations=code and start)
        
        if code:
            self.highlightCode('i = self.hash(key)', callEnviron)
        addressCharsAndArrow, i = self.hashAndGetIndex(
            key, animate=code and self.showHashing.get(), sleepTime=wait / 10)
        callEnviron |= set(addressCharsAndArrow)
        localVars = set(addressCharsAndArrow)

        if i is not None:
            iArrow = self.createArrayIndex(i, 'i')
            callEnviron |= set(iArrow)
            localVars |= set(iArrow)

        if code:
            self.highlightCode('self.__table[i] is not None', callEnviron,
                               wait=wait)
        colors = None
        if self.table[i] is not None:
            if code:
                self.highlightCode('self.__table[i].delete(key)', callEnviron)
                colors = self.fadeNonLocalItems(localVars)
            if self.deleteFromList(
                    key, i, callEnviron, animate=code, wait=wait):
                if code:
                    self.restoreLocalItems(localVars, colors)
                    self.highlightCode('self.__nItems -= 1', callEnviron,
                                       wait=wait)
                self.nItems -= 1
                self.updateNItems()
                if code:
                    self.highlightCode('return True', callEnviron)
                self.cleanUp(callEnviron)
                return True

        if code:
            if colors:
                self.restoreLocalItems(localVars, colors)
            self.highlightCode(('ignoreMissing', 2), callEnviron, wait=wait)
        if ignoreMissing:
            self.highlightCode('return False', callEnviron)
            self.cleanUp(callEnviron)
            return False


        if code:
            self.highlightCode(
                self.hashDeleteException, callEnviron, wait=wait,
                color=self.EXCEPTION_HIGHLIGHT)
        self.cleanUp(callEnviron)
        return

    def deleteFromList(
            self, key, cellIndex, callEnviron=None, animate=True, wait=0.1):
        if self.table[cellIndex] is None or len(self.table[cellIndex].val) == 0:
            return
        if callEnvrion is None: callEnviron = set()
        linkedList = self.table[cellIndex].val
        if animate:
            itemArrow = self.createLinkIndex(cellIndex)
            callEnviron |= set(itemArrow)
        linkIndex = 0
        while linkIndex < len(linkedList):
            if animate:
                self.moveItemsTo(itemArrow, self.linkIndexCoords(
                    linkedList[linkIndex]), sleepTime=wait / 10)
                self.wait(wait / 2)
            if linkedList[linkIndex].val == key:
                break
            linkIndex += 1

        found = linkIndex < len(linkedList)
        if found:
            if linkIndex == 0:
                self.dispose(callEnviron, *self.table[cellIndex].items)
                self.table[cellIndex].items = self.createInitialLink(
                    cellIndex,
                    linkedList[linkIndex + 1] if linkIndex + 1 < len(linkedList)
                    else None)
            else:
                self.linkNodes(
                    linkedList[linkIndex - 1],
                    linkedList[linkIndex + 1] if linkIndex + 1 < len(linkedList)
                    else None)
            self.dispose(callEnviron, *linkedList[linkIndex].items)
            linkedList[linkIndex:linkIndex + 1] = []
        else:
            if animate:
                self.moveItemsTo(itemArrow, self.linkIndexCoords(cellIndex),
                                 sleepTime=wait / 10)
        return found
        
    traverseCode = '''
def traverse(self):
   for i in range(len(self.__table)):
      if self.__table[i]:
         for item in self.__table[i].traverse():
            yield item
'''

    def traverse(self, code=traverseCode):
        wait = 0.1
        callEnviron = self.createCallEnvironment(code=code)

        self.highlightCode('i in range(len(self.__table)', callEnviron,
                           wait=wait)
        iArrayIndex, itemIndex = None, None
        for i in range(len(self.table)):
            if iArrayIndex is None:
                iArrayIndex = self.createArrayIndex(i, 'i')
                callEnviron |= set(iArrayIndex)
            else:
                self.moveItemsTo(iArrayIndex, self.arrayIndexCoords(i),
                                 sleepTime=wait / 10)

            self.highlightCode('self.__table[i]', callEnviron, wait=wait)
            if self.table[i]:
                self.highlightCode('item in self.__table[i].traverse()',
                                   callEnviron, wait=wait)
                for link in self.table[i].val:
                    if itemIndex is None:
                        itemIndex = self.createLinkIndex(link, 'item')
                        callEnviron |= set(itemIndex)
                    else:
                        self.moveItemsTo(itemIndex, self.linkIndexCoords(link),
                                         sleepTime=wait / 10)

                    self.highlightCode('yield item', callEnviron)
                    itemCoords = self.yieldCallEnvironment(
                        callEnviron, sleepTime=wait / 10)
                    yield i, link
                    self.resumeCallEnvironment(
                        callEnviron, itemCoords, sleepTime=wait / 10)
                    self.highlightCode('item in self.__table[i].traverse()',
                                       callEnviron, wait=wait)
        
        self.highlightCode([], callEnviron)
        self.cleanUp(callEnviron)
        
    def cellCoords(self, index):
        x0 = self.array_x0 + index * self.cellWidth
        y0 = self.array_y0
        return (x0, y0, 
                x0 + self.cellWidth - self.CELL_BORDER,
                y0 + self.cellHeight - self.CELL_BORDER)
    
    def arrayIndexCoords(self, indexOrCoords, level=1):
        'Coordinates of an index arrow and anchor of its text label'
        cell_coords = (
            self.cellCoords(indexOrCoords) if isinstance(indexOrCoords, int)
            else indexOrCoords)
        tip = ((cell_coords[0] + cell_coords[2]) // 2, 
               cell_coords[1] + self.cellIndexFont[1] * 3 // 2)
        base = V(tip) + V(0, level * self.VARIABLE_FONT[1])
        return (base + tip, base)

    def linkIndexCoords(self, linkOrCoords, level=1, orientation=-160):
        corner = (tuple(self.canvas.coords(linkOrCoords.items[2])[:2])
                  if isinstance(linkOrCoords, drawnValue) else
                  self.arrayCellCoords(linkOrCoords)[:2]
                  if isinstance(linkOrCoords, int) else
                  linkOrCoords[2][:2] if len(linkOrCoords) == 5 else
                  linkOrCoords)
        base = V(V(abs(self.VARIABLE_FONT[1]) * level, 0).rotate(
            orientation)) + V(corner)
        return base + corner, base
    
    def linkCoords(self, corner, nextLink=None, key=''):
        '''Coordinates for all the canvas items in a linked list Link:
        colored rectangle, text key, box outline, dot, arrow to next link
        When the next link is None, the arrow will have zero length.
        The nextLink can be a corner coordinate or a drawnValue for a link.
        '''
        vCorner = V(corner)
        rectAt = (vCorner + V(self.linkHeight, 0))
        width = (self.textWidth(self.VALUE_FONT, str(key) + '  ') 
                 if key else self.linkWidth)
        rectAt += V(rectAt) + V(width, self.linkHeight)
        keyAt = BBoxCenter(rectAt)
        boxAt =  (vCorner - V(1, 1)) + rectAt[2:]
        dot = (vCorner + V(self.linkHeight, self.linkHeight) // 2) * 2
        arrow = dot if nextLink is None else (
            dot[:2] + 
            (dot[0], nextLink[1] if isnstance(nextLink, (tuple, list)) else
             self.canvas.coords(nextLink.items[0])[1]))
        if nextLink is not None:
            dotRadius = (self.linkDotRadius, ) * 2
            dot = (V(dot[:2]) - V(dotRadius)) + (V(dot[:2]) + V(dotRadius))
        return rectAt, keyAt, boxAt, dot, arrow

    def newLinkCoords(self, key=''):
        delta = self.newValueCoords()
        return tuple(V(coords) + V(delta * (len(coords) // len(delta)))
                     for coords in self.linkCoords((0, 0), key=key))
    
    def outputBoxCoords(self, font=None, pad=4, nLines=4):
        '''Coordinates for an output box in upper right of canvas with enough
        space to hold several lines of text'''
        if font is None:
            font = getattr(self, 'outputFont', self.VALUE_FONT)
        lineHeight = self.textHeight(font, ' ')
        left = self.targetCanvasWidth * 4 // 10
        top = pad + abs(self.VARIABLE_FONT[1])
        return (left, top,
                self.targetCanvasWidth - pad, pad * 3 + lineHeight * nLines)

    def createLinkItems(self, cornerOrCoords, key, nextLink=None, color=None):
        '''Create all the canvas items in a linked list Link containing a key:
        colored rectangle, text key, box outline, dot, arrow to next link
        The upper left corner can be provided or a tuple of coordinates for
        each of the 5 items.
        When the next link is None, the arrow will have zero length.
        The nextLink can be a corner coordinate or a drawnValue for a link.
        '''
        coords = (self.linkCoords(cornerOrCoords, nextLink=nextLink, key=key)
                  if len(cornerOrCoords) == 2 else cornerOrCoords)
        if color is None:
            color = drawnValue.palette[self.nextColor]
            self.nextColor = (self.nextColor + 1) % len(drawnValue.palette)
        box = self.canvas.create_rectangle(
            *coords[2], fill=None, outline=self.linkBoxColor, width=1,
            tags=('link', 'linkBox'))
        rect = self.canvas.create_rectangle(
            *coords[0], fill=color, outline='', width=0,
            tags=('link', 'linkShape'))
        textKey = self.canvas.create_text(
            *coords[1], text=str(key), fill=self.VALUE_COLOR,
            font=self.VALUE_FONT, tags=('link', 'linkVal'))
        dot = self.canvas.create_oval(
            *coords[3], fill=self.linkDotColor, outline='', width=0,
            tags=('link', 'linkDot'))
        arrow = self.canvas.create_line(
            *coords[4], fill=self.linkArrowColor, width=self.linkArrowWidth,
            arrow=LAST, tags=('link', 'linkArrow'))
        for item in (box, rect, textKey, dot):
            self.canvas.tag_bind(item, '<Button>',
                                 lambda e: self.setArgument(str(key)))
        return rect, textKey, box, dot, arrow

    def createInitialLink(self, cell, firstNodeOrCoords=None):
        center = V(self.cellCenter(cell))
        radius = V((self.cellDotRadius if firstNodeOrCoords else 0, ) * 2)
        dot = self.canvas.create_oval(
            *((center - radius) + (center + radius)), fill=self.cellDotColor,
            outline='', width=0, tags=('cell', 'cellDot'))
        if firstNodeOrCoords is None:
            tip = center
        elif isinstance(firstNodeOrCoords, drawnValue):
            boxCoords = self.canvas.coords(firstNodeOrCoords.items[2])
            tip = (max(boxCoords[0], min(boxCoords[2], center[0])), boxCoords[1])
        else:
            tip = firstNodeOrCoords
        arrow = self.canvas.create_line(
            *center, *tip, fill=self.linkArrowColor, width=self.linkArrowWidth,
            arrow=LAST, tags=('cell', 'cellArrow'))
        return dot, arrow
    
    def createLinkIndex(
            self, link, label='', level=1, orientation=-160, color='black',
            width=1, anchor=SW, font=None):
        if font is None: font = self.VARIABLE_FONT
        coords = self.linkIndexCoords(
            link, level=level, orientation=orientation)
        arrow = self.canvas.create_line(
            *coords[0], arrow=LAST, width=width, fill=color)
        label = self.canvas.create_text(
            *coords[1], text=label or '', fill=color, anchor=anchor, font=font)
        return arrow, label
        
    def createArrayIndexLabel(self, index, tags='cellIndex'):
        coords = self.arrayCellCoords(index)
        return self.canvas.create_text(
            (coords[0] + coords[2]) // 2, coords[1] - 1, anchor=S,
            text=str(index), tags=tags,
            font=self.cellIndexFont, fill=self.CELL_INDEX_COLOR)

    def createArraySizeLabel(self, tags='sizeLabel'):
        coords = self.cellCenter(len(self.table))
        return self.canvas.create_text(
            *coords, text='{} cells'.format(len(self.table)), anchor=W,
            tags=tags, font=self.VALUE_FONT, fill=self.VARIABLE_COLOR)
        
    def setupDisplay(self, hasherHeight=70):
        'Define dimensions and coordinates for display items'
        self.hasherHeight = hasherHeight
        self.cellWidth = 14
        self.cellHeight = self.cellWidth
        self.array_x0 = self.cellWidth * 4
        self.array_y0 = hasherHeight + 40
        self.cellDotRadius = 4 # (self.cellWidth - 4) // 2
        self.cellDotColor = 'red'

        self.outputFont = (self.VALUE_FONT[0], - 12)
        self.VALUE_FONT = (self.VALUE_FONT[0], - 10)
        self.cellIndexFont = (self.VARIABLE_FONT[0], - 10)

        self.linkHeight = 12
        self.linkWidth = self.textWidth(self.VALUE_FONT,
                                        'W' * (self.maxArgWidth + 2))
        self.linkDotRadius = 4
        self.linkDotColor = 'red'
        self.linkArrowColor = 'black'
        self.linkArrowWidth = 1
        self.linkBoxColor = 'black'
        
    def display(self):
        '''Erase canvas and redisplay contents.  Call setupDisplay() before
        this to set the display parameters.'''
        saveCoords = dict(
            (item, self.canvas.coords(item)) for item in
            flat(*(d.items + flat(*(n.items for n in d.val))
                   for d in self.table if d)))
        saveColors = dict(
            (item, self.canvas_itemConfig(item, 'fill')) for item in
            flat(*(n.items for d in self.table if d for n in d.val)))
        self.canvas.delete("all")
        self.setCanvasBounds(self.initialRect, expandOnly=False)
        self.createHasher(y0=1, y1=self.hasherHeight + 1)
        self.updateNItems()
        self.updateMaxLoadFactor()
        self.arrayCells = [
            self.createArrayCell(j) for j in range(len(self.table))]
        self.arrayLabels = [
            self.createArrayIndexLabel(j) for j in range(len(self.table))]
        self.createArraySizeLabel()
        for j, item in enumerate(self.table):
            if item:
                for l, link in enumerate(item.val):
                    item.val[l] = drawnValue(
                        link.val, *self.createLinkItems(
                            [saveCoords[i] for i in link.items], link.val,
                            nextLink=saveCoords[item.val[l + 1].items[2]]
                            if l < len(item.val) - 1 else None,
                            color=saveColors[link.items[0]]))
                    self.expandCanvasFor(*item.val[l].items)
                self.table[j] = drawnValue(
                    item.val,
                    *self.createInitialLink(
                        j, item.val[0] if len(item.val) > 0 else None))
                self.expandCanvasFor(*self.table[j].items)
                    
        self.window.update()

    def linkNodes(self, fromNode, toNode=None):
        dotItem, arrowItem = fromNode.items[-2:]
        dotCenter = BBoxCenter(self.canvas.coords(dotItem))
        radius = V((self.linkDotRadius if toNode else 0,) * 2)
        self.canvas.coords(dotItem,
                           (V(dotCenter) - radius) + (V(dotCenter) + radius))
        toBox = self.canvas.coords((toNode or fromNode).items[2]) 
        self.canvas.coords(
            arrowItem,
            dotCenter + (dotCenter if toNode is None else
                         (max(toBox[0], min(toBox[2], dotCenter[0])), toBox[1])))
        self.canvas_itemConfig(arrowItem, fill=self.linkArrowColor)
        self.expandCanvasFor(dotItem, arrowItem)
        
    def updateNItems(self, nItems=None, gap=4):
        if nItems is None:
            nItems = self.nItems
        outputBoxCoords = self.outputBoxCoords()
        if self.nItemsText is None or self.canvas.type(self.nItemsText) != 'text':
            self.nItemsText = self.canvas.create_text(
                *(V(outputBoxCoords[:2]) + V(gap, - gap)), anchor=SW,
                text='', font=self.VARIABLE_FONT, fill=self.VARIABLE_COLOR)
        self.canvas_itemConfig(self.nItemsText,
                               text='nItems = {}'.format(nItems))
        
    def updateMaxLoadFactor(self, maxLoadFactor=None, gap=4):
        if maxLoadFactor is None:
            maxLoadFactor = self.maxLoadFactor
        outputBoxCoords = self.outputBoxCoords()
        if (self.maxLoadFactorText is None or
            self.canvas.type(self.maxLoadFactorText) != 'text'):
            self.maxLoadFactorText = self.canvas.create_text(
                outputBoxCoords[2] - gap, outputBoxCoords[1] - gap, anchor=SE,
                text='', font=self.VARIABLE_FONT,
                fill=self.VARIABLE_COLOR)
        self.canvas_itemConfig(
            self.maxLoadFactorText, text='maxLoadFactor = {}%'.format(
                int(100 * maxLoadFactor)))
            
    def hashAndGetIndex(
            self, key, animate=True, width=1, indexLineColor='darkblue',
            tags=('hashLine',), **kwargs):
        '''Hash the input key into a hash address and get the index to
        the hash table.  This wraps the animateStringHashing method when
        animation is enabled, passing along all its keyword args.
        Regardless of animation, this returns the animation characters
        of the hashed key and the spline arrow connecting them to the
        indexed cell in the hash table (as a tuple of integers).  
        It also returns the cell index as the second value.
        '''
        hashAddress = self.hash(key)
        i = hashAddress % len(self.table)
        self.hashAddressCharacters = self.animateStringHashing(
            key, hashAddress, **kwargs) if self.showHashing.get() else [
                self.canvas.create_text(
                    *self.hashOutputCoords(), anchor=W,
                    text=' ' + str(hashAddress), font=self.VARIABLE_FONT,
                    fill=self.VARIABLE_COLOR)]
        bbox = BBoxUnion(*(self.canvas.bbox(c) 
                           for c in self.hashAddressCharacters))
        bottom = ((bbox[0] + bbox[2]) // 2, bbox[3])
        arrayIndex, label = self.arrayIndexCoords(i, level=2)
        steps = int(max(abs(c) for c in V(bottom) - V(arrayIndex[2:])))
        arrow = self.canvas.create_line(
            *bottom, *(V(bottom) + V(0, self.hasherHeight // 3)), *arrayIndex, 
            arrow=LAST, width=width, fill=indexLineColor,
            splinesteps=steps, smooth=True, tags=tags)
        if animate and 'sleepTime' in kwargs:
            self.wait(kwargs['sleepTime'] * 5)
        return tuple(self.hashAddressCharacters) + (arrow,), i  
      
    def animateStringHashing(
            self, text, hashed, textItem=None, sleepTime=0.01,
            callEnviron=None, dx=2, font=VisualizationApp.VARIABLE_FONT, 
            color=VisualizationApp.VARIABLE_COLOR):
        """Animate text flowing into left of hasher and producing
        hashed output string while hasher churns.  Move characters by dx
        on each animation step. Returns list of canvas items for output
        characters. If textItem is provided, it is a text item that is
        moved into the input of the hasher."""
        
        if not self.hasher:
            return
        h = self.hasher

        if textItem and self.canvas.type(textItem) == 'text':
            self.changeAnchor(E, textItem)
            bbox = self.canvas.bbox(textItem)
            self.moveItemsTo(
                textItem, self.hashInputCoords(nInputs=1),
                sleepTime=sleepTime, startFont=self.getItemFont(textItem),
                endFont=self.VARIABLE_FONT)
            self.canvas_itemConfig(textItem, fill=color)
            
        # Create individual character text items to feed into hasher
        text, hashed = str(text), str(hashed)
        inputCoords = self.hashInputCoords(nInputs=1)
        outputCoords = self.hashOutputCoords()
        charWidth = self.textWidth(font, 'W')
        characters = set([
            self.canvas.create_text(
                inputCoords[0] - ((len(text) - i) * charWidth),
                inputCoords[1], anchor=E, text=c, font=font, fill=color,
                state=DISABLED)
            for i, c in enumerate(text)])
        if textItem:
            self.dispose(callEnviron, textItem)
        for c in characters:
            self.canvas.lower(c)
        if callEnviron:
            callEnviron |= characters

        output = []        # Characters of hashed output
        pad = abs(font[1])
        rightEdge = h['BBox'][2] + pad
        leftmostOutput = rightEdge

        # While there are input characters or characters yet to output or
        # characters to move out of hasher
        while (characters or len(output) < len(hashed) or
               leftmostOutput < rightEdge):
            self.moveItemsBy(    # Move all characters
                characters.union(output), (dx, 0), sleepTime=sleepTime, steps=1)
            self.incrementHasherPhase()
            deletion = False
            for char in list(characters): # For all input characters
                coords = self.canvas.coords(char)  # See if they entered the
                if coords[0] - pad >= h['BBox'][0]: # hasher bounding box and
                    deletion = True       # delete them if they did
                    if callEnviron:
                        self.dispose(callEnviron, char)
                    else:
                        self.canvas.delete(char)
                    characters.discard(char)
                    
            if output:
                leftmostOutput = self.canvas.coords(output[-1])[0]

            # When there are characters to ouput and we've either already
            # output a character or deleted an input character and there
            # is room for the next output character, create it
            if (len(output) < len(hashed) and (output or deletion) and
                leftmostOutput >= rightEdge):
                output.append(
                    self.canvas.create_text(
                        max(leftmostOutput - charWidth, outputCoords[0]),
                        outputCoords[1], text=hashed[-(len(output) + 1)], 
                        font=font, fill=color, state=DISABLED))
                self.canvas.lower(output[-1], h['Blocks'][0])
                if callEnviron:
                    callEnviron.add(output[-1])
        return output

    def adjustArrows(self, start=True, code='adjust arrows'):
        wait = 0.1 if code else 0
        callEnviron = self.createCallEnvironment(code=code)
        if code:
            self.highlightCode('arrows', callEnviron)
        vertices = set(flat(*(
            (tuple(self.canvas.coords(l)[:2]), tuple(self.canvas.coords(l)[-2:]))
            for l in self.canvas.find_withtag('linkArrow'))))
        arrows, coords, significant = [], [], []
        box = V(1, 1)
        for cell in self.table:
            if cell:
                arrow = cell.items[1]
                arrows.append(arrow)
                adjCoords, verts = self.adjustArrow(
                    arrow, vertices, cell.val[0].items[2])
                coords.append(adjCoords)
                if code and verts:
                    sig = [self.canvas.create_rectangle(
                        *(V(vert) - box), *(V(vert) + box),
                        fill='red', outline=None, tags='significant')]
                    significant.extend(sig)
                    callEnviron |= set(sig)
                for linkIndex in range(len(cell.val) - 1):
                    arrow = cell.val[linkIndex].items[-1]
                    arrows.append(arrow)
                    adjCoords, verts = self.adjustArrow(
                        arrow, vertices, cell.val[linkIndex + 1].items[2])
                    coords.append(adjCoords)
                    if code and verts:
                        sig = [self.canvas.create_rectangle(
                            *(V(vert) - box), *(V(vert) + box),
                            fill='red', outline=None, tags='significant')]
                        significant.extend(sig)
                        callEnviron |= set(sig)
        if code:
            self.highlightCode('adjust arrows', callEnviron)
        self.moveItemsTo(arrows, coords, steps=10 if code else 1, 
                         sleepTime=wait / 10)
        self.cleanUp(callEnviron)

    def adjustArrow(self, arrow, vertices, box, distanceThreshold=2):
        arrowCoords = self.canvas.coords(arrow)
        base, tip = tuple(arrowCoords[:2]), tuple(arrowCoords[2:])
        if distance2(base, tip) <= 1:
            return arrowCoords, ()
        unitNormal = V(V(V(V(tip) - V(base)).normal2d()).unit(minLength=1))
        significant, score = set(), 0
        otherVerts = vertices - set((base, tip))
        for vert in otherVerts:
            distance = self.distanceToSegment(vert, base, tip, unitNormal)
            if distance <= distanceThreshold:
                significant.add(vert)
            if distance <= 10 * distanceThreshold:
                score += 1 / max(distance, 1e-4)
        if score == 0:
            return arrowCoords, significant
        boxCoords = self.canvas.coords(box)
        boxWidth = int(boxCoords[2] - boxCoords[0])
        for newTipIndex in range(boxWidth + 1):
            s = 0
            newTip = V(boxCoords[0]) + V(newTipIndex, 0)
            s = sum(1 / max(
                1e-4, self.distanceToSegment(vert, base, newTip, unitNormal))
                    for vert in otherVerts)
            if s < score:
                score, tip = s, newTip
        return base + tip, significant

    def distanceToSegment(self, point, base, tip, unitNormal):
        v = V(V(point) - V(base))
        segment = V(V(tip) - V(base))
        xProject = segment.dot(v)
        if xProject < 0 or segment.len2() < xProject:
            return math.inf
        return abs(v.dot(unitNormal))
        
    # Button functions

    def clickTraverse(self):
        self.traverseExample(start=self.startMode(), indexLabel='')

    def clickAdjustArrows(self):
        self.adjustArrows(start=self.startMode())
        
    def makeButtons(self):
        vcmd = (self.window.register(
            makeFilterValidate(self.maxArgWidth)), '%P')
        self.insertButton = self.addOperation(
            "Insert", self.clickInsert, numArguments=1, validationCmd=vcmd,
            helpText='Insert a key into the hash table',
            argHelpText=['key'])
        searchButton = self.addOperation(
            "Search", self.clickSearch, numArguments=1, validationCmd=vcmd,
            helpText='Search for a key in the hash table',
            argHelpText=['key'])
        deleteButton = self.addOperation(
            "Delete", self.clickDelete, numArguments=1, validationCmd=vcmd,
            helpText='Delete a key in the hash table',
            argHelpText=['key'])
        newButton = self.addOperation(
            "New", lambda: self.clickNew(defaultMaxLoadFactor=1.0),
            numArguments=2, validationCmd=vcmd,
            helpText='Create new hash table with\n'
            'number of cells & max load factor',
            argHelpText=['number of cells', 'max load factor'])
        randomFillButton = self.addOperation(
            "Random fill", self.clickRandomFill, numArguments=1,
            validationCmd=vcmd, helpText='Fill with N random items',
            argHelpText=['number of items'])
        self.showHashing = IntVar()
        self.showHashing.set(1)
        showHashingButton = self.addOperation(
            "Animate hashing", self.clickShowHashing, buttonType=Checkbutton,
            variable=self.showHashing, 
            helpText='Show/hide animation during hashing')
        traverseButton = self.addOperation(
            "Traverse", self.clickTraverse, 
            helpText='Traverse items in hash table')
        adjustButton = self.addOperation(
            "Adjust arrows", self.clickAdjustArrows, 
            helpText='Adjust arrow links to avoid conflicts')
        self.addAnimationButtons()

if __name__ == '__main__':
    hashTable = HashTableChaining()
    animate = '-a' in sys.argv[1:]
    showHashing = hashTable.showHashing.get()
    hashTable.showHashing.set(1 if animate else 0)
    for arg in sys.argv[1:]:
        if not(arg[0] == '-' and len(arg) == 2 and arg[1:].isalpha()):
            if animate:
                hashTable.setArgument(arg)
                hashTable.insertButton.invoke()
            else:
                hashTable.insert(int(arg) if arg.isdigit() else arg, code='')
        
    hashTable.showHashing.set(showHashing)
    if not animate:
        hashTable.stopAnimations()
    hashTable.runVisualization()