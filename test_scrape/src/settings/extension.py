# =============================================================================
# Override Extension
# =============================================================================

EXTENSIONS = {

    # Disable Telnet Console
    "scrapy.extensions.telnet.TelnetConsole": None,

    # Jobdir
    "src.extensions.jobdir.JobdirState": 110,
    "src.extensions.jobdir.JobdirCleaner": 120,

    # Cache
    "src.extensions.cache.CacheExtension":300,
}