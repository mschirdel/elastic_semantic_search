"""Configuration for all log messages under src."""

import inspect
import json
import logging
import logging.config
import logging.handlers
import os
import os.path
import sys
import time
import traceback

import psutil
import yaml
from watchdog import events
from watchdog.observers import Observer

# src modules
from src.utils.constants import PYTHON_LOG_CONFIG


def getLogger(loggerName: str) -> logging.LoggerAdapter:
    """This is a weapper method.

    This is a wrapper around logging.getLogger(loggerName) that returns a
    _LoggerAdapter_.  The adapter allows you to do this:

        logger = src.integration.log_util.getLogger("foo.bar.baz")
        logger.debug("Your number is {}.", 3.14)

    As opposed to the usual:

        logger = logging.getLogger("foo.bar.baz")
        logger.debug("Your number is {}.".format(3.14))

    You might not perceive much of a difference, but there is: without the
    adapter, you're paying at runtime for the string formatting regardless of
    the log level threshold.

    Warning: The adapter does *not* affect the root logger!  (Not yet,
    anyway.)  So:

        logging.debug("Your number is {}.".format(3.14))

    Will not work.  Declare your own logger by calling getLogger instead.
    """

    # This idea was adapted from the Python logging cookbook:
    # https://docs.python.org/3/howto/logging-cookbook.html#format-styles
    class Message:
        def __init__(self, fmt, args):
            # Always a danger with str.format().
            if fmt is not None:
                fmt = str(fmt).replace('{', '{{')
                fmt = str(fmt).replace('}', '}}')
            else:
                fmt = ""
            self.fmt = fmt
            self.args = args

        def __str__(self):
            return self.fmt.format(*self.args)

    class StyleAdapter(logging.LoggerAdapter):
        def __init__(self, logger, extra=None):
            super(StyleAdapter, self).__init__(logger, extra or {})

        def log(self, level, msg, *args, **kwargs):
            if self.isEnabledFor(level):
                msg, kwargs = self.process(msg, kwargs)
                self.logger._log(level, Message(msg, args), (), **kwargs)

    return StyleAdapter(logging.getLogger(loggerName))


def current_function_name(frameIndex: int = 1) -> str:
    """A small utility that returns the name of our caller.

    This can be useful for exception logging.

    Arguments:

      frameIndex: The index of the stack frame on the call stack whose caller
                  name should be returned.

                  * 0 is _this function_ (i.e., it will return
                    'log_util.current_function_name'.)

                  * 1 is _your function_ (i.e., it will return the name of the
                    function that called current_function_name().)  This is the
                    default.

                  * 2 is _your caller_ (i.e., it will return the name of the
                    function that invoked the caller of
                    current_function_name().)

                  * And so on.
    """
    if frameIndex < 0:
        frameIndex = 0
    callStack = inspect.stack()

    className = ""
    if len(callStack) == 1 and frameIndex > 0:
        # The only time a function can be said _not_ to have a caller is when
        # we're being called from the module level, such as __main__.  In that
        # case, our "method name" is just the module name.
        #
        # I mean, what else can we do?
        return "__main__"
    elif frameIndex >= len(callStack):
        # You drilled too far up the callstack.
        #
        # This should not cause an error since we call current_function_name()
        # while we're already handling unrelated errors.
        frameIndex = len(callStack) - 1

    methodName = callStack[frameIndex].function

    # Figure out the class that the function belonged to, if there was one.
    #
    # Note: This won't work for @staticmethod static functions that do not
    # define 'self', nor does it handle nested functions correctly.  (Nested
    # function could be added pretty easily, though extracting the class from
    # static methods will take more work.)
    if "self" in callStack[frameIndex].frame.f_locals:
        # Handles instance methods.
        className = callStack[frameIndex].frame.f_locals["self"].__class__.__name__
        className += "."
        methodName = callStack[frameIndex].frame.f_code.co_name
    elif "cls" in callStack[frameIndex].frame.f_locals:
        # Handles @classmethods.
        className = callStack[frameIndex].frame.f_locals["cls"].__name__
        className += "."
        methodName = callStack[frameIndex].frame.f_code.co_name

    return f"{className}{methodName}"


def log_exception(e: BaseException = None, loggerName: str = None):
    """
    Here's a common scenario: an exception has just been thrown and you want
    to log it.  We do this all over the place, and found ourselves repeating
    the same code for it time and time again, so we decided to hoist that
    here.

    Arguments:
      e:          The exception that was thrown.  We'll get it form the
                  callstack if it was not supplied.

      loggerName: The name of the logger to log the exception in.  If not
                  supplied, we assume that the caller is using its module
                  __name__ as the logger name and we grab that from the
                  callstack.
    """
    logger = None

    if loggerName:
        logger = getLogger(loggerName)
    else:
        # Again, frame #1 in the callstack is the function that called us.
        callStack = inspect.stack()
        frameIndex = 1
        if len(callStack) == 1:
            # We were most likely called from __main__, or perhaps called
            # interactively.  I can't think of other reasons why there
            # wouldn't be a calling function.
            logger = getLogger("__main__")
        elif len(callStack) > frameIndex and "__name__" in callStack[frameIndex].frame.f_globals:
            moduleName = callStack[frameIndex].frame.f_globals["__name__"]
            logger = getLogger(moduleName)
        else:
            # The caller apparently had no module.  Fall back to a reasonable
            # default (it's just a logger, after all), but this shouldn't
            # happen.
            logger = logging.root

    e = e if e is not None else sys.exc_info()[1]
    caller = current_function_name(2)
    logger.exception(f'{caller}{"()" if caller != "__main__" else ""} raised {e.__class__.__name__}: {e}')


def profiler(*args, **kwargs):
    '''
    this method profiles the time and memory of functions operation as per
    Time : cpu clock time
    RSS  : resident set size
    VMS  : virtual memory size

    Parameters
    -----------------
    log_file_path :str = filepath to store the profile info

    Example:
    @profiler(log_file_path='path/to/log')
    def test_func():
        pass
    '''
    # pop the data is needed here
    log_file_path = kwargs.pop('log_file_path', None)
    if log_file_path is not None and log_file_path != '':
        write_log_to_file = True
    else:
        write_log_to_file = False

    def inner(func):
        def elapsed_since(start):
            '''get lapsed cpu time'''
            # return time.strftime("%H:%M:%S", time.gmtime(time.time() - start))
            elapsed = time.time() - start
            if elapsed < 1:
                return str(round(elapsed * 1000, 2)) + "ms"
            if elapsed < 60:
                return str(round(elapsed, 2)) + "s"
            if elapsed < 3600:
                return str(round(elapsed / 60, 2)) + "min"
            else:
                return str(round(elapsed / 3600, 2)) + "hrs"

        def get_process_memory():
            '''get process memory'''
            process = psutil.Process(os.getpid())
            mi = process.memory_info()
            return mi.rss, mi.vms

        def format_bytes(bytes):
            '''convert the bytes to kB,MB or GB'''
            if abs(bytes) < 1000:
                return str(bytes) + "B"
            elif abs(bytes) < 1e6:
                return str(round(bytes / 1e3, 2)) + "kB"
            elif abs(bytes) < 1e9:
                return str(round(bytes / 1e6, 2)) + "MB"
            else:
                return str(round(bytes / 1e9, 2)) + "GB"

        def wrapper(*args, **kwargs):

            # Measure before
            rss_before, vms_before = get_process_memory()
            start = time.time()

            # Run method
            retval = func(*args, **kwargs)

            # Measure after
            elapsed_time = elapsed_since(start)
            rss_after, vms_after = get_process_memory()
            rss_mem = format_bytes(rss_after - rss_before)
            vms_mem = format_bytes(vms_after - vms_before)

            # Report
            logger = logging.getLogger('Profiler')
            if write_log_to_file:
                # Add a FileHandler to the logger if write_log_to_file is
                # True.  (True, the same could be accomplished by having the
                # programmer edit logging.yaml instead, but the Principle of
                # Least Surprise applies here: this is the way the DS code
                # used to work.)
                handler = logging.FileHandler(log_file_path)
                formatter = logging.Formatter(
                    '%(levelname)-8s | %(asctime)s | PID=%(process)d | \
                        %(filename)s:%(lineno)s [%(name)s]: %(message)s'
                )
                handler.setFormatter(formatter)
                logger.addHandler(handler)

            logger.debug(f'Time & Memory Profiling Report for {func.__name__}().')
            logger.debug(f'Time : {elapsed_time}')
            logger.debug(f'RSS  : {rss_mem} VMS : {vms_mem}')

            if write_log_to_file:
                try:
                    logger.debug(f'Time & Memory Profiling Report for {func.__name__}().')
                    logger.debug(f'Time : {elapsed_time}')
                    logger.debug(f'RSS  : {rss_mem} VMS : {vms_mem}')
                except Exception:
                    logger.debug('Warning: no process log file was identified.')
            return retval

        return wrapper

    return inner


class LogConfigFileWatcher(events.PatternMatchingEventHandler):
    '''
    Watches for changes in our DS logging configuration YAML, and re-reads the
    config as necessary when there are changes.
    '''

    # These variables are actually constructor arguments for
    # watchdog.events.events.PatternMatchingEventHandler.
    #
    # - patterns:           The file path(s) to observe within the monitored
    #                       directories.  A change in any file matching one of
    #                       these patterns will trigger the appropriate
    #                       on_modified or on_created event.
    # - ignore_directories: Set to True because we're only watching for
    #                       changes to particular files, not directories.
    patterns = ["*/" + os.path.basename(PYTHON_LOG_CONFIG)]
    ignore_directories = True

    @classmethod
    def _readLogitConfig(cls, logit_cfg_file_path, dictConfig):
        '''
        This helper function for reloadConfigFiles() reads the relevant portions
        of the given logitcfg.json file and translates these onto the Python
        logging convention.
        '''
        with open(logit_cfg_file_path) as f:
            logit_cfg_dict = json.loads(f.read())

            # This determines the minimum threshold for logging messages.  If
            # it's "DEBUG", we log everything.
            if "level" in logit_cfg_dict:

                # logit [server, golang]: DEBUG, DBGX | WARN | INFO | ERR
                # logging [ds, python]:   DEBUG       | WARN | INFO | ERROR
                serverLevel = logit_cfg_dict["level"]
                level = ""
                if serverLevel == "DBGX":
                    level = "DEBUG"
                elif serverLevel == "DEBUG" or serverLevel == "WARN" or serverLevel == "INFO":
                    level = serverLevel
                elif serverLevel == "ERR":
                    level = "ERROR"
                else:
                    # Unrecognized server level; shouldn't happen.
                    level = "DEBUG"

                if "root" not in dictConfig:
                    dictConfig["root"] = {}
                dictConfig["root"]["level"] = level

            # Enable named loggers.
            if "debugFlags" in logit_cfg_dict:
                for obj in logit_cfg_dict["debugFlags"]:

                    loggerName = obj["pkg"]
                    if loggerName != "main":

                        if "loggers" not in dictConfig:
                            dictConfig["loggers"] = {}
                        if loggerName not in dictConfig["loggers"]:

                            dictConfig["loggers"][loggerName] = {"level": level}
                        else:
                            pass

    @classmethod
    def _reloadConfigFiles(cls):
        '''
        Once we need to reload _a_ config file, we reload _both_ config files, the
        Python one first.

        This is a helper function for both _process() and initiateObserver().
        Both of them need to reload configurations -- one conditionally, and
        one unconditionally -- but the process is identical either way.
        '''

        dictConfig = {}
        if os.path.exists(cls.pythonConfigPath):
            try:
                with open(cls.pythonConfigPath, "r") as f:
                    dictConfig = yaml.load(f, Loader=yaml.Loader)
                    oldDir = os.getcwd()
                    os.chdir(os.path.dirname(__file__))
                    logging.config.dictConfig(dictConfig)
                    os.chdir(oldDir)
            except Exception as e:
                # Perhaps the yaml file is unreadable?  Perhaps it's
                # broken?
                #
                # We could log this:
                print(traceback.format_exc())

                logging.error(
                    "Could not reload config file {}: \
                                {}".format(
                        cls.pythonConfigPath, e
                    )
                )

    def _process(self, event):
        '''
        Deals with Watchdog events by reloading configurations as needed.

        This is a helper function for all of this class's event listeners.

        Parameters:
        - event: The watchdog event that we are processing.
          * event.src_path: The full path to the file that triggered the event
          * event.event_type: A watchdog.event with more information on the
                              nature of the event.  We care about
                              events.FileModifiedEvent and events.FileCreatedEvent.
        '''

        reconfigure = None
        if isinstance(event, events.FileModifiedEvent):
            reconfigure = "{} modified".format(event.src_path)
        elif isinstance(event, events.FileCreatedEvent):
            reconfigure = "{} created".format(event.src_path)

        if reconfigure is not None:
            self.__class__._reloadConfigFiles()
            logging.info("{}.  Reloading log configuration.".format(reconfigure))

    def on_modified(self, event):
        '''When a file or directory is created, this gets called.

        Parameters:
        - event: A events.FileModifiedEvent or DirectoryModifiedEvent.
        '''
        self._process(event)

    def on_created(self, event):
        '''When a file or directory is created, this gets called.

        Parameters:
        - event: A events.FileCreatedEvent or DirectoryCreatedEvent.
        '''
        self._process(event)

    @classmethod
    def initiateObserver(cls):
        '''
        Starts or restarts the sole observation thread for this class.  It will be
        responsible for listening to the configuration directory for changes.
        '''
        try:
            cls.logger = getLogger(cls.__name__)
            if not hasattr(cls, "observer"):
                # Create the one file observation thread.
                cls.currentDirectory = os.path.dirname(__file__)
                cls.pythonConfigPath = PYTHON_LOG_CONFIG
                cls.observer = Observer()

                # Watch for logging.yaml.
                if os.path.exists(PYTHON_LOG_CONFIG):
                    cls.observer.schedule(LogConfigFileWatcher(), path=os.path.dirname(PYTHON_LOG_CONFIG))
                else:
                    # Also not an error, but we'll at least warn the user this
                    # time.
                    print(
                        f"WARNING: Could not open {PYTHON_LOG_CONFIG} for reading. \
                             Logging will use default thresholds."
                    )

            if not cls.observer.is_alive():
                # Start or restart the observation thread.
                # print('Starting observer,
                # listening to changes in {}'.format(configDirectory))
                cls.observer.start()

                # Perform the initial read.
                cls._reloadConfigFiles()
                cls.logger.info("Loading log configuration.")

        except Exception as e:
            cls.logger.error("ERROR occurred while initializing observer thread: {}".format(e))
            if hasattr(cls, "observer") and cls.observer.is_alive():
                cls.observer.stop()

    @classmethod
    def stopObserver(cls):
        try:
            if hasattr(cls, "observer") and cls.observer.is_alive():
                cls.observer.stop()
        except Exception as e:
            cls.logger.error("ERROR occurred while stopping observer thread: {}".format(e))


# Start the watcher.  Does nothing if the watcher is already started.
LogConfigFileWatcher.initiateObserver()
