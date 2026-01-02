from ..feature import KitFeature



class InvokerData:
    
    pass

class Feature(KitFeature):
    
    feature_type = 'django_start_project'
    def __init__(self):
        self.params = {}
    
    def execute(self):
        pass