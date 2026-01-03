# leafsdk/utils/redis_helpers.py
# Redis helper functions for LeafSDK

from leafsdk import logger
from leafsdk.utils.logstyle import LogIcons
from petal_app_manager.proxies.redis import RedisProxy
from typing import Optional

def setup_redis_subscriptions(pattern: str, callback: callable, redis_proxy: Optional[RedisProxy] = None):
    """Setup Redis subscriptions - call this after object creation if using Redis"""
    if redis_proxy is None:
        logger.warning(f"{LogIcons.WARNING} Redis proxy not provided, skipping Redis subscriptions")
        return
        
    try:
        # Subscribe to a general broadcast channel
        redis_proxy.register_pattern_channel_callback(channel=pattern, callback=callback)

        logger.info(f"{LogIcons.SUCCESS} Redis subscriptions set up successfully to {pattern}.")
    except Exception as e:
        logger.error(f"{LogIcons.ERROR} Failed to set up Redis subscriptions: {e}")

def unsetup_redis_subscriptions(pattern: str, redis_proxy: Optional[RedisProxy] = None):
    """Unsubscribe from Redis channels - call this when the step is no longer needed"""
    if redis_proxy is None:
        logger.warning(f"{LogIcons.WARNING} Redis proxy not provided, skipping Redis unsubscriptions")
        return
        
    try:
        redis_proxy.unregister_pattern_channel_callback(channel=pattern)
        logger.info(f"{LogIcons.SUCCESS} Redis subscriptions to {pattern} have been removed.")
    except Exception as e:
        logger.error(f"{LogIcons.ERROR} Failed to remove Redis subscriptions: {e}")