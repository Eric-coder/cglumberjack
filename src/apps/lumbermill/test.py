from cglcore.path import PathObject, CreateProductionData
import os

test_path = r'D:/VFX/companies/cgl-fsutests/render/comptestB/assets/Library/bob/ref/publish/000.000/high\rolling_logs.gif'
path_object = PathObject(test_path)
print path_object.path_root


CreateProductionData(test_path, json=True, test=True)
