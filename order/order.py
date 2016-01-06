import SoftLayer as sl
import yaml, logging, os, fnmatch

class Node:
    _required_definitions = ['name']
    def __init__(self, node_definition):
        for requirement in self._required_definitions:
            try:
                node_definition[requirement]
            except KeyError:
                logging.critical("Node definition %s does not have required field %s\n"
                                 "Node definition passed: %s \n"
                                 "Exiting!" % (self.name, requirement, node_definition))
                exit(1)
        self.name = node_definition['name']
        self.node = node_definition
    def __repr__(self):
        rep = "%s\n" % self.name
        for spec in sorted(self.node.keys(), key=str.lower):
            rep = rep + "\t%r:\t%r\n" % (spec, self.node[spec])
        return rep

class Environment:
    _required_definitions = []
    def __init__(self, environment_definition, node_types):
        self.name = name
        self.env = []
        for node in environment_definition:
            # make sure node has required definitions
            for requirement in self._required_definitions:
                try:
                    node[requirement]
                except KeyError:
                    logging.critical("Environment definition %s does not have required field %s\n"
                                     "Environment definition passed: %s\n"
                                     "Exiting!" % (self.name, requirement, environment_definition))
                    exit(1)

            if node['node'] not in node_types.keys():
                logging.error("No node definition for not type: %s\n"
                              "Exiting!" % node['node'])
                exit(1)
    def __repr__(self):
        rep = "%s\n" % self.name
        for node in self.env:
            rep = rep + ("\t%r\n" 
                         "-------------------\n" % node)
        return rep

def parser_generator(ftype, obj = None):
    def parser(dir, object_dict = {}):
        file_list = [file for file in os.listdir(dir) if fnmatch.fnmatch(file, ftype)]
        for file in file_list:
            with open(dir+'/'+file, 'r') as f:
                object_list = yaml.safe_load(f)
            if obj is not None:
                for object in object_list:
                    object = obj(object)
                    object_dict[object.name] = object
            else:
                object_dict = object_list
        if not file_list:
            logging.warn('No %s definition files in %s!' % (ftype, dir))
        return object_dict
    return parser

if __name__ == '__main__':
    
    # find all node definition files
    node_parser = parser_generator('*.node', Node)
    node_types = node_parser('definitions/std')
    node_types = node_parser('definitions/usr', object_dict = node_types)
    # find all environment definition files
#    env_parser = parser_generator('*.env', Environment)
#    env_types = env_parser('definitions/std')
#    env_types = env_parser('definitions/usr', object_dict = env_types)

    for node in node_types:
        print node
#    for env in env_types:
#        print env
