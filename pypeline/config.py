import sys
import configargparse

TRUE_STRINGS = ('true', 't', 'yes', 'y', '1')


def str_to_bool(v):
    """ Convert a string to boolean value.

    Returns True if the string is in TRUE_STRINGS
    and False otherwise.  The comparison is done after
    converting the string to lowercase.

    Notes
    -----
    I don't know what happens if the string is unicode.

    Parameters
    ----------
    v : str
        string to convert to boolean value

    Returns
    -------
    bool : boolean representation
    """
    return v.lower() in TRUE_STRINGS


class Defaults(object):
    """ Manages the default values for class parameters.

    Should be initialized with Param objects.

    """
    def __init__(self, *args, **kwargs):
        self._names = []
        for p in args:
            self._add_param(p)
        try:
            self.__name__ = kwargs['name']
        except KeyError:
            pass

    def __getitem__(self, key):
        return self.__dict__[key].default

    def __setitem__(self, key, value):
        self.__dict__[key].default = default

    def __iter__(self):
        for key in self._names:
            yield self.__dict__[key]

    def items(self):
        for key in self._names:
            yield key, self.__dict__[key].default

    def _add_param(self, p):
        """ """
        self._names.insert(0, p.name)
        self.__dict__[p.name] = p

    def add_param(self, *args, **kwargs):
        self._add_param(Param(*args, **kwargs))


class Param(object):
    """ Define a configuration parameter.

    Parameters
    ----------
    name : str
        parameter name

    Additional parameters
    ---------------------
    Additional key-value pairs will be passed along to argparse.
    It should include these argparse parameters as required

    default : default value
    help : message for command line help
    action : argparse action string
    type : type
    metavar : str
    nargs :

    """
    def __init__(self, name, **args):
        self.name = name
        for key, value in args.items():
            self.__dict__[key] = value


class _ConfigParser(object):
    """ Manage the argument parser.

    Configuration parameters are collected from the classes specified in the
    argument.  ConfigArgParse will be initialized to read inputs from the
    command line or config file.

    After initialization parameters may be accessed by item or by attribute.

    >>> config = _ConfigParser([class_a, class_b])
    >>> p = config['param1']
    >>> q = config.param2

    The configuration protocol looks for the following class attributes or
    methods

    _default_params : instance of Defaults class containing configuration 
                    parameters.
    _dependencies : list of other classes that should be collected
                    for configuration parameters.
    check_config : method to validate the configuration parameters
                    (defined with @staticmethod).


    Parameters
    ----------
    objects : list of class objects
        List of class objects to collect config parameters.
    description : str
        Text to print at the top of the command line help message.
    """
    argparse_keys = ('default', 'type', 'action', 'help', 'metavar', 'nargs', 'choices')

    def __init__(self,
                    objects=(),
                    description="""Run the Pypelid bypass simulation of 
                    Euclid observations."""):
        """ Parse arguments """
        parser = configargparse.ArgumentParser(
            description=description,
            args_for_setting_config_path = ['-c','--conf'],
            formatter_class=configargparse.ArgumentDefaultsHelpFormatter)

        parser.register('type', 'bool', str_to_bool)

        parser.add_argument("-w", metavar='filename', nargs='?', const=sys.stdout, type=configargparse.FileType('w'),
            help="write out config file and exit",is_write_out_config_file_arg=True)
        # self.parser.add_argument('--version', action='version', version='%s'%str(misc.GitEnv()), help="show git hash and exit")


        param_list = []

        objs = []
        for o in objects:
            try:
                for dep in o._dependencies:
                    objects.append(dep)
            except AttributeError:
                pass
            if o not in objs:
                objs.append(o)

        for o in objs:
            if isinstance(o, Defaults):
                default_params = o
            else:
                try:
                    default_params = o._default_params
                except:
                    continue

            arg_group = parser.add_argument_group(o.__name__)

            for p in default_params:
                if p.name in param_list:
                    continue

                try:
                    if p.hidden:
                        continue
                except AttributeError:
                    pass

                param_list.append(p.name)
                a = {}
                for k in self.argparse_keys:
                    try:
                        a[k] = p.__dict__[k]
                    except KeyError:
                        pass
                args = ["--%s"%p.name]
                try:
                    args.append("-%s"%p.__dict__['alias'])
                except:
                    pass
                arg_group.add_argument(*args, **a)

        self.__dict__['_parser'] = parser
        self.__dict__['_args'] = parser.parse_args()

        # Run validation in each class
        for o in objs:
            try:
                o.check_config(self._args.__dict__)
            except AttributeError:
                pass

    def __getitem__(self, key):
        """ Access arguments by name like a dictionary. """
        return self._args.__dict__[key]

    def __setitem__(self, key, value):
        """ """
        self._args.__dict__[key] = value

    def __getattr__(self, key):
        """ Access arguments by name as asttributes. """
        return getattr(self._args, key)

    def __setattr__(self, key, value):
        """ """
        if key in self.__dict__['_args']:
            setattr(self._args, key, value)
            return
        self.__dict__[key] = value

    def dump(self, file=sys.stdout):
        """ """
        self._parser.write_config(file)

    def __str__(self):
        """ Return string representation of the Config object. """
        return 'Config: \n\t'+'\n\t'.join([key + ' = ' + str(self[key]) for key in self._args.__dict__])

# fake a singleton class
_config = None
def Config(*args, **kwargs):
    global _config
    if _config is None:
        _config = _ConfigParser(*args, **kwargs)
    return _config