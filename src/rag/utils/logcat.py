import datetime
from .config import DebugLevel, getConfig

CONFIG = getConfig()


class bcolors:
    DEBUG = "\033[92m"
    WARNING = "\033[93m"
    VERBOSE = "\033[94m"
    FAIL = "\033[91m"
    ENDC = "\033[0m"
    BOLD = "\033[1m"

class Log:
    @staticmethod
    def _make_text(type, TAG, *argv) -> str:
        out: str = f"{type} {str(datetime.datetime.now())} {TAG}: "
        for a in argv:
            out += str(a)
        return out

    @staticmethod
    def _print(m):
        print(m + bcolors.ENDC)

    @staticmethod
    def d(TAG, *argv):
        """Debug log, only printed when debug level is DEBUG or higher"""
        if CONFIG.debugLevel >= DebugLevel.DEBUG:
            Log._print(bcolors.DEBUG + Log._make_text("[D]", TAG, *argv))

    @staticmethod
    def i(TAG, *argv):
        """Info log, always printed"""
        Log._print(Log._make_text("[I]", TAG, *argv))

    @staticmethod
    def w(TAG, *argv):
        """Warning log, only printed when debug level is DEBUG or higher"""
        if CONFIG.debugLevel >= DebugLevel.DEBUG:
            Log._print(bcolors.WARNING + Log._make_text("[W]", TAG, *argv))

    @staticmethod
    def e(TAG, *argv):
        """Error log, only printed when debug level is DEBUG or higher"""
        if CONFIG.debugLevel >= DebugLevel.DEBUG:
            Log._print(bcolors.FAIL + Log._make_text("[E]", TAG, *argv))

    @staticmethod
    def v(TAG, *argv):
        """Verbose log, only printed when debug level is VERBOSE"""
        if CONFIG.debugLevel >= DebugLevel.VERBOSE:
            Log._print(bcolors.VERBOSE + Log._make_text("[V]", TAG, *argv))
