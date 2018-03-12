"""
#Examples of usage:

#create an instance of a Dataset:
container = Dataset()
#assign value to row and col. If needed, row and col will be automatically created:
container[0,"x"] = 12
print container.data
container[5,"y"] = 99
print container.data
print container.names
#tell the dataset to save its content to a file with passed file name:
container.saveToFile("test.csv")
"""

from __main__ import *


class Dataset(object):
    
    def __init__(self, nRows=0):
        self.names = []
        self.data = {}
        self.__nRows = nRows

    def __setitem__(self, access, item):
        rowIndex = access[0]
        colName = str(access[1])
        
        if self.__nRows is None or rowIndex > self.__nRows-1:
            self.__nRows = rowIndex+1
            for key in self.data:
                for row in range(0,rowIndex):
                    self.data[key].append(None)
        
        if colName in self.data:
            self.data[colName][rowIndex] = item
        else:
            self.names.append(colName)
            newCol = [None] * self.__nRows
            newCol[rowIndex] = item
            self.data[colName] = newCol

    def __getitem__(self, access):
        rowIndex = access[0]
        colName = access[1]
        
        if rowIndex > self.__nRows-1:
            print "ERROR: dataset has only " + str(self.__nRows) + " rows."
            return None
        if colName not in self.data:
            print "ERROR: dataset does not have variable " + colName + "."
            return None
        return self.data[colName][rowIndex]
        
    def nRows(self):
        return self.__nRows
        
    def nCols(self):
        return len(self.data)
        
    def saveToFile(self, fileName):
        self.__saveMethod(fileName)
        
    def saveRowToFile(self, rowToSave, fileName):
        self.__saveMethod(fileName, rowToSave)
        
    def __saveMethod(self, fileName, whichRow=None):
        outputFile = open(fileName, 'wb')
        csvData = csv.writer(outputFile, lineterminator='\n')

        nCols = len(self.data)

        line = [None] * nCols
        for col in range(0, nCols):
            line[col] = self.names[col]
        csvData.writerow(line)

        for row in range(0,self.__nRows):
            if row == whichRow or whichRow is None:
                line = [None] * nCols
                for col in range(0, nCols):
                    variableName = self.names[col]
                    value = self.data[variableName][row]
                    value = "NA" if value is None else value
                    line[col] = value
                csvData.writerow(line)
        outputFile.close()