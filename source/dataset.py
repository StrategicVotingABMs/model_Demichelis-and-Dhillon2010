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
        self.names = [None] * nRows
        self.data = {}
        self.nRows = None

    def __setitem__(self, access, item):
        rowIndex = access[0]
        colName = str(access[1])
        
        if self.nRows is None or rowIndex > self.nRows-1:
            self.nRows = rowIndex+1
            for key in self.data:
                for row in range(0,rowIndex):
                    self.data[key].append(None)
        
        if colName in self.data:
            self.data[colName][rowIndex] = item
        else:
            self.names.append(colName)
            newCol = [None] * self.nRows
            newCol[rowIndex] = item
            self.data[colName] = newCol

    def __getitem__(self, access):
        rowIndex = access[0]
        colName = access[1]
        
        if rowIndex > self.nRows-1:
            print "ERROR: dataset has only " + str(self.nRows) + " rows."
            return None
        if colName not in self.data:
            print "ERROR: dataset does not have variable " + colName + "."
            return None
        return self.data[colName][rowIndex]
        
    def nRows(self):
        return self.nRows
        
    def nCols(self):
        return len(self.data)
        
    def saveToFile(self, fileName):
        outputFile = open(fileName, 'wb')
        csvData = csv.writer(outputFile, lineterminator='\n')

        nCols = len(self.data)

        line = [None] * nCols
        for col in range(0, nCols):
            line[col] = self.names[col]
        csvData.writerow(line)

        for row in range(0,self.nRows):
            line = [None] * nCols
            for col in range(0, nCols):
                variableName = self.names[col]
                value = self.data[variableName][row]
                line[col] = value
            csvData.writerow(line)
        outputFile.close()