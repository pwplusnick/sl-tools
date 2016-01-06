import SoftLayer as sl
import yaml, logging, os, fnmatch

hw_nicks = {}

class OrderType:
    """ The Grand class that will be the base class for all orders
    It has definitions and keywords and makes sure that the definition meets the minimum requirements
    and only uses keywords."""
    _required_definitions = []
    _keywords = []
    def __init__(self, definition, nicks = {}):
        self.definition = definition

    def check_requirements(self):
        # make sure it has required definitions
        for requirement in self._required_definitions:
            if requirement not in self.definition.keys():
                logging.critical("%s definition %s does not have required field %s\n"
                                 "Exiting!" % (self.__class__.__name__, self.definition, requirement))
                exit(1)
    def check_keywords(self):
        for arg in self.definition.keys():
            if arg not in self._keywords:
                logging.critical("%s definition %s has no keyword called %s."
                                 "Exiting!" % (self.__class__.__name__, self.definition, requirement))
                exit(1)

class Node (OrderType):
    """ A node defines a name that is assigned to a particular hardware configurations """
    _required_definitions = ['name', 'cpu']
    _keywords = []
    def __init__(self, node_definition):
        OrderType.__init__(self, node_definition)
        self.check_requirements()
        self.check_keywords
        self.name = node_definition['name']
        self.node = node_definition
    def __repr__(self):
        rep = "%s\n" % self.name
        for spec in sorted(self.node.keys(), key=str.lower):
            rep = rep + "\t%r:\t%r\n" % (spec, self.node[spec])
        return rep

class Environment:
    """ Environment defines a particular configuration of nodes """
    _required_definitions = ['node']
    def __init__(self, environment_definition, node_types):
        self.env = []
        self.keywords = self.keywords + self.required_keywords + node_types.keys()
        OrderType.__init__(self, environment_definition)
        self.check_requirements()
        self.check_arguments()

    def __repr__(self):
        rep = "%s\n" % self.name
        for node in self.env:
            rep = rep + ("\t%r\n" 
                         "-------------------\n" % node)
        return rep

def parser_generator(ftype, obj = None):
    """ Generate a function that will parse the yaml files with a specificied name convention
    and returns a list of a specified object of parsed files """
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
            logging.info('No %s definition files in %s!' % (ftype, dir))
        return object_dict
    return parser

if __name__ == '__main__':

    # find all hardware nicknames
    hw_nick_parser = parser_generator('*.hwn', None)
    hw_nicks = hw_nick_parser('definitions/std')
    hw_nicks = hw_nick_parser('definitions/usr', object_dict = hw_nicks)
    
    # find all node definition files
    node_parser = parser_generator('*.node', Node)
    node_types = node_parser('definitions/std')
    node_types = node_parser('definitions/usr', object_dict = node_types)
    # find all environment definition files
#    env_parser = parser_generator('*.env', Environment)
#    env_types = env_parser('definitions/std')
#    env_types = env_parser('definitions/usr', object_dict = env_types)

    print hw_nicks
    print node_types
    print node_types['FooBar']
#    for env in env_types:
#        print env
