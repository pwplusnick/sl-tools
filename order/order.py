import SoftLayer as sl
import yaml, logging, os, fnmatch


hw_nicks = {}

def identity(arg):
    "Returns its argument"
    return arg

class OrderType:
    """ The Grand class that will be the base class for all orders
    It has definitions and keywords and makes sure that the definition meets the minimum requirements
    and only uses keywords."""
    _required_definitions = []
    _keywords = []
    _keyword_handler = {}
    def __init__(self, definition, nicks = {}):
        self.definition = definition
        self._keywords = self._keywords + self._required_definitions
        self._order = {}

        self._check_requirements()
        self._check_keywords()
        self._parse()

    def __getitem__(self, index):
        try:
            return self._order[index]
        except KeyError:
            logging.critical("%s definition %s has no field %s\n"
                             "Exiting!" % (self.__class__.__name__, self.definition, index))

    def __repr__(self):
        return self.__class__.__name__

    def _check_requirements(self):
        # make sure it has required definitions
        for requirement in self._required_definitions:
            if requirement not in self.definition.keys():
                logging.critical("%s definition %s does not have required field %s\n"
                                 "Exiting!" % (self.__class__.__name__, self.definition, requirement))
                exit(1)

    def _check_keywords(self):
        # check to make sure every field is both defined and has a handler
        for field in self.definition.keys():
            if field not in self._keywords:
                logging.critical("%s definition %s has no keyword called %s.\n"
                                 "Exiting!" % (self.__class__.__name__, self.definition, field))
                exit(1)
        for keyword in self._keywords:
            if keyword not in self._keyword_handler.keys():
                logging.critical("%s keyword %s has no handler."
                                 "Exiting!" % (self.__class__.__name__, keyword))
                exit(1)


    def _parse(self):
        for field in self.definition.keys():
            self._order[field] = self._keyword_handler[field](self.definition[field])

class Node (OrderType):
    """ A node defines a name that is assigned to a particular hardware configurations """
    _required_definitions = ['name', 'cpu']
    _keywords = ['hd']
    _keyword_handler = \
        {
        'name': identity,
        'cpu': identity,
        'hd': identity
        }

    def __init__(self, node_definition):
        OrderType.__init__(self, node_definition)

    def __repr__(self):
        rep = ("%s\n" 
               "%s\n" % (OrderType.__repr__(self), self['name']))
        for spec in sorted(self._order.keys(), key=str.lower):
            rep = rep + "\t%r:\t%r\n" % (spec, self._order[spec])
        return rep

class Environment (OrderType):
    """ Environment defines a particular configuration of nodes """
    _required_definitions = ['nodes', 'name']
    _keywords = []
    _keyword_handler = {'name': identity}

    def __init__(self, environment_definition, node_types={}):
        self.node_types = node_types
        self._env = {}
        self._keyword_handler['nodes'] = self._parse_nodes

        OrderType.__init__(self, environment_definition)
        self._check_requirements()
        self._check_keywords()

    def __repr__(self):
        rep =("%r\n"
              "%s\n" % (OrderType.__repr__(self), self['name']))
        for name, node in self._env.iteritems():
            rep = rep + ("\t%r: %r\n" 
                         "-------------------\n" % (name, node))
        return rep

    def _parse(self):
        OrderType._parse(self)
        for name, node in self._order.iteritems():
            if name not in self._keywords:
                self._env[name] = node

    def _parse_nodes(self, nodes):
        for name, num in nodes.iteritems():
            try:
                self._order[name] = {'node': self.node_types[name], 'num': num}
            except KeyError:
                logging.critical("%s calls non-existant node %s"
                                 % (self.__class__.__name__,
                                    name))
                exit(1)

def yaml_parser_generator(ftype, obj = None, **kwargs):
    """ Generate a function that will parse the yaml files with a specificied name convention
    and returns a list of a specified object of parsed files """
    def parser(dir, object_dict = {}):
        file_list = [file for file in os.listdir(dir) if fnmatch.fnmatch(file, ftype)]
        for file in file_list:
            with open(dir+'/'+file, 'r') as f:
                object_list = yaml.safe_load(f)
            if obj is not None:
                for object in object_list:
                    object = obj(object, **kwargs)
                    object_dict[object['name']] = object
            else:
                object_dict = object_list
        if not file_list:
            logging.info('No %s definition files in %s!' % (ftype, dir))
        return object_dict
    return parser

if __name__ == '__main__':

    # find all hardware nicknames
    hw_nick_parser = yaml_parser_generator('*.hwn', None)
    hw_nicks = hw_nick_parser('definitions/std')
    hw_nicks = hw_nick_parser('definitions/usr', object_dict = hw_nicks)
    
    # find all node definition files
    node_parser = yaml_parser_generator('*.node', Node)
    node_types = node_parser('definitions/std')
    node_types = node_parser('definitions/usr', object_dict = node_types)
    # find all environment definition files
    env_parser = yaml_parser_generator('*.env', Environment, node_types=node_types)
    env_types = env_parser('definitions/std')
    env_types = env_parser('definitions/usr', object_dict = env_types)

#    print hw_nicks
#    print node_types
#    print node_types['FooBar']['cpu']
    print env_types
