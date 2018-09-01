'''
Created on Nov 21, 2012

@author: boiruc and eismie1
'''

'''
Important debug flags that must be False before releasing!
\/\/\/\/
'''
release = True

devTest = True ##EE
LRCdebug = False
noMetrics = True

'''
/\/\/\/\
Important debug flags that must be False before releasing!
'''

if release:
    devTest = False ##EE
    LRCdebug = False
    noMetrics = False

from csv import reader as csvReader#import csv
from fnmatch import fnmatch #import fnmatch
from datetime import datetime as datetimeDotDatetime #import datetime
from datetime import timedelta as datetimeDotTimedelta
from time import sleep as sleep#import time
from win32com.client import Dispatch
#import pythoncom
import CPL4
from re import sub as reDotSub
import os
import sys
#import wx
import cPickle as pickle
from traceback import print_exc as tracebackDotPrint_exc# import traceback


'''
Checkpoint system control 
'''

savingCheckpoints = False
resuming = False
startPoint = 1
endPoint = 2

checkpoint1 = 'C:\\C9\\checkpoint1.pkl'
checkpoint2 = 'C:\\C9\\checkpoint2.pkl'
checkpoint3 = 'C:\\C9\\checkpoint3.pkl'
checkpoint4 = 'C:\\C9\\checkpoint4.pkl'


mode = 'dirs'
#mode = 'paths'
parallelTest = False
deployed = True
B = True 
quicktest = False #changes inputlist to just one short file



debugIterating = False
devSyncTest = False
lastUpdateDate = False
LRCFirst = False

# Global Definations #
if release:
    pneRulesPath = r'\\n1gfs01.mw.na.cat.com\shares\EPC913-640\P&E Scoreboard\Web Version\pneleads.txt'
else:
    pneRulesPath= os.path.join(os.path.dirname(__file__), "pneleads.txt")
usageHistoryPath = r'\\n1gfs01.mw.na.cat.com\shares\EPC913-640\P&E Scoreboard\Usage Logs\usage.txt'
errorLogDir = r'\\n1gfs01.mw.na.cat.com\shares\EPC913-640\P&E Scoreboard\P & E Scoreboard Source Code\Error Logs'
if deployed:
    masterDataFile = r'\\n1gfs01.mw.na.cat.com\shares\EPC913-640\P&E Scoreboard\DataDumps\MasterDataFile\mdf.pkl'
    scoreboardDataFile = r'\\n1gfs01.mw.na.cat.com\shares\EPC913-640\P&E Scoreboard\DataDumps\MasterDataFile\sdf3.pkl'
elif B:
    masterDataFile = r'C:\C9\mdf.pkl'
    scoreboardDataFile = r'C:\C9\sdf.pkl'
#masterDataFile = r'C:\Users\eismie1\Desktop\mdf.pkl'
if devTest:
    print"**** Warning **** In Development Test Mode **** Warning ****"
    #scoreboardDataFile = r'C:\C9\sdf_boiruc_mistake.pkl'
    #scoreboardDataFile = r'C:\C9\sdf - 18Feb13.pkl'
    scoreboardDataFile = r'C:\C9\sdf.pkl'
    localTest = True
    if devSyncTest:
        print
        print"\\\\ DANGER //// In Super Secret Sync Test Mode \\\\ DANGER ////"
        print
        scoreboardDataFile = r'\\n1gfs01.mw.na.cat.com\shares\EPC913-640\P&E Scoreboard\DataDumps\MasterDataFile\sdfTest.pkl'
else:
    localTest = False
unblankables = ['P & E Documentation Engineer\\/Notes', 'P & E Manager\\/Notes', 'Process Issues\\/Encountered']
#newBlankAllowed = ['Engineering Sign-Off\\/Actual Date', 'Performance / Emissions\\/Actual Date']#, 'Lab Rating Chart\\/Actual Date','Production Release Checklist\\/Actual Date']
manualAllowed = ['Bore Size', 'P&E Lead', 'Test Specification\\/Actual Date', 'Test Specification Engineer\\/Notes', 'P & E Documentation Engineer\\/Notes', 'P & E Manager\\/Notes', 'Process Issues\\/Encountered', 'Lab Rating Chart\\/Actual Date']
showAllHistoryColumns = ['Engineering Sign-Off\\/Actual Date','Lab Rating Chart\\/Actual Date','Production Release Checklist\\/Actual Date','Performance / Emissions\\/Actual Date', 'Test Specification\\/Actual Date']

# Sb2Db and Db2Sb translates to/from the database-defined key for a column to/from the human readable one used
# on the scoreboard itself. It only contains keys for column labels that have a different database key value
# than scoreboard label

# Actually, label2KeyMap now renames the column in the database to match the specification on the left and breaks
# backwards compatibility. The effects of this map are not cascadable by default.
#label2KeyMap = {'SOL Target Date':'SOL Date'}
label2KeyMap = {'Target SOL Date':'SOL Target Date'}
                
#label2KeyMap = {}
key2LabelMap = {}
for key in label2KeyMap.keys():
    value = label2KeyMap[key]
    key2LabelMap[value] = key

NEW_SOL_DATE_KEY = 'Target SOL Date'
OLD_SOL_DATE_KEY = 'SOL Target Date'
    
def key2Label(header):
    '''
    converts a string from it's original database key to the new mapping as defined
    by 'key2LabelMap'
    '''
    if header in key2LabelMap.keys():
        header = key2LabelMap[header]
    return header

white = 0
red = 3
darkOrange = 53 
#red = darkOrange
green = 4
yellow = 6
periwinkle = 17
pinkPlus = 26
tan = 40
orange = 46

def colorRedef(color):
    '''
    allows color formatting changes for entire scoreboard
    '''
    if color == darkOrange:
        color = red
#    if color == red:
#        color = darkOrange
    
    return color

#colorDef = {'0':white,
#              '3':red,
#              '53':darkOrange,
#              '4':green,
#              '6':yellow,
#              '17':periwinkle,
#              '26':pinkPlus,
#              '40':tan,
#              '46':orange,
#              }

colorRank = [red, #just for testing
             pinkPlus, #Some extreme situation to alert everyone about
             periwinkle, #job no longer exists (canceled, dropped from JRS, etc.)
             orange, # something bad but job is still around
             tan, # basic warning for date innacuracy warning
             white, #nothing is wrong
             ]
             
colorChange = {}





good = green
bad = red
unknownSuspectColor = periwinkle
#SuspectColorRules = [('JRS SOL Date < Its time history date',periwinkle),
#                      ('Part numbers changed after ESO Signed Off',pinkPlus),
#                      ('P&E Tdate - ESO Tdate < 6 days',tan),
#                      ('SOL Date - P&E Tdate < 24 days',tan)
#                      ]
#SuspectColorCodes = {}
#for code, color in suspectRules:
#    SuspectColorCodes[code]=color

years = ['2012', '2013']
monthsOfTheYear = ['January',
                    'February',
                    'March',
                    'April',
                    'May',
                    'June',
                    'July',
                    'August',
                    'September',
                    'October',
                    'November',
                    'December']
#global dataDate 
dataDate = datetimeDotDatetime.now()
#global timeBuilding
timeBuilding = False

#SourceFilters defines values that are not allowed for a certain column 
#from a certain source. If a job number line in a Source has a forbidden
#Value at a specified column, then that line will be ignored.
#Form: SourceFileters = {<Source>: {<Column>:<Value>}}
SourceFilters = {'Aardvark': {'Status':'Rescinded',
                              },
                 }
testData = {}
if parallelTest:
    print
    print"\\\\ DANGER //// In Super Secret Sync Test Mode \\\\ DANGER ////"
    print
    scoreboardDataFile = r'\\n1gfs01.mw.na.cat.com\shares\EPC913-640\P&E Scoreboard\DataDumps\MasterDataFile\sdfTest.pkl'

def py2date(now_pytime):
    now_datetime = datetimeDotDatetime (
      year=now_pytime.year,
      month=now_pytime.month,
      day=now_pytime.day,
      hour=now_pytime.hour,
      minute=now_pytime.minute,
      second=now_pytime.second
    )
    return now_datetime

class ExcelGrabJobNumbers(CPL4.ExcelGrabColumns):
    def __init__(self, xlsPath, LeaveOpen, SheetNames=[], HeaderRows={}):
        self.jobNumbers = []
        CPL4.ExcelGrabColumns.__init__(self, xlsPath, LeaveOpen, SheetNames=[], HeaderRows={})
        self.Activate(self.sheets[0])
    
    def CreateLookupItemReference(self):
        self.LookupItems = {}
        self.LookupList = []
        self.firstColumn = firstColumn = self.GetColList(self.LookupItem)
        badThings = ['', None, 'None']
        for i, item in enumerate(firstColumn):
            if i > self.activeSheetHeaderRow and not item in badThings:
                ignore = False
                #only accept data from job numbers that are all Caps
                #This is changed to accept only job numbers that start with J
                # and to capitalize any job numbers with lower case values
                if item.upper() != item:
                    item = item.upper()
                    if item[0] != 'J':
                        ignore = True
                jobData = self.GetRowDict(i)
                
                if hasattr(self, 'source'):
                    #This code will perform Source Prefiltering, such as duplicate 
                    #jobNumbers occuring in Aardvark 
                    #a job Number entry in Aardvark that has a 'Status' of 'Rescinded'
                    #will have all of its values ignored
                    if self.source in SourceFilters.keys():
                        filters = SourceFilters[self.source]
                        for key in filters.keys():
                            fullKey = key + '-->' + self.source
                            if fullKey in jobData.keys():
                                forbidden = filters[key]
                                value = jobData[fullKey][-1]['value'][0]
                                if value == forbidden:
                                    ignore = True
                                    break
                    #This code will perform Source Preprocessing, such as determining what
                    #value to use for LRC Actual Date
                    if self.source == 'ProjectPlan':
                        if item == 'J5419W':
                            pass
                        ignore = self.getLatestLRC(firstColumn, item, i, jobData)
                if not ignore:
                    if self.source == 'ProjectPlan':
                        pass
                    self.LookupDict[item] = i
                    self.LookupList.append(item)
                    self.jobDict[item] = jobData

    def getLatestLRC(self, firstColumn, item, i, jobData):
        LRCactualDate = '$blank A'
        loc = firstColumn.index(item)
        #if this is the first occurrence of the number
        ignore = False
        if loc == i:
            count = firstColumn.count(item)
            locs = []
            dates = []
            stats = []
            lines = []
            loc = 0
            for j in range(count):
                loc = firstColumn.index(item, loc + 1)
                newLine = self.GetRowDict(loc)
                stat = newLine['Activity Status-->ProjectPlan'][-1]['value'][0]
                if stat == "Completed":
                    date = newLine['Finish-->ProjectPlan'][-1]['value'][0][:-2]
                    date = datetimeDotDatetime.strptime(date, '%d-%b-%y')
                    dates.append(date)
                locs.append(loc)
                lines.append(newLine)
                stats.append(stat)
            #if all occurances are completed:
            if stats.count('Completed') == len(stats):
                if len(dates) > 1:
                    LRCactualDate = getLastDate(dates, style='datetime')
                    if not LRCactualDate:
                        LRCactualDate='$blank'
                    #print LRCactualDate
                elif len(dates) == 1:
                    LRCactualDate = dates[0]
            jobData['Finish-->ProjectPlan'][-1]['value'][0] = LRCactualDate
        else:
            ignore = True 
        return ignore
                        
def getLastDate(dateList, style='string', format='%y-%b-%d', jobNumber = False):
    '''
    Returns a sorted list of dates given a list of dates in string format
    format = YY-MMM-D, or any format string supplied in keyword 'format'
    '''
    if style == 'string':
#        tempList = []
#        for thing in dateList:
#            if ' A' in thing:
#                tempList.append(thing[:-3])
        #dateList
        tempList = dateList
        tempList.sort(key=lambda x: datetimeDotDatetime.strptime(x, format))
    elif style == 'datetime':
        dateList.sort()
    tempList = dateList
    if len(tempList)<1:
        return False
    return tempList[-1]

def getDeltaDays(date1, date2, format='%y-%b-%d'):
    '''
    returns the number of days seperating two dates
    '''
    date1T = datetimeDotDatetime.strptime(date1)
    date2T = datetimeDotDatetime.strptime(date2)
    delta = date1T - date2T
    days = delta.days
    return days

class ExcelGrabProjectPlan(ExcelGrabJobNumbers):
    def __init__(self, xlsPath, LeaveOpen, SheetNames=[], HeaderRows={}):
        self.LookupItem = 'Job Number'
        self.source = 'ProjectPlan'
        ExcelGrabJobNumbers.__init__(self, xlsPath, LeaveOpen, SheetNames=[], HeaderRows={})
        
class ExcelGrabJRS(ExcelGrabJobNumbers):
    def __init__(self, xlsPath, LeaveOpen, SheetNames=[], HeaderRows={}):
        self.LookupItem = 'Job No'
        self.source = 'JRS'
        ExcelGrabJobNumbers.__init__(self, xlsPath, LeaveOpen, SheetNames=[], HeaderRows={})
        
class ExcelGrabScoreBoard(ExcelGrabJobNumbers):
    def __init__(self, SheetNames=[], HeaderRows={}):
        self.isScoreboard = True
        self.LookupItem = 'Job #'
        xlsPath = 'macro'
        self.excel = False
        LeaveOpen = True
        self.sheets1 = ['Metrics', 'ScoreBoard', 'Dena Cassidy Metrics']
        self.hRows = hRows = {'ScoreBoard' : [2, 3], 'Metrics' : [1, 2], 'Dena Cassidy Metrics' : [1, 2]}
        self.startPoints = {'ScoreBoard' : [4, 0],
                            'Metrics' : [3, 2],
                            'Dena Cassidy Metrics' : [3, 2]}
        self.jobNumbers = []
        CPL4.ExcelGrabColumns.__init__(self, xlsPath, LeaveOpen, SheetNames=[], HeaderRows={})
        self.Activate(self.sheets[1])
        
		
    def getHeaders(self):
        self.Headers1 = {'Metrics': [],
                         'ScoreBoard': [],
                         'Dena Cassidy Metrics': []}
        for sheet in self.sheets1:
            startCol = self.startPoints[sheet][1]
            row1 = self.data[sheet]['contents'][self.hRows[sheet][0]]
            row2 = self.data[sheet]['contents'][self.hRows[sheet][1]]
            if isinstance(row1[0],datetimeDotDatetime) or '/' in row1[0]:
                row1[0] = 'None'
            upperStarted = False
            upperHeader = ''
            for i in range(len(row2))[startCol:]:
                header = ''
                
                
                if row1[i] != 'None' and not fnmatch(row1[i], 'T-[0-9][0-9]') : #row1[i] == 'None' and upperStarted:
                    upperStarted = True
                    upperHeader = row1[i] + '\\/'
                if row2[i] == 'None':
                    break
                    
                lowerHeader = row2[i]
                header += upperHeader + lowerHeader
                self.Headers1[sheet].append(header)
                    
    def AnySheets(self):
        return self.sheets1
    
    def CreateLookupItemReference(self):
        if self.activeSheetName != 'Metrics':
            self.LookupItems = {}
            self.LookupList = []
            self.firstColumn = firstColumn = self.GetColList(self.LookupItem)
            for i, item in enumerate(firstColumn):
                if i > self.activeSheetHeaderRow and not item == 'None':
                    self.LookupDict[item] = i
                    self.LookupList.append(item)
                    self.jobDict[item] = self.GetRowDict(item)
                
    def Activate(self, sheetName):
        """
        Sets a sheet to be the active sheet that will be used to return data for all of the following methods
        """
        if self.isNum(sheetName):
            sheetName = "Sheet" + str(sheetName)
        if sheetName in self.data.keys():
            self.activeSheet = self.data[sheetName]['contents']
            self.activeSheetName = sheetName
            self.activeSheetIDX = self.sheets.index(sheetName)
            self.activeSheetHeaderRow = self.hRows[sheetName][1]
            startCol = self.startPoints[sheetName][1]
            self.getHeaders()
            self.aheaders = self.Headers1[sheetName]
            self.activeSheetHeaders = self.aheaders #= self.data[sheetName]['contents'][self.activeSheetHeaderRow]
            self.excel.Worksheets(sheetName).Activate
            self.GetColList(self.LookupItem)
            self.CreateLookupItemReference()
        else:
            print("%s not found in sheets" % sheetName)
            print("valid options are:")
            lastSheet = ''
            for item in self.data.keys():
                lastSheet = item
            if len(self.data.keys()) == 1:
                self.Activate(item)
                    
class ExcelGrabPRC(ExcelGrabJobNumbers):
    def __init__(self, xlsPath, LeaveOpen, SheetNames=[], HeaderRows={}):
        self.LookupItem = 'Job Number'
        self.source = 'PRC'
        ExcelGrabJobNumbers.__init__(self, xlsPath, LeaveOpen, SheetNames=[], HeaderRows={})
        
    def CreateLookupItemReference(self):
        self.LookupItems = ['Job Number 1', 'Job Number 2', 'Job Number 3']
        self.LookupList = []
        self.jobDict = {}
        self.LookupItem = 'Job Number'
        self.firstColumn = firstColumn = []
        self.firstColumn.extend(self.GetColList(self.LookupItems[0]))
        for item in self.LookupItems:
            for i, lookupItem in enumerate(firstColumn):
                if i > self.activeSheetHeaderRow:
                    newItems = reDotSub(r'[^a-zA-Z0-9]', ' ', lookupItem)
                    candidates = newItems.split()
                    if not isinstance(candidates, str):
                        for candidate in candidates:
                            if fnmatch(candidate, 'J[0-9][0-9][0-9][0-9]*'):
                                self.jobDict[candidate] = self.GetRowDict(i)
                                self.jobDict[candidate]['Job Number'] = add2JobNumber(candidate)
#                    '''
#                    CodeSwitch Start \/
#                    '''
                    else:
                        if fnmatch(candidate, 'J[0-9][0-9][0-9][0-9]*'):
                            self.jobDict[candidates] = self.GetRowDic(lookupItem)
                            self.jobDict[candidates]['Job Number'] = add2JobNumber(candidate)
#                    '''
#                    IF Problem: Then switch these pieces of code /\  \/  
#                    '''
#                    else:
#                        self.jobDict[candidates] = self.GetRowDic(lookupItem)
#                        self.jobDict[candidates]['Job Number'] = add2JobNumber(candidate)
#                    '''
#                    CodeSwitch End /\
#                    '''
        for item in firstColumn:
            if i > self.activeSheetHeaderRow and not item == 'None':
                self.LookupDict[item] = i
                self.LookupList.append(item)                 
        
class ExcelGrabAardvark(ExcelGrabJobNumbers):
    def __init__(self, xlsPath, LeaveOpen, SheetNames=[], HeaderRows={}):
        self.LookupItem = 'Job Number'
        self.source = 'Aardvark'
        ExcelGrabJobNumbers.__init__(self, xlsPath, LeaveOpen, SheetNames=[], HeaderRows={})
        
class ExcelGrabAardvarkAuto(ExcelGrabJobNumbers):
    def __init__(self, xlsPath, LeaveOpen, SheetNames=[], HeaderRows={}):
        self.LookupItem = 'Job Number'
        self.source = 'AardvarkAuto'
        ExcelGrabJobNumbers.__init__(self, xlsPath, LeaveOpen, SheetNames=[], HeaderRows={})
        
    def CreateLookupItemReference(self):
        '''
        This version of the function is as simple as possible, it will save dates for each "long name" 
        header from the Aardvark Example Scoreboard created by Anthony Marretti - which hard codes
        assignee names for tasks into the tasks.
        
        For now it will not attempt to color items based on date variance, it will just grab the dates.
        
        This report requires multiple job number entries to be identified as containing unique values
        that will have to be appended to a list of values for a given header, specifically:
        
        WorkListAssigned
        WorkListDate    
        WorkListFilter    
        WorkListItem    
        WorkListStatus
        '''
#        AardvarkColumnsList = ['EAC (or Core) setup in CDM Complete',
#                               'LRC Updated/Published',
#                               'PRC Approved',
#                               'Perform Lab Rating Review',
#                               'Certification Needs Reviewed',
#                               'Emissions Validation Plan Approved',
#                               'Specify Required Emissions Certification Types',
#                               'Certification Date Assigned',
#                               'FFR Launched',
#                               'Interlock defined',
#                               'PSPS Approval Complete',
#                               's/w Staged',
#                               'Submit s/w MO45 request',
#                               'TSpec determined',
#                               'Validation Testing Complete',
#                               'Verify s/w available on SISweb',
#                               'Specify Required Emissions Certification Types',
#                               'FFR Launched',
#                               'PSR Launched',
#                               'Exempt Label(s) Requested',
#                               "ENGINE/AIDB/TMI updates made (includes new p//n's)"
#                               ]
        AardvarkColumnsList = [
'EAC (or Core) setup in CDM Complete [Same as PRC/LRC/Engr Completion Date Above]:Niraj Bidkar:bidkans',
'LRC Updated/Published [Cert Date - 12 or Target SOL - 30   see above]:Matt Musec:musecmj',
'LRC Updated/Published [Cert Date - 12 or Target SOL - 30   see above]:Prasad Joshi:joshipl'
'LRC Updated/Published [Cert Date - 12 or Target SOL - 30   see above]:Lavanya Rangubhotla:rangul',
'LRC Updated/Published [Cert Date - 12 or Target SOL - 30   see above]:Brandon Ferree:ferreb',
'LRC Updated/Published [Cert Date - 12 or Target SOL - 30   see above]:Patty Applegate:applepm',
'LRC Updated/Published [Cert Date - 12 or Target SOL - 30   see above]:Ryan Kominkiewicz:kominrj',
'PRC Approved [Cert Date - 12 or Target SOL - 30   see above]:Ryan Kominkiewicz:kominrj',
'PRC Approved [Cert Date - 12 or Target SOL - 30   see above]:Brandon Ferree:ferreb',
'PRC Approved [Cert Date - 12 or Target SOL - 30   see above]:Patty Applegate:applepm',
'PRC Approved [Cert Date - 12 or Target SOL - 30   see above]:Lavanya Rangubhotla:rangul',
'PRC Approved [Cert Date - 12 or Target SOL - 30   see above]:Prasad Joshi:joshipl',
'PRC Approved [Cert Date - 12 or Target SOL - 30   see above]:Matt Musec:musecmj',
'Perform Lab Rating Review [Cert Date - 12 or Target SOL - 30 see above]:Lavanya Rangubhotla:rangul',
'Perform Lab Rating Review [Cert Date - 12 or Target SOL - 30 see above]:Matt Musec:musecmj',
'Perform Lab Rating Review [Cert Date - 12 or Target SOL - 30 see above]:Prasad Joshi:joshipl',
'Perform Lab Rating Review [Cert Date - 12 or Target SOL - 30 see above]:Patty Applegate:applepm',
'Perform Lab Rating Review [Cert Date - 12 or Target SOL - 30 see above]:Ryan Kominkiewicz:kominrj',
'Perform Lab Rating Review [Cert Date - 12 or Target SOL - 30 see above]:Brandon Ferree:ferreb',
'Certification Needs Reviewed [SOL - 90 days]:Doug Friede:frieddw2',
'Emissions Validation Plan Approved [SOL - 90 days]:Scott Butzin:butzisa',
'Specify Required Emissions Certification Types [Cert Date - 38 days]:Doug Friede:frieddw2',
'Certification Date Assigned [Cert Date - 5 day]:Laura Jones:jonesla1',
'Certification Date Assigned [Cert Date - 5 day]:Karen Chen:chenz',
'FFR Launched [SOL - 8 weeks]:L4 Job Owner:l4core',
'Interlock defined [SOL - 8 weeks]:L4 Job Owner:l4core',
'PSPS Approval Complete [SOL-5 days]:L4 Job Owner:l4core',
's/w Staged [SOL - 7 days]:L4 Job Owner:l4core',
'Submit s/w MO45 request [SOL - 7 days]:L4 Job Owner:l4core',
'TSpec determined [SOL - 8 weeks]:L4 Job Owner:l4core',
'Validation Testing Complete (PPG or other) [Varies]:L4 Job Owner:l4core',
'Verify s/w available on SISweb [SOL plus 5 days]:L4 Job Owner:l4core',
'Specify Required Emissions Certification Types [Cert Date - 38 days]:Matt Roth:rothmr',
'Specify Required Emissions Certification Types [Cert Date - 38 days]:Drew Heisel:heisede',
'FFR Launched [SOL - 8 weeks]:Scott Smith:smithsr',
'FFR Launched [SOL - 8 weeks]:Drew Heisel:heisede',
'PSR Launched [varies]:Matt Roth:rothmr',
'PSR Launched [varies]:Drew Heisel:heisede',
'Exempt Label(s) Requested [once engine S/N defined]:Bill Stratton:stratwl',
"ENGINE/AIDB/TMI updates made (includes new p/n's) [SOL - 12 days]:Robert Christopher-Murphy:murphrm",
]
        

        self.LookupList = []
        self.jobDict = {}
        self.LookupItem = 'Job Number'
        self.jobColumn = jobColumn = []
        self.jobColumn.extend(self.GetColList(self.LookupItem))
        lastNum = ''
        dateKeys = ['Certification Date',
                    'Target SOL',
                    'Target TSpec Update Date',
                    'Target P/E Date',
                    'Target PRC/LRC/Engr Completion Date',
                    ]
        source = self.source
        for i, lookupItem in enumerate(self.jobColumn):
            if i > self.activeSheetHeaderRow:
                if lookupItem not in ['None',None]:
                    if lookupItem not in self.jobDict.keys():
                        self.jobDict[lookupItem] = {}
                    jobData = self.jobDict[lookupItem]
                    oldNum = (lookupItem == lastNum)
                    newNum = not oldNum
                    rowData = self.GetRowDict(i)
                    if newNum: 
                        '''
                        this is the start of a section of data for a new job number
                        '''
                        taskList = {}
                        self.jobDict[lookupItem] = rowData
                    else:
                        
                        '''
                        this is within the section of data for the last job number
                        '''
                        pass
                    lastNum = lookupItem
    #                dates = {}
    #                for key in dateKeys:
    #                    dates[key] = rowData[key+'-->AardvarkAuto']
                    taskName = rowData['WorkListItem'+'-->' + source][0]['value'][0]
                    if taskName != 'None':
                        actualDate = rowData['WorkListDate'+'-->' + source]
                        status = rowData['WorkListStatus'+'-->' + source]
                        jobData[taskName + '-->AardvarkAuto'] = actualDate
                        jobData[taskName + '__Status-->AardvarkAuto'] = status
                        #targetDate = parseTargetDate(task,dates)
                        #WorkListAssigned
                        #WorkListStatus
        pass
    
        '''
        TODO: Finish creating an interface to the aardvark auto process report
        '''    
    def CreateLookupItemReference2(self):
        '''
        This report requires multiple job number entries to be identified as containing unique values
        that will have to be appended to a list of values for a given header, specifically:
        
        WorkListAssigned
        WorkListDate    
        WorkListFilter    
        WorkListItem    
        WorkListStatus
        '''
        AardvarkColumnsList = ['EAC (or Core) setup in CDM Complete',
                               'LRC Updated/Published',
                               'PRC Approved',
                               'Perform Lab Rating Review',
                               'Certification Needs Reviewed',
                               'Emissions Validation Plan Approved',
                               'Specify Required Emissions Certification Types',
                               'Certification Date Assigned',
                               'FFR Launched',
                               'Interlock defined',
                               'PSPS Approval Complete',
                               's/w Staged',
                               'Submit s/w MO45 request',
                               'TSpec determined',
                               'Validation Testing Complete',
                               'Verify s/w available on SISweb',
                               'Specify Required Emissions Certification Types',
                               'FFR Launched',
                               'PSR Launched',
                               'Exempt Label(s) Requested',
                               "ENGINE/AIDB/TMI updates made (includes new p//n's)"
                               ]

        self.LookupList = []
        self.jobDict = {}
        self.LookupItem = 'Job Number'
        self.jobColumn = jobColumn = []
        self.jobColumn.extend(self.GetColList(self.LookupItem))
        lastNum = ''
        dateKeys = ['Certification Date',
                    'Target SOL',
                    'Target TSpec Update Date',
                    'Target P/E Date',
                    'Target PRC/LRC/Engr Completion Date',
                    ]
        source = self.source
        for i, lookupItem in enumerate(self.jobColumn):
            if i > self.activeSheetHeaderRow:
                if lookupItem not in self.jobDict.keys():
                    self.jobDict[lookupItem] = {}
                newNum = (lookupItem == lastNum)
                rowData = self.GetRowDict(i)
                if newNum: 
                    '''
                    this is the start of a section of data for a new job number
                    '''
                    taskList = {}
                    self.jobDict[lookupItem] = rowData
                else:
                    '''
                    this is within the section of data for the last job number
                    '''
                    pass
                dates = {}
                for key in dateKeys:
                    dates[key] = rowData[key+'-->AardvarkAuto']
                task = rowData['WorkListItem'+'-->' + source]
                actualDate = rowData['WorkListDate'+'-->' + source]
                
                targetDate = parseTargetDate(task,dates)
                #WorkListAssigned
                #WorkListStatus    
        
                '''
                TODO: Finish creating an interface to the aardvark auto process report
                '''
def parseTargetDate(task, dates):
    task = task[0]['value'][0]
    dateInfo1 = task.split('[')[1].split(']')[0]
    print dateInfo
    return targetDate
    sys.exit()

class metricsColumn(object):
    def __init__(self):
        self.data = {'2012': {'July' : 0,
                        'August': 0,
                        'September': 0,
                        'October': 0,
                        'November': 0,
                        'December': 0, },
               '2013': {'January': 0,
                        'February': 0,
                        'March': 0,
                        'April': 0,
                        'May': 0,
                        'June': 0,
                        'July': 0,
                        'August': 0,
                        'September': 0,
                        'October': 0,
                        'November': 0,
                        'December': 0}
               }
#def makeRules(self):
#    '''
#    Creates the rules dictionary for the parent object
#    '''
#    self.rules = {'Job #':['Job Number-->Job Number'],
#                 'Charge #': ['Charge #-->Aardvark'],
#                 'Owner': ['Posted by-->Aardvark', 'Creator-->JRS', [self.getOwner, 'Description-->JRS', 'Requestor-->JRS']],
#                 'Bore Size': ['Bore Size-->Aardvark', [self.getBoreSize, 'Platform-->JRS', 'Description-->JRS']],
#                 'Platform': ['Platform-->JRS'],
#                 'P&E Lead': [[self.getPNELead, 'Bore Size-->self', 'Platform-->JRS']],
#                 'EPC Bore Lead': ['EPC Bore Lead-->Aardvark'],
#                 'Status': ['Review Status-->JRS'],
#                 NEW_SOL_DATE_KEY: ['Target SOL-->Aardvark', 'SOL-->JRS'],
#                 'JRS SOL Date': ['SOL-->JRS'],
#                 'Standard Timeline':['Follow JRS?-->Aardvark'],
#                 'All Tasks Signed Off T-0\\/Actual Date':[[self.getAllSignedOffActual,
#                                                           'Review Status-->JRS',
#                                                           'MO45 Status Date-->JRS',
#                                                           'Engineering Status Date-->JRS',
#                                                           'Logistics Status Date-->JRS',
#                                                           'Planning Status Date-->JRS',
#                                                           'Software Status Date-->JRS',
#                                                           'Purchasing Status Date-->JRS',
#                                                           'Perf/Emissions Status Date-->JRS',
#                                                           'Specmaker/ESO Status Date-->JRS',
#                                                           'Manufacturing Engineering Status Date-->JRS',
#                                                           'Labels Status Date-->JRS',
#                                                           'Certification Status Date-->JRS',
#                                                           ]],
#                 'All Tasks Signed Off T-0\\/Variance':[[self.calculateVariance,
#                                                      'populateDate-->global',
#                                                      'JRS SOL Date-->self',
#                                                      'All Tasks Signed Off T-0\\/Actual Date-->self']],
#                 'Engineering Sign-Off\\/Target Date': ['Target PRC/LRC/Engr Completion Date-->Aardvark', [self.getTargetDate, NEW_SOL_DATE_KEY + '-->self', 'ESOTminusDays-->global', 'Job No-->JRS']],
#                 'Engineering Sign-Off\\/Actual Date': ['Engineering Status Date-->JRS'],
#                 'Engineering Sign-Off\\/Variance': [[self.calculateVariance,
#                                                      'populateDate-->global',
#                                                      'Engineering Sign-Off\\/Target Date-->self',
#                                                      'Engineering Sign-Off\\/Actual Date-->self']],
#                 'Lab Rating Chart\\/Target Date': ['Target PRC/LRC/Engr Completion Date-->Aardvark', [self.getTargetDate, NEW_SOL_DATE_KEY + '-->self', 'LRCTminusDays-->global', 'Job No-->JRS']],
#                 #'Lab Rating Chart\\/Actual Date': ['Finish-->ProjectPlan'],
#                 'Lab Rating Chart\\/Actual Date': [[self.getLRCactual, 'Finish-->ProjectPlan', 'Activity Status-->ProjectPlan', 'Job Number-->Job Number']],
#                 'Lab Rating Chart\\/Variance': [[self.calculateVariance,
#                                                 'populateDate-->global',
#                                                 'Lab Rating Chart\\/Target Date-->self',
#                                                 'Lab Rating Chart\\/Actual Date-->self']],
#                 'Production Release Checklist\\/Target Date': ['Target PRC/LRC/Engr Completion Date-->Aardvark', [self.getTargetDate, NEW_SOL_DATE_KEY + '-->self', 'PRCTminusDays-->global', 'Job No-->JRS']],
#                 'Production Release Checklist\\/Actual Date': [[self.getPRCactual,'Date_Approved-->PRC','PRC Required?-->Aardvark']],
#                 'Production Release Checklist\\/Variance': [[self.calculateVariance,
#                                                              'populateDate-->global',
#                                                              'Production Release Checklist\\/Target Date-->self',
#                                                              'Production Release Checklist\\/Actual Date-->self']],
#                 'Performance / Emissions\\/Target Date': ['Target P/E Date-->Aardvark', [self.getTargetDate, NEW_SOL_DATE_KEY + '-->self', 'PNETminusDays-->global', 'Job No-->JRS']],
#                 'Performance / Emissions\\/Actual Date': ['Perf/Emissions Status Date-->JRS'],
#                 'Performance / Emissions\\/Variance': [[self.calculateVariance,
#                                                        'populateDate-->global',
#                                                        'Performance / Emissions\\/Target Date-->self',
#                                                        'Performance / Emissions\\/Actual Date-->self']],
#                 'P and E Requirements\\/Engineering Signoff, LRC and PRC Complete': [[self.getPandEReqs,
#                                                                                       'Job #-->self',
#                                                                                       'Engineering Sign-Off\\/Actual Date-->self',
#                                                                                       'Lab Rating Chart\\/Actual Date-->self',
#                                                                                       'Production Release Checklist\\/Actual Date-->self']],
#                 'Test Specification\\/Target Date': ['Target TSpec Update Date-->Aardvark', [self.getTargetDate, NEW_SOL_DATE_KEY + '-->self', 'TSTminusDays-->global', 'Job No-->JRS']],
#                 'Test Specification\\/Actual Date': ['Actual TSpec Update Date-->Aardvark'],
#                 'Test Specification\\/Variance': [[self.calculateVariance,
#                                                        'populateDate-->global',
#                                                        'Test Specification\\/Target Date-->self',
#                                                        'Test Specification\\/Actual Date-->self']]
#                 }
        
class inputWorkbooks(object):
    """
    holds data from multiple excel files for quick processing
    """
    def __init__(self):
        self.workbooks = {}
        self.jobDict = {}
        self.jobList = []
        self.sources = []
        self.view = []
        self.CreateDataMatrix()
        self.metricsData = {}
        self.denaMetricsData = {}
        self.calcHeaders = []
        self.scoreboard = ExcelGrabScoreBoard()
        self.sbJobDict = self.scoreboard.jobDict
        self.sbJobList = self.scoreboard.LookupList
        self.scoreboardHeaders = self.scoreboard.Headers1['ScoreBoard']
        for line in self.scoreboardHeaders:
            if 'Variance' in line:
                self.calcHeaders.append(line)
		self.metricsDataHeaders = self.metricsHeaders = self.scoreboard.Headers1['Metrics']
        denaTab = 'Dena Cassidy Metrics'
        self.denaMetricsHeaders = False
        if denaTab in self.scoreboard.Headers1.keys():
            self.denaMetricsHeaders = self.scoreboard.Headers1[denaTab]
            for header in self.denaMetricsHeaders:
                newthing = metricsColumn()
                self.denaMetricsData[header] = newthing.data
        for header in self.metricsDataHeaders:
            newthing = metricsColumn()
            self.metricsData[header] = newthing.data
        self.metricsFormulaHeaders = {'% Jobs Processed by P&E': ['# of Jobs Requiring P&E Work', '# of Jobs'],
                                      'P&E per Spec\\/% Jobs on Time': ['P&E per Spec\\/# Jobs On Time', '# of Jobs Requiring P&E Work'],
                                      'P&E per Duration\\/% Jobs on Time': ['P&E per Duration\\/# Jobs On Time or Completed within 6 days of Engineering Sign-Off', '# of Jobs Requiring P&E Work'],
                                      'Engineering Sign Off\\/% Jobs on Time': ['Engineering Sign Off\\/# Jobs On Time', '# of Jobs Requiring P&E Work'],
                                      }       
        ##EE
        # of Jobs Finished    # of Jobs Incomplete    % Jobs Finished

        self.denaFormulaHeaders = {'% Jobs On Time':['# of Jobs On Time', '# of Jobs'],
                                   '% Jobs Finished':['# of Jobs Finished', '# of Jobs']}
        
        self.metricsFormulaPNELeadTemplate = {'Spec': ['LEAD per Spec\\/# Jobs On Time', 'LEAD per Spec\\/# Jobs Requiring P&E Work'],
                                      'Duration': ['LEAD per Duration\\/# Jobs On Time or Completed within 6 days of Engineering Sign-Off', 'LEAD per Spec\\/# Jobs Requiring P&E Work'],
                                      }                   
        
        self.populateDate = datetimeDotDatetime.now()
        
    def calcScoreboardValues(self, updated = False):
        """
        Calculates variances and other values that are based on values in the Scoreboard.
        Also checks to see if jobs have been dropped from JRS and flags them.
        """
        print"Calculating Variances for Scoreboard..."
        #self.calcHeaders
        
        i,j,k = pBar(self.sbJobDict)
        for jobNumber in self.sbJobDict.keys():
            i, j, k = pBar(i, j, k)
            if updated:
                self.JRSDropCheck(jobNumber)
            for header in self.scoreboardHeaders:
                if header in self.calcHeaders:
                    value, color, source = self.GetValue(jobNumber, header)
                    self.sbJobDict[jobNumber][header] = add2JobNumber(value, color)
       
        print"Done Calculating"
        
    def preFilter(self, jobNumber):
        '''
        Data from the input data dump reports is checked for this job number to see if
        it meets any of the criteria stored in the rule dictionary self.preFilters. If
        so, this function will return True - which means that the job should not be 
        displayed in the scoreboard.
        '''
        for Header in self.preFilters.keys():
            if Header in self.jobDict[jobNumber].keys():
                value = self.jobDict[jobNumber][Header][-1]['value'][0]
                for evil in self.preFilters[Header]:
                    if evil in value:
                        return True
        return False
                    
    def postFilter(self, jobNumber, header, value):
        if jobNumber == 'J9511L':
            #print "found job 'J2341X'"
            pass
        if header in self.postFilters.keys():
            for evil, rule in self.postFilters[header]:
                if rule == 'IN':
                    if evil in value:
                        #print"evil: %s found in %s for job Number %s"%(evil,value,jobNumber)
                        if jobNumber == 'J9504W' or jobNumber == 'J2012R':
                            pass
                        return False
                elif rule == '=':
                    if evil == value:
                        #print"evil: %s is value for job Number %s"%(evil,jobNumber)
                        if jobNumber == 'J9504W':
                            pass
                        return False
                elif rule == 'Not StartsWith':
                    found=False
                    includeKeys=evil.split('|')
                    for key in includeKeys:
                        if value.find(key) == 0:
                            found=True
                    return found
        return True
    
    def LRC_PRC_exlusion(self, jobNumber):
        '''
        Changes the final value for LRC or PRC actual date to 'NA' if P&E has signed off before the
        scoreboard has received the actual date from a data dump.
        '''
        jobData = self.sbJobDict[jobNumber]
        value = jobData["Performance / Emissions\\/Actual Date"][-1]['value'][0]
        if value != '':
            lrcActualDate, junk = jobData['Lab Rating Chart\\/Actual Date'][-1]['value']
            prcActualDate, junk = jobData['Production Release Checklist\\/Actual Date'][-1]['value']
            if lrcActualDate == '':
                jobData['Lab Rating Chart\\/Actual Date'][-1]['value'] = ["NA", 0]
                jobData['Lab Rating Chart\\/Variance'][-1]['value'] = ["NA", green]      
            if prcActualDate == '':
                jobData['Production Release Checklist\\/Actual Date'][-1]['value'] = ["NA", 0]
                jobData['Production Release Checklist\\/Variance'][-1]['value'] = ["NA", green]
    
    def gatherScoreboardValues(self):
        """
        Gathers the scoreboard INPUT values by applying the set of rules to whatever data is 
        available in the data dumps combined job dictionary. This will overwrite anything that is
        currently in the sbJobDict (which is created upon opening the spreadsheet)
        """
        headers = self.scoreboardHeaders
        self.sbJobDict = {}
        for jobNumber in self.sbJobList:
            if not jobNumber in self.jobDict.keys():
                self.jobDict[jobNumber] = {}
                
        i, j, k = pBar(self.jobDict)
        #print"There are %d job Numbers after combining files" % k
        badJobs = 0
        for jobNumber in self.jobDict.keys():
            bad = False
            i, j, k = pBar(i, j, k)
            """
            Prefilter the jobNumber for unacceptable data contents in data sources
            """
            bad = self.preFilter(jobNumber)
            self.sbJobDict[jobNumber] = {}
            if not bad:
                self.JRSDropCheck(jobNumber)
                for header in headers:
                    if header not in self.calcHeaders:
                        if jobNumber == 'J3423A' and 'Lab Rating Chart' in header and 'Actual' in header:
                            pass
                        value, color, source = self.GetValue(jobNumber, header)
                        self.sbJobDict[jobNumber][header] = add2JobNumber(value, color, source=source)
                for header in self.calcHeaders:
                    value, color, source = self.GetValue(jobNumber, header)
                    self.sbJobDict[jobNumber][header] = add2JobNumber(value, color)
                self.LRC_PRC_exlusion(jobNumber)
            else:
                self.sbJobDict[jobNumber]['Platform-->JRS'] = add2JobNumber('FilterOut',0)
                self.sbJobDict[jobNumber]['P&E Lead'] = add2JobNumber('NA',0)
                badJobs += 1
            #self.JRSDropCheck(jobNumber)
        print badJobs, 'were prefilterd out of appearing in the scoreboard'
        
    def JRSDropCheck(self, jobNumber):
        '''
        Checks to see if a job number was found in the current JRS report.
        If not, it will create and/or set a 'Dropped from JRS' field for this job number.
        '''
        JRSNum = self.getInputVal(jobNumber,'Job No-->JRS')
        JRSdropOut = JRSNum == False or JRSNum == '' or JRSNum == 'None'
        if JRSdropOut:
            self.sbJobDict[jobNumber]['Dropped from JRS'] = add2JobNumber('Y')
        else:
            self.sbJobDict[jobNumber]['Dropped from JRS'] = add2JobNumber('N')
    ##EE    
    def parseTargetDate(self, dataKey, jobNumber, source):
        '''
        This function only pertains to AardvarkAuto data at the moment
        given a workListTask dataKey and a jobNumber this will return the target date
        '''
        dateLookup = {'Cert Date': 'Certification Date',
                      'Target SOL': 'Target SOL',
                      'SOL': 'Target SOL',
                      'PRC/LRC/Engr Completion Date Above': 'Target PRC/LRC/Engr Completion Date'}
        exclusions = ['varies',
                      'PPG',
                      ]
        
        dataKey = dataKey.split('-->')[0]
        originalKey = dataKey
        if 'Same as' in dataKey:
            dataKey = dataKey.replace('Same as','')
            dataKey = dataKey.split('[')[1].split(']')[0].strip().rstrip()
            if dataKey in dateLookup.keys():
                dataKey = dateLookup[dataKey]+'-->'+source
                tDate,jnk = self.jobDict[jobNumber][dataKey][-1]['value']
                return tDate
        elif '-' not in dataKey:
            if 'plus' or '+' in dataKey:
                operation = '+'
            else:
                return False
        else:
            dataKey = dataKey.replace('see above', '')
            d1 = dataKey.split('[')[1].split(']')[0]
            conditions = d1.split('or')
            dayVals = []
            type = 'days'
            tDate = False
            for condition in conditions:
                noSkip = True
                tMinus = False
                plus = False
                for exclusion in exclusions:
                    if exclusion in condition:
                        noSkip = False
                        break
                if noSkip:
                    if '-' not in condition:
                        if 'plus' in condition:
                            dataKey, rest = condition.split('plus')
                            plus = True
                        elif '+' in condition:
                            plus = True
                            dataKey, rest = condition.split('+')
                    else:
                        dataKey, rest = condition.split('-')
                    dataKey = dataKey.rstrip()
                    dataKey = dataKey.strip()
                    restParts = rest.split()
                    for part in rest:
                        try:
                            tMinus = int(part)
                        except:
                            if 'weeks' in part:
                                tMinus = tMinus*7
                    dataKey = dateLookup[dataKey]+'-->'+source#self.source
                    date,jnk = self.jobDict[jobNumber][dataKey][-1]['value']
                    if isinstance(date,int):
                        date = datetimeDotDatetime(days=date)
                    if date != 'None':
                        if tMinus:
                            if plus:
                                date = date + datetimeDotTimedelta(days=tMinus)
                            else:
                                date = date - datetimeDotTimedelta(days=tMinus)
                        dayVals.append(date)
            if len(dayVals)>1:
                try:
                    dayVals.sort()
                    tDate = dayVals[0]
                except:
                    pass
            elif len(dayVals)==1:
                tDate = dayVals[0]
#            if not tDate:
#                print 'JobNumber:',jobNumber,originalKey
            return tDate
        
    def getScoreboardPNELeads(self):
        peLeads = []
        checkLeads = []
        for jobNumber in self.sbJobList:
            if jobNumber in self.sbJobDict.keys():
                peLead = self.sbJobDict[jobNumber]['P&E Lead'][-1]['value'][0]
                checkLead = peLead.lower()
                if checkLead not in checkLeads:
                    checkLeads.append(checkLead)
                    peLeads.append(peLead)
        return peLeads
    ##EE
    def getMetricsPNELeads(self):
        PNELeads = self.getScoreboardPNELeads()
        for header in self.metricsDataHeaders:
            splitHeader = header.split("\\/")
            topHeader = splitHeader[0]
            Lead = topHeader.split()[0]
            if Lead in PNELeads:
                if len(splitHeader) > 1:
                    bottomHeader = splitHeader[1]
                    if '% Jobs on Time' in bottomHeader:
                        sources = self.metricsFormulaPNELeadTemplate[topHeader.split()[2]]
                        formula = []
                        for source in sources:
                            newSource = source.replace('LEAD', Lead)
                            formula.append(newSource)
                        self.metricsFormulaHeaders[header] = formula
#                    else:
#                        self.metricsPNELeadHeaders.append(header)

                
                      
    def calcMetricsValues(self, jobList, tabs):
        global testData
        self.getMetricsPNELeads() ##EE
        i, j, k = pBar(jobList)
        for jobNumber in jobList:
            i, j, k = pBar(i, j, k)
            self.calcAllMetrics(jobNumber, tabs)
        #print testData
        checkHeaders = ['P&E per Duration\\/# Jobs On Time or Completed within 6 days of Engineering Sign-Off', 'P&E per Duration\\/# Jobs Late and Completed outside of 6 days of Engineering Sign-Off']
#        for job in testData.keys():
#            jobData = testData[job]
#            test = 0
#            for header in checkHeaders:
#                if header in jobData.keys():
#                    test += jobData[header]
            #if test >1:
                #print job
            
        self.calcMetricPercents()
        self.calcMetricPercents(tab = 'Dena Cassidy Metrics')
        

    def calcMetricPercents(self, tab = 'Metrics'):
        if tab == 'Dena Cassidy Metrics':
            headers = self.denaMetricsHeaders
            formulaHeaders = self.denaFormulaHeaders
            data = self.denaMetricsData
        else:
            headers = self.metricsDataHeaders
            formulaHeaders = self.metricsFormulaHeaders
            data = self.metricsData
        
        for header in headers:
            
            if header in formulaHeaders.keys():
                if header == '% Jobs On Time':
                    pass
                years = data[header]
                for year in years.keys():
                    months = years[year]
                    for month in months.keys():
                        numerator = data[formulaHeaders[header][0]][year][month]
                        denominator = data[formulaHeaders[header][1]][year][month]
                        if denominator != 0:
                            denominator += 0.0
                            answer = numerator / denominator #*100
                            data[header][year][month] = answer
                        else:
                            if tab != 'Metrics':
                                if header == '% Jobs On Time':
                                    pass
                            data[header][year][month] = 0
        pass
                            
                
    def calcAllMetrics(self, jobNumber, tabs):
        jobData = self.sbJobDict[jobNumber]
        year, month = self.getDate(jobData)
        Includable = False
        fakeHeader=self.metricsData.keys()[0]
        if str(year) in self.metricsData[fakeHeader].keys() and monthsOfTheYear[month] in self.metricsData[fakeHeader][str(year)]:
            Includable = True
        if Includable:
            if 'Metrics' in tabs or 'All' in tabs:
                for header in self.metricsDataHeaders:
                    if not header in self.metricsFormulaHeaders.keys():
                            self.metricsData[header][str(year)][monthsOfTheYear[month]] += self.calcMetric(header, jobData)
                
            if self.denaMetricsHeaders and 'Dena Cassidy Metrics' in tabs or 'All' in tabs:
                for header in self.denaMetricsHeaders:
                    if not header in self.denaFormulaHeaders.keys():
                        headerData = self.denaMetricsData[header]
                        theMonth = monthsOfTheYear[month]
                        theYear = str(year)
                        self.denaMetricsData[header][str(year)][monthsOfTheYear[month]] += self.calcMetric(header, jobData)
        
    def getDate(self, jobDict):
        date = jobDict[NEW_SOL_DATE_KEY][-1]['value'][0]
        try:
            year = date.year
            month = date.month
        except:
            return False, False
        return year, month - 1
        
    def calcMetric(self, header, jobDict):
        #print"performing metric calc"
        global testData
        value = 0
        PNELead = jobDict['P&E Lead'][-1]['value'][0]
        peActualDate = jobDict['Performance / Emissions\\/Actual Date'][-1]['value'][0]
        peVariance = jobDict['Performance / Emissions\\/Variance'][-1]['value'][0]
        peVarianceColor = jobDict['Performance / Emissions\\/Variance'][-1]['value'][1]
        badStuff = ['', 'NA']
        esVariance = jobDict['Engineering Sign-Off\\/Variance'][-1]['value'][0]
        esVarianceColor = jobDict['Engineering Sign-Off\\/Variance'][-1]['value'][1]
        jobNumber = jobDict['Job #'][-1]['value'][0]
        denaDone = self.getLVal(jobNumber,'All Tasks Signed Off T-0\\/Actual Date')
        denaVariance = self.getLVal(jobNumber,'All Tasks Signed Off T-0\\/Variance')     
        
        
        month = jobDict[NEW_SOL_DATE_KEY][-1]['value'][0].month
        year = jobDict[NEW_SOL_DATE_KEY][-1]['value'][0].year
        
        ##EE
        titleLead = header.split()[0]
        genericHeader = header.replace(titleLead, 'LEAD')
        '''
            Changing to Jobs completed in alloted time:
            
            Alloted time is 6 days after whichever of these dates comes last: 
                Engineering Signoff Actual, LRC Actual, PRC Actual.
        '''

        if header == '# of Jobs':
            '''
            Every Job gets counted
            '''
            value = 1

        elif header == '# of Jobs Requiring P&E Work':
            '''
            Jobs that do not have blank or 'NA' for P and E Actual Date
            '''
            if peActualDate not in badStuff:
                value = 1

        elif header == 'P&E per Spec\\/# Jobs On Time':
            '''
            Jobs that have good P E variance Color and variance is not blank or 'NA'
            '''
            if peVarianceColor == good and peVariance not in badStuff:
                value = 1

        elif header == 'P&E per Spec\\/# Jobs Late':
            if peVarianceColor == bad and peVariance not in badStuff:
                value = 1

        elif header == 'P&E per Duration\\/# Jobs On Time or Completed within 6 days of Engineering Sign-Off':
            '''
            Jobs that have a P & E date, and Duration Variance >= -6 or P E variance is on time
            '''
            #print'calculating stuff'
            #if jobNumber in ['J3045T']:#,'J2333P']:
                #pass
            if peVariance not in badStuff and (peVarianceColor == good or self.calculatePneEngVariance(jobDict)):
                value = 1
                #if jobNumber in ['J3045T','J2333P']:
                    #pass
                    #print"Job Number:",jobNumber,"Value:",value

        elif header == 'P&E per Duration\\/# Jobs Late and Completed outside of 6 days of Engineering Sign-Off':
            #print 'Checking duration stuff'
            #if jobNumber in ['J3045T']:#,'J2333P']:
                #pass
            if peVariance not in badStuff and (peVarianceColor == bad and not self.calculatePneEngVariance(jobDict)):
                value = 1

        elif header == 'Engineering Sign Off\\/# Jobs On Time':
            if esVarianceColor == good and esVariance not in badStuff and peActualDate not in badStuff:
                value = 1

        elif header == 'Engineering Sign Off\\/# Jobs Late':
            if esVarianceColor == bad and peActualDate not in badStuff:
                value = 1      
        ##EE        
        elif genericHeader == 'LEAD per Spec\\/# Jobs':
            if PNELead == titleLead:
                value = 1
                    
        elif genericHeader == 'LEAD per Spec\\/# Jobs Requiring P&E Work':
            if PNELead == titleLead and peActualDate not in badStuff:
                value = 1

        elif genericHeader == 'LEAD per Spec\\/# Jobs On Time':
            if PNELead == titleLead and peActualDate not in badStuff and peVarianceColor == good:
                value = 1

        elif genericHeader == 'LEAD per Spec\\/# Jobs Late':
            if PNELead == titleLead and peActualDate not in badStuff and peVarianceColor == bad:
                value = 1

        elif genericHeader == 'LEAD per Duration\\/# Jobs On Time or Completed within 6 days of Engineering Sign-Off':
            if PNELead == titleLead and peActualDate not in badStuff and peVariance not in badStuff and (peVarianceColor == good or self.calculatePneEngVariance(jobDict)):
                value = 1

        elif genericHeader == 'LEAD per Duration\\/# Jobs Late and Completed outside of 6 days of Engineering Sign-Off':
            if PNELead == titleLead and peActualDate not in badStuff and peVariance not in badStuff and (peVarianceColor == bad and not self.calculatePneEngVariance(jobDict)):
                value = 1
                
        elif header == '# of Jobs Finished':
            if denaDone:
                value = 1
                
        elif header == '# of Jobs Incomplete':
            if not denaDone:
                value = 1
                
        elif header == '# of Jobs On Time':
            if denaDone:
                late = denaVariance<0
                if not late:
                    value = 1
            
        elif header == '# of Jobs Late':
            if denaDone:
                late = denaVariance<0
                if late:
                    value = 1
#        else:
#            print header
        
        if month == 3 and year == 2013:
            if jobNumber not in testData.keys():
                testData[jobNumber] = {}
            if header not in testData[jobNumber].keys():
                testData[jobNumber][header] = value
                
        return value

    def createMetricsView(self, tab = 'Metrics'):
        metricsRows = []
        rowHeaders = []
        dataView = []
        fileLines = []
        
        startPoints = self.scoreboard.startPoints[tab]
        if tab == 'Dena Cassidy Metrics':
            fakeHeader = self.denaMetricsData.keys()[0]
            headers = self.denaMetricsHeaders
            firstLine = '\t'.join(headers)
            data = self.denaMetricsData
            
        else:
            fakeHeader = self.metricsData.keys()[0]
            headers = self.metricsDataHeaders
            firstLine = '\t'.join(headers)
            data = self.metricsData
            
        fileLines.append(firstLine + '\n')
        for year in years:
            for month in monthsOfTheYear:
                if month in data[fakeHeader][year].keys():
                    rowHeaders.append(year + '-->' + month)
        for monthYear in rowHeaders:
            year, month = monthYear.split('-->')
            row = []
            fileLine = []
            for header in headers:
                value = str(data[header][year][month])
                row.append(value)
            dataView.append(row)
            fileLine = '\t'.join(row)
            fileLines.append(fileLine + '\n')
        CPL4.xl_writeRange3(self.scoreboard.excel.ActiveWorkbook, tab, startPoints, dataView)

    def createScoreBoardView(self, updated = False):
        '''
        Final step before data is printed in Excel. This will perform post filtering and
        post calculations on data that would otherwise appear in the scoreboard. Jobs that 
        have been marked by setting their 'P&E Lead' column to 'NA' will now be excluded from
        the scoreboard and metrics calculations. 
        
        ***
        Any changes made at this point will be reflected in the metrics calculations.
        ***
        
        ''' 
        print"Formatting and writing Scoreboard View Data for Excel"
        startPoints = self.scoreboard.startPoints['ScoreBoard']
        jobLines = []
        cLines = []
        hLines = []
        """if a jobNumber is in the scoreboard database file but was not present in the
        actual scoreboard (due to hiding of jobs that lack sufficient information), it 
        is appended to the list of job numbers displayed in the current view that will
        be evaluated to see if they contain enough information to be visible. This way
        jobs are kept in the order that they were viewed in last by the user, and 
        additional jobs that may now be available for viewing will show up at the very
        bottom of the scoreboard"""
        
        hiddenJobs = []
        toHide = []
        
        for jobNumber in self.sbJobDict.keys():
            if 'J9511L' == jobNumber:
                pass
            if jobNumber not in self.sbJobList:
                self.sbJobList.append(jobNumber)
            numVal = jobVal(self.sbJobDict, jobNumber, 'Job #')
            if jobNumber != numVal or not numVal:
                hiddenJobs.append(jobNumber)
                self.sbJobList.remove(jobNumber)
        '''
        Master job number callout for printing to excel
        '''
        self.sbJobList = set(self.sbJobList)
        self.sbJobList = list(self.sbJobList)
        for jobNumber in self.sbJobList: 
            
            if jobNumber in self.sbJobDict.keys() and jobNumber not in hiddenJobs:
                jobData = self.sbJobDict[jobNumber]
                worthSeeing = True
                for header in jobData.keys():
                    if header in self.postCalcHeaders:
                        value,color,source = self.GetValue(jobNumber, header, postCalc = True)
                        jobData[header].extend(add2JobNumber(value, color = color, source = source))
                    try:
                        value= jobData[header][-1]['value'][0]
                    except:
                        pass
                    """
                    Postfilter the rule-based scoreboard values for this jobNumber and check it for suspect violations
                    """
                    worthSeeing = self.postFilter(jobNumber, header, value)
                    if not worthSeeing:
                        toHide.append(jobNumber)
                        break
                if worthSeeing:
                    if jobNumber == 'J5307H':
                        pass
                    self.SuspectCheck(jobNumber)
                    jobLine, cLine, hLine = self.makeScoreboardJobRow(jobData)
                    jobLines.append(jobLine)
                    cLines.append(cLine)
                    hLines.append(hLine)
            else:
                toHide.append(jobNumber)
        for num in toHide:
            if num in self.sbJobList:
                self.sbJobList.remove(num)
                '''
                TODO:
                This is only for use when calculating metrics
                '''

        targetSheet = "ScoreBoard"
        activesheet = self.scoreboard.excel.Worksheets("ScoreBoard")
        LastRow = activesheet.Rows.Count
        
        self.scoreboard.excel.Worksheets("ScoreBoard").Rows("5:65536").Value = ""
        self.scoreboard.excel.Worksheets("ScoreBoardColor").Rows("5:65536").Value = ""
        self.scoreboard.excel.Worksheets("TimeHistory").Rows("5:65536").Value = ""
        self.scoreboard.excel.Worksheets("ScoreBoard").Rows("5:65536").Interior.ColorIndex = 0
        self.scoreboard.excel.Worksheets("ScoreBoard").Cells.ClearComments()
        
        self.scoreboard.excel.Worksheets("ScoreBoardColor").Visible = True
        self.scoreboard.excel.Worksheets("TimeHistory").Visible = True
        CPL4.xl_writeRange3(self.scoreboard.excel.ActiveWorkbook, 'ScoreBoard', startPoints, jobLines)
        CPL4.xl_writeRange3(self.scoreboard.excel.ActiveWorkbook, 'ScoreBoardColor', startPoints, cLines)
        CPL4.xl_writeRange3(self.scoreboard.excel.ActiveWorkbook, 'TimeHistory', startPoints, hLines)
        #if updated:
        self.DateScoreBoard()
        self.scoreboard.excel.Worksheets("ScoreBoardColor").Visible = False
        self.scoreboard.excel.Worksheets("TimeHistory").Visible = False
        
    def DateScoreBoard(self):
        '''
        will change the Population Date: value in the score board (at cell "D2") to show 
        the current date.
        
        ToDo: make the current update date be saved into the .sdf file and load it without 
            interfering with jobdict information somehow. (since the .sdf file only contains
            job number and needs a special entry for metadata).
        '''
        #print"DatingScoreboard, lastUpdateDate:", lastUpdateDate
        #sleep(3)
        if lastUpdateDate:
            now = lastUpdateDate#datetimeDotDatetime.now()
            todayStr = now.strftime("%m/%d/%Y")
            self.scoreboard.excel.Worksheets('ScoreBoard').Range("C2").Value = "Last Updated: " + todayStr
        
    def makePretty(self, header, data):
        if header == 'EPC Bore Lead':
            data = ' '.join(data.split()[:2])
        return data
    
    def getSuspectColor(self, jobNumber, reasons):
        '''
        grabs the most severe color from the suspect color rankings that is present in the
        suspect violations for this instance.
        '''
        colorRank
        color = '0'
        worst = len(colorRank)-1
        if jobNumber == 'J9273P':
            pass
        if len(reasons)>0:

            for violation,color in self.suspectRules:
                if violation in reasons:
                    goodness = colorRank.index(color)
                    if goodness < worst:
                        worst = goodness
            color = colorRank[worst]
        return color
        
    def makeScoreboardJobRow(self, jobData):
        jobLine = []
        cLine = []
        hLine = []
        for header in self.scoreboardHeaders:
            if header in jobData.keys():
                value, color = jobData[header][-1]['value']
                color = colorRedef(color)
#                if 'Lab Rating Chart' in header and 'Actual Date' in header:
#                    pass
                manEntry = jobData[header][-1]['manEntry']
                value = self.makePretty(header, value)
                jobLine.append(str(value))
                hstr = ''
                if header == 'Job #':
                    color = '0'
                    if 'Suspect' in jobData.keys():
                        reasons = []
                        isSuspect = False
                        for item in jobData['Suspect']:
                            date = str(item['date'])
                            user = str(item['user'])
                            value = str(item['value'][0])
                            if value != 'False' and value:
                                oldWay = False
                                if oldWay:
                                    hstr += ("%s-%s: %s\n" % (date[0:10], user, value))
                                else:
                                    hstr += ("%s\n" % (value))
                                isSuspect = True
                        if isSuspect:
                            jobNumber = jobData['Job #'][-1]['value'][0]
                            if jobNumber == 'J9273P':
                                pass
                            value = jobData['Suspect'][-1]['value'][0]
                            #values = value.replace('\n',' ')
                            values = value.split('\n')
                            reasons.extend(values)
                            
                            color = self.getSuspectColor(jobNumber, reasons)
                    cLine.append(color)
                else:
                    cLine.append(str(color))
                
                if (len(jobData[header]) > 1 and 'Job #' not in header) or (len(jobData[header]) == 1 and manEntry) or header in showAllHistoryColumns:
                    #i = 0
                    for item in jobData[header]:
                        source = ''
                        date = str(item['date'])
                        user = str(item['user'])
                        value = str(item['value'][0])
                        if 'source' in item.keys():
                            try:
                                source = '-' + item['source']
                            except:
                                pass
                                source = 'self'
                        hstr += ("%s-%s%s: %s\n" % (date[0:10], user, source, value))
                if len(hstr) > 747:
                    line1 = hstr.split('\n')[0] + '\n'
                    line2 = '...\n'
                    rest = hstr[-746:]
                    hstr = line1 + line2 + rest
                hLine.append(hstr)
            else:
                jobLine.append('')
                cLine.append('0')
                hLine.append('')
        return jobLine, cLine, hLine
    
    def calculatePneEngVariance_original(self, jobDict):
        peActualDate = jobDict['Performance / Emissions\\/Actual Date'][-1]['value'][0]
        esActualDate = jobDict['Engineering Sign-Off\\/Actual Date'][-1]['value'][0]
        variance = ""
        if peActualDate != "NA" and esActualDate != "NA" and esActualDate != "":
            if peActualDate == "":
                peEsVariance = esActualDate - self.populateDate
            else:
                peEsVariance = esActualDate - peActualDate
            variance = peEsVariance.days
            
        if variance != "":
            if abs(variance) <= self.PNEminusESOLRCPRC:
                return True
            else:
                return False
        else:        
            return False 
        
    def calculatePneEngVariance(self, jobDict):
        #print'calculating stuff'
        peActualDate = jobDict['Performance / Emissions\\/Actual Date'][-1]['value'][0]
        esActualDate = jobDict['Engineering Sign-Off\\/Actual Date'][-1]['value'][0]
        jobNumber = jobDict['Job #'][-1]['value'][0]
        badStuff = ['', 'NA']

        variance = ""
        '''
        Jobs that have P E date, and engineering signoff date
        '''
        if peActualDate not in badStuff and esActualDate not in badStuff:
            date1 = []
            PRCa = jobDict['Production Release Checklist\\/Actual Date'][-1]['value'][0]
            if isinstance(PRCa,datetimeDotDatetime):
                date1.append(PRCa)
            LRCa = jobDict['Lab Rating Chart\\/Actual Date'][-1]['value'][0]
            if isinstance(LRCa,datetimeDotDatetime):
                date1.append(LRCa)
            ESOa = esActualDate
            if isinstance(ESOa,datetimeDotDatetime):
                date1.append(ESOa)
            dates = []
            for date in date1:
                if date not in badStuff:
                    dates.append(date)
            PNEa = peActualDate
            alottedDate = getLastDate(dates, style='datetime')
            if alottedDate:
                peEsVariance = alottedDate - peActualDate
                variance = peEsVariance.days
            else:
                variance = ''

        if variance != "":
            if variance >= -self.PNEminusESOLRCPRC:
                return True
            else:
                return False
        else:        
            return False 
    
    def addFile(self, filePath, sourceType):
        if sourceType == 'PRC':
            newFile = ExcelGrabPRC(filePath, True)
        elif sourceType in ['JRS', 'JRSG', 'JRSM']:
            newFile = ExcelGrabJRS(filePath, True)
        elif sourceType == 'Aardvark':
            newFile = ExcelGrabAardvark(filePath, True)
        elif sourceType == 'AardvarkAuto':
            newFile = ExcelGrabAardvarkAuto(filePath, True)
        elif sourceType == 'ProjectPlan': 
            newFile = ExcelGrabProjectPlan(filePath, True)

        self.workbooks[filePath] = newFile
        if not sourceType in self.sources:
            self.sources.append(sourceType)
#        bads = ['Batch', 'ACP']
        for jobNumber in newFile.jobDict.keys():
            if jobNumber in self.jobDict.keys():# and ok2Add:
                oldData = self.jobDict[jobNumber]
                newData = newFile.jobDict[jobNumber]
                oldData.update(newData)
                sourceList = oldData['Source'][-1]['value'][0]
                sourceList.append(sourceType)
                oldData['Source'] = add2JobNumber(sourceList)
            else:
                newData = newFile.jobDict[jobNumber]
                newData['Source'] = add2JobNumber([sourceType])
                self.jobDict[jobNumber] = newData
        pass
    
    def Export2CSV(self, path):
        csvFile = open(path, 'w')
        head, ext = os.path.splitext(path)
        cPath = head + '_color' + ext
        csvCFile = open(cPath, 'w')
        fileHeaders = []
        cFileHeaders = []
        fileLines = []
        cFileLines = []
        manualHeaders = ['Job Number', 'Source']
        manualHeaders.extend(self.scoreboardHeaders)
        manualColors = ['0', '0']
        fileHeaders.extend(manualHeaders)
        cFileHeaders.extend(manualColors)
        for jobNumber in self.jobDict.keys():
            job = self.jobDict[jobNumber]
            for header in job.keys():
                if not header in fileHeaders:
                    fileHeaders.append(header)
                    cFileHeaders.append('0')
        headerLine = '\t'.join(fileHeaders) + '\n'
        cHeaderLine = '\t'.join(cFileHeaders) + '\n'
        fileLines.append(headerLine)
        cFileLines.append(cHeaderLine)
        for jobNumber in self.jobDict.keys():
            jobVals = []
            colorVals = []
            job = self.jobDict[jobNumber]
            for header in fileHeaders:
                if header == 'Job Number':
                    value = jobNumber
                    color = '0'
                elif header in job.keys():
                    try:
                        value = str(job[header][-1]['value'][0])
                        color = str(job[header][-1]['value'][1])
                    except:
                        value = str(job[header][0])
                        color = str(job[header][1])
                else:
                    value = ''
                    color = '0'
                jobVals.append(value)
                colorVals.append(str(color))
            jobLine = '\t'.join(jobVals) + '\n'
            cLine = '\t'.join(colorVals) + '\n'
            fileLines.append(jobLine)
            cFileLines.append(cLine)
        csvFile.writelines(fileLines)
        csvCFile.writelines(cFileLines)
        csvFile.close()
        csvCFile.close()
        
    def getAllSignedOffActual(self, inputs, sources):
        '''
        returns the latest date of all task dates that have been signed off if they are all signed off,
        otherwise it will return ''
        
        engineering Status Date must be a date or 'NA'
        
        inputs are in this order:
       #'MO45 Status Date-->JRS',
       'Engineering Status Date-->JRS',
       'Logistics Status Date-->JRS',
       'Planning Status Date-->JRS',
       'Software Status Date-->JRS',
       'Purchasing Status Date-->JRS',
       'Perf/Emissions Status Date-->JRS',
       'Specmaker/ESO Status Date-->JRS',
       'Manufacturing Engineering Status Date-->',
       'Labels Status Date-->JRS',
       'Certification Status Date-->JRS',
       ],
        '''
        namedInput = {}
        dates = []
        inputDates = inputs[1:-1]
        reviewStatus = inputs[0]
        if reviewStatus == 'Completed':
            for thing in inputDates:
                if thing not in ['NA', 'None']:
                    dates.append(thing)
            #print dates
            value = getLastDate(dates, style='datetime', jobNumber = inputs[-1])
            if not value:
                value='$blank'
                
        else:
            value = ''
        color = 0
        source = 'JRS'
        return value, color, source
    
    def getPandEReqs(self,inputs,sources):
        '''
        determines if Engineering Signoff, LRC, and PRC have actual Dates
        '''
#        print 'inputs:', inputs
        if '' not in inputs and 'Not Found' not in inputs:#'None' not in inputs and '' not in inputs:
            value, color = 'Yes', green
        else:
            value, color = 'No', red
        #print 'shitBALLS:',inputs, value
        return value, color, 'self'
    
    def CreateDataMatrix(self):
        """
        The TminusDays indicate target date lead times for various tasks using SOL (Start On Line) Date as the
        reference. i.e. PNETminusDays = 24 means that the P & E target date will be set as 24 days prior to the
        SOL Date.
        """
        self.ESOTminusDays = 30 #Engineering Signoff target date
        self.LRCTminusDays = 30 #LRC target date
        self.PRCTminusDays = 30 #PRC target date
        self.PNETminusDays = 24 #P & E target date
        self.TSTminusDays = 21 #test spec target date
        self.PNEminusESOLRCPRC = 6 #days allowed to elapse after the latest of ESO, LRC, PRC actual dates
        """
        The self.rules is a priority list that indicates in what order and what sources and/or functions
        should be used to find a value for a scoreboard column. The format is as follows:
        
        <scoreboard column label> : [priority list]
        
        the priority list can contain direct references: 'Charge #-->Aardvark'
        where the source document will be an Aardvark report and the column label will be 'Charge #'
        
        the priority list can also contain sublists of a function with its inputs: [self.getOwner, 'Description-->JRS', 'Requestor-->JRS']
        where the first entry (self.getOwner) is the function and all other entries are direct references that will be evaluated and 
        then passed to the function as a list of input arguments and their sources.
        
        the priority list is evaluated from left to right. If a value is not found from a direct reference or function, then the next
        item in the list will be evaluated until a nonblank value is returned or the end of the priority list is reached, in which
        case a blank value is returned.
        """
        #makeRules(self)
        self.rules = {'Job #':['Job Number-->Job Number'],
                      'Dropped from JRS': ['Dropped from JRS-->self'],
                 'Charge #': ['Charge #-->Aardvark'],
                 'Owner': ['Posted by-->Aardvark', 'Creator-->JRS', [self.getOwner, 'Description-->JRS', 'Requestor-->JRS']],
                 'Bore Size': ['Bore Size-->Aardvark', [self.getBoreSize, 'Platform-->JRS', 'Description-->JRS','Job Number-->Job Number']],
                 'Platform': ['Platform-->JRS'],
                 'P&E Lead': [[self.getPNELead, 'Bore Size-->self', 'Platform-->JRS','Job Number-->Job Number']],
                 'EPC Bore Lead': ['EPC Bore Lead-->Aardvark'],
                 'Status': ['Review Status-->JRS'],
                 NEW_SOL_DATE_KEY: ['Target SOL-->Aardvark', 'SOL-->JRS'],
                 'JRS SOL Date': ['SOL-->JRS'],
                 'Standard Timeline':['Follow JRS?-->Aardvark'],
                 'All Tasks Signed Off T-0\\/Actual Date':[[self.getAllSignedOffActual,
                                                           'Review Status-->JRS',
                                                           'MO45 Status Date-->JRS',
                                                           'Engineering Status Date-->JRS',
                                                           'Logistics Status Date-->JRS',
                                                           'Planning Status Date-->JRS',
                                                           'Software Status Date-->JRS',
                                                           'Purchasing Status Date-->JRS',
                                                           'Perf/Emissions Status Date-->JRS',
                                                           'Specmaker/ESO Status Date-->JRS',
                                                           'Manufacturing Engineering Status Date-->JRS',
                                                           'Labels Status Date-->JRS',
                                                           'Certification Status Date-->JRS',
                                                           ]],
                 'All Tasks Signed Off T-0\\/Variance':[[self.calculateVariance,
                                                      'populateDate-->global',
                                                      'JRS SOL Date-->self',
                                                      'All Tasks Signed Off T-0\\/Actual Date-->self']],
                 'Engineering Sign-Off\\/Target Date': ['Target PRC/LRC/Engr Completion Date-->Aardvark', [self.getTargetDate, NEW_SOL_DATE_KEY + '-->self', 'ESOTminusDays-->global', 'Job No-->JRS']],
                 'Engineering Sign-Off\\/Actual Date': [[self.getEngineeringActual,
                                                         'Engineering Status Date-->JRS',
                                                         'Engineering Approved-->JRS',
                                                         'Dropped from JRS-->self',
                                                         'Job Number-->self']],
                 'Engineering Sign-Off\\/Variance': [[self.calculateVariance,
                                                      'populateDate-->global',
                                                      'Engineering Sign-Off\\/Target Date-->self',
                                                      'Engineering Sign-Off\\/Actual Date-->self']],
                 'Lab Rating Chart\\/Target Date': ['Target PRC/LRC/Engr Completion Date-->Aardvark', [self.getTargetDate, NEW_SOL_DATE_KEY + '-->self', 'LRCTminusDays-->global', 'Job No-->JRS']],
                 #'Lab Rating Chart\\/Actual Date': ['Finish-->ProjectPlan'],
                 'Lab Rating Chart\\/Actual Date': [[self.getLRCactual, 'Finish-->ProjectPlan', 'Activity Status-->ProjectPlan', 'Job Number-->Job Number']],
                 'Lab Rating Chart\\/Variance': [[self.calculateVariance,
                                                 'populateDate-->global',
                                                 'Lab Rating Chart\\/Target Date-->self',
                                                 'Lab Rating Chart\\/Actual Date-->self']],
                 'Production Release Checklist\\/Target Date': ['Target PRC/LRC/Engr Completion Date-->Aardvark', [self.getTargetDate, NEW_SOL_DATE_KEY + '-->self', 'PRCTminusDays-->global', 'Job No-->JRS']],
                 'Production Release Checklist\\/Actual Date': [[self.getPRCactual,'Date_Approved-->PRC','PRC Required?-->Aardvark']],
                 'Production Release Checklist\\/Variance': [[self.calculateVariance,
                                                              'populateDate-->global',
                                                              'Production Release Checklist\\/Target Date-->self',
                                                              'Production Release Checklist\\/Actual Date-->self']],
                 'Performance / Emissions\\/Target Date': ['Target P/E Date-->Aardvark', [self.getTargetDate, NEW_SOL_DATE_KEY + '-->self', 'PNETminusDays-->global', 'Job No-->JRS']],
                 'Performance / Emissions\\/Actual Date': [[self.getPnEActual,
                                                            'Dropped from JRS-->self',
                                                            'Perf/Emissions Status Date-->JRS',
                                                            'Job Number-->self']],
                 'Performance / Emissions\\/Variance': [[self.calculateVariance,
                                                        'populateDate-->global',
                                                        'Performance / Emissions\\/Target Date-->self',
                                                        'Performance / Emissions\\/Actual Date-->self']],
                 'P and E Requirements\\/Engineering Signoff, LRC and PRC Complete': [[self.getPandEReqs,
                                                                                       'Job #-->self',
                                                                                       'Engineering Sign-Off\\/Actual Date-->self',
                                                                                       'Lab Rating Chart\\/Actual Date-->self',
                                                                                       'Production Release Checklist\\/Actual Date-->self']],
                 'Test Specification\\/Target Date': ['Target TSpec Update Date-->Aardvark', [self.getTargetDate, NEW_SOL_DATE_KEY + '-->self', 'TSTminusDays-->global', 'Job No-->JRS']],
                 'Test Specification\\/Actual Date': ['Actual TSpec Update Date-->Aardvark'],
                 'Test Specification\\/Variance': [[self.calculateVariance,
                                                        'populateDate-->global',
                                                        'Test Specification\\/Target Date-->self',
                                                        'Test Specification\\/Actual Date-->self']]
                 }
        
        #The following keys identify specific scoreboard headers that don't play by the 
        # above defined rules.
        self.headerExceptions = {'CoCOE\\/':'AardvarkAuto',
                                    'EPC Bore\\/':'AardvarkAuto',
                                    'ERC\\/':'AardvarkAuto',
                                    'L4 Core\\/':'AardvarkAuto',
                                    'L5\\/':'AardvarkAuto',
                                    'P/E\\/':'AardvarkAuto',
                                    }
        
        #Jobs that contain any values for the following data sources will be excluded
        self.preFilters = {'Platform-->JRS':['ACP',
                                             'Batch',
#                                             '3408',
#                                             '3412',
#                                             'C27',
#                                             'C32',
#                                             'C140',
                                             ],
                           'Application-->JRS':['ACP',
                                                'Batch',
                                                ],
                           'Description-->JRS':[#'3408',
#                                                '3412',
#                                                'C27',
#                                                'C32',
#                                                'C140',
                                                'Batch',
                                                ],
                           }
        
        #Jobs that have the following values for the following headers (after scoreboard is populated) will be excluded
        self.postFilters = {'P&E Lead':[['NA', '='],
                                        ['', '='],
                                        ],
                            'Owner':[['Blankenship', 'IN'],
                                     ['Jason Hudgens', 'IN']
                                     ],
                            'Job #':[['J|ARD','Not StartsWith'],
                                     ]
                            }
        
        #Jobs that fail the following tests will be marked as suspicious with the accompanying colors
        self.suspectRules = [('JRS SOL Date < Its time history date',periwinkle),
                              ('Part numbers changed after ESO Signed Off',pinkPlus),
                              ('P&E Tdate - ESO Tdate < 6 days',tan),
                              ('SOL Date - P&E Tdate < 24 days',tan),#tan), #CHANGE BACK
                              ('P&E Lead = Cancelled',periwinkle),
                              ('Dropped from JRS',periwinkle)
                              ]
        '''
        Color Ranking Definition
        colorRank = [red, #just for testing
                     pinkPlus, #Some extreme situation to alert everyone about
                     periwinkle, #job no longer exists (canceled, dropped from JRS, etc.)
                     orange, # something bad but job is still around
                     tan, # basic warning for date innacuracy warning
                     white, #nothing is wrong
                     ]
        '''
        
        self.postCalcHeaders = ['P and E Requirements\\/Engineering Signoff, LRC and PRC Complete',
                                ]
        
        #Jobs that have the following values for the 
        self.transforms = {}
        
        #The following are rules that determine P&E Lead assignments
        
        self.getPneRules(pneRulesPath)
#        self.i6Leads = i6Leads ={'Lehman': ['C7','C8.8','C9','C9.3'],
#                                 'Pichla': ['C10','C11','C12','C13'],
#                                 'Tamma': ['C15','C16','C17','C18'],
#                                }
#
#        self.vees = vees = ['C27','C32','C30','C140','C175','3408','3412']
        
        self.i6toLead = i6toLead = {}
        self.i6s = i6s = []
        for lead in self.i6Leads.keys():
            for bore in self.i6Leads[lead]:
                i6toLead[bore] = lead
                i6s.append(bore)
#        def getLead(boresize):
#            
#            indexes = ['Lehman','Pichla','Tamma']
#            i6Leads = [['C7','C8.8','C9','C9.3'],
#                       ['C10','C11','C12','C13'],
#                       ['C15','C16','C17','C18']]
#            i6s = ['C7','C8.8','C9','C9.3','C10','C11','C12','C13','C15','C16','C17','C18']
#            if boresize in i6s:
#                for row in i6Leads:
#                    if boresize in row:
#                        lead = indexes(row)
#                        break
#            else:
#                lead = False
#            return lead

    def getPneRules(self,path):
        """
        returns the PNE leads from the external document stored in the shared drive.
        
        input: path to the pickle file where the PNE Leads are stored
        output: PNE leads for the different bore sizes
        """
        fle = open(path,'r')
        onLeads = False
        onSpecial = False
        i6Leads = {}
        vees = []
        for line in fle.readlines():
            line1 = line.lstrip()
            if '#' not in line1: #if not a commented line
                if '::LeadNames::' in line:
                    onLeads = True
                    
                if onLeads:
                    if '::Vees::' in line:
                        onSpecial = True
                        onLeads = False
                    else:
                        lineList = line.split()
                        if len(lineList)>1:
                            lead = lineList[0]
                            bores = lineList[1:]
                            i6Leads[lead] = bores
                            #print lead, bores
                if onSpecial:
                    lineList = line.split()
                    if len(lineList)>1:
                        vees = lineList[1:]
        self.i6Leads=i6Leads
        self.vees=vees
    def getLVal(self, jobNumber, column):
        """
        returns the latest value in the SCOREBOARD time history for the given 
        jobNumber for the given column, if it exists, if not it will return 
        a boolean False.
        
        Note: This is the same data that you will be printed to the scoreboard
        (if it is not post calculated and/or filtered out)
        """
        value = False
        if jobNumber in self.sbJobDict.keys():
            jobData = self.sbJobDict[jobNumber]
            if column in jobData.keys():
                value = jobData[column][-1]['value'][0]
        return value
    
    def getInputVal(self, jobNumber, column):
        '''
        returns the value found by the source in the input data compiled during the
        database update process from the various system reports.
        '''
        value = False
        if jobNumber in self.jobDict.keys():
            jobData = self.jobDict[jobNumber]
            if column in jobData.keys():
                value = jobData[column][-1]['value'][0]
        return value
        
    def SuspectCheck(self, jobNumber):
        self.sbJobDict[jobNumber]['Suspect'] = []
        violations = []
        if 'J9850G' == jobNumber:
            pass
        updating = len(self.jobDict.keys())>0
        for rule, color in self.suspectRules:
            #if updating:
            
            if rule == 'Dropped from JRS':
#                if updating:
#                    JRSNum = self.getInputVal(jobNumber,'Job No-->JRS')
#                    JRSdropOut = JRSNum == False or JRSNum == '' or JRSNum == 'None'
#                else:
                dropped = self.getLVal(jobNumber,'Dropped from JRS')
                JRSdropOut = dropped == 'Y'
                
                
                if JRSdropOut:
                    #print jobNumber, 'Job No-->JRS', JRSNum
                    violations.append(rule + '\n')
                    
            if rule == 'P&E Lead = Cancelled':
                lead = self.getLVal(jobNumber,'P&E Lead')
                if lead == 'Cancelled':
                    violations.append(rule + '\n')
                    
            if rule == 'JRS SOL Date < Its time history date':
                #ToDo: write these rule functions
                pass
            
            if rule == 'Part numbers changed after ESO Signed Off':
                pass
            
            if rule == 'P&E Tdate - ESO Tdate < 6 days':
                PnETdate = self.getLVal(jobNumber, 'Performance / Emissions\\/Target Date')
                ESOTdate = self.getLVal(jobNumber, 'Engineering Sign-Off\\/Target Date')
                pDate = self.populateDate
                inputs = [pDate, PnETdate, ESOTdate]
                diff, junk, junk = self.calculateVariance(inputs)
                if diff < 6:
                    violations.append(rule + '\n')
            
            if rule == 'SOL Date - P&E Tdate < 24 days':
                PnETdate = self.getLVal(jobNumber, 'Performance / Emissions\\/Target Date')
                SOL = self.getLVal(jobNumber, NEW_SOL_DATE_KEY)
                pDate = self.populateDate
                inputs = [pDate, SOL, PnETdate]
                diff, junk, junk = self.calculateVariance(inputs)
                if diff < 24:
                    violations.append(rule + '\n')
                    
        violations = ''.join(violations)
        self.sbJobDict[jobNumber]['Suspect'].extend(add2JobNumber(violations))

    def GetValue(self, JobNumber, Header, postCalc = False):
        source = ''
        if Header in self.rules:
            rules = self.rules[Header]
            value = "None"#False
            for rule in rules:
                if not isinstance(rule, str):
                    function = rule[0]
                    inputs = []
                    sources = []
                    for piece in rule[1:]:
                        value, color, source = self.evalRule(JobNumber, piece)
                        inputs.append(value)
                        sources.append(source)
                    inputs.append(JobNumber)
                    value, color, source = function(inputs, sources=sources)
                else:
                    value, color, source = self.evalRule(JobNumber, rule)
                if value != "None":
                   break 
            if value == "None":
                value, color = '', 0
            return value, color, source
        else:
            return '', 0, source
    
    def evalRule(self, JobNumber, rule):
        sourceHeader, source = rule.split('-->')
        value = "None"
        color = 0
        if source == 'Job Number':
            source = ''
            value, color = JobNumber, 0
        elif source == 'self':
            source = sourceHeader
            if sourceHeader in self.sbJobDict[JobNumber].keys():
                value, color = self.sbJobDict[JobNumber][sourceHeader][-1]['value']
            else:
                value, color = '',0
        elif source == 'global':
            source = ''
            value = getattr(self, sourceHeader)
            color = 0
        else:
            source = rule
            if JobNumber in self.jobDict.keys():
                jobData = self.jobDict[JobNumber]
                if rule in jobData.keys():
                    value, color = jobData[rule][-1]['value']
        return value, color, source
                    
    def getOwner(self, inputs, sources):
        description = str(inputs[0])
        requestor = str(inputs[1])
        lParaPos = description.find("(") + 1
        rParaPos = description.find(")")
        owner = ""
        if not lParaPos == 0:
            if rParaPos > (len(description) - 10):
                owner = description[lParaPos:rParaPos]
                if len(owner.split()) > 3:
                    owner = ""
                else:
                    for let in owner:
                        if let.isdigit():
                            owner = ""
                            break
        if owner == "":
            clrIndex = 6
            owner = requestor
        else:
            clrIndex = 0
        return owner, clrIndex, 'JRS'
    
    def calculateVariance(self, inputs, sources=''):
        '''
        If SOL <> "" Then
            If peActualDate <> "" And peActualDate <> "NA" Then
                peVariance = DateDiff("d", peActualDate, peTargetDate)
            ElseIf peActualDate = "NA" Then
                peVariance = "NA"
            Else
                peVariance = ""
            End If
        End If
        '''
        populateDate = inputs[0]
        targetDate = inputs[1]
        actualDate = inputs[2]
        dayB4PopulateDate = populateDate - datetimeDotTimedelta(days=1)
        
        if isinstance(actualDate, datetimeDotDatetime) and isinstance(targetDate, datetimeDotDatetime):
            variance = targetDate - actualDate
            variance = variance.days 
            if variance >= 0:
                clrIndex = green
            else: 
                clrIndex = red
        elif actualDate == "NA":
            variance = "NA"
            clrIndex = green
        else: 
            try:
                actualDate = datetimeDotDatetime.strptime(actualDate.split()[0], "%d-%b-%y")
                variance = targetDate - actualDate
                variance = variance.days 
                if variance >= 0:
                    clrIndex = green
                else:
                    clrIndex = red
            except:
                variance = ""
                if isinstance(targetDate, datetimeDotDatetime):
                    if targetDate < dayB4PopulateDate:
                        clrIndex = red
                    else:
                        clrIndex = 0
                else:
                    clrIndex = 0
        return variance, clrIndex, ''
    
    def getBoreSize(self, inputs, sources):
        '''
        Attempts to figure out boreSizes
        inputs:
        'Platform-->JRS',
        'Description-->JRS'
        'Job Number-->Job Number'
        '''
        platform = str(inputs[0])
        description = str(inputs[1])
        jobNumber = inputs[2]
        if jobNumber == 'J9511L':
            pass
        wildCards = []
        wildCards.append("C[0-9]")
        wildCards.append("C[0-9][0-9]")
        wildCards.append("C[0-9][0-9][0-9]")
        wildCards.append("[0-9][0-9][0-9][0-9]")
        wildCards.append("C[0-9]-C[0-9]")
        wildCards.append("C[0-9][0-9]-C[0-9][0-9]")
        first = True
        tempPlatform = reDotSub(r'[^a-zA-Z0-9]', ' ', platform)
        boreSize = ""
        for word in tempPlatform.split():
            for i, wildCard in enumerate(wildCards):
                if fnmatch(word, wildCard):
                    if i < 5:
                        if first:
                            boreSize = word
                            first = False
                        else:
                            boreSize = boreSize + "," + word
                    else:
                        splitBoreSize = word.split("-")
                        firstBoreSize = splitBoreSize[0]
                        if firstBoreSize != "C15":
                            firstBoreSize = firstBoreSize[2:]
                            secondBoreSize = splitBoreSize[1]
                            secondBoreSize = secondBoreSize[2:]
                            for l in range(firstBoreSize, secondBoreSize):
                                if first:
                                    boreSize = "C" + str(l)
                                    first = False
                                else:
                                    boreSize = boreSize + ",C" + str(l)
                        else:
                            boreSize = word.replace("-", ",")
                else:
                    if word == "Seguin" or word == "GN":
                        boreSize = "C9"
                    if word == "MCOE":
                        #print("MCOE Job found")
                        boreSizes = ["MCOE"]
                        for h in description.split():
                            for wildCard in wildCards:
                                if fnmatch(word, wildCard):
                                    boreSizes.append(h)
                        boreSize = ','.join(boreSizes)
                    #if word == "CAT-India":
                        
        return boreSize, 0, 'JRS'
    
    def getPNELead(self, inputs, sources):
        '''
        Gets the PNE Lead according to logic keywords in external file
        inputs:
        'Bore Size-->self',
        'Platform-->JRS',
        'Job Number-->Job Number'
        '''
        
        boreSize = str(inputs[0])
        platform = str(inputs[1])
        jobNumber = inputs[2]
        PNEtemp = ""
        bores = boreSize.split(',')
        bores.extend(boreSize.split())
        
        if jobNumber == 'J9511L':
            pass
        '''
        P&E Lead Assignment rule definition
        \/\/\/
        '''
#        i6Leads = {'Lehman': ['C7','C8.8','C9','C9.3'],
#                       'Pichla': ['C10','C11','C12','C13'],
#                       'Tamma': ['C15','C16','C17','C18'],
#                      }
#        vees = ['C27','C32','C30','C140','C175','3408','3412']
#        
#        i6toLead = {}
#        i6s = []
#        for lead in i6Leads.keys():
#            for bore in i6Leads[lead]:
#                i6toLead[bore] = lead
#                i6s.append(bore)
        i6Leads = self.i6Leads
        vees = self.vees
        i6s = self.i6s
        i6toLead = self.i6toLead
        '''
        /\/\/\
        P&E Lead Assignment rule definition
        '''
        hasI6 = False
        for bore in bores:
            if bore in i6s:
                hasI6 = True
                PNEtemp = i6toLead[bore]
                break
        
        if hasI6 and len(bores)>1:
            '''
            Check for Vees
            '''
            hasV = False  
            for bore in bores:
                if bore in vees:
                    hasV = True
                    PNEtemp = 'Wuthrich'
                    break
        
#        if hasI6 and hasV:
#            PNE = 'Wuthrich'
#            
#        if len(bores)>1:
#            pass
        
#        for bore in boreSize.split(","):
#            
#            if bore == "C7" or bore == "C8.8" or bore == "C9" or bore == "C9.3":
#                PNEtemp = "Lehman"
#            if bore == "C10" or bore == "C11" or bore == "C12" or bore == "C13":
#                PNEtemp = "Pichla"
#            if bore == "C15" or bore == "C16" or bore == "C17" or bore == "C18":
#                PNEtemp = "Tamma"
#            if bore == "MCOE":
#                PNEtemp = 'Wuthrich'
#                break
                
        if boreSize != "":
            PNE = PNEtemp
        else:
            PNE = "NA"
            
        if platform == "CAT-India":
            if "J69" in jobNumber:
                PNE="Tamma"
            elif "J68" in jobNumber:
                PNE="Konnepati"
            else:
                PNE = 'Wuthrich'
                
        if platform == "MCOE":
            PNE = 'Wuthrich'
            
        if platform == 'FilterOut':
            PNE = 'NA'
    
        return PNE, 0, 'JRS'
    
    def getTargetDate(self, inputs, sources):
        '''
        Determines a target date based on "authoritative" Start on Line date,
        ESOTminusDays, and checks to see if the job number is in JRS - if is not, then
        this will return blanks so as not to overwrite any preexisting information due
        to a job no longer being held within JRS ( a JRSdropOut.
        
        inputs:
        
        NEW_SOL_DATE_KEY + '-->self', 'TMinusGoalDays-->global', 'Job No-->JRS'
        
        '''
        strtSrc =sources[0]
        start, delta, JRSNumber = inputs[0], inputs[1], inputs[2]
        src = ''
        JRSdropOut = JRSNumber == ''
        targetDate = ''
        if not JRSdropOut:
            if isinstance(start, datetimeDotDatetime):
                targetDate = start - datetimeDotTimedelta(days=delta)
            
        src = strtSrc
        
        return targetDate, 0, src
    
    def getEngineeringActual_New(self, inputs, sources):
        '''
        Determines the Engineering Sign Off Actual date, keeping in mind if a job has
        been 'un-signed off' for engineering that there will be 'incomplete' in the
        status and we want a blank value.
        inputs:
        'Engineering Status Date-->JRS',
        'Engineering Approved-->JRS',
        'Review Status-->JRS',
        'Status-->self',
        'Job Number-->Job Number'
        '''
        date, esoStatus, jrsStatus, sbStatus, jobNumber = inputs
        
        JRSDropped = jrsStatus == 'None'
        value = ''
        source = ''
        if JRSDropped:
            return '',0,''
        else:
            if 'J3266H' in jobNumber:
                pass
            #if job is incomplete, return blank
            if 'Incomplete' in esoStatus:
                value = '$blank'
                source = 'Engineering Approved-->JRS'
            #if job is not incomplete
            else:
                value = date
                source = 'Engineering Status Date-->JRS'

                
    
            return value, 0, source
            
#        #get last time history value for EOS actual (may not have access to this data yet)
#        lastESOActual = False
#        jobData = self.sbJobDict[jobNumber]
#        esoAKey = 'Engineering Sign-Off\\/Actual Date'
#        if esoAKey in jobData.keys():
#            esoData = jobData[esoAKey]
#            if len(esoData)>1:
#                lastESOActual = esoData[-2]['value'][0]
        
        '''
        TODO: Figure out how to fix this mess and rollback ESOactual dates that have
        been incorrectly left blank (as well as P & E actual dates)
        '''
        #source = 'JRS'
        value = 'Not Found'
        
    def getEngineeringActual(self, inputs, sources):
        '''
        Determines the Engineering Sign Off Actual date, keeping in mind if a job has
        been 'un-signed off' for engineering that there will be 'incomplete' in the
        status and we want a blank value.
        inputs:
        ['Engineering Status Date-->JRS',
        'Engineering Approved-->JRS',
        'Dropped from JRS-->self',
        'Job Number-->self']
        '''
        date, status, JRSdropped, jobNumber= inputs[:4]
        if jobNumber == 'J3266H':
            pass
        droppedFromJRS = JRSdropped == 'Y'
        #isBlank = date in ['',"None"]
        value = date
        color = 0
        source = ''

        if droppedFromJRS:
            value = '$unblank'
        elif 'Incomplete' in status:
            value = '$blank'
            
        return value, 0, source
    
    def getPnEActual(self, inputs, sources):
        '''
        Determines P & E Actual date - will determine if a blank date can be
        returned based on Engineering Signoff Actual Date and may cause 
        a blank P & E Actual date to be "$unblanked", or rolled back to the last
        non-blank value. This is the case if a job is dropped from JRS and has 
        blank values for Engineering Signoff Actual Date and P & E Actual when the
        last known date should be kept as long as Engineering Signoff Status was
        not "Incomplete" immediately prior to being Dropped from JRS. This last
        Situation is not covered and is not anticipated - but is noted here just
        in case future problems arrise.
        
        inputs: ['Dropped from JRS-->self',
                'Perf/Emissions Status Date-->JRS',
                'Job Number-->self']
        '''
        JRSdropped, PnEstatus, jobNumber = inputs[:3]
        if jobNumber == 'J3266H':
            pass

        droppedFromJRS = JRSdropped == 'Y'
        value = PnEstatus
        color = 0
        source = 'JRS'
        if droppedFromJRS:
            value = '$unblank'

#        if value in ['','None']:
#            if ESOactual in ['','None','$unblank']:
#                value = '$unblank'
                
        return value, color, source
    
    def getPRCactualOld(self, inputs, sources):
        '''
        determines what value goes for PRC Actual Date
        
        inputs: ['Date_Approved-->PRC',
                 'PRC Required?-->Aardvark']
        '''
        
        PRCapprovedDate, AaRequired = inputs[:2]
        inPRC = PRCapprovedDate != 'None'
        inAar = AaRequired != 'None'
        source = False
        color = white
        
        if inAar:
            if 'N' == AaRequired:
                value = 'NA'
                color = green
                source = 'Aardvark'
                return value, color, source
            elif 'Y' == AaRequired:
                value = '$blank'
                color = red
                source = 'Aardvark'
        if inPRC:
            value = PRCapprovedDate
            color = green
            if source:
                source = source + ' and PRC'
            else:
                source = 'PRC'
        elif not inPRC:
            if not source:
                value = 'Not Found'
                color = white
                source = ''

        
        return value, color, source
    
    def getPRCactual(self, inputs, sources):
        '''
        determines what value goes for PRC Actual Date
        
        inputs: ['Date_Approved-->PRC',
                 'PRC Required?-->Aardvark']
        '''
        
        PRCapprovedDate, AaRequired = inputs[:2]
        jobNumber=inputs[-1]
        inPRC = PRCapprovedDate != 'None'
        inAar = AaRequired != 'None'
        source = False
        color = white
        
        if inAar:
            if 'N' == AaRequired:
                value = 'NA'
                color = green
                source = 'Aardvark'
#                return value, color, source
            elif 'Y' == AaRequired:
                value = '$blank'
                color = red
                source = 'Aardvark'
        if inPRC:
            value = PRCapprovedDate
            color = green
            if source:
                source = source + ' and PRC'
            else:
                source = 'PRC'
        elif not inPRC:
            if not source:
                value = 'Not Found'
                color = red
                source = ''
        if jobNumber in self.jobDict.keys():
            jobData = self.jobDict[jobNumber]
        
            keyPart = 'PRC Approved'
            items = "\n".join(jobData.keys())
            start = items.find(keyPart)
            
            if start >=0: #if Aardvark Auto shows LRC is needed
                subItems = items[start:]
                item = subItems.split('\n')[0]
                if '__' in item:
                    item = item.split('__')[0]
                item = item.split('-->')[0]
                source = 'AardvarkAuto'
                Avalue = jobData[item+'-->AardvarkAuto'][-1]['value'][0]
                Status = jobData[item + '__Status-->AardvarkAuto'][-1]['value'][0]
                epoch = datetimeDotDatetime(1899,12,30)
                StatusCodes = ['Complete','Rejected','N/A']
                '''
                TODO: Fix this terrible hack, and make sure this works in all versions
                        of Excel
                '''
                if Status == 'None':
                    Status = ''
                else:
                    delta = Status - epoch
                    Status = delta.days-1
                    Status = StatusCodes[Status]
                if Status == '':
                    value = 'Not Found'
                    color = red
                elif Status == 'Complete':
                    value = Avalue
                    color = green 
                elif Status == 'Rejected':
                    value = '$blank' #Aardvark indicates the LRC is not finished and it is needed
                    color = red
                elif Status == 'N/A':
                    value = 'N/A'
                    color = green #Aardvark contains the completion date of the LRC that is needed
                
        
    
        
        return value, color, source
    
            

    def getLRCactual(self, inputs, sources):
        '''
        Performs the following logic to determine the proper value for the
        'LRC Actual Date' in the scoreboard.
        
        
        value = 'Not Found' if job is not found in
            Project Plan AND Job Number/Job Number's LRC task is not found 
            in Aardvark Auto
            
        src = '' initially
        
        Check to see if LRC information exists in the Project Plan:
            -Yes: Check if complete:
                  -Yes: Pvalue = date from 'Finish' field
                  -No: Pvalue = $blank 

        Check if job number is in AardvarkAuto:
            -Yes: Check if LRC task is in job number's task list:
                  -Yes: Check if there is a date in the task's worklistdate:
                        -Yes: Avalue = date
                        -No:  Avalue = $blank
        if Avalue:
        
        '''
        lrcDate = inputs[0] #'Finish-->ProjectPlan', 
        lrcStatus = inputs[1] #'Activity Status-->ProjectPlan'
        jobNumber = inputs[2] 
        
        value = 'Not Found'
        color = white
        src = ''
        if jobNumber == 'J5307H':
            pass
        if jobNumber in self.jobDict.keys():
            jobData = self.jobDict[jobNumber]

            Avalue = False
            Pvalue = False

            #Check LRC has data
            if lrcStatus != 'None':
                if "Completed" == lrcStatus and lrcDate != '$blank A':
                    Pvalue = lrcDate #PP shows LRC was completed
                    color = green
                else:
                    Pvalue = '$blank' #PP shows LRC is needed but not ALL LRCs are completed (can be multiple)
                    color = red
                
            #Check if Aardvark Auto Data indicates the LRC is needed
            keyPart = 'LRC Updated/Published'
            items = "\n".join(jobData.keys())
            start = items.find(keyPart)
#            if '__Status' in found:
#                statusStart = found
#            else:
#                dateStart = found
#            last = len(items[found:].split('\n')[0])+found
#            found = items.find(keyPart,last)
#            if '__Status' in found:
#                statusStart = found
#            else:
#                dateStart = found
            
            if start >=0: #if Aardvark Auto shows LRC is needed
                subItems = items[start:]
                item = subItems.split('\n')[0]
                if '__' in item:
                    item = item.split('__')[0]
                item = item.split('-->')[0]
                src = 'AardvarkAuto'
                Avalue = jobData[item+'-->AardvarkAuto'][-1]['value'][0]
                Status = jobData[item + '__Status-->AardvarkAuto'][-1]['value'][0]
                epoch = datetimeDotDatetime(1899,12,30)
                StatusCodes = ['Complete','Rejected','N/A']
                '''
                TODO: Fix this terrible hack, and make sure this works in all versions
                        of Excel
                '''
                if Status == 'None':
                    Status = ''
                else:
                    delta = Status - epoch
                    Status = delta.days-1
                    Status = StatusCodes[Status]
                if Status == '':
                    value = 'Not Found'
                    color = red
                elif Status == 'Complete':
                    value = Avalue
                    color = green 
                elif Status == 'Rejected':
                    value = '$blank' #Aardvark indicates the LRC is not finished and it is needed
                    color = red
                elif Status == 'N/A':
                    value = 'N/A'
                    color = green #Aardvark contains the completion date of the LRC that is needed
                    
                if Pvalue == value:
                    src = src + ' and ProjectPlan' #Project Plan agrees with Aardvark
            elif Pvalue: #if aardvark had nothing, but Project Plan did
                value = Pvalue
                src = 'ProjectPlan'
                
        return value, color, src
    
    def filterData(self, jobData):
        """
        This determines if a job number will be included in the scoreboard view
        """
            
        pneActualDate, color = jobData['Performance / Emissions\\/Actual Date'][-1]['value']
        lrcActualDate, color = jobData['Lab Rating Chart\\/Actual Date'][-1]['value']
        prcActualDate, color = jobData['Production Release Checklist\\/Actual Date'][-1]['value']
        
        if isinstance(pneActualDate, datetimeDotDatetime):
            pNeComplete = True  
        elif pneActualDate == 'NA':   
            pNeComplete = True 
        else:
            pNeComplete = False
        
        if lrcActualDate == '':
            if pNeComplete:
                jobData['Lab Rating Chart\\/Actual Date'][-1]['value'] = ["NA", 0]
                jobData['Lab Rating Chart\\/Variance'][-1]['value'] = ["NA", green]      
                
        if prcActualDate == '':
            if pNeComplete:
                jobData['Production Release Checklist\\/Actual Date'][-1]['value'] = ["NA", 0]
                jobData['Production Release Checklist\\/Variance'][-1]['value'] = ["NA", green]
    
        PNE, color = jobData['P&E Lead'][-1]['value']
        
        if PNE != "NA" and PNE != "":
            return True
        else:
#            jNum = jobData['Job #'][-1]['value'][0]
#            print"filtered out job number %s"%jNum
            return False
        
        
    def compareStuff(self, inString, checkArray):
        if inString != "":
            try:
                check = True
                for j in checkArray:
                    if j in inString:
                        check = False
                return check
            except:
                return True
        else:
            return False

class login(object):
    def __init__(self):
        self.data = {'empty':''}
        self.edit = []
        self.view = []
        self.user = ''
        self.role = ''
        self.roles = []
        self.filePath = r'\\n1nasfan4.corp.cat.com\MECPerfEng\Process Improvement Project\P&E Scoreboard\UserAccess.csv'
        self.filePath = r'\\n1gfs01.mw.na.cat.com\shares\EPC913-640\P&E Scoreboard\UserAccess.csv'
        self.userProfiles = {'Developer':{'Edit':['All'],
                                         'View':['All']},
                            'Executive':{'Edit':[''],
                                        'View':['All']},
                            'JRSpert':{'Edit':[''],
                                       'View':['Dena Cassidy Metrics']},
                            'Test Spec Engineer':{'Edit':['Test Specification\\/Actual Date', 'Test Specification Engineer\\/Notes'],
                                        'View':['ScoreBoard']},
                            'P&E Manager':{'Edit':['P&E Lead', 'P & E Manager\\/Notes', 'Bore Size'],
                                        'View':['All']},
                            'P&E Engineer':{'Edit':['P & E Documentation Engineer\\/Notes'],
                                        'View':['ScoreBoard']},
                            'Default':{'Edit':['Process Issues\\/Encountered'],
                                        'View':['ScoreBoard']}
                                         }
        roles = self.userProfiles
        self.edit.append('Public\\/Notes')
        self.view.append('ScoreBoard')
        self.open()
        self.read()
        self.login()
    
    def open(self):
		try:
			self.xlFile = open(self.filePath, "rb")
		except:
			self.xlFile = False
    
    def read(self):
        if self.xlFile:
            csvData = csvReader(self.xlFile)
            data = self.xlFile.readlines()
            self.data = data
        
    def login(self):
        jobDict = data = self.data
        #self.currentUser = user = os.getenv('USERNAME')
        self.currentUser = user = os.environ.get("USERNAME")
        roles = []
        userFound = False
        user = user.lower()
        for line in data:
            if user in line.lower():
                userFound = True
                parts = line.split(',')
                roles = []
                for part in parts[1:]:
                    role = part
                    if '\r\n' in part:
                        role = part[0:-2]
                    if role != '':
                        roles.append(role)
                self.roles = roles
                self.role = ', '.join(self.roles)
                break
        #if not userFound:
        roles.append('Default')
        for role in roles:
            #print role
            self.edit.extend(self.userProfiles[role]['Edit'])
            self.view.extend(self.userProfiles[role]['View'])

    def printInfo(self):
        #print"User:"
        #print self.user
        print"Roles:"
        print self.roles
        print"Edit Rights:"
        for right in self.edit:
            print right
        #print"View Rights:"
        #for right in self.view:
            #print right
        
    def testLogin(self):
        self.currentUser = 'Test'
        self.currentAccessProfile = 'Default'
        self.currentAccess = self.userProfiles[self.currentAccessProfile]
        
def py2date(now_pytime):
    now_datetime = datetimeDotDatetime (
      year=now_pytime.year,
      month=now_pytime.month,
      day=now_pytime.day,
      hour=now_pytime.hour,
      minute=now_pytime.minute,
      second=now_pytime.second
    )
    return now_datetime
        
def pBar(*argss):
    """
    text based progress bar function
    
    if inputs: (i, j, k)
    outputs are: i+1, j, k and prints without a newline to the progress bar
    
    if inputs: (list) OR (dict)
    outputs are: 0, 0, len(list) OR 0, 0, len(dict.keys())
    witch are: i, j, k
    
    i is the current item in the iterable
    j is the last percentage printed
    k is the length of the iterable
    
    Example Usage:
    
    #(initialization outside of loop)
    i,j,k = pBar(dictionary)
    for item in dictionary.Keys:
        i, j, k = pBar(i, j, k)
        #(in-loop code goes here)
    """
    dotInterval = 2
    numInterval = 10
    
    if len(argss) == 3 and not isinstance(argss, list):
        i = argss[0]
        j = argss[1]
        k = argss[2]
        i += 1
        percent = (i / 1.0) / k * 100
        #print percent
        if percent > j:
            j += dotInterval
            if j % numInterval == 0:
                print"%d%%" % j,
            else:
                print'.',
    else:
        i = 0
        j = 0
        if isinstance(argss[0], list):
            k = len(argss[0])
        elif isinstance(argss[0], dict):
            k = len(argss[0].keys())
    return i, j, k

             
        
def add2JobNumber(value, color=0, source='', manual=False):
    """
    Adds a value and other information to a column of a job number's dictionary
    which is specified by jobData.
    """
    entry = {'value': [value, color],
             'user': os.environ.get("USERNAME"),
             'date': datetimeDotDatetime.now(),
             'manEntry':manual}
    if source != '':
        entry['source'] = source
    if timeBuilding:
        entry['date'] = dataDate
    return [entry]

def setView():
    #print("Determining current user access..."),
    credentials = login()
    #print("Done.")
    print("Current User: %s" % (credentials.currentUser))
    print("Access Level: %s" % (credentials.role))
    credentials.printInfo()
    sleep(2)

    excel = CPL4.GetActiveExcel()
    #import win32com
    #excel1 = win32com.client.gencache.EnsureDispatch('Excel.Application')
    #veryHidden = win32com.client.constants.xlSheetVeryHidden
    #view = credentials.currentAccess['View']
    veryHidden = 2
    view = credentials.view#currentAccess['View']
    #sheets = []
    #sheets.extend(excel.Sheets)
    #sheets.extend(['ScoreBoardColor','TimeHistory'])
    for workSheet in excel.Sheets:
        name = workSheet.Name
        if name in view:
            workSheet.Visible = True
        elif 'All' in view:
            workSheet.Visible = True
        elif 'None' in view:
            workSheet.Visible = False
        else:
            workSheet.Visible = veryHidden

    if credentials.currentUser in ['boiruc', 'wuthrme']:
        pass
        #sleep(4)
    return excel
        
        
def getPaths(inputDirs, ext='.xls'):
    """
    Given a list of directories, this function will return a list of paths to 
    the newest file found in each directory. By default it will look for .xls
    files. 
    
    The inputDirs list will be duplicated with full paths where directory paths
    once were, it will also pass through any data that occurs after the first
    element in each sublist (in case each directory is contained in a list of
    information)
    """
    outputPaths = []
    if LRCFirst:
        f = inputDirs[0]
        l = inputDirs[-1]
        inputDirs[0] = l
        inputDirs[-1] = f
    for fdir in inputDirs:
        if isinstance(fdir, list):
            fdir, other = fdir[0], fdir[1:]
            newPath = getNewest(fdir, ext)
            info = [newPath]
            info.extend(other)
            outputPaths.append(info)
    return outputPaths
            
def getNewest(fdir, ext):
    """
    returns the full path of the newest file matching the type defined by ext
    found in the directory defined by dir.
    """
    fileList = os.listdir(fdir)
    latestFle = False
    latestTime = False
    for fle in fileList:
        thisFle = os.path.join(fdir, fle)#fdir + '\\' +fle#os.path.join(fdir, fle)
        ThisExt = os.path.splitext(thisFle)[1]
        if ThisExt == ext:
            thisTime = os.path.getmtime(thisFle)
            if not latestTime:
                latestTime = thisTime
                latestFle = thisFle
            elif thisTime > latestTime:
                latestTime = thisTime
                latestFle = thisFle
    return latestFle

def loadCheckpoint(checkpoint,data):
    '''
    Loads required data to resume program at predefined checkpoints.
    '''
    if resuming:
        print'Loading checkpoint',checkpoint
        
        if checkpoint == 1:
            newBooks1,dataDumpDate1 = data
            newBooks2, dataDumpDate = pLoad(checkpoint1)
            newBooks2.scoreboard.excel = newBooks1.scoreboard.excel
            newBooks2.rules = newBooks1.rules
            resumed = True
            data = newBooks2, dataDumpDate
            return data, resumed
        
        print'Done Loading checkpoint',checkpoint
    else:
        return data,False
    
def saveCheckpoint(checkpoint,data):
    '''
    Saves required data to be able to resume this position of the program
        at a later time.
    '''
    if savingCheckpoints:
        print"Saving checkpoint",checkpoint
        
        if checkpoint == 1:
            newBooks, dataDumpDate = data
            excelTemp = newBooks.scoreboard.excel
            newBooks.scoreboard.excel = ''
            newBooks.rules = ''
            for workbook in newBooks.workbooks.keys():
                book = newBooks.workbooks[workbook]
                book.excel = ''
#            newBooks.rules = ''
            data = newBooks, dataDumpDate
            #data = newBooks, dataDumpDate
            filePath = checkpoint1
            
            pSave(data, filePath)
            data[0].scoreboard.excel = excelTemp
        
        print"Done saving checkpoint",checkpoint
    if endPoint <= checkpoint:
        print'Program completed at checkpoint',checkpoint
        sleep(2)
        sys.exit()
    
def createDatabase(inputPaths):
    """
    This will compile job number data from all data dumps listed in the 
    inputPaths list, overwrite the master data file (mdf) on the share drive,
    calculate the job data to create a scoreboard view, and sync the new 
    scoreboard view with the previous time history that is stored on the 
    share drive in the scoreboard data file.
    """
    '''
    State 1 Begin
    '''
    newBooks = inputWorkbooks()
    dataDumpDate = datetimeDotDatetime.now()
    data = newBooks, dataDumpDate
    data, resumed = loadCheckpoint(1,data)
    newBooks, dataDumpDate = data
    
    if not resumed:
        print("Creating Database")
        print("Gathering information from Dump files...")
        
        for book, sourceType in inputPaths:
            newBooks.addFile(book, sourceType)
        data = newBooks, dataDumpDate
        saveCheckpoint(1,data)
    print("Done loading input data.")

    
    '''
    State 1 End
    '''
    '''
    State 2 Begin
    '''
    print("Calculating Job Data for the latest Scoreboard View...")
    newBooks.gatherScoreboardValues()
    #if not timeBuilding:
        #newBooks.createScoreBoardView()
    print("Done.")
    '''
    State 2 End
    '''
    sync(newBooks, updated=True)
    
def sync(newBooks, updated=False):
    '''
    State 3 Start
    '''
    print("Syncing with Scoreboard Data File time history...")
    newJobDict = newBooks.sbJobDict
    print"New Jobs Before Sync: %d" % len(newJobDict.keys())
    myFilePath = False
    if os.path.exists(scoreboardDataFile):
        oldJobDict, myFilePath = lockAccess(scoreboardDataFile)
        #print"Old Jobs Before Sync: %d" % len(oldJobDict.keys())
        '''
        State 3 End
        '''
        '''
        State 4 Begin
        '''
        newJobDict, dupes, appendages, rollbacks, deletedJobs = compairDicts(oldJobDict, newJobDict, updated)
        newBooks.sbJobDict = newJobDict
        '''
        State 4 End
        '''
        '''
        State 5 Begin
        '''
        for jobNumber in deletedJobs:
            if jobNumber in newBooks.sbJobList:
                if jobNumber == 'J5307H':
                    pass
                newBooks.sbJobList.remove(jobNumber)
        #print"Jobs AFTER Sync: %d" % len(newJobDict.keys())
        print"Number of duplicate jobs: %d" % dupes
        print"Number of value appendages: %d" % appendages
        print"Number of value rollbacks: %d" % rollbacks
        '''
        State 5 End
        '''
    '''
    State 6 Begin
    '''
    newBooks.calcScoreboardValues(updated = updated)
    '''
    State 6 End
    '''
    '''
    State 7 Begin
    '''
    if updated:
        newJobDict["LastUpdateDate"] = datetimeDotDatetime.now()# - datetimeDotTimedelta(days=5)
        #print"Updated just now, - 5 days, this time is:", newJobDict["LastUpdateDate"]
    pSave(newJobDict, scoreboardDataFile)
    if updated:
        newJobDict.pop("LastUpdateDate")
    if myFilePath:
        unLockAccess(myFilePath)
    if not timeBuilding:
        refresh(newBooks, syncing=True, updated=updated)
    
def refresh(workbooks, syncing=False, updated=False):
    print("Refreshing Scoreboard View")
    print
    if not syncing and os.path.exists(scoreboardDataFile):
        workbooks.sbJobDict = readSDF()
    workbooks.createScoreBoardView(updated = updated)
    refreshMetrics(workbooks)
    workbooks.scoreboard.excel.Worksheets('ScoreBoard').Activate#wth doesn't this work!??
    print
    print("Refreshing Complete")
    #r = raw_input()
        
    
def refreshMetrics(workbooks):
    if not noMetrics:
        credentials = login()
        viewAccess = credentials.view
        metView = ['Metrics','All','Dena Cassidy Metrics']
        tabs = []
        for tab in viewAccess:
            if tab in metView:
                tabs.append(tab)
        print"Tabs:",tabs
        if len(tabs)>0:
            jobList = workbooks.sbJobList
            print("Calculating metrics values...")
            workbooks.calcMetricsValues(jobList, tabs)
            if 'Metrics' in viewAccess or 'All' in viewAccess:
                print("Done.")
                print("Gathering Data for Metrics View..."),
                workbooks.createMetricsView()
            if 'Dena Cassidy Metrics' in viewAccess or 'All' in viewAccess:
                workbooks.createMetricsView(tab='Dena Cassidy Metrics')
            print("Done refreshing metrics.")
    else:
        print"Skipping Metrics Calculations"
        sleep(2)
    
def getWaits(dir, string):
    """
    returns filenames in dir that contain the string
    """
    contents = os.listdir(dir)
    stuff = []
    for fle in contents:
        if string in fle:
            stuff.append(fle)
    return stuff

def cleanupWaitList(dir):
    """
    searches for leftover waiting files that may have resulted from errors
    and deletes them from the directory dir.
    
    files will have file names in the following format:
    waiting_<user name>_<number>.txt
    """
    waitList = getWaits(dir, 'waiting')
    junk = []
    ME = os.getenv('USERNAME')
    timeout = 60 * 2
    #print"WaitList Cleanup:", waitList
    if len(waitList) > 0:
        for item in waitList:
            if 'waiting' in item:
                junk, junk2, user = item.split('_')
                #print"user:",user
                if ME in user:
                    path = dir + '\\' + item
                    os.remove(path)
                    
def lockAccess(path, scoreboard=True):
    """
    performse thread safe accessing of a data file.
    
    checks the directory for "waiting" files that indicate another thread
    is trying to access the file. "Waiting" files are numbered according
    to the order in which threads attempt to access the file, if any are
    detected, this thread will find the highest numbered waiting file and
    create a new one with an incrimented number. As soon as there are no
    waiting files with lower numbers than this one, it will access the file
    and when done, will delete it's waiting file.
    """
    if scoreboard:
        path = scoreboardDataFile
    dir = os.path.dirname(path)
    waitTime = .5
    
    myFilePath = False
    ME = os.getenv('USERNAME')
    cleanupWaitList(dir)
    waitList = getWaits(dir, 'waiting')
    if len(waitList) > 0:
        waitList.sort()
        print waitList
        fileName = os.path.splitext(waitList[-1])[0]
        mynum = int(fileName.split('_')[1]) + 1
        myFileName = 'waiting_%d_%s.txt' % (mynum, ME)
        print myFileName
        myFilePath = dir + '\\' + myFileName
        myFile = open(myFilePath, 'w')
        myFile.close()
        print"Waiting for access to database..."
        ahead1 = len(waitList)
        ahead2 = 0
        totalET = 0
        noMoveET = 0
        queMoveTime = 40
        messaged = False
        while True:
            waitList = getWaits(dir, 'waiting')
            waitList.sort()
            if waitList[0] == myFileName:
                break
            try:
                ahead1 = waitList.index(myFileName)
            except:
                ahead1 = len(waitList)
            if ahead1 > 0 and ahead1 != ahead2:
                if ahead1 == 1:
                    print"Your request will be processed next."
                else:
                    print"There are %d requests ahead of you." % ahead1
                ahead2 = ahead1
                noMoveET = 0
                messaged = False
            if noMoveET > queMoveTime and messaged != True:
                fname = os.path.splitext(waitList[0])[0]
                junk, junk, badUser = fname.split('_')
                print
                print"We are sorry but the queue has not moved in %d seconds" % noMoveET
                print"%s was the last user to attempt access and there may have been an error" % badUser
                print"Please contact %s and have %s attempt to resynchronize." % (badUser, badUser)
                print"If this is does not work or is not possible, please contact Curtis Boirum at:"
                print"309-578-1651,"
                print"Curtis_Boirum@cat.com"
                messaged = True
            sleep(waitTime)
            totalET += waitTime
            noMoveET += waitTime    
    else:
        myFileName = 'waiting_0_%stxt' % ME
        myFilePath = dir + '\\' + myFileName
        myFile = open(myFilePath, 'w')
        myFile.close()
    print"Access to database granted."
    if scoreboard:
        jobDict = readSDF()
    else:
        jobDict = pLoad(path)
    return jobDict, myFilePath
    
def unLockAccess(path):
    os.remove(path)
    
def dictKeys2Labels(jobDict):
    '''
    Scans through a dictionary and converts the keys for each job number
    into scoreboard column labels. (This is in case any columns are redefined
    by the key2LabelMap.)
    '''
    for jobNumber in jobDict.keys():
        jobData = jobDict[jobNumber]
        for header in jobData.keys():
            if header in key2LabelMap.keys():
                newHeader = key2Label(header)
                jobData[newHeader] = jobData.pop(header)
    return jobDict

def readSDF():
    """
    loads scoreboard job dictionary data file from share drive and applies 
    conversion from database keys to scoreboard column labels.
    """
    global lastUpdateDate
    sdfPath = scoreboardDataFile
    if os.path.exists(sdfPath):
        jobDict = pLoad(sdfPath)
        if "LastUpdateDate" in jobDict.keys():
            lastUpdateDate = jobDict.pop("LastUpdateDate")
            #print"Loaded lastUpdateDate:", lastUpdateDate
        jobDict = dictKeys2Labels(jobDict)
        return jobDict
    else:
        print('Scoreboard Data File Does not exist in path: %s' % sdfPath)
        return None
        
def pSave(data, filePath):
    print"Saving Data to:",
    print filePath,
    print "...",
    file = open(filePath, 'wb')
    pickle.dump(data, file, 2)
    file.close()
    print"Done."
        
def pLoad(filePath):
    if os.path.exists(filePath):
        print"Loading Data from:",
        print filePath,
        print "...",
        file = open(filePath, 'rb')
        data = pickle.load(file)
        file.close()
        print"Done."
        return data
    else:
        print "File not found: %s" % filePath
        return None
    
def try2Add2(self, jobNumber, column, value, creating = False):
    '''
    Attempts to add a value to a job number's time history by applying the 
    ok2append logic using a simplified function 
    '''
    credentials = login()
    if jobNumber not in sbJobDict.keys():
        sbJobDict[jobNumber] = {}
        
    oldJobData = sbJobDict[jobNumber]
    
    if column not in oldJobData.keys():
        oldJobData[column] = add2JobNumber('')
    oldData = oldJobData[column]
    newData = add2JobNumber(value)
    okToAppend = ok2Append2(credentials, oldData, newData, column, jobNumber, creating=creating)
    if okToAppend:
        oldJobData[column].extend(newData)
    
def compairDicts(oldJobDict, newJobDict, creating):
    """
    compair job dictionaires and append new data to the master data file
    jobDictionary format:
        old:
            jobDictionary[jobNumber]['columnName-->Source'] = [{'value': 'cell contents',
                                                                'user': 'user',
                                                                'date': 'date'}]
        new:
            jobDictionary[jobNumber]['columnName-->Source'] = [{'value': 'cell contents',
                                                                'user': 'user',
                                                                'date': 'date'}]
                                                                    
    """
    credentials = login()
    print("Starting comparison of New Scoreboard values to Scoreboard Data File time history...")
#    DataOutput = newJobDict['J5307H']
#    DataInput = oldJobDict['J5307H']
#    
#    print"ofInterest..." 
    dupes = 0
    appendages = 0
    rollbacks = 0
    badJobs = []
    print"jobs at first: %d" % len(oldJobDict.keys())
    i,j,k = pBar(newJobDict)
    for jobNumber in newJobDict.keys():
        i, j, k = pBar(i, j, k)
        if jobNumber == 'J2341V':
            pass
        newJobData = newJobDict[jobNumber]
        
        if jobNumber not in oldJobDict.keys():
                oldJobDict[jobNumber] = {}
        else:
            dupes += 1
#        if jobNumber in ['J2302E', 'J2302H', 'J2301D']:
#            pass   
        checkColumn = 'Platform-->JRS'
        checkVal = jobVal(newJobDict, jobNumber, checkColumn)
        if checkVal and 'FilterOut' in checkVal:
            leadColumn = 'P&E Lead'
            newJobDict[jobNumber][leadColumn] = []
            newJobDict[jobNumber][leadColumn] = add2JobNumber('NA',manual='Override')
        oldJobData = oldJobDict[jobNumber]
        
        for column in newJobData.keys():
            newData = newJobData[column]
            if column not in oldJobData.keys():
                oldJobData[column] = add2JobNumber('')
            
            oldData = oldJobData[column]
            if jobNumber == 'J5207T' and 'Lab Rating Chart' in column and 'Actual Date' in column:
                pass
            okToAppend, steps = ok2Append(credentials, oldData, newData, column, jobNumber, creating=creating)
            if okToAppend:
                if 'rollback' == okToAppend:
                    length = len(oldJobData[column]) - 1
                    if abs(steps) > length:
                        oldJobData[column] = add2JobNumber('')
                        rollbacks += length + 1
                    else:
                        if steps < 0:
                            steps = len(oldJobData[column]) + steps
                        for i in range (steps):
                            oldJobData[column].pop()
                            rollbacks += 1
                        
                    #sleep(10)
                    #ajdk = raw_input()
                elif 'delete' == okToAppend:
                        #poppedItem = oldJobDict.pop(jobNumber)
                        badItem = oldJobDict[jobNumber]
                        if badItem != None:
                            print("%s manually tagged for deletion" % jobNumber)
                            badJobs.append(jobNumber)
                            
                elif 'blank' == okToAppend:
#                        source = column.split('-->')[1]
#                        if len(source)<0:
                        if 'source' in newData[-1].keys():
                            source = newData[-1]['source']
                        else:
                            source=False
                        color = newData[-1]['value'][1]
                        
                        newData = add2JobNumber('', color = color, source=source)
                        oldJobData[column].extend(newData)
                        appendages += 1
                elif 'unblank' == okToAppend:
                    '''
                    Will rollback until the first non-blank value is found and set that as the 
                    current value 
                    '''
                    length = len(oldJobData[column])
                    isBlank = oldJobData[column][-1]['value'][0] == ''
                    while length > 1 and isBlank:
                        isBlank = oldJobData[column][-1]['value'][0] == ''
                        if isBlank:
                            oldJobData[column].pop()
                        length = len(oldJobData[column])
                else:
                    '''
                    Normal data additions for new values
                    '''
                    oldJobData[column].extend(newData)
                    appendages += 1
                    
            if len(oldJobData[column]) > 1 and oldJobData[column][0]['value'][0] == '':
                #If the first value in a time history is blank, then we want to remove that value
                # instead of creating a frivalous time history.
                #print"job data with empty first entry found'"
                oldJobData[column] = oldJobData[column][1:]
                
    '''
    The following code removes "bad" job numbers. It does so by checking to see if the 
    'Job #' field matches the jobNumber key in the job dictionary. If there is not a 
    match then the job is deleted permanently.
    
    It also makes sure that the job number is fully capitalized.
    '''            
    #
    if jobNumber == 'J3423A':
        pass
    manDelete = len(badJobs)
    print manDelete,'manually marked for deletion'
    for jobNumber in oldJobDict.keys():
#        if jobNumber == 'J9504W':
#            pass
        if 'Job #' in oldJobDict[jobNumber].keys():
            numVal = oldJobDict[jobNumber]['Job #'][-1]['value'][0]
            if jobNumber != numVal:
                #print jobNumber,"Needs Deleted", numVal
                badJobs.append(jobNumber)
            elif jobNumber.upper() != jobNumber:
                badJobs.append(jobNumber)
            '''
            if job is not in JRS anymore then delete it.
            '''
    print (len(badJobs)-manDelete), 'jobs needed to be automatically deleted'
    for jobNumber in badJobs:
        oldJobDict.pop(jobNumber)
    """
    If you want to put in code to remove unwanted job numbers, this is the place to do it.
    Bad Job Numbers jobnumbers Remove remove remove job numbers
    """
                
    print("Done.")
    print"Jobs at end: %d" % len(oldJobDict.keys())
#    DataOutput = newJobDict['J5307H']
#    DataInput = oldJobDict['J5307H']
#    
#    print"ofInterest..." 
    return oldJobDict, dupes, appendages, rollbacks, badJobs

def ok2Append2(credentials, oldData, newData, column, jobNumber, creating=False):
    '''
    Simplified version of ok2Append for use in code complexity reduction
    '''
    oldVal = oldData[-1]['value'][0]
    newVal = newData[0]['value'][0]
    user = os.environ.get('USERNAME')
    try:
        author = oldData[-1]['user']
    except:
        pass
        
    oldVal, newVal = None2Space(oldVal, newVal)
    oldVal, newVal = try2Date(oldVal, newVal)
    okToAppend = False
    oldIsManual = oldData[-1]['manEntry']
    newIsManual = newData[-1]['manEntry']
    if oldIsManual and column not in manualAllowed:
        oldData[-1]['manEntry'] = False
        oldIsManual = False
#    if jobNumber == 'J9272B' and column in newBlankAllowed:
#        pass

    if oldVal != newVal and newVal != 'None' and (newVal != '' or column in newBlankAllowed):
        if column in unblankables and newVal == '':
            return False, False
        if not creating:
            editAccess = credentials.edit
            if 'None' not in editAccess and (column in editAccess or 'All' in editAccess):
                if 'Variance' in column:
                    newData[0]['manEntry'] = False
                else:
                    newData[0]['manEntry'] = True
                #print("New Value Found: %s for %s"%(column,jobNumber))
                okToAppend = True
            else:
                if column != 'EPC Bore Lead':
                    print("You do not have permission to overwrite %s" % (column))
                okToAppend = False
        elif creating:
            if oldIsManual:
                if newIsManual == 'Override':
                    okToAppend = True
                else:
                    okToAppend = False 
            else:
                okToAppend = True
            '''
            TODO:
            put in logic case for when creating is true and old is not manual
            This could be causing a problem. Problem Confirmed.
            '''
    return okToAppend

def ok2Append(credentials, oldData, newData, column, jobNumber, creating=False):
    '''
    Decides if a new value can overwrite the old value based on user permission, 
    value and/or history uniqueness, and based on if the scoreboard is being updated
    or not. Also determines if "$" functions can be
    used based on user permission and/or previous data authorship.
    '''
    oldVal, oldColor = oldData[-1]['value']
    newVal, newColor = newData[0]['value']
    user = os.environ.get('USERNAME')
    try:
        author = oldData[-1]['user']
    except:
        pass
    okToAppend = False
    if jobNumber == 'J5307H' and 'Lab Rating Chart' in column and 'Actual' in column:
        pass
    if isinstance(newVal, str):
        if '$rollback' in newVal[:9]:
            #print"user:",user
            #print"author:",author
            #sleep(2)
            if user == author and 'Developer' not in credentials.roles:
                return 'rollback', 1
            elif 'Developer' in credentials.roles:
                steps = newVal.split('$rollback')[1]
                #print"steps:",steps
                #print"newVal.split('$rollback'):",newVal.split('$rollback')
                if steps == '':
                    steps = 1
                else:
                    steps = int(steps)
                return 'rollback', steps
            else:
                print"You may only rollback values that you yourself authored."
                #sleep(2)
                return False, False
        if newVal == '$blank' and 'Developer' in credentials.roles:
            if oldVal != '':
                return 'blank', True
            else:
                return False, False
        if newVal == '$delete' and 'Developer' in credentials.roles:
            return 'delete', True
        if newVal == '$unblank' and 'Developer' in credentials.roles:
            return 'unblank', True
    oldVal, newVal = None2Space(oldVal, newVal)
    oldVal, newVal = try2Date(oldVal, newVal)
    oldIsManual = oldData[-1]['manEntry']
    newIsManual = newData[-1]['manEntry']
    if oldIsManual and column not in manualAllowed:
        oldData[-1]['manEntry'] = False
        oldIsManual = False
        
    forceUpdate = False
    oldSource = False
    newSource = False
    if 'source' in oldData[-1].keys():
        oldSource = oldData[-1]['source']
    if 'source' in newData[-1].keys():
        newSource = newData[-1]['source']
    
    differentValue = oldVal != newVal
    differentSource = oldSource != newSource
    differentColor = oldColor != newColor
    #SameValueDifferentSource = not differentValue and differentSource
    notNone = newVal != 'None'
    notEmpty = newVal != ''
    
    if (differentValue or differentSource or differentColor) and notNone and notEmpty:
        if not creating:
            editAccess = credentials.edit
            if 'None' not in editAccess and (column in editAccess or 'All' in editAccess):
                if 'Variance' in column:
                    newData[0]['manEntry'] = False
                else:
                    newData[0]['manEntry'] = True
                okToAppend = True
            else:
                if column != 'EPC Bore Lead':
                    print("You do not have permission to overwrite %s" % (column))
                okToAppend = False
        elif creating:
            if oldIsManual:
                if newIsManual == 'Override':
                    okToAppend = True
                else:
                    okToAppend = False 
            else:
                okToAppend = True

    return okToAppend, False

def None2Space(*args):
    newstuff = []
    for value in args:
        if value == "None" or value == None:
            newstuff.append("")
        else:
            newstuff.append(value)
    return newstuff

def try2Date(*args):
    newstuff = []
    for value in args:
        try:
            newValue = datetimeDotDatetime.strptime(value, "%d-%b-%y")
        except:
            newValue = value
        newstuff.append(newValue)
    return newstuff

def dictDate(dictionary):
    """
    used to sort a list of dictionaries by date, if the dictionaries
    contain the keyword 'date', will return None if it doesn't
    """
    if isinstance(dictionary, dict):
        if 'date' in dictionary.keys():
            return dictionary['date']
        else:
            return None
    else:
        return None
    
def pathSetup():
    if not quicktest:
        if mode == 'paths':
            if B:
#                if not quicktest:
#                    inputPaths = [[r"C:\Users\boiruc\workspace\Mr Wuthritch's Opus\dataDumps\aardvark\aardvark_11-27-2012.xls", 'Aardvark'],
#                                  #[r"C:\Users\boiruc\workspace\Mr Wuthritch's Opus\dataDumps\aardvark\aardvark_12-05-2012.xls", 'Aardvark'],
#                                  #[r"C:\Users\boiruc\workspace\Mr Wuthritch's Opus\dataDumps\aardvark\aardvark_12-06-2012.xls", 'Aardvark'],
#                                  #[r"C:\Users\boiruc\workspace\Mr Wuthritch's Opus\dataDumps\aardvark\aardvark_12-07-2012.xls", 'Aardvark'],
#                                  ]
                inputPaths = [[r"C:\Users\boiruc\workspace\Mr Wuthritch's Opus\dataDumps\aardvark\aardvark_11-27-2012.xls", 'Aardvark'],
                              [r"C:\Users\boiruc\workspace\Mr Wuthritch's Opus\dataDumps\JRS\JRS_greenville_11-27-2012.xls", 'JRS'],
                              [r"C:\Users\boiruc\workspace\Mr Wuthritch's Opus\dataDumps\JRS\JRS_mossville_11-27-2012.xls", 'JRS'],
                              [r"C:\Users\boiruc\workspace\Mr Wuthritch's Opus\dataDumps\PRC\PRC_11-27-2012.xls", 'PRC']
                              ]
            else:
                inputPaths = [[r"E:\Dev\PandE Scoreboard v2.0\Mr Wuthritch's Opus Excel\aardvark\aardvark_11-27-2012.xls", 'Aardvark'],
                              [r"E:\Dev\PandE Scoreboard v2.0\Mr Wuthritch's Opus Excel\JRS\JRS_greenville_11-27-2012.xls", 'JRS'],
                              [r"E:\Dev\PandE Scoreboard v2.0\Mr Wuthritch's Opus Excel\JRS\JRS_mossville_11-27-2012.xls", 'JRS'],
                              [r"E:\Dev\PandE Scoreboard v2.0\Mr Wuthritch's Opus Excel\PRC\PRC_11-27-2012.xls", 'PRC'],
                              [r"E:\Dev\PandE Scoreboard v2.0\Mr Wuthritch's Opus Excel\ProjectPlan\Lab Ratings Charts with Job Numbers 20Nov12.xls", 'ProjectPlan']
                              ]
        elif mode == 'dirs':
            if B:
                inputPaths = [
                              [r"C:\Users\boiruc\workspace\Mr Wuthritch's Opus\dataDumps\aardvark", 'Aardvark'],
                              [r"C:\Users\boiruc\workspace\Mr Wuthritch's Opus\dataDumps\JRS Greenville", 'JRS'],
                              [r"C:\Users\boiruc\workspace\Mr Wuthritch's Opus\dataDumps\JRS Mossville", 'JRS'],
                              [r"C:\Users\boiruc\workspace\Mr Wuthritch's Opus\dataDumps\PRC", 'PRC'],
                              [r"C:\Users\boiruc\workspace\Mr Wuthritch's Opus\dataDumps\ProjectPlan", 'ProjectPlan']
                              ]
            else:
                inputPaths = [[r"E:\Dev\PandE Scoreboard v2.0\Mr Wuthritch's Opus Excel\aardvark", 'Aardvark'],
                              [r"E:\Dev\PandE Scoreboard v2.0\Mr Wuthritch's Opus Excel\JRS", 'JRS'],
                              [r"E:\Dev\PandE Scoreboard v2.0\Mr Wuthritch's Opus Excel\JRS", 'JRS'],
                              [r"E:\Dev\PandE Scoreboard v2.0\Mr Wuthritch's Opus Excel\PRC", 'PRC'],
                              [r"E:\Dev\PandE Scoreboard v2.0\Mr Wuthritch's Opus Excel\ProjectPlan", 'ProjectPlan']
                              ]
            if deployed:
                
                inputPaths = [[r"\\n1gfs01.mw.na.cat.com\shares\EPC913-640\P&E Scoreboard\DataDumps\Aardvark AutoDump", "AardvarkAuto"],
							  [r"\\n1gfs01.mw.na.cat.com\shares\EPC913-640\P&E Scoreboard\DataDumps\Aardvark", 'Aardvark'],
                              [r"\\n1gfs01.mw.na.cat.com\shares\EPC913-640\P&E Scoreboard\DataDumps\JRS Greenville", 'JRS'],
                              [r"\\n1gfs01.mw.na.cat.com\shares\EPC913-640\P&E Scoreboard\DataDumps\JRS Mossville", 'JRS'],
                              [r"\\n1gfs01.mw.na.cat.com\shares\EPC913-640\P&E Scoreboard\DataDumps\PRC", 'PRC'],
                              [r"\\n1gfs01.mw.na.cat.com\shares\EPC913-640\P&E Scoreboard\DataDumps\ProjectPlan", 'ProjectPlan']
							  ]
            if localTest:
                if debugIterating:
                    inputPaths = [#[r"C:\C9\DataDumps\Aardvark AutoDump", "AardvarkAuto"],
                                  #[r"C:\C9\DataDumps\Aardvark", 'Aardvark'],
                                  #[r"C:\C9\DataDumps\JRS Greenville", 'JRS'],
                                  [r"C:\C9\DataDumps\JRS Mossville", 'JRS'],
                                  #[r"C:\C9\DataDumps\PRC", 'PRC'],
                                  #[r"C:\C9\DataDumps\ProjectPlan", 'ProjectPlan']
                                      ]
                else:
                    inputPaths = [[r"C:\C9\DataDumps\Aardvark AutoDump", "AardvarkAuto"],
                                  [r"C:\C9\DataDumps\Aardvark", 'Aardvark'],
                                  [r"C:\C9\DataDumps\JRS Greenville", 'JRS'],
                                  [r"C:\C9\DataDumps\JRS Mossville", 'JRS'],
                                  [r"C:\C9\DataDumps\PRC", 'PRC'],
                                  [r"C:\C9\DataDumps\ProjectPlan", 'ProjectPlan']
                                      ]
                if LRCdebug:
                    inputPaths = [[r"C:\C9\DataDumps\Aardvark AutoDump", "AardvarkAuto"],
                                  #[r"C:\C9\DataDumps\Aardvark", 'Aardvark'],
                                  #[r"C:\C9\DataDumps\JRS Greenville", 'JRS'],
                                  #[r"C:\C9\DataDumps\JRS Mossville", 'JRS'],
                                  #[r"C:\C9\DataDumps\PRC", 'PRC'],
                                  [r"C:\C9\DataDumps\ProjectPlan", 'ProjectPlan']
                                      ]
            inputPaths = getPaths(inputPaths, '.xls')
    else:
        print " NOTICE: This is a quick test and is using hard coded local input files. These results are for testing only. Terminate this program immediately if this is not your intent"
        inputPaths = inputPaths = [[r"C:\Users\boiruc\workspace\Mr Wuthritch's Opus\dataDumps\aardvark\aardvark_11-27-2012.xls", 'Aardvark'],
                              #[r"C:\Users\boiruc\workspace\Mr Wuthritch's Opus\dataDumps\aardvark\aardvark_12-05-2012.xls", 'Aardvark'],
                              #[r"C:\Users\boiruc\workspace\Mr Wuthritch's Opus\dataDumps\aardvark\aardvark_12-06-2012.xls", 'Aardvark'],
                              #[r"C:\Users\boiruc\workspace\Mr Wuthritch's Opus\dataDumps\aardvark\aardvark_12-07-2012.xls", 'Aardvark'],
                              ]
    return inputPaths

def getDirs(paths):
    """
    given a list of [path,source], this will return a list of [directory, source]
    """
    dirs = []
    for path in paths:
        dir = os.path.dirname(path[0])
        source = path[1]
        dirs.append([dir, source])
    return dirs

def sourceCheck(sourcePaths):
    '''
    Checks to see if there is a file from all available data dump sources
    available
    '''
    for source in sourcePaths.keys():
        if sourcePaths[source][0] == '':
            return False
    return True

def printDateInfo(solidDates, dateList):
    '''
    Testing print function that will show changes in source files over time
    '''
    for date in dateList:
        print date, ':'
        for fle in solidDates[date]['files']:
            try:
                print fle[1], fle[0][-14:-4]
            except:
                print fle
        print
    #sys.exit()

def getAvailableDates(dirs):
    """
    given a list of directories, this will return a dictionary
    
    the directories must have data dumps for various dates in them, this will
    determine which dates have at least one data dump file. The files that are 
    returned for each date will include files from past dates that did not have 
    a new file on the date in question. This will replicate the day to day 
    operation of the scoreboard, since it will use the latest data dumps 
    available at a certain date.
    """
    dates = {}
    
    solidDates = {}
    paths = {}
    for dir, source in dirs:
        if 'Greenville' in dir:
            source = 'JRSG'
        if 'Mossville' in dir:
            source = 'JRSM'
        files = os.listdir(dir)
        for fle in files:
            date = parseDate(fle)
            if ' ' not in date:
                flePath = dir + '\\' + fle
                if date not in dates.keys():
                    dates[date] = {'sources': [],
                                   'files': []}
                dates[date]['sources'].append(source)
                dates[date]['files'].append([flePath, source])
                if date not in paths.keys():
                    paths[date] = {}
                paths[date][source] = [flePath, source]
    Aard = ''
    JRSG = ''
    JRSM = ''
    PrPl = ''
    PRC = ''
    sources = ['ProjectPlan', 'PRC', 'JRSM', 'JRSG', 'Aardvark']
    sourcePaths = {}#{'Aardvark': '',
#                   'JRSG': '',
#                   'JRSM': '',
#                   'PRC': '',
#                   'ProjectPlan': ''}
    dateList = dates.keys()
    dateList.sort(key=lambda x: datetimeDotDatetime.strptime(x, '%m-%d-%Y'))
    '''
    Build a dictionary that, given a date, will return what the latest data
    dump files would have been for that date. Will include early dates
    that did not have a data dump from all sources.
    '''
    '''TODO: this is working, but not including files from previous dates
    '''
    #print paths.keys()
    #sys.exit()
    for date in dateList:
        for source in sources:
            if source in paths[date].keys():
                sourcePaths[source] = paths[date][source]
        sourceList = []
        srcLst = []
        for item in sources:
            if item in sourcePaths.keys():
                srcLst.append(sourcePaths[item][1])
                sourceList.append(sourcePaths[item])
        solidDates[date] = {}    
        solidDates[date]['files'] = sourceList
        solidDates[date]['sources'] = srcLst
    #printDateInfo(solidDates,dateList)
    return solidDates, dateList
            
def parseDate(fle):
    """
    given a file path, this will return the date of the data dump
    that is found in the file name
    """
    name = os.path.basename(fle)
    name = os.path.splitext(fle)[0]
    date = name[-10:]
    return date

class Logger(object):
    def __init__(self):
        self.terminal = sys.stdout
        self.history = []
        #self.log = open("log.dat", "a")

    def write(self, message):
        self.terminal.write(message)
        self.history.append(message)



def saveLog(runMode, logger):
    """
    saves a printout of all python's stdiout text, including the full traceback
    in case an error occurs
    """
    user = os.environ.get("USERNAME")
    now = datetimeDotDatetime.now()
    timeStr = now.strftime('%d-%m-%y')
    logName = runMode + '_' + user + '_' + timeStr + '_' + '1'
    ext = '.txt'
    logPath = errorLogDir + '\\' + logName + ext
    headerLines = ['Error Log from ' + os.path.basename(__file__),
                   'Generated: ' + str(now),
                   'Error occurred while attempting to ' + runMode,
                   'Program output is as follows:']
    header = '\n'.join(headerLines)
    body = ''.join(logger.history)
    #body = ''.join(traceback.format_stack())
    content = header + '\n\n' + body
    while os.path.exists(logPath):
        name = os.path.basename(logPath)
        name, ext = os.path.splitext(name)
        n1, n2, n3, num = name.split('_')
        num = str(int(num) + 1)
        logPath = os.path.dirname(logPath) + '\\' + '_'.join([n1, n2, n3, num]) + ext
        
    fle = open(logPath, 'w')
    fle.write(content)
    fle.close()
    raise

def edit_DB(workbooks):
    """
    loads and edits the scoreboard database file
    """
    if os.path.exists(scoreboardDataFile):
        print"Opening scoreboard data file from:", scoreboardDataFile
        workbooks.sbJobDict = readSDF()
        jobDict = workbooks.sbJobDict
        applyEditLogic(jobDict)
        workbooks.calcScoreboardValues()
        print"Saving scoreboard data file to:", scoreboardDataFile
        pSave(jobDict, scoreboardDataFile)
        
def applyEditLogic(jobDict):
    '''
    Replaces all time entry values for LRC and PRC actual date with
    'Not Found' so as to avoid false positives by old data that is not
    being overwritten properly and/or still shows 'NA' when the job
    number is no longer in data dumps.
    '''
    for jobNumber in jobDict.keys():
        jobData = jobDict[jobNumber]
        key = 'Lab Rating Chart\\/Actual Date'
        if key in jobData.keys():
            jobData[key] = add2JobNumber('Not Found')
        key = 'Production Release Checklist\\/Actual Date'
        if key in jobData.keys():
            jobData[key] = add2JobNumber('Not Found')
        
def applyEditLogic_OLD(jobDict):
    i = 0
    j = 0
    k = 0
    z = 0
    badJobs = []
    for jobNum in jobDict.keys():
        i += 1
        jobData = jobDict[jobNum]
        jobVal = jobData['Job #'][-1]['value']
        if jobVal != jobNum:
            print jobNum, 'needs deletion', jobVal
        for column in jobData.keys():
            j += 1
            columnData = jobData[column]
            badStuff = []
            for history in columnData:
                k += 1
                user = history['user']
                date = history['date']
                dateStuff = [date.year, date.month, date.day]
                #print'dateStuff:',dateStuff
                badDate = datetimeDotDatetime(2013, 02, 18)
                badDateStuff = [badDate.year, badDate.month, badDate.day]
                #print'badDateStuff:',badDateStuff
                badUser = 'boiruc'
                if dateStuff == badDateStuff:
                    #print'bad date'
                    if user == badUser:
                        badStuff.append(history)
                        #print"bad user"
            for evil in badStuff:
                columnData.remove(evil)
                z += 1
            if len(columnData) < 1:
                columnData.extend(add2JobNumber(''))
            #sys.exit()
    print i, "job numbers interrogated"
    print j, "data columns infiltrated"
    print k, "history items besieged"
    print z, "bad data entries annihilated"
    
    sleep(10)
        
def applyEditLogic_Old2(jobDict):
    i = 0
    j = 0
    k = 0
    z = 0
    badJobs = []
    for jobNum in jobDict.keys():
        i += 1
        jobData = jobDict[jobNum]
        Manual_Rollback(jobData)
    print i, "job numbers interrogated"
#    print j, "data columns infiltrated"
#    print k, "history items besieged"
#    print z, "bad data entries annihilated"
    #sys.exit()
    
    sleep(10)

def Manual_Rollback(jobData):
    '''
    rolls back anything in 'P&E Lead' that boiruc or laguik updated since 5-17-13 that
    has a last value (the one shown in scoreboard) that was not manually entered (ie it 
    was not automatically filtered out)
    '''
    column = 'P&E Lead'
    date = jobData[column][-1]['date']
    badDay = datetimeDotDatetime(2013, 5, 17)
    diff = date - badDay 
    diff = diff.days
    if diff >=0:
        leadData = jobData[column]
        if len(leadData)>1:
            lastMan = leadData[-1]['manEntry']
            oldMan = leadData[-2]['manEntry']
            if not lastMan and oldMan:
                print date
                user = leadData[-1]['user']
                print 'user:',user
                newVal = leadData[-1]['value'][0]
                print 'lastVal:',newVal
                print 'lastMan:',lastMan
                oldVal = leadData[-2]['value'][0]
                print 'oldVal:',oldVal
                print 'oldMan:',oldMan
                junk = leadData.pop(-1)
                
                
    #timeStr = date.strftime('%d-%m-%y')
    #if timeStr == '17-05-13':
        
        
#    checkDate = datetimeDotDatetime(2013,)
#    manual = 
#    
#    
#    
#    
    
    
def jobVal(sbJobDict, jobNumber, column):
    """
    returns the latest value in the time history for the given jobNumber for
    the given column
    """
    if jobNumber in sbJobDict.keys():
        jobData = sbJobDict[jobNumber]
        if column in jobData.keys():
            return jobData[column][-1]['value'][0]
    return False

#class main_window(wx.Frame):
#    """wxProject MainFrame."""
#    def __init__(self, parent, title):
#        """Create the wxProject MainFrame."""
#        wx.Frame.__init__(self, parent, title=title, size=(500, 500),
#                          style=wx.DEFAULT_FRAME_STYLE|wx.NO_FULL_REPAINT_ON_RESIZE)
#
#
#        # Set up menu bar for the program.
#        self.mainmenu = wx.MenuBar()                  # Create menu bar.
#
#        # Make the 'Project' menu.
#        menu = wx.Menu()
#
#        item = menu.Append(wx.ID_OPEN, '&Open', 'Open project')  # Append a new menu
#        self.Bind(wx.EVT_MENU, self.OnProjectOpen, item)  # Create and assign a menu event.
#
#        item = menu.Append(wx.ID_NEW, '&New', 'New project')
#        self.Bind(wx.EVT_MENU, self.OnProjectNew, item)
#
#        item = menu.Append(wx.ID_EXIT, 'E&xit', 'Exit program')
#        self.Bind(wx.EVT_MENU, self.OnProjectExit, item)
#
#        self.mainmenu.Append(menu, '&Project')  # Add the project menu to the menu bar.
#
#        # Make the 'File' menu.
#        menu = wx.Menu()
#
#        item = menu.Append(wx.ID_ANY, '&Add', 'Add file to project')
#        self.Bind(wx.EVT_MENU, self.OnFileAdd, item)
#
#        item = menu.Append(wx.ID_ANY, '&Remove', 'Remove file from project')
#        self.Bind(wx.EVT_MENU, self.OnFileRemove, item)
#
#        item = menu.Append(wx.ID_ANY, '&Open', 'Open file for editing')
#        self.Bind(wx.EVT_MENU, self.OnFileOpen, item)
#
#        item = menu.Append(wx.ID_ANY, '&Save', 'Save file')
#        self.Bind(wx.EVT_MENU, self.OnFileSave, item)
#
#        self.mainmenu.Append(menu, '&File') # Add the file menu to the menu bar.
#
#        # Attach the menu bar to the window.
#        self.SetMenuBar(self.mainmenu)
#
#        # Create the splitter window.
#        splitter = wx.SplitterWindow(self, style=wx.NO_3D|wx.SP_3D)
#        splitter.SetMinimumPaneSize(1)
#
#        # Create the tree on the left.
#        self.tree = wx.TreeCtrl(splitter, style=wx.TR_DEFAULT_STYLE)
#        self.tree.Bind(wx.EVT_TREE_BEGIN_LABEL_EDIT, self.OnTreeLabelEdit)
#        self.tree.Bind(wx.EVT_TREE_END_LABEL_EDIT, self.OnTreeLabelEditEnd)
#        self.tree.Bind(wx.EVT_TREE_ITEM_ACTIVATED, self.OnTreeItemActivated)
#
#        # Create the editor on the right.
#        self.editor = wx.TextCtrl(splitter, style=wx.TE_MULTILINE)
#        self.editor.Enable(0)
#
#        # Install the tree and the editor.
#        splitter.SplitVertically(self.tree, self.editor)
#        splitter.SetSashPosition(180, True)
#
#        # Some global state variables.
#        self.projectdirty = False
#        self.root = None
#        self.close = False
#
#        self.Bind(wx.EVT_CLOSE, self.OnProjectExit)
#
#        self.Show(True)
#
#    # ----------------------------------------------------------------------------------------
#    # Some nice little handlers.
#    # ----------------------------------------------------------------------------------------
#
#    def project_open(self, project_file):
#        """Open and process a wxProject file."""
#        try:
#            input = open(project_file, 'r')
#            self.tree.DeleteAllItems()
#
#            self.project_file = project_file
#            name = input.readline().replace ('\n', '')
#            self.SetTitle(name)
#
#            # create the file elements in the tree control.
#            self.root = self.tree.AddRoot(name)
#            self.activeitem = self.root
#            for line in input.readlines():
#                self.tree.AppendItem(self.root, line.replace ('\n', ''))
#            input.close()
#            self.tree.Expand(self.root)
#
#            self.editor.Clear()
#            self.editor.Enable(False)
#
#            self.projectdirty = False
#        except IOError:
#            pass
#
#    def project_save(self):
#        """Save a wxProject file."""
#        try:
#            output = open(self.project_file, 'w+')
#            output.write(self.tree.GetItemText(self.root) + '\n')
#            count = self.tree.GetChildrenCount(self.root)  # collect all file (tree) items.
#            iter = 0
#            child = ''
#            for i in range(count):
#               if i == 0:
#                  child, cookie = self.tree.GetFirstChild(self.root)
#               else:
#                  child, cookie = self.tree.GetNextChild(self.root, cookie)
#               output.write(self.tree.GetItemText(child) + '\n')
#            output.close()
#            self.projectdirty = False
#        except IOError:
#            MsgDlg(self, 'There was an error saving the new project file.', 'Error!', wx.OK)
#
#    def CheckProjectDirty(self):
#        """Were the current project changed? If so, save it before."""
#        open_it = True
#        if self.projectdirty:
#            # save the current project file first.
#            result = MsgDlg(self, 'The project has been changed.  Save?')
#            if result == wx.ID_YES:
#                self.project_save()
#            if result == wx.ID_CANCEL:
#                open_it = False
#        return open_it
#
#    def CheckTreeRootItem(self):
#        """Is there any root item?"""
#        if not self.root:
#            MsgDlg(self, 'Please create or open a project before.', 'Error!', wx.OK)
#            return False
#        return True
#
#    # ----------------------------------------------------------------------------------------
#    # Event handlers from here on out.
#    # ----------------------------------------------------------------------------------------
#
#    def OnProjectOpen(self, event):
#        """Open a wxProject file."""
#        open_it = self.CheckProjectDirty()
#        if open_it:
#            dlg = wx.FileDialog(self, 'Choose a project to open', '.', '', '*.wxp', wx.OPEN)
#            if dlg.ShowModal() == wx.ID_OK:
#                self.project_open(dlg.GetPath())
#            dlg.Destroy()
#
#    def OnProjectNew(self, event):
#        """Create a new wxProject."""
#        open_it = self.CheckProjectDirty()
#        if open_it:
#            dlg = wx.TextEntryDialog(self, 'Name for new project:', 'New Project',
#                                     'New project', wx.OK|wx.CANCEL)
#            if dlg.ShowModal() == wx.ID_OK:
#                newproj = dlg.GetValue()
#                dlg.Destroy()
#                dlg = wx.FileDialog(self, 'Place to store new project.', '.', '', '*.wxp', wx.SAVE)
#                if dlg.ShowModal() == wx.ID_OK:
#                    try:
#                        # save the project file.
#                        proj = open(dlg.GetPath(), 'w')
#                        proj.write(newproj + '\n')
#                        proj.close()
#                        self.project_open(dlg.GetPath())
#                    except IOError:
#                        MsgDlg(self, 'There was an error saving the new project file.', 'Error!', wx.OK)
#            dlg.Destroy()
#
#    def SaveCurrentFile(self):
#        """Check and save current file."""
#        go_ahead = True
#        if self.root:
#            if self.activeitem != self.root:
#                if self.editor.IsModified():  # Save modified file before
#                    result = MsgDlg(self, 'The edited file has changed.  Save it?')
#                    if result == wx.ID_YES:
#                        self.editor.SaveFile(self.tree.GetItemText(self.activeitem))
#                    if result == wx.ID_CANCEL:
#                        go_ahead = False
#                if go_ahead:
#                    self.tree.SetItemBold(self.activeitem, 0)
#        return go_ahead
#
#    def OnProjectExit(self, event):
#        """Quit the program."""
#        if not self.close:
#            self.close = True
#            if not self.SaveCurrentFile():
#                self.close = False
#            if self.projectdirty and self.close:
#                result = MsgDlg(self, 'The project has been changed.  Save?')
#                if result == wx.ID_YES:
#                    self.project_save()
#                if result == wx.ID_CANCEL:
#                    self.close = False
#            if self.close:
#                self.Close()
#        else:
#            event.Skip()
#
#    def OnFileAdd(self, event):
#        """Adds a file to the current project."""
#        if not self.CheckTreeRootItem():
#            return
#
#        dlg = wx.FileDialog(self, 'Choose a file to add.', '.', '', '*.*', wx.OPEN)
#        if dlg.ShowModal() == wx.ID_OK:
#            path = os.path.split(dlg.GetPath())
#            self.tree.AppendItem(self.root, path[1])
#            self.tree.Expand(self.root)
#            self.project_save()
#
#    def OnFileRemove(self, event):
#        """Removes a file to the current project."""
#        if not self.CheckTreeRootItem():
#            return
#        item = self.tree.GetSelection()
#        if item != self.root:
#            self.tree.Delete(item)
#            self.project_save()
#
#    def OnFileOpen(self, event):
#        """Opens current selected file."""
#        if self.root:
#            item = self.tree.GetSelection()
#            if item != self.root:
#                self.OnTreeItemActivated(None, item)
#                return
#        MsgDlg(self, 'There is no file to load.', 'Error!', wx.OK)
#
#    def OnFileSave(self, event):
#        """Saves current selected file."""
#        if self.root:
#            if self.activeitem != self.root:
#                self.editor.SaveFile(self.tree.GetItemText(self.activeitem))
#                return
#        MsgDlg(self, 'There is no file to save.', 'Error!', wx.OK)
#
#
#    def OnTreeLabelEdit(self, event):
#        """Edit tree label (only root label can be edited)."""
#        item = event.GetItem()
#        if item != self.root:
#            event.Veto()
#
#    def OnTreeLabelEditEnd(self, event):
#        """End editing the tree label."""
#        self.projectdirty = True
#
#
#    def OnTreeItemActivated(self, event, item=None):
#        """Tree item was activated: try to open this file."""
#        go_ahead = self.SaveCurrentFile()
#
#        if go_ahead:
#            if event:
#                item = event.GetItem()
#            self.activeitem = item
#            if item != self.root:
#                # load the current selected file
#                self.tree.SetItemBold(item, 1)
#                self.editor.Enable(1)
#                self.editor.LoadFile(self.tree.GetItemText(item))
#                self.editor.SetInsertionPoint(0)
#                self.editor.SetFocus()
#            else:
#                self.editor.Clear()
#                self.editor.Enable(0)
#    
#class App(wx.App):
#    """Scoreboard Application."""
#    def OnInit(self):
#        """Create the Scoreboard Application."""
#        frame = main_window(None, 'Scoreboard'+ __file__.split(' ')[1][:-4])
#        if projfile != 'Unnamed':
#            frame.project_open(projfile)
#        return True
#
#def startExternal():
#    '''
#    Entry point function for creating and using the non-Excel based
#    scoreboard viewing application
#    '''
#    app = App(0)
#    app.MainLoop()
    
def Run_Scoreboard(runMode, logger):
    '''
    Runs the scoreboard in the requested 'mode'
    '''
    if runMode == 'login':
        """
        this will be called when the scoreboard is first opened
        and will determine what the user can do and see
        based on their user rights profile
        """
        try:
            setView()
           # workbooks = inputWorkbooks()
           # refresh(workbooks)
        except:
            tracebackDotPrint_exc(file=sys.stdout)
            saveLog(runMode, logger)
        #excels.append(setView())
#            workbooks = readScoreboardDatabase()
#            refresh(workbooks)
    elif runMode == 'create':
        """
        this will look for new copies of the data dumps and compile
        a new series of data that will be compared against the master
        data file. Any new values will be logged and dated, and the 
        scoreboard will be populated with the latest information
        """
        try:
            credentials = login()
            if 'Developer' in credentials.roles:
                inputPaths = pathSetup()
                createDatabase(inputPaths)
        except:
            tracebackDotPrint_exc(file=sys.stdout)
            saveLog(runMode, logger)
            #excels.extend(createDatabase(inputPaths))
    elif runMode == 'refresh':
        """
        This will read the latest data from the master data file (mdf)
        on the share drive and populate the user's scoreboard view.
        """
        #workbooks = readScoreboardDatabase()
        try:
            workbooks = inputWorkbooks()
            refresh(workbooks)
        except:
            tracebackDotPrint_exc(file=sys.stdout)
            saveLog(runMode, logger)
        #excels.extend(refresh(workbooks))
    elif runMode == 'sync':
        """
        This will save changes made by the user to the scoreboard to 
        the scoreboard data file on the share drive, and will also apply 
        the latest changes from the sdf to the user's scoreboard view.
        """
        try:
            newBooks = inputWorkbooks()
            sync(newBooks)
        except:
            tracebackDotPrint_exc(file=sys.stdout)
            saveLog(runMode, logger)

    elif runMode == 'createA':
        """
        this will run through all dates available that have data dumps
        so that a complete time history can be created
        """
        try:
            timeBuilding = True
            inputPaths = pathSetup()
            dirs = getDirs(inputPaths)
            dates, dateList = getAvailableDates(dirs)
            for date in dateList:#[:3]:
                if len(dates[date]['files']) >= 5:
                    print date
                    dataDate = date
                    print"%d Sources:" % len(dates[date]['files'])
                    for fle, source in dates[date]['files']:
                        print source, fle
                    print
                    createDatabase(dates[date]['files'])
        except:
            tracebackDotPrint_exc(file=sys.stdout)
            saveLog(runMode, logger)
            
    elif runMode == 'editDB':
        """
        this will edit the database file using whatever logic is presented in the
        "edit_DB()" function.
        """
        try:
            newBooks = inputWorkbooks()
            edit_DB(newBooks)
            refresh(newBooks)
        except:
            tracebackDotPrint_exc(file=sys.stdout)
            saveLog(runMode, logger)
            
    elif runMode == 'externalView':
        '''
        This will create a wxWidgets application to render scoreboard information
        without using Excel as a middle man. At first it will be view only without 
        much formatting but will slowly gain functionality from the excel based
        scoreboard and eventually elimintate the need for excel.
        '''
        try:
            startExternal()
        except:
            tracebackDotPrint_exc(file=sys.stdout)
            saveLog(runMode, logger)
            
def cleanup():
    '''
    cleans up any open com servers to excel
    '''
    excel = CPL4.GetActiveExcel()
    #for excel in excels:
    excel.Application.DisplayAlerts = 1
    del excel
    for i in range(9):
        excel = CPL4.GetActiveExcel()
        del excel
    #print"Com objects left:",pythoncom._GetInterfaceCount() 
    #pythoncom.CoUnintialize()
    #pythoncom.CoUninitialize()
    #print"Com objects left:",pythoncom._GetInterfaceCount() 
    
def Initialize():
    '''
    starts process, gets system variables or sets mode based on 
    hardcoded value
    '''
    global timeBuilding
    global dataDate
    sys.stdout = Logger()
    logger = sys.stdout
    if len(sys.argv) > 1:
        args = sys.argv
        runMode = args[1]
    else:
        runMode = 'create'
        #runMode = 'login'
#        runMode = 'refresh' ##EE
        #runMode = 'sync'
        #runMode = 'refresh'
        #runMode = 'editDB'
        #runMode = 'Sync2' #(run through synching as if creating)
    return runMode, logger

if __name__ == '__main__':
    runMode, logger = Initialize()
    
    Run_Scoreboard(runMode, logger)
    
    cleanup()
