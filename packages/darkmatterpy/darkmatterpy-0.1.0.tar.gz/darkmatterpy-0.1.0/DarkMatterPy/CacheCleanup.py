#     Copyright 2025, QutaYba, nasr2python@gmail.com find license text at end of file


""" Cleanup of caches for OxNJAC.

This is triggered by "--clean-cache=" usage, and can cleanup all kinds of
caches and is supposed to run before or instead of OxNJAC compilation.
"""

import os

from darkmatterpy.BytecodeCaching import getBytecodeCacheDir
from darkmatterpy.Tracing import cache_logger
from darkmatterpy.utils.AppDirs import getCacheDir
from darkmatterpy.utils.FileOperations import removeDirectory


def _cleanCacheDirectory(cache_name, cache_dir):
    from darkmatterpy.Options import shallCleanCache

    if shallCleanCache(cache_name) and os.path.exists(cache_dir):
        cache_logger.info(
            "Cleaning cache '%s' directory '%s'." % (cache_name, cache_dir)
        )
        removeDirectory(
            cache_dir,
            logger=cache_logger,
            ignore_errors=False,
            extra_recommendation=None,
        )
        cache_logger.info("Done.")


def cleanCaches():
    _cleanCacheDirectory("ccache", getCacheDir("ccache"))
    _cleanCacheDirectory("clcache", getCacheDir("clcache"))
    _cleanCacheDirectory("bytecode", getBytecodeCacheDir())
    _cleanCacheDirectory("dll-dependencies", getCacheDir("library_dependencies"))



