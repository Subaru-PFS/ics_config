from __future__ import absolute_import, print_function

import logging
import os
import string

import ruamel_yaml


class YamlConfig(object):
    def __init__(self, actor, root=None, logger=None, logLevel=logging.INFO):
        """
        Container for a tree of configuration files.

        Args
        ----
        actor : string (or None)
           The controlling actor's name (e.g. enu, ccd, mcs)
        root : string
           The configuration tree's root directory. By default, the ics_config products's config/ directory
        logger : logging.Logger
           By default, the logger named 'config'
        logLevel : int

        By default, configuration entries are indexed by a
        dot-delimited name starting with the controlling actor's name

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
        self.actor = actor

        self.flush()

    @property
    def _rootPath(self):
        if self.actor is None:
            return self.root
        else:
            return os.path.join(self.root, self.actor)

    def flush(self):
        """ Cause all our configuration to be reloaded from disk files. """

        self.configs = dict()

    def _loadOne(self, parts):
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
            path = os.path.join(self._rootPath, *parts)
            if os.path.isdir(path):
                self.configs[name] = (path, None)
                return None
            yamlPath = "%s.yaml" % (path)
            if os.path.isfile(yamlPath):
                with open(yamlPath, 'r') as yamlFile:
                    cfg = ruamel_yaml.load(yamlFile)
                    self.configs[name] = (yamlPath, cfg)
                    return cfg

            raise KeyError('do not know what %s is' % (name))

    def _loadOnDemand(self, path):
        parts = path.split('.')
        for i in range(len(parts)):
            cfg = self._loadOne(parts[0:i+1])
            self.logger.debug('loaded %s: %s' % (parts[0:i+1], cfg))
            if cfg is not None:
                return cfg, parts[i+1:]

        raise KeyError('%s is not contained in a configuration file' % path)

    def get(self, path, interpEnv=None):
        """ Return the configuration value for the given dotted path. 

        Args
        ----
        path : dot-delimited string
          The name of the configuration variable to load.
        interpEnv : dict-like
          If passed in, string values are treated as string.Templates,
          evaluated using this dictionary.

        Returns
        -------
        value : object

        Raises
        ------
        KeyError 
        """

        if interpEnv is not None:
            path = string.Template(path).substitute(interpEnv)

        cfg, cfgParts = self._loadOnDemand(path)
        for name in cfgParts:
            cfg = cfg[name]

        if not isinstance(cfg, (str, unicode)) or interpEnv is None:
            return cfg

        return string.Template(cfg).substitute(interpEnv)
