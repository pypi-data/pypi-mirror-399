from _typeshed import Incomplete
from enum import StrEnum
from gllm_core.schema import Component
from gllm_datastore.cache.hybrid_cache.hybrid_cache import BaseHybridCache as BaseHybridCache
from typing import Any

class CacheOperationType(StrEnum):
    """The type of operation for the cache manager.

    Attribute:
        RETRIEVE (str): The operation type for retrieving the cache.
        STORE (str): The operation type for storing the cache.
    """
    RETRIEVE = 'retrieve'
    STORE = 'store'

class CacheManager(Component):
    """A class for managing cache in Gen AI applications.

    This class provides functionality for storing and retrieving cache.

    Attributes:
        data_store (BaseHybridCache): The cache store to use for storing and retrieving the cache.
    """
    data_store: Incomplete
    def __init__(self, data_store: BaseHybridCache) -> None:
        """Initializes a new instance of the CacheManager class.

        Args:
            data_store (BaseCacheDataStore): The data store to use for the cache manager.
        """
    async def retrieve(self, key: str | dict[str, Any] | tuple[Any, ...]) -> tuple[Any, bool]:
        """Retrieves the cache of a given key.

        This method stringifies the key and then calls the `retrieve` method of the data store to retrieve the cache.
        It returns the retrieved cache and a boolean indicating if the cache was found.

        Args:
            key (str | dict[str, Any] | tuple[Any, ...]): The key of the cache to retrieve.

        Returns:
            tuple[Any, bool]: The retrieved cache and a boolean indicating if the cache was found.
        """
    async def store(self, key: str | dict[str, Any] | tuple[Any, ...], value: Any, ttl: int | str | None = None) -> None:
        '''Stores the cache of a given key.

        This method stringifies the key and then calls the `store` method of the data store to store the cache.
        If the value is None, the method will skip the storage process.

        Args:
            key (str | dict[str, Any] | tuple[Any, ...]): The key of the cache to store.
            value (Any): The value of the cache to store.
            ttl (int | str | None, optional): The time-to-live (TTL) for the cache data.
                Must be an integer in seconds or a string in a valid time format (e.g. "1h", "1d", "1w", "1m", "1y").
                If None, the cache data will not expire.

        Returns:
            None
        '''
