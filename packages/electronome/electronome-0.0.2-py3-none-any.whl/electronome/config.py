from configparser import ConfigParser
import argparse
from pathlib import Path
from typing import Set, Dict

class MyAction(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None): # type: ignore
        setattr(namespace, self.dest, values)
        setattr(namespace, self.dest+'_nondefault', True)

class Config:

    def __init__(self):

        self._attrs : Dict[str,str|bool]  = {}
        self._transient : Set[str] = set()


        parser = argparse.ArgumentParser(
            prog='electronome',
            description='Simple but configurable metronome',
        )
        parser.add_argument('-t', '--tempo', default="60",
                            help='Tempo in beats per minute', 
                            action=MyAction)
        parser.add_argument('-b', '--beats', default="4",
                            help='Beats per bar', 
                            action=MyAction)
        parser.add_argument('-e', '--emphasize', default="1", 
                            help='Beats to emphasize, eg 1 or 1,3', 
                            action=MyAction)
        parser.add_argument('-s', '--size', default="200x120", 
                            help='Window size', 
                            action=MyAction)
        parser.add_argument('-H', '--half', 
                            help='Half notes (1 + 2 + ... vs 1 2 ...)', 
                            action='store_true')
        parser.add_argument('--no-half', 
                            help='Turn of --half (override ini file)', 
                            action='store_true')
        parser.add_argument('--low', default="_builtin_",
                            help='WAV file for low (unemphasized) beats', 
                            action=MyAction)
        parser.add_argument('--high', default="_builtin_",
                            help='WAV file for high (emphasized) beats', 
                            action=MyAction)
        args = parser.parse_args()

        home = Path.home()
        conf_file = home / ".electronome.ini"
        ini_options = []
        configparser = ConfigParser()
        if (conf_file.exists()):
            try:
                configparser.read(conf_file)
                ini_options = configparser.options('electronome')
            except:
                print("Warning: invalid config file", conf_file)
        
        for opt in ini_options:
            if (opt == "half"):
                self._attrs[opt] = configparser.getboolean('electronome', opt)
            else:
                self._attrs[opt] = configparser.get('electronome', opt)

        if ("tempo" in ini_options):
            if hasattr(args, 'tempo_nondefault'):
                self._attrs["tempo"] = args.tempo
        else:
            self._attrs["tempo"] = args.tempo

        if ("beats" in ini_options):
            if hasattr(args, 'beats_nondefault'):
                self._attrs["beats"] = args.beats
        else:
            self._attrs["beats"] = args.beats

        if ("size" in ini_options):
            if hasattr(args, 'size_nondefault'):
                self._attrs["size"] = args.size
        else:
            self._attrs["size"] = args.size

        if ("half" in ini_options):
            if args.half:
                self._attrs["half"] = True
            elif args.no_half:
                self._attrs["half"] = False
        else:
            if (args.half):
                self._attrs["half"] = True
            elif args.no_half:
                self._attrs["half"] = False
            else:
                self._attrs["half"] = False

        if ("emphasize" in ini_options):
            if hasattr(args, 'emphasize_nondefault'):
                self._attrs["emphasize"] = args.emphasize
        else:
            self._attrs["emphasize"] = args.emphasize

        if ("high" in ini_options):
            if hasattr(args, 'high_nondefault'):
                self._attrs["high"] = args.high
        else:
            self._attrs["high"] = args.high
            if hasattr(args, 'high_nondefault'):
                self._transient.add("high")

        if ("low" in ini_options):
            if hasattr(args, 'low_nondefault'):
                self._attrs["low"] = args.low
        else:
            self._attrs["low"] = args.low
            if hasattr(args, 'low_nondefault'):
                print("Low is transient")
                self._transient.add("low")

        self._save()

    def _save(self):
        configparser = ConfigParser()
        home = Path.home()
        conf_file = home / ".electronome.ini"
        cfgfile = open(conf_file, 'w')

        configparser.add_section('electronome')
        for attr in self._attrs:
            if (attr not in self._transient):
                configparser.set('electronome', attr, str(self._attrs[attr]))
        configparser.write(cfgfile)
        cfgfile.close()

    def get(self, attr : str) -> str|None:
        if (attr not in self._attrs): 
            return None
        return str(self._attrs[attr])

    def get_boolean(self, attr : str) -> bool:
        if (attr not in self._attrs): 
            return False
        val = self._attrs[attr]
        if (type(val) == bool):
            return val
        return val.lower() in ["t", "true", "1", "y", "yes", "on"]

    def set(self, attr: str, val: str):
        self._attrs[attr] = val
        self._save()

