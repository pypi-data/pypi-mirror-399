from ..feature import KitFeature



class InvokerData:
    
    pass

class Feature(KitFeature):
    
    feature_type = 'flow_wbs'
    def __init__(self, version):
        self.params = {'version':version}
    
    def init(self):
        pass
    
    def execute(self):
        pass