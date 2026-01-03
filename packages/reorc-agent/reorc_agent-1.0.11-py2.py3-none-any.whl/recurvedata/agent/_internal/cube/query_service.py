import asyncio
from threading import Lock

import psycopg2
import psycopg2.pool
from psycopg2.pool import PoolError
from loguru import logger

from recurvedata.agent._internal.cube.cube_utils import _convert_to_json_serializable, normalize_sql_query
from recurvedata.agent._internal.schemas import CubeSqlRequestPayload

# Global connection pools - one pool per unique connection string
_connection_pools = {}
_pool_lock = Lock()
SEMANTIC_API_INTERNAL_USER = "system_cube_internal_user"
SEMANTIC_API_SIGHT_USER = "system_cube_sight_user"
CLIENT_CODE_SIGHT = "sight"
SEMANTIC_DEFAULT_QUERY_TIMEOUT = 60
SEMANTIC_DEFAULT_CONNECT_TIMEOUT = 10


def get_connection_pool(db_name, db_user, db_password, db_host, db_port):
    """Get or create a connection pool for the given database parameters."""
    # Create a unique key for this connection configuration

    # Check if user is using OTP password (INTERNAL_USER) - do not pool OTP connections
    db_user_name_only = db_user.split(":")[0]
    if db_user_name_only == SEMANTIC_API_INTERNAL_USER:
        logger.info(
            f"get_connection_pool: INTERNAL_USER user detected ({db_user_name_only}), skipping connection pooling"
        )
        return None

    # SIGHT_USER use connection pooling
    if db_user_name_only == SEMANTIC_API_SIGHT_USER:
        # diff otp pass but same user name
        logger.info(f"get_connection_pool: SIGHT_USER user detected ({db_user_name_only}), using connection pooling")
        pool_key = f"{db_host}:{db_port}:{db_name}:{db_user}"
    else:
        pool_key = f"{db_host}:{db_port}:{db_name}:{db_user}:{db_password}"

    with _pool_lock:
        if pool_key not in _connection_pools:
            try:
                # Create a new connection pool
                _connection_pools[pool_key] = psycopg2.pool.ThreadedConnectionPool(
                    minconn=1,  # Minimum number of connections in pool
                    maxconn=100,  # Maximum number of connections in pool
                    dbname=db_name,
                    user=db_user,
                    password=db_password,
                    host=db_host,
                    port=db_port,
                    connect_timeout=SEMANTIC_DEFAULT_CONNECT_TIMEOUT,
                )
                logger.info(f"get_connection_pool: Created new connection pool for {pool_key} (min=1, max=100)")
            except Exception as e:
                logger.error(f"get_connection_pool: Failed to create connection pool for {pool_key}: {e}")
                raise

        return _connection_pools[pool_key]


def get_connection_pool_stats() -> dict[str, dict]:
    """Get statistics for all connection pools.

    Returns:
        A dictionary mapping pool keys to their statistics:
        {
            "host:port:db:user": {
                "used": int,  # Number of connections currently in use
                "free": int,  # Number of available connections in pool
                "max": int,   # Maximum pool size
            }
        }

    Note: This function reads pool state without locking for performance.
    The returned values are approximate and may be slightly stale.
    """
    stats = {}
    # Iterate over a snapshot of keys to avoid RuntimeError during iteration
    for pool_key in list(_connection_pools.keys()):
        pool = _connection_pools.get(pool_key)
        if pool:
            try:
                stats[pool_key] = {
                    "used": len(pool._used),
                    "free": len(pool._pool),
                    "max": pool.maxconn,
                }
            except Exception:
                pass
    return stats


def get_direct_connection(db_name, db_user, db_password, db_host, db_port):
    """Create a direct connection to the database without pooling."""
    try:
        conn = psycopg2.connect(
            dbname=db_name,
            user=db_user,
            password=db_password,
            host=db_host,
            port=db_port,
            connect_timeout=SEMANTIC_DEFAULT_CONNECT_TIMEOUT,
        )
        logger.info(f"get_direct_connection: Created direct connection to {db_host}:{db_port}/{db_user}")
        return conn
    except Exception as e:
        logger.error(f"get_direct_connection: Failed to create connection to {db_host}:{db_port}/{db_user}: {e}")
        raise


def pg_query(
    query,
    db_name,
    db_user,
    db_password,
    db_host,
    db_port,
    include_column_names=False,
    client_code=None,
    statement_timeout=None,
):
    """Execute a PostgreSQL query using connection pooling only for 'sight' client, otherwise use direct connections."""
    conn = None
    cursor = None
    use_pooling = client_code == CLIENT_CODE_SIGHT
    pool = None

    try:
        if use_pooling:
            # Use connection pooling for sight client
            logger.info(f"pg_query: Using connection pooling for client_code='{client_code}'")
            pool = get_connection_pool(db_name, db_user, db_password, db_host, db_port)
            if pool is None:
                # SEMANTIC_API_SIGHT_USER user detected, fall back to direct connection
                logger.info("pg_query: SEMANTIC_API_SIGHT_USER user detected, falling back to direct connection")
                conn = get_direct_connection(db_name, db_user, db_password, db_host, db_port)
                use_pooling = False
            else:
                try:
                    conn = pool.getconn()
                except PoolError as e:
                    logger.error(f"pg_query: Connection pool exhausted: {e}")
                    raise
                if conn is None:
                    raise Exception("pg_query: Failed to get connection from pool")
                # Reset connection to ensure clean state
                conn.reset()
        else:
            # Use direct connection for other clients
            logger.info(f"pg_query: Using direct connection for client_code='{client_code}'")
            conn = get_direct_connection(db_name, db_user, db_password, db_host, db_port)

        # Normalize query to handle newlines and formatting issues
        normalized_query = normalize_sql_query(query)

        # Log query normalization for debugging
        if query != normalized_query:
            logger.info(
                f"pg_query: SQL query normalized: Original length: {len(query)}, Normalized length: {len(normalized_query)}"
            )

        # Log query with max 500 characters
        logger.info(f"pg_query: Executing query: {normalized_query[:500]}")

        # Execute query
        cursor = conn.cursor()

        # Set statement_timeout to ensure database-level timeout
        # Use SET LOCAL so the setting is automatically cleared when transaction ends (rollback)
        if statement_timeout:
            cursor.execute(f"SET LOCAL statement_timeout = {int(statement_timeout * 1000)}")

        cursor.execute(normalized_query)
        rows = cursor.fetchall()

        # Convert Decimal and datetime objects to JSON-serializable types
        if rows:
            rows = _convert_to_json_serializable(rows)

        # Return with column names only if requested
        if include_column_names and cursor.description:
            columns = [desc[0] for desc in cursor.description]
            return [columns] + list(rows)
        else:
            # Original behavior
            return rows

    finally:
        # Close cursor first
        if cursor:
            try:
                cursor.close()
            except Exception:
                pass

        # Handle connection cleanup based on whether pooling was used
        if conn:
            try:
                # Rollback to ensure clean transaction state before returning to pool
                conn.rollback()
                if use_pooling and pool:
                    # Return connection to pool
                    pool.putconn(conn)
                    logger.info("pg_query: Connection returned to pool")
                else:
                    # Close direct connection
                    conn.close()
                    logger.info("pg_query: Direct connection closed")
            except Exception as e:
                logger.error(f"pg_query: Failed to cleanup connection: {e}")
                # If cleanup fails, try to force close the connection
                try:
                    conn.close()
                except Exception:
                    pass


# Convert the sync function to async with timeout wrapper
async def async_pg_query(*args, **kwargs):
    """
    Async wrapper for pg_query using asyncio.to_thread with timeout protection.

    This wrapper prevents the agent from hanging indefinitely when database queries
    block due to network issues or unresponsive database servers.

    Args:
        *args: Arguments to pass to pg_query
        **kwargs: Keyword arguments to pass to pg_query, including:
            timeout (float): Query timeout in seconds (default: 60.0)

    Returns:
        Query results from pg_query

    Raises:
        asyncio.TimeoutError: If query execution exceeds the timeout
        Exception: Any other error from the underlying pg_query function

    Example:
        # Test timeout with a long-running query:
        try:
            result = await async_pg_query("SELECT pg_sleep(60)", "test_db", "user", "pass", "localhost", 5432, timeout=5.0)
        except asyncio.TimeoutError as e:
            print(f"Query timed out as expected: {e}")
    """
    # Extract timeout parameter if provided
    timeout = kwargs.pop("timeout", SEMANTIC_DEFAULT_QUERY_TIMEOUT)

    # Pass timeout to pg_query as statement_timeout for database-level timeout
    # This ensures the database will cancel the query even if Python-level timeout fires
    kwargs["statement_timeout"] = timeout

    try:
        return await asyncio.wait_for(asyncio.to_thread(pg_query, *args, **kwargs), timeout=timeout)
    except asyncio.TimeoutError:
        logger.error(f"SQL query timed out after {timeout} seconds")
        raise asyncio.TimeoutError(f"SQL query execution timed out after {timeout} seconds")
    except Exception as e:
        logger.error(f"SQL query execution failed: {e}")
        raise


class CubeQueryService:
    """Service for executing SQL queries with connection pooling only for sight client"""

    @staticmethod
    async def execute_sql_query(
        payload: CubeSqlRequestPayload, timeout: int = SEMANTIC_DEFAULT_QUERY_TIMEOUT
    ) -> list[tuple]:
        """Execute SQL query using psycopg2 with connection pooling only for sight client"""

        logger.info(
            f"Executing SQL query on {payload.host}:{payload.port}/{payload.user} for client_code='{payload.client_code}' with timeout={timeout}s"
        )

        # Use the async version of pg_query with conditional connection pooling and timeout
        result = await async_pg_query(
            query=payload.query,
            db_name=payload.database,
            db_user=payload.user,
            db_password=payload.password,
            db_host=payload.host,
            db_port=payload.port,
            include_column_names=payload.include_column_names,
            client_code=payload.client_code,
            timeout=timeout,
        )

        logger.info(f"SQL query executed successfully, returned {len(result) if result else 0} rows")
        return result


# Global service instance
cube_query_service = CubeQueryService()
