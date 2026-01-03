import pprint
import time
import uuid
import pickle
import traceback
from collections.abc import Callable

from swc_utils.exceptions.package_exceptions import MissingDependencyError

try:
    from redis import Redis
except ImportError:
    raise MissingDependencyError("redis")

try:
    from flask import Flask
except ImportError:
    raise MissingDependencyError("flask")

from threading import Thread
from swc_utils.caching import CachingService


class SessionEventManager:
    """
    A class that manages events between different services using Redis as a message broker.
    It can be used to send queries to other services and receive responses.
    The class can also act as a listener for incoming queries and execute callbacks based on the query channel,
    similar to an event listener.
    """
    __MESSAGE_ID_BASE = str(uuid.uuid4()).split("-")[0]
    __MESSAGE_ID = 0

    def __init__(self, app: Flask, redis: Redis, redis_cache: CachingService, data_lifetime=10, host=False):
        """
        :param app: Flask application
        :param redis: Redis connection
        :param redis_cache: CachingService instance
        :param data_lifetime: Lifetime of the cached data in seconds
        :param host: If True, the event manager will start listening for incoming queries
        """
        self.app = app
        self.redis = redis
        self.cache = redis_cache.get_cache("redis-event-manager", dict)
        self.__events = {}
        self.__data_lifetime = data_lifetime

        if host:
            self._start()

    def _start(self):
        try:
            import gevent
            from gevent import monkey

            monkey.patch_all()
            gevent.spawn(self.__thread, self.app)

        except ImportError:
            self.app.logger.warn("REDIS EM Gevent not found, using threading instead. This is not recommended!")
            Thread(target=self.__thread, args=(self.app,), daemon=True).start()

    # Event handling ----------------------------------------------------------

    def on_callback(self, channel: str, callback: Callable, *e_args, **e_kwargs):
        """
        Adds a callback to the event manager
        :param channel: Message channel
        :param callback: Callback function
        :param e_args: Additional arguments for the callback
        :param e_kwargs: Additional keyword arguments for the callback
        :return:
        """
        if channel in self.__events:
            raise Exception(f"Event {channel} already exists")

        self.__events[channel] = lambda *args, **kwargs: callback(*args, *e_args, **kwargs, **e_kwargs)

    def on(self, channel: str) -> Callable:
        """
        Decorator for adding a callback to the event manager.
        Operates like the on_callback method, but allows for a more concise syntax.
        :param channel: Message channel
        :return: Decorator
        """
        def decorator(func, *args, **kwargs):
            self.on_callback(channel, func, *args, **kwargs)

        return decorator

    def off(self, channel):
        """
        Removes a callback from the event manager
        :param channel: Message channel
        :return:
        """
        self.__events.pop(channel)

    def __call_callback(self, channel: str, *args: object, **kwargs: object) -> object:
        if channel not in self.__events:
            return None

        return self.__events[channel](*args, **kwargs)

    def __thread(self, app: Flask):
        while True:
            queries = [f"events:query:{channel}" for channel in self.__events.keys()]
            if len(queries) == 0:
                app.logger.info(f"REDIS [HOST] has no events - waiting for registrations...")
                time.sleep(1)
                continue

            query_key, request_data = self.redis.blpop(queries)

            query = pickle.loads(request_data)

            query_id = query.get("id")
            query_channel = query.get("channel")
            response_key = query.get("response_key")
            args = query.get("args") or []
            kwargs = query.get("kwargs") or {}

            res = None
            err = None
            try:
                with app.app_context():
                    response = app.ensure_sync(self.__call_callback)(query_channel, *args, **kwargs)

                res = pickle.dumps(response)

            except Exception as e:
                err = {
                    "message": str(e),
                    "traceback": traceback.format_exc(),
                    "args": args,
                    "kwargs": kwargs
                }

            finally:
                response_pprint = pprint.pformat(response, width=500, depth=1, compact=True).replace("\n", "")
                app.logger.info(f"REDIS [{query_channel} #{query_id}] {args} {kwargs} -> {err or response_pprint}")
                self.redis.rpush(response_key, pickle.dumps({"id": query_id, "res": res, "err": err}))
                self.redis.expire(response_key, 15)

    # Event sending -----------------------------------------------------------

    @staticmethod
    def __parse_response(response: bytes | object) -> object:
        if type(response) is bytes:
            return pickle.loads(response)
        return response

    @staticmethod
    def __new_message_id() -> str:
        SessionEventManager.__MESSAGE_ID += 1
        return SessionEventManager.__MESSAGE_ID_BASE + str(SessionEventManager.__MESSAGE_ID)

    def query(self, channel: str, *args: object, timeout: int = 5,
              fail_on_timeout: bool = True, **kwargs: object) -> object:
        """
        Sends a query to the event manager and waits for a response.
        :param channel: Message channel
        :param args: Query data arguments
        :param timeout: Timeout in seconds
        :param fail_on_timeout: If True, raises a TimeoutError on timeout instead of returning None
        :param kwargs: Query data keyword arguments
        :return: Response data or None
        """
        cache_key = f"{channel}:{args}:{kwargs}"
        self.cache.clear_expired(self.__data_lifetime)
        if cache_hit := self.cache.get(cache_key):
            return self.__parse_response(cache_hit)

        query_id = SessionEventManager.__new_message_id()
        query_key = f"events:query:{channel}"
        response_key = f"events:response:{channel}:{query_id}"

        self.redis.rpush(query_key, pickle.dumps(
            {"id": query_id, "channel": channel, "response_key": response_key, "args": args, "kwargs": kwargs})
        )
        result = self.redis.blpop([response_key], timeout=timeout)

        if result is None:
            if not fail_on_timeout:
                return None

            raise TimeoutError(f"Timeout waiting for response from channel {channel} with query id {query_id} on {response_key}")

        response = pickle.loads(result[1])

        err = response.get("err")
        if err is not None:
            raise RuntimeError(f"Error in response from channel {channel}: {err['message']}\n"
                               f"Traceback:\n{err['traceback']}\n"
                               f"Args: {err['args']} \n"
                               f"Kwargs: {err['kwargs']}\n"
                               f"This error originated from the remote service! It was not raised here.")

        resp_data = response.get("res")

        if resp_data is not None:
            self.cache[cache_key] = resp_data
            return self.__parse_response(resp_data)

        return None
