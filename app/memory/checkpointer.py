# """LangGraph checkpoint persistence."""

# import logging
# from functools import lru_cache

# import psycopg
# from langgraph.checkpoint.postgres import PostgresSaver
# from psycopg.rows import dict_row

# from app.config.settings import get_settings

# logger = logging.getLogger(__name__)


# @lru_cache
# def get_checkpointer() -> PostgresSaver:
#     settings = get_settings()
#     conn = psycopg.connect(
#         settings.database_url,
#         autocommit=True,
#         row_factory=dict_row,
#     )
#     checkpointer = PostgresSaver(conn)
#     checkpointer.setup()
#     logger.info("PostgreSQL checkpointer initialized")
#     return checkpointer


"""LangGraph checkpoint persistence."""

import logging
from functools import lru_cache

import psycopg
from langgraph.checkpoint.postgres import PostgresSaver
from psycopg.rows import dict_row

from app.config.settings import get_settings

logger = logging.getLogger(__name__)


@lru_cache
def get_checkpointer() -> PostgresSaver:
    settings = get_settings()

    database_url = settings.database_url.replace("+psycopg", "")

    conn = psycopg.connect(
        database_url,
        autocommit=True,
        row_factory=dict_row,
    )

    checkpointer = PostgresSaver(conn)
    checkpointer.setup()

    logger.info("PostgreSQL checkpointer initialized")
    return checkpointer