
class SplitState:
    INORDER = 1
    OUTORDER = 2
    DELETED = 3


class Split:

    def __init__(self, master, filename:str, state:SplitState) -> None:
        self.master = master
        self.filename = filename
        self.state = state

        if self.state == SplitState.INORDER:
            self.position = master.requestInorderSpot(self)

        if self.state == SplitState.OUTORDER:
            self.position = master.requestOutorderSpot(self)

        if self.state == SplitState.DELETED:
            self.position = master.requestDeletedSpot(self)

    def getFilename(self) -> str:
        ''' returns the filename. '''
        return self.filename
    
    def getPosition(self) -> int|None:
        ''' returns the position. '''
        return self.position
    
    def getState(self) -> SplitState:
        ''' returns the state. '''
        return self.state
    
    def setNewPosition(self, position) -> None:
        ''' sets a new position. '''
        self.position = position

    def setNewState(self, state:SplitState) -> None:
        ''' sets a new state. '''
        if state == self.state:
            return

        self.state = state
        if self.state == SplitState.INORDER:
            self.master.toInorder(self)
        elif self.state == SplitState.OUTORDER:
            self.master.toOutorder(self)
        elif self.state == SplitState.DELETED:
            self.master.toDeleted(self)


class OrderHolder:
    def __init__(self):
        self.inorder_items_list = []
        self.outorder_items_list = []
        self.deleted_items_list = []

        self.splits_dict = {}

################################## REQUESTS #######################################################
    def requestInorderSpot(self, obj:Split) -> int:
        if obj not in self.inorder_items_list:
            self.inorder_items_list.append(obj)
            self.splits_dict[obj.getFilename()] = obj
        return self.inorder_items_list.index(obj)
    
    def requestOutorderSpot(self, obj:Split) -> None:
        if obj not in self.outorder_items_list:
            self.outorder_items_list.append(obj)
            self.splits_dict[obj.getFilename()] = obj
        return None
    
    def requestDeletedSpot(self, obj:Split) -> None:
        if obj not in self.deleted_items_list:
            self.deleted_items_list.append(obj)
            self.splits_dict[obj.getFilename()] = obj
        return None
    
################################## ORDER TRANITIONS ###############################################
    def toInorder(self, obj:Split, position:int|None) -> None:
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

    def toOutorder(self, obj:Split) -> None:
        split = obj
        if split in self.outorder_items_list:
            return
        
        if split in self.inorder_items_list:
            self.inorder_items_list.remove(split)

        if split in self.deleted_items_list:
            self.deleted_items_list.remove(split)

        self.outorder_items_list.append(split)

    def toDeleted(self, obj:Split) -> None:
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
        obj:Split = self._getObj(filename)
        position = obj.getPosition()

        if position != spot:
            self.inorder_items_list.remove(obj)
            self.inorder_items_list.insert(spot, obj)
            self.reorderAll()

    def reorderAll(self) -> None:
        ''' makes shure that all the `Split` instances have the right position. '''
        for index, split_obj in enumerate(self.inorder_items_list):
            split_obj.setNewPosition(index)


################################## INORDER CHECKS #################################################
    def isNext(self, filename:str) -> bool:
        ''' returns `True` if there is a next split, else `False`. '''
        obj:Split = self._getObj(filename)
        position = obj.getPosition()

        return position < len(self.inorder_items_list)-1
    
    def isPrevious(self, filename:str) -> bool:
        ''' returns `True` if there is a previous split, else `False`. '''
        obj:Split = self._getObj(filename)
        position = obj.getPosition()

        return position > 0
    
################################## GETS ###########################################################
    def _getObj(self, filename) -> Split:
        ''' returns the object with that filename. '''
        if filename not in self.splits_dict.keys():
            raise Exception('file does not exist')
        
        obj:Split = self.splits_dict[filename]

        return obj

    def getState(self, filename:str) -> SplitState:
        ''' returns the state of the split with that filename. '''
        obj:Split = self._getObj(filename)
        state = obj.getState()

        return state
    
    def getNext(self, filename:str) -> str:
        ''' returns the name of the next split. '''
        obj:Split = self._getObj(filename)
        position = obj.getPosition()

        if position == len(self.inorder_items_list)-1:
            raise Exception('next file does not exist')
        
        next_obj:Split = self.inorder_items_list[position+1]
        next_filename:str = next_obj.getFilename()

        return next_filename
    
    def getPrevious(self, filename:str) -> str:
        ''' returns the name of the previous split. '''
        obj:Split = self._getObj(filename)
        position = obj.getPosition()

        if position == 0:
            raise Exception('previous file does not exist')
        
        prev_obj:Split = self.inorder_items_list[position-1]
        prev_filename:str = prev_obj.getFilename()

        return prev_filename
    


import unittest

class TestOrderHolderAndSplit(unittest.TestCase):

    def setUp(self):
        '''This method sets up the necessary data for each test.'''
        self.order_holder = OrderHolder()
        
        # Create sample splits
        self.split1 = Split(self.order_holder, "file1.gmb", SplitState.INORDER)
        self.split2 = Split(self.order_holder, "file2.gmb", SplitState.OUTORDER)
        self.split3 = Split(self.order_holder, "file3.gmb", SplitState.DELETED)

    def test_basic_creation(self):
        '''Tests basic object creation and attributes.'''
        self.assertEqual(self.split1.getFilename(), "file1.gmb")
        self.assertEqual(self.split1.getPosition(), 0)
        self.assertEqual(self.split1.getState(), SplitState.INORDER)
        
        # Check if split has been added to the appropriate list
        self.assertIn(self.split1, self.order_holder.inorder_items_list)
        self.assertIn(self.split2, self.order_holder.outorder_items_list)
        self.assertIn(self.split3, self.order_holder.deleted_items_list)

    def test_navigation(self):
        '''Tests basic navigation functions.'''
        split4 = Split(self.order_holder, "file4.gmb", SplitState.INORDER)
        
        self.assertEqual(self.order_holder.getNext("file1.gmb"), "file4.gmb")
        self.assertEqual(self.order_holder.getPrevious("file4.gmb"), "file1.gmb")
        
        with self.assertRaises(Exception):
            # Should raise an exception as file1 is the first split
            self.order_holder.getPrevious("file1.gmb")
        
        with self.assertRaises(Exception):
            # Should raise an exception as file4 is the last split
            self.order_holder.getNext("file4.gmb")

    def test_state_transition(self):
        '''Tests state transition via the Split methods.'''
        self.split1.setNewState(SplitState.OUTORDER)
        
        self.assertNotIn(self.split1, self.order_holder.inorder_items_list)
        self.assertIn(self.split1, self.order_holder.outorder_items_list)
        self.assertEqual(self.split1.getState(), SplitState.OUTORDER)
        
        self.split1.setNewState(SplitState.DELETED)
        self.assertNotIn(self.split1, self.order_holder.outorder_items_list)
        self.assertIn(self.split1, self.order_holder.deleted_items_list)
        self.assertEqual(self.split1.getState(), SplitState.DELETED)


    def test_position_modification(self):
        '''Tests position modification methods.'''
        split5 = Split(self.order_holder, "file5.gmb", SplitState.INORDER)
        self.order_holder.atSpot("file5.gmb", 0)
        self.assertEqual(self.split1.getPosition(), 1)
        self.assertEqual(split5.getPosition(), 0)

        self.order_holder.atSpot("file5.gmb", 1)
        self.assertEqual(self.split1.getPosition(), 0)
        self.assertEqual(split5.getPosition(), 1)

    # Add more tests as needed ...

if __name__ == '__main__':
    unittest.main()