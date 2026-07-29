# =============================================================================
# Override Extension
# =============================================================================

EXTENSIONS = {

    # Disable Telnet Console
    "scrapy.extensions.telnet.TelnetConsole": None,

    # Cleaning Jobdir
    "src.extensions.clean_jobdir.JobdirCleaner": 500,
}