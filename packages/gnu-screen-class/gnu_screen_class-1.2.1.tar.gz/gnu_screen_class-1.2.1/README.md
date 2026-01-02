# gnuscreen
Wrapper around GNU screen

### As Python module
```plaintext
Help on package gnuscreen:

NAME
    gnuscreen

PACKAGE CONTENTS
    main

CLASSES
    builtins.object
        GnuScreen
    
    class GnuScreen(builtins.object)
     |  GnuScreen(id: int, name: str, launched: datetime.datetime, attached: bool) -> None
     |  
     |  GnuScreen(id: int, name: str, launched: datetime.datetime, attached: bool)
     |  
     |  Methods defined here:
     |  
     |  __eq__(self, other)
     |  
     |  __init__(self, id: int, name: str, launched: datetime.datetime, attached: bool) -> None
     |  
     |  __repr__(self)
     |  
     |  close(self)
     |      Close screen
     |  
     |  execute(self, cmds: Iterable[str]) -> None
     |      Execute commands on screen
     |  
     |  ----------------------------------------------------------------------
     |  Static methods defined here:
     |  
     |  get(name: str) -> 'GnuScreen'
     |      Get existing screen or create new one
     |  
     |  list() -> Iterable[ForwardRef('GnuScreen')]
     |      List existing screens
     |  
     |  query(name: str) -> Union[ForwardRef('GnuScreen'), NoneType]
     |      Get existing screen if it exists
     |  
     |  ----------------------------------------------------------------------
     |  Readonly properties defined here:
     |  
     |  exists
     |      Return true if screen with 'name' exists
     |  
     |  ----------------------------------------------------------------------
     |  Data descriptors defined here:
     |  
     |  __dict__
     |      dictionary for instance variables (if defined)
     |  
     |  __weakref__
     |      list of weak references to the object (if defined)
     |  
     |  ----------------------------------------------------------------------
     |  Data and other attributes defined here:
     |  
     |  __annotations__ = {'attached': <class 'bool'>, 'id': <class 'int'>, 'l...
     |  
     |  __dataclass_fields__ = {'attached': Field(name='attached',type=<class ...
     |  
     |  __dataclass_params__ = _DataclassParams(init=True,repr=True,eq=True,or...
     |  
     |  __hash__ = None

DATA
    Iterable = typing.Iterable
    Optional = typing.Optional
    gnuscreen_logger = <Logger gnuscreen (WARNING)>

VERSION
    1.1

FILE
    /git/NMRhub/gnuscreen/src/gnuscreen/__init__.py



```

### Command line interface 
Although intended for primarily as a module, a command line interface is provided
```
usage: gnuscreen [-h] [-l LOGLEVEL]
                 (--list | --start START | --query QUERY | --close CLOSE | --execute EXECUTE [EXECUTE ...] | --version)

optional arguments:
  -h, --help            show this help message and exit
  -l LOGLEVEL, --loglevel LOGLEVEL
                        Python logging level
  --list                List screens
  --start START         Start screen if necesary
  --query QUERY         Test for existing screen
  --close CLOSE         Close screen if it exits
  --execute EXECUTE [EXECUTE ...]
                        Execute commands on screen: screen name, commands
  --version             show version
```
