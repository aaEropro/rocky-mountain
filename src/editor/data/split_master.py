from copy import deepcopy


class SplitState:
    INORDER = 1
    OUTORDER = 2
    DELETED = 3


class Split:

    def __init__(self, filename:str) -> None:
        self.filename = filename

    def getFilename(self) -> str:
        ''' returns the filename. '''
        return self.filename
    
    def getPosition(self) -> int|None:
        ''' returns the position. '''
        return self.position
    
    def getState(self) -> SplitState:
        ''' returns the state. '''
        return self.state
    
    def _setPosition(self, position) -> None:
        ''' sets a new position. '''
        self.position = position

    def _setState(self, state:SplitState) -> None:
        ''' sets a new state. '''
        self.state = state


class OrderHolder:
    def __init__(self):
        self.inorder_items_list = []
        self.outorder_items_list = []
        self.deleted_items_list = []

        self.splits_dict = {}

################################## PLACING #######################################################
    def addSplit(self, obj:Split, state:SplitState, position:int|None=None):
        ''' add split `obj` to `OrderHolder`. '''
        if state == SplitState.INORDER:
            self._addInorder(obj)
        elif state == SplitState.OUTORDER:
            self._addOutorder(obj)
        elif state == SplitState.DELETED:
            self._addDeleted(obj)
        else:
            raise Exception(f'no such state {state}')

    def _addInorder(self, obj:Split, position:int|None=None) -> None:
        if obj not in self.inorder_items_list:
            obj._setState(SplitState.INORDER)
            if position is not None:
                self.inorder_items_list.insert(position, obj)
            else:
                self.inorder_items_list.append(obj)
            self.splits_dict[obj.getFilename()] = obj
            self.reorderAll()
    
    def _addOutorder(self, obj:Split) -> None:
        if obj not in self.outorder_items_list:
            obj._setState(SplitState.OUTORDER)
            self.outorder_items_list.append(obj)
            self.splits_dict[obj.getFilename()] = obj
    
    def _addDeleted(self, obj:Split) -> None:
        if obj not in self.deleted_items_list:
            obj._setState(SplitState.DELETED)
            self.deleted_items_list.append(obj)
            self.splits_dict[obj.getFilename()] = obj
    
################################## ORDER TRANITIONS ###############################################
    def setState(self, filename:str, state:SplitState):
        ''' set the state of the split with filename `filename`. '''
        obj = self.getObj(filename)
        obj_state = obj.getState()
        if obj_state == state:
            return
        if state == SplitState.INORDER:
            obj._setState(SplitState.INORDER)
            self._toInorder(obj)
        elif state == SplitState.OUTORDER:
            obj._setState(SplitState.OUTORDER)
            self._toOutorder(obj)
            self.reorderAll()
        elif state == SplitState.DELETED:
            obj._setState(SplitState.DELETED)
            self._toDeleted(obj)
            self.reorderAll()

    def _toInorder(self, obj:Split, position:int|None) -> None:
        split = obj
        if split in self.inorder_items_list:
            return
        
        if split in self.outorder_items_list:
            self.outorder_items_list.remove(split)

        if split in self.deleted_items_list:
            self.deleted_items_list.remove(split)

        if position is None:
            self.inorder_items_list.append(split)
        else:
            self.inorder_items_list.insert(position, split)
        self.reorderAll()

    def _toOutorder(self, obj:Split) -> None:
        split = obj
        if split in self.outorder_items_list:
            return
        
        if split in self.inorder_items_list:
            self.inorder_items_list.remove(split)

        if split in self.deleted_items_list:
            self.deleted_items_list.remove(split)

        self.outorder_items_list.append(split)

    def _toDeleted(self, obj:Split) -> None:
        split = obj
        if split in self.deleted_items_list:
            return
        
        if split in self.inorder_items_list:
            self.inorder_items_list.remove(split)

        if split in self.outorder_items_list:
            self.outorder_items_list.remove(split)

        self.deleted_items_list.append(split)

    
################################## INORDER MOVES ##################################################
    def atSpot(self, filename: str, spot: int):
        ''' move an existing split to another spot. '''
        obj:Split = self.getObj(filename)
        position = obj.getPosition()

        if position != spot:
            self.inorder_items_list.remove(obj)
            self.inorder_items_list.insert(spot, obj)
            self.reorderAll()

    def reorderAll(self) -> None:
        ''' makes shure that all the `Split` instances have the right position. '''
        for index, split_obj in enumerate(self.inorder_items_list):
            split_obj._setPosition(index)


################################## INORDER CHECKS #################################################
    def isNext(self, filename:str) -> bool:
        ''' returns `True` if there is a next split, else `False`. '''
        obj:Split = self.getObj(filename)
        position = obj.getPosition()

        return position < len(self.inorder_items_list)-1
    
    def isPrevious(self, filename:str) -> bool:
        ''' returns `True` if there is a previous split, else `False`. '''
        obj:Split = self.getObj(filename)
        position = obj.getPosition()

        return position > 0
    
################################## GETS ###########################################################
    def getObj(self, filename) -> Split:
        ''' returns the object with that filename. '''
        if filename not in self.splits_dict.keys():
            raise Exception('file does not exist')
        
        obj:Split = self.splits_dict[filename]

        return obj

    def getState(self, filename:str) -> SplitState:
        ''' returns the state of the split with that filename. '''
        obj:Split = self.getObj(filename)
        state = obj.getState()

        return state
    
    def getNext(self, filename:str) -> str:
        ''' returns the name of the next split. '''
        obj:Split = self.getObj(filename)
        position = obj.getPosition()

        if position == len(self.inorder_items_list)-1:
            raise Exception('next file does not exist')
        
        next_obj:Split = self.inorder_items_list[position+1]
        next_filename:str = next_obj.getFilename()

        return next_filename
    
    def getPrevious(self, filename:str) -> str:
        ''' returns the name of the previous split. '''
        obj:Split = self.getObj(filename)
        position = obj.getPosition()

        if position == 0:
            raise Exception('previous file does not exist')
        
        prev_obj:Split = self.inorder_items_list[position-1]
        prev_filename:str = prev_obj.getFilename()

        return prev_filename

    def getInorder(self) -> list[str]:
        ''' returns a list containing the inorder splits filenames. '''
        inorder_filenames = []
        for obj in self.inorder_items_list:
            filename = obj.getFilename()
            inorder_filenames.append(filename)
        return inorder_filenames

    def getOutorder(self) -> list[str]:
        ''' returns a list containing the outorder splits filenames. '''
        outorder_filenames = []
        for obj in self.outorder_items_list:
            filename = obj.getFilename()
            outorder_filenames.append(filename)
        return outorder_filenames

    def getDeleted(self) -> list[str]:
        ''' returns a list containing the deleted splits filenames. '''
        deleted_filenames = []
        for obj in self.deleted_items_list:
            filename = obj.getFilename()
            deleted_filenames.append(filename)
        return deleted_filenames
    
    def getAt(self, index:int) -> str|None:
        ''' returns the filename of the inorder split at index `index`. '''
        if (index < 0) or (index >= len(self.inorder_items_list)):
            raise Exception(f'no inorder index {index}')
        return self.inorder_items_list[index]