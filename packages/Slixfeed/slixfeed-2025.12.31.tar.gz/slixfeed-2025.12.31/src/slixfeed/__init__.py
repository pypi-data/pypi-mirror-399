from slixfeed.utility.logger import UtilityLogger
from slixfeed.version import __version__

logger = UtilityLogger(__name__)
# Useful with test versions.
logger.set_level("info")
logger.info(f"Slixfeed		{__version__}")
