---
layout:  post
title:  "python中Redis, StrictRedis, ConnectPool的联系与区别"
subtitle:  'Redis, StrictRedis, ConnectPool'
date:  2019-10-29 18:00:00
author:  "rpl"
header-style:  "text"
catalog: true
tags:
    - 原创
    - python
    - 技术
    - redis
    - StrictRedis
    - ConnectPool
    - 连接池

---


先上结论：**直接使用 StrictRedis() 即可**。


原因如下:

1. 官方考虑向后兼容性，推荐使用StrictRedis()。两者没有任何差别，redis.client.py 源码中可以直接看出StrictRedis就是Redis
```python
StrictRedis = Redis
```
2. ConnectPool是redis的连接池类, 是用来实现连接池及其管理的， 而StrictRedis()默认使用连接池，不必在单独使用ConnectPool。（这个在后面的源码里会详细解释）

3. 因此，我们无需考虑redis关于连接的细节，直接使用StrictRedis()即可


***

下面我们通过源码，深入探寻Redis， StrictiRedis， connectionPool之间的联系，以及实现原理。

既然StrictRedis就是Redis， 那就直接扒Redis源码看看：


#### Redis.\_\_init\_\_(...)

```python
def __init__(self, host='localhost', port=6379,
         db=0, password=None, socket_timeout=None,
         socket_connect_timeout=None,
         socket_keepalive=None, socket_keepalive_options=None,
         connection_pool=None, unix_socket_path=None,
         encoding='utf-8', encoding_errors='strict',
         charset=None, errors=None,
         decode_responses=False, retry_on_timeout=False,
         ssl=False, ssl_keyfile=None, ssl_certfile=None,
         ssl_cert_reqs='required', ssl_ca_certs=None,
         max_connections=None):
if not connection_pool:
    ... # 为了阅读效果，精简了部分注释和无关代码。

    kwargs = {
        'db': db,
        'password': password,
        'socket_timeout': socket_timeout,
        'encoding': encoding,
        'encoding_errors': encoding_errors,
        'decode_responses': decode_responses,
        'retry_on_timeout': retry_on_timeout,
        'max_connections': max_connections
    }
    
    ... # 为了阅读效果，精简了部分注释和无关代码。
    connection_pool = ConnectionPool(**kwargs)
    
self.connection_pool = connection_pool
```

从 connection_pool, max_connections 这几个参数可以看到 Redis()是支持使用连接池的，可以直接在实例化Redis的时候加上连接池的设置：
```python
import redis
pool = redis.ConnectionPool(host='127.0.0.1',port=6379,password='123456')
r = redis.StrictRedis(connection_pool=pool)

```
接着往下看 \_\_init\_\_()的代码：
```python
if not connection_pool:
    ...
    'max_connections': max_connections
    
 connection_pool = ConnectionPool(**kwargs)
```
也就是说，Redis() 是默认使用连接池的，就算我们不显式的设置 connection_pool， Redis也会默认初始化一个连接池：connection_pool = ConnectionPool(\*\*kwargs)，并使用默认的最大连接数： 'max_connections': max_connections。 

所以，如果我们对连接池没有特殊要求，不需要考虑连接池的问题。Redis默认就已经使用了连接池。

***
#### ConnectionPool()

Redis()是通过ConnectionPool()实现连接池的, 那么我们看一下这个类的源码。
```python
class ConnectionPool(object):
    ...
    
    def __init__(self, connection_class=Connection, max_connections=None,
                 **connection_kwargs):
        ...
        max_connections = max_connections or 2 ** 31
        if not isinstance(max_connections, (int, long)) or max_connections < 0:
            raise ValueError('"max_connections" must be a positive integer')

        self.connection_class = connection_class
        self.connection_kwargs = connection_kwargs
        self.max_connections = max_connections

        self.reset()
```

可以发现connection_pool = ConnectionPool(\*\*kwargs) 只是实例化了这个类，具体并没有redis连接池的实现。

***

那么Redis() 是怎么使用连接池的呢？从Redis的get()，set()等操作中下手找

先看一下Redis.set()的实现：

#### Redis.set()

```python
def set(self, name, value, ex=None, px=None, nx=False, xx=False):
    ...
    return self.execute_command('SET', *pieces)

```

可以看到 Redis.set() 是通过 self.execute_command()这个封装好的方法实现的，其实Redis的所有操作都是通过这个方法实现的。

继续深扒self.execute_command()函数：

```python
# COMMAND EXECUTION AND PROTOCOL PARSING
def execute_command(self, *args, **options):
    "Execute a command and return a parsed response"
    pool = self.connection_pool
    command_name = args[0]
    connection = pool.get_connection(command_name, **options)
    try:
        connection.send_command(*args)
        return self.parse_response(connection, command_name, **options)
    except (ConnectionError, TimeoutError) as e:
        connection.disconnect()
        if not (connection.retry_on_timeout andisinstance(e, TimeoutError)):
            raise
        connection.send_command(*args)
        return self.parse_response(connection, command_name, **options)
    finally:
        pool.release(connection)
```
通过这个函数，我们能清晰的看到 Redis() 使用连接池的整个过程：

1. 通过连接池，获取一个与redis的连接（pool.get_connection）。
2. 通过这个连接进行redis操作。 
3. 操作完成连接池释放这个连接（pool.release(connection)，有异常的话,断开连接（connection.disconnection)


***
现在有个大概了解了，继续查看关于连接池的部分函数

#### self.get_connection()

```python
def get_connection(self, command_name, *keys, **options):
    "Get a connection from the pool"
    self._checkpid()
    try:
        connection = self._available_connections.pop()
    except IndexError:
        connection = self.make_connection()
        
    self._in_use_connections.add(connection)
    try:
        # ensure this connection is connected to Redis
        connection.connect()
        # connections that the pool provides should be ready to send
        # a command. if not, the connection was either returned to the
        # pool before all data has been read or the socket has been
        # closed. either way, reconnect and verify everything is good.
        if not connection.is_ready_for_command():
            connection.disconnect()
            connection.connect()
            if not connection.is_ready_for_command():
                raise ConnectionError('Connection not ready')
    except:  # noqa: E722
        # release the connection back to the pool so that we don't leak it
        self.release(connection)
        raise
        
return connection

def reset(self):
    ...
    self._available_connections = []
    self._in_use_connections = set()
    ...

```

get_connection()的实现：
1. 可用连接池中获取一个现有的连接（）self.\_available_connections.pop()）没有的话就新建一个连接（make_connection()).
2. 将这个连接加入到正在使用的连接池里（self.\_in_use_connection.add(connection).
3. 异常情况的处理，断开连接（connection.disconnec()）或释放连接（self.release(connection)）

self.\_available_connections，self.\_in_use_connections是列表和集合实现的。因此获取连接池的原理就是 从可用连接池里中获取一个连接，然后将这个连接加入到正在使用的连接池中。

***
#### self.make_connection()
```python
def make_connection(self):
    "Create a new connection"
    if self._created_connections >= self.max_connections:
        raise ConnectionError("Too many connections")
    self._created_connections += 1
    return self.connection_class(**self.connection_kwargs)
```
很简单，就是在最大连接数的限制下，创建一个连接类。

***
#### self.release()
```python
def release(self, connection):
    "Releases the connection back to the pool"
    self._checkpid()
    if connection.pid != self.pid:
        return
    self._in_use_connections.remove(connection)
    self._available_connections.append(connection)
```
将连接从正在使用的连接池里移除，完成了整个释放过程。同时又将其添加到可用连接池里，可以后续继续使用这个连接。

***
#### self.disconnect()

不同于release(),  disconnect()函数是断开所有的全部连接。
```python
def release(self, connection):
    "Releases the connection back to the pool"
    self._checkpid()
    if connection.pid != self.pid:
        return
    self._in_use_connections.remove(connection)
    self._available_connections.append(connection)
```

***
**ConnectionPool**连接池通过可用连接表（\_available_connections）获取连接，将连接加入到正在使用的连接表（\_in_use_connections）里。
连接使用后，释放连接。 从正在使用的连接表里移除连接，并加入到可用连接表里，实现连接的重复使用。
当可用连接表为空时，才创建新的连接。并加入到上面的两个表里进行管理。
因此在高并发时，Redis不会频繁的去创建新的连接，而是会通过连接池去获取已有的连接，这样整个性能就不会收到影响了，这就是使用连接池的目的。


通过以上，StrictRedis()本身就已经是通过连接池获取连接了。除非我们对连接池的大小等方面有特殊要求，这才需要去显示的配置连接池。没有的话，直接大胆的使用**StrictRedis()**吧。
