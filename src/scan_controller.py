####################################################################
#    Class CONTROLLER: contral scan                                 #
####################################################################
# External modules
import os
import random
import time
from math import log10
import math
# Internal modules
import auxfun as af

class CONTROLLER:
    def __init__(self):
        self._FolderName = 'test'
        self._PointNum   = 2
        self._ScanMethod = 'random'
        self._RandomSeed = -1
        self._PrintNum   = 10
        self._AccepRate  = 0.25
        self._FlagTuneR  = False
        
        self._Prog    = {}
        self.AllPar   = {}
        self.InPar    = {}
        self.FixedPar    = {}
        self.OutPar   = {}

        self.InputPar = {} # Different to InPar, including prior, value
        
        self.GridBin = {} # Number of bins
        self.MCMCss = {}  # Step size
        self.MCMCiv = {}  # Initial value

        self.MNOutputFile = 'test/MultiNestData/'
    
        self._Count   = 0
    
    def setScanMethod(self, method):
        self._ScanMethod = method.upper()
        if self._ScanMethod not in af._all:
            af.ErrorStop('%s is not a supported scan method'%method)
        af.Info('Scan method       = %s'%self._ScanMethod)
        
    def backup_result(self, FolderName, cp=False):
        if not os.path.exists(os.path.join(af.CurrentPath,"Backup")):
            os.mkdir(os.path.join(af.CurrentPath,"Backup"))
        BackupTime = time.strftime("_%Y_%m_%d_%H_%M_%S", time.localtime())
        name = os.path.basename(os.path.normpath(FolderName))
        BackupPath = os.path.join(af.CurrentPath,"Backup/%s%s"%(name, BackupTime))
        action = r'cp -r ' if cp else r'mv '
        af.Info('Back up previous result into %s.'%BackupPath)
        os.system(action+r" %s %s" %(FolderName, BackupPath))
    
    def setFolderName(self, name):
        # Turn the result folder path into absolute path
        if name.startswith('/home') or name.startswith('~'):
            self._FolderName = name
        else:
            self._FolderName = os.path.join(af.CurrentPath, name)
        
        if self._ScanMethod in af._post:
            if not os.path.exists(self._FolderName):
              af.ErrorStop("The result folder %s does not exist."%self._FolderName)

            if self._ScanMethod == af._postprocess:
              # Backup previous results
              self.backup_result(self._FolderName, cp=True)
              # rm Figure and SavedFile folder
              os.system(r"find %s -type f -name '*' | xargs rm" %os.path.join(self._FolderName,'SavedFile'))
              os.system(r"find %s -type f -name '*' | xargs rm" %os.path.join(self._FolderName,'Figures'))
              # rename data file
              if not os.path.exists(os.path.join(self._FolderName,af.ResultFile_post)):
                if not os.path.exists(os.path.join(self._FolderName,af.ResultFile)):
                  af.ErrorStop("No result data file in %s."%self._FolderName)
                else:
                  os.system(r"mv %s %s"%(os.path.join(self._FolderName, af.ResultFile), os.path.join(self._FolderName, af.ResultFile_post)))
              else:
                if af.flag_resume:
                  # TODO Add resume
                  af.ErrorStop("no resume function")
            else: # af._plot
              if not os.path.exists(os.path.join(self._FolderName,af.ResultFile)):
                af.ErrorStop("No result data file in %s."%self._FolderName)
                           
        else:
            # Deal with the situation that the result folder already exists.
            if os.path.exists(self._FolderName):
                af.Info(("* The Result file [%s] already exists." % name ))
                while True:
                    c = input("Choose: (r)replace, (b)backup, (s)stop\n")
                    if c == "r":
                        os.system(r"rm -r %s" %self._FolderName)
                        break
                    elif c == "b":
                        self.backup_result(self._FolderName)
                        break
                    elif c == "s":
                        exit(1)
                    else:
                        af.Info("Wrong input! Please type in one of ('r','b','s')")
            # Create result folder
            os.mkdir(self._FolderName)
            os.mkdir(os.path.join(self._FolderName,'SavedFile'))
            if self._ScanMethod == af._multinest:
                self.MNOutputFile = os.path.join(self._FolderName, "MultiNestData/")
                os.mkdir(self.MNOutputFile)
        af.Info('...............................................')
        af.Info('Result file name  = %s'%self._FolderName)


    def setPointNum(self, ntot):
        self._PointNum = int(ntot)
        if self._PointNum < 1 :
            af.ErrorStop('"Number of points" should larger than 0')
        af.Info('Number of points  = %s'%self._PointNum)

    def setRandomSeed(self, iseed):
        self._RandomSeed = int(iseed)
        # If iseed is provided in the input file, initialize the basic random number generator
        # Otherwise, it will be initialized by current system time, and self._RandomSeed = -1,
        # which means also initialized by current system time in MultiNest
        random.seed( self._RandomSeed )
        af.Info('Random seed       = %s'%self._RandomSeed)

    def setAccepRate(self, AccepRate):
        self._AccepRate = float(AccepRate)
        if self._AccepRate >= 1 or self._AccepRate <= 0:
            af.ErrorStop('"Acceptance rate" must be in [0,1]. The suggest value is 0.5 for d<=2, 0.25 otherwise.')
        self._FlagTuneR = True
        af.Info('Acceptance rate   = %s'%self._AccepRate)

    def setPrintNum(self, nprint):
        self._PrintNum = int(nprint)
        if self._PrintNum < 1 :
            af.ErrorStop('"Interval of print" should be larger than 0')
        af.Info('Interval of print = %s'%self._PrintNum)


    def InputCheck(self, name, num, items):
        return 'Input parameter "%s" need %i iterms [ID, Prior, %s]'%(name, num, items)
        
    def setInputPar(self, inputvar):
        inputvar = af.string2nestlist(inputvar)

        # inputvar is list of list of input parameters define in section [scan]
        af.Info('Input parameters   =  ')
        for ii in inputvar:
            lenii = len(ii)
            
            if self._ScanMethod == af._postprocess:
              self.InPar[ii[0]] = af.NaN
              self.AllPar[ii[0]] = af.NaN
              af.Info('  ID= %s, read from previous '%(ii[0]))
              continue
            
            if lenii < 3 :
              af.ErrorStop(self.InputCheck(ii[0], 3, "Value"))
            
            # Set fixed par
            if ii[1].upper() == "FIXED":
              if lenii > 3 :
                af.WarningNoWait(self.InputCheck(ii[0], 3, "Value"))
                af.WarningWait("The rest %i values will be ignore."%(lenii-3) )
              af.Info('  ID= %s\tPrior= %s\t =%f'%(ii[0],ii[1],ii[2]))
              self.FixedPar[ii[0]] = ii[2]
              self.AllPar[ii[0]] = ii[2]
              continue
            
            # Initialize other input par to NaN
            self.InputPar[ii[0]] = ii
            self.InPar[ii[0]] = af.NaN
            self.AllPar[ii[0]] = af.NaN
            if lenii < 4 :
              af.ErrorStop(self.InputCheck(ii[0], 4, "Minimum, Maximum"))
            
            if self._ScanMethod in [af._random, af._multinest]:
              if lenii > 4 :
                af.WarningNoWait(self.InputCheck(ii[0], 4, "Minimum, Maximum"))
                af.WarningWait("The rest %i values will be ignore."%(lenii-4) )
              af.Info('  ID= %s\tPrior= %s\tMin= %f\tMax= %f'%(ii[0],ii[1],ii[2],ii[3]))
              continue
                
            if self._ScanMethod == af._grid:
              if lenii == 4:
                self.GridBin[ii[0]]=20
                af.WarningNoWait(self.InputCheck(ii[0], 5, "Minimum, Maximum, Number of bins"))
                af.WarningWait("'Number of bins' will take default value, 20.")
              else:
                self.GridBin[ii[0]]=ii[4]
                if self.GridBin[ii[0]] < 0 or type(ii[4]) != int:
                  af.WarningNoWait(InputCheck(ii[0], 5, "Minimum, Maximum, Number of bins"))
                  af.ErrorStop("'Number of bins' is not a positive integer.")
                if lenii> 5:
                  af.WarningNoWait(self.InputCheck(ii[0], 5, "Minimum, Maximum, Number of bins"))
                  af.WarningWait("The rest %i values will be ignore."%(lenii-5) )
              af.Info('  ID= %s\tPrior= %s\tMin= %f\tMax= %f\tNbin=%i'%(ii[0],ii[1],ii[2],ii[3],self.GridBin[ii[0]]))
              continue
            
            if self._ScanMethod == af._mcmc:
              if lenii < 6:
                af.WarningNoWait(self.InputCheck(ii[0], 6, "Minimum, Maximum, Interval, Initial value"))
                self.MCMCiv[ii[0]] = 1./2.
                IniV = float(ii[3]+ii[2])/2.
                af.WarningWait("'Initial value' will take default value, (Max-Min)/2.")
                if lenii < 5:
                  self.MCMCss[ii[0]] = 1./30.
                  Step = float(ii[3]-ii[2])/30.
                  af.WarningWait("'Interval' will take default value, (Max-Min)/30.")
              else:
                # The scan range is normalized to 1
                self.MCMCss[ii[0]] = 1.0/float(ii[4])
                Step = float(ii[3]-ii[2])/float(ii[4])
                if ii[1].lower() == 'flat':
                  self.MCMCiv[ii[0]] = float(ii[5]-ii[2])/float(ii[3]-ii[2])
                elif ii[1].lower() == 'log':
                  self.MCMCiv[ii[0]] = (log10(ii[5])-log10(ii[2]))/(log10(ii[3]) - log10(ii[2]))
                IniV = ii[5]
                if lenii > 6:
                  af.WarningNoWait(self.InputCheck(ii[0], 6, "Minimum, Maximum, Interval, Initial value"))
                  af.WarningWait("The rest %i values will be ignore."%(lenii-6) )
              af.Info('  ID= %s\tPrior= %s\tMin= %f\tMax= %f\tStep=%f\tIniV=%f'%(ii[0],ii[1],ii[2],ii[3],Step,self.MCMCiv[ii[0]]))
              continue
    
    def setProgram(self,prog):
        self._Prog = prog
        # Copy input vars of prog into allvars
        for ii in prog:
            af.Debug('Programe ID', ii)
            af.Debug('Corresponding output vars', prog[ii].outvar)

            # save all parameters
            for jj in prog[ii].outvar:
                self.AllPar[jj] = prog[ii].outvar[jj]
                self.OutPar[jj] = prog[ii].outvar[jj]

            for jj in prog[ii].invar:
                if jj not in list(self.AllPar.keys()):
                    self.AllPar[jj] = prog[ii].invar[jj]
                    self.OutPar[jj] = prog[ii].invar[jj]
            for jj in prog[ii].boundvar:
                if jj not in list(self.AllPar.keys()):
                    self.AllPar[jj] = prog[ii].boundvar[jj]
                    self.OutPar[jj] = prog[ii].boundvar[jj]
            for jj in prog[ii].cgauvar:
                if jj not in list(self.AllPar.keys()):
                    self.AllPar[jj] = prog[ii].cgauvar[jj]
                    self.OutPar[jj] = prog[ii].cgauvar[jj]
            for jj in prog[ii].cffchi2var:
                if jj not in list(self.AllPar.keys()):
                    self.AllPar[jj] = prog[ii].cffchi2var[jj]
                    self.OutPar[jj] = prog[ii].cffchi2var[jj]

        # Order parameters
        self.InPar = af.sortDic(self.InPar)
        self.FixedPar = af.sortDic(self.FixedPar)
        self.OutPar = af.sortDic(self.OutPar)

        af.Debug('All vars:   ', self.AllPar)
        af.Debug('Input Pars: ', self.InPar)
        af.Debug('Fixed Pars: ', self.FixedPar)
        af.Debug('Output Pars:', self.OutPar)
                
    def getFolderName(self):
        return self._FolderName
    def getPointNum(self):
        return self._PointNum
    def getScanMethod(self):
        return self._ScanMethod
    def getRandomSeed(self):
        return self._RandomSeed
    def getPrintNum(self):
        return self._PrintNum
    def getDebugFlag(self):
        return self._DebugFlag
    
    def getStepSize(self):
        return self.MCMCss
    def getInitialValue(self):
        return self.MCMCiv

    def getFlagTuneR(self):
        return self._FlagTuneR
    def getAccepRate(self):
        return self._AccepRate
