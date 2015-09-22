import yaml

class yld(object):
    """description of class"""
    def __init__ (self):
                data = {}
                
    def yaml_loader(filepath):
                """Loads a yaml file"""
                with open(filepath, "r") as file_descriptor:
                        data = yaml.load(file_descriptor)
                return data

    def ymal_dump(filepath, data):
                """Dump data to a yaml file"""
                with open(filepath, "w") as file_desxriptor:
                        yaml.dump(data, file_desxriptor)


