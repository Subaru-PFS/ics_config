from __future__ import absolute_import, print_function

import logging
import os
import string

import ruamel_yaml


class YamlConfig(object):
    def __init__(self, topLevel, root=None,
                 namespace=None,
                 logger=None, logLevel=logging.INFO):
        """
        Container for a tree of configuration files.

        Args
        ----
        topLevel : string (or None)
           The controlling topLevel's name (e.g. pfs, enu, ccd, mcs)
        root : string
           The configuration tree's root directory. By default, the ics_config 
           products's config/ directory
        namespace : dict
           A dictionary through which yaml string variables
           are evaluated.
        logger : logging.Logger
           By default, the logger named 'config'
        logLevel : int

        By default, configuration entries are indexed by a
        dot-delimited name starting with the controlling topLevel's name

        Internally, we keep a dictionary of nodes keyed by the partial
        dot-delimited names, where the values are (fullpath, content)
        pairs, and content is the yaml-interpreted python structure if
        the name resolves to a YAML file, or None if it resolves to a
        directory.
        """

        if logger is None:
            logger = logging.getLogger('config')
        logger.setLevel(logLevel)
        self.logger = logger

        if root is None:
            import os
            configRoot = os.environ.get('ICS_CONFIG_DIR', None)
            if configRoot is None:
                root = '.'
            else:
                root = os.path.join(configRoot, 'config')

        self.root = root
        self.topLevel = topLevel

        self.namespace = namespace

        self.flush()

    @property
    def _rootPath(self):
        if self.topLevel is None:
            return self.root
        else:
            return os.path.join(self.root, self.topLevel)

    def flush(self):
        """ Cause all our configuration to be reloaded from disk files. """

        self.configs = dict()

    def _yamlPath(self, parts):
        return os.path.join(self._rootPath, *parts)

    def finalNamespace(self, extraNamespace=None):
        if extraNamespace is not None:
            namespace = self.namespace.copy() if self.namespace is not None else dict()
            namespace.update(extraNamespace)
        else:
            namespace = self.namespace

        return namespace
    
    def loadYamlFile(self, yamlPath, extraNamespace=None):
        """ Return a YAML loader which interpolates strings with our namespace. """

        if not os.path.isfile(yamlPath):
            raise ValueError('not a file path: %s' % (yamlPath))

        namespace = self.finalNamespace(extraNamespace)

        with open(yamlPath, 'r') as yamlFile:
            loader = ruamel_yaml.Loader(yamlFile)
            if namespace is not None:
                def interpolateString(loader, node, namespace=namespace):
                    return string.Template(node.value).substitute(namespace)

                loader.add_constructor(u'tag:yaml.org,2002:str', interpolateString)

            cfg = loader.get_data()
            return cfg

    def _loadOne(self, parts, extraNamespace=None):
        """ returns the value for a perhaps partial list of name parts. 

        Args
        ----
        parts : list-like
           elements of a perhaps partial namespace

        Returns:
           content : None if a directory, parsed yaml content otherwise.
        """

        name = '.'.join(parts)
        try:
            return self.configs[name][1]
        except KeyError:
            path = self._yamlPath(parts)
            if os.path.isdir(path):
                self.configs[name] = (path, None)
                return None

            yamlPath = "%s.yaml" % (path)
            cfg = self.loadYamlFile(yamlPath, extraNamespace=extraNamespace)
            self.configs[name] = (yamlPath, cfg)

            return cfg

    def _loadOnDemand(self, path, extraNamespace=None):
        parts = path.split('.')
        for i in range(len(parts)):
            cfg = self._loadOne(parts[0:i+1], extraNamespace=extraNamespace)
            self.logger.debug('loaded %s: %s' % (parts[0:i+1], cfg))
            if cfg is not None:
                return cfg, parts[i+1:]

        raise KeyError('%s is not contained in a configuration file' % path)

    def rawConfig(self, path):
        """ Return the raw YAML file """

        with open(self._yamlPath(path.split('.'))+'.yaml', 'r') as f:
            return '\n'.join(f.readlines())

    def get(self, path, extraNamespace=None, flush=False):
        """ Return the configuration value for the given dotted path. 

        Args
        ----
        path : dot-delimited string
          The name of the configuration variable to load.
        extraNamespace : dict-like
           update self.namespace with this before interpolating.
           If s

        Returns
        -------
        value : object

        Raises
        ------
        KeyError 
        """

        namespace = self.finalNamespace(extraNamespace)
        cfg, cfgParts = self._loadOnDemand(path, extraNamespace=extraNamespace)
        for n_i, name in enumerate(cfgParts):
            finalName = string.Template(name).substitute(namespace)
            try:
                cfg = cfg[finalName]
            except KeyError:
                raise KeyError('%s not found in %s' % (finalName, path))
            
        if extraNamespace is not None:
            self.flush()

        return cfg
