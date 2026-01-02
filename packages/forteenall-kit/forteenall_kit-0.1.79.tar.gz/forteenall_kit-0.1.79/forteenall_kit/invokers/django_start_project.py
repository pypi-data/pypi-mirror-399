from ..feature import KitFeature



class InvokerData:
    
    pass

class Feature(KitFeature):
    
    feature_type = 'django_start_project'
    def __init__(self, project_name):
        self.params = {'project_name':project_name}
    
    def execute(self):
        pass