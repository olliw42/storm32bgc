# Version v0.42 18. Aug. 2020

###############################################################################
# cLogDataItemTranslator
# cStorm32GuiLogItemTranslator(cLogItemTranslator)
# helper class to translate data field names from various source files to
# the standard NTLogger data field names
#-----------------------------------------------------------------------------#

###############################################################################
# cLogDataItemList
# class to handle the data columns for various data log files
# translates data field names according to the given translator
# organizes the standard NTLogger data field names into catagories
#-----------------------------------------------------------------------------#

###############################################################################
# cLogReader
# this is the base class to read a data log file
#-----------------------------------------------------------------------------#


from copy import deepcopy


###################################################################
# some constants
###################################################################

cDATATYPE_U8  = 0
cDATATYPE_U16 = 1
cDATATYPE_U32 = 2
cDATATYPE_U64 = 3
cDATATYPE_Ux  = 7   #Ux is a mask for all U types
cDATATYPE_S8  = 16
cDATATYPE_S16 = 17
cDATATYPE_S32 = 18
cDATATYPE_S64 = 19
cDATATYPE_Sx  = 20  #Sx is a mask for all S types
cDATATYPE_FLOAT = 32


cLOGTYPE_UNINITIALIZED = 0
cLOGVERSION_UNINITIALIZED = 0


###############################################################################
# cLogDataItemTranslator
# cStorm32GuiLogItemTranslator(cLogItemTranslator)
# helper class to translate data field names from various source files to
# the standard NTLogger data field names
#-----------------------------------------------------------------------------#
class cLogDataItemTranslator:

    def translate(self,_name):
        return _name

        
###############################################################################
# cLogDataItemList
# class to handle the data columns for various data log files
# translates data field names according to the given translator
# organizes the standard NTLogger data field names into catagories
#-----------------------------------------------------------------------------#
class cLogDataItemList:

    def __init__(self,_translator=None):
        self.translator = _translator #cStorm32GuiLogItemTranslator() #cLogItemTranslator()
        self.list = [] #this is the item list of the log file
        self.graphSelectorList = [] #this is a human-readable list of how to organize the data field names into catagories
        self.curIndex = 0

    def clear(self):
        self.list = []
        self.graphSelectorList = []
        self.curIndex = 0

    def clearList(self):
        self.list = []
        self.curIndex = 0
        
    #adds a data field item to the list
    #needs: name, uint, raw data type (as in the log data stream), data type (as return by the log data reader)
    def addItem(self, _name, _unit, _rawtype, _type):
        self.list.append( {'index':self.curIndex, 'name':_name, 'unit':_unit, 'rawtype':_rawtype, 'type':_type} )
        self.curIndex += 1

    #extracts a data field item list from a string, typically the first&2nd line(s) of a .dat/.txt/.csv file
    def setFromStr(self, _names, _units, _rawtype, _type, _sep):
        nameList = _names.split(_sep)
        unitList = _units.split(_sep)
        #self.clear() #BUG! this also kills self.graphSelectorList, which we want to keep if available however 
        self.clearList()
        for i in range(len(nameList)):
            if i<len(unitList):
                u = unitList[i].replace("[", "").replace("]", "") #remove brackets
            else:
                u = ''
            self.addItem( nameList[i], u, _rawtype, _type )

    #moves the 'time' axis to position zero, as needed for graphing
    def swapTimeToZeroIndex(self):
        timePosInList = -1
        zeroPosInList = -1
        for i in range(len(self.list)):
            if self.list[i]['name'].lower() == 'time':
                timePosInList = i
            if self.list[i]['index'] == 0:
                zeroPosInList = i
        if timePosInList == -1: return -1 #a Time column doesn't exist
        if timePosInList == zeroPosInList: return 0 #Time column is already at index zero
        self.list[zeroPosInList]['index'] = self.list[timePosInList]['index']
        self.list[timePosInList]['index'] = 0
        return self.list[zeroPosInList]['index'] #return which index Time was before

    def getNamesAsList(self, _translator=None):
        if( not _translator ): _translator = self.translator #use the translator set by __init__
        if( not _translator ): _translator = cLogDataItemTranslator() #self.stdTranslator #still non edefined, use the std Translator
        l = []
        for item in self.list:
            l.append( _translator.translate(item['name']) )
        return l

    def getNamesAsStr(self, _sep, _translator=None):
        return _sep.join( self.getNamesAsList(_translator) )

    def getUnitsAsStr(self, _sep):
        s = ''
        for item in self.list:
            s += '[' + item['unit'] + ']' + _sep
        s = s[:-len(_sep)]
        return s

    def getNameIndexTypeDictionary(self):
        d = {}
        for item in self.list:
            d[item['name']] = { 'index':item['index'], 'rawtype':item['rawtype'] }
        return d

    #returns a list, which can be directly used to set the Graph Selector
    # structured as follows: [ ['catergory',[item,item,item]], ['catergory',[item,item,item]], ... ]
    # the list may not be identical to self.graphSelectorList, i.e., unused fields are taken out
    def getGraphSelectorList(self, _translator=None):
        if( not _translator ): _translator = self.translator  #use the translator set by __init__
        if( not _translator ): _translator = cLogDataItemTranslator()  #self.stdTranslator #still non edefined, use the std Translator
        #populate Selection with items
        l = []  #this is the graphselectorlist to build
        slist = deepcopy(self.list)  #this is a copy, once an entry is used it is taken out
        for gslitem in self.graphSelectorList:
            il = []
            for item in self.list:
                if _translator.translate(item['name']) in gslitem[1]:
                    il.append(item['index'])
                    slist.remove(item)
            if il: l.append( [gslitem[0], il] )
        #remove items which shall never be shown
        for item in self.list:
            if _translator.translate(item['name']).lower() in ['time','yawtarget1']:
                if item in slist: slist.remove(item)
            if item['unit'].lower() == 'hex':
                if item in slist:
                    slist.remove(item)
        #add not yet consumed items
        for item in slist:
            l.append( [_translator.translate(item['name']), [item['index']]] )
        return l
        
    def getGraphSelectorDefaultIndex(self, graphSelectorList=None):
        return None
        
    def getIndexByName(self, name):
        return None
        

###############################################################################
# cLogReader
# this is the base class to read a data log file
#-----------------------------------------------------------------------------#
class cLogReader:

    def __init__(self):
        self.logType = cLOGTYPE_UNINITIALIZED
        self.logVersion = cLOGVERSION_UNINITIALIZED
        
    #this is called by the parser
    # returns a bool, True if error occured
    def appendDataFrame(self,_frame):
        self.datalog.append( _frame.getDataLine() )
        self.rawdatalog.append( _frame.getRawDataLine() )
        return False

    def getLogType(self):
        return self.logType

    def getLogVersion(self):
        return self.logVersion
        
        
        
        
