
class Debug(object):
    
    isOn = False
    
    @staticmethod
    def Print(args):
        if Debug.isOn:
            print args
            
    @staticmethod
    def PrintIf(condition, args):
        if condition and Debug.isOn:
            print args