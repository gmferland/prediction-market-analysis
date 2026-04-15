"""Indexer for Kalshi markets data."""

from datetime import datetime
from pathlib import Path

from src.common import config
from src.common.indexer import Indexer
from src.common.storage import ParquetStorage
from src.indexers.kalshi.client import KalshiClient

DATA_DIR = Path(config.DATA_DIR, "kalshi/markets")
CURSOR_FILE = Path(config.DATA_DIR, "kalshi/.backfill_cursor")


class KalshiMarketsIndexer(Indexer):
    """Fetches and stores Kalshi markets data."""

    def __init__(self):
        super().__init__(
            name="kalshi_markets",
            description="Backfills Kalshi markets data to parquet files",
        )

    def run(
        self,
        start_date: datetime | None = None,
        end_date: datetime | None = None,
        max_records: int | None = None,
    ) -> None:
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        CURSOR_FILE.parent.mkdir(parents=True, exist_ok=True)

        client = KalshiClient()
        storage = ParquetStorage(data_dir=DATA_DIR)

        cursor = None
        if CURSOR_FILE.exists():
            cursor = CURSOR_FILE.read_text().strip() or None
            if cursor:
                print(f"Resuming from cursor: {cursor[:20]}...")

        total = 0
        for markets, next_cursor in client.iter_markets(
            limit=1000,
            cursor=cursor,
            min_close_ts=start_date.timestamp() if start_date is not None else None,
            max_close_ts=end_date.timestamp() if end_date is not None else None,
        ):
            if markets:
                total_stored = storage.append_markets(markets)
                total += len(markets)
                print(f"Fetched {len(markets)} markets (total: {total}, stored: {total_stored})")

            if next_cursor:
                CURSOR_FILE.write_text(next_cursor)
            else:
                if CURSOR_FILE.exists():
                    CURSOR_FILE.unlink()
                break

            if total >= max_records:
                break

        print(f"\nBackfill complete: {total} markets fetched")
