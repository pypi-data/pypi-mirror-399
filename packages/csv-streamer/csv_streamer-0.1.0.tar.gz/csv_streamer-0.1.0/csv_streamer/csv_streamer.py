"""
CSV Streaming Library

Stream CSV files (including from ZIP archives) as PyArrow tables.
"""

import csv
import logging
from pathlib import Path
from typing import Iterable, Iterator, Optional, Union

import pyarrow as pa
import requests

from .zipzip import zipzip

logger = logging.getLogger(__name__)

ZIP_SIGNATURES = {b"PK\x03\x04", b"PK\x05\x06", b"PK\x07\x08"}


class StreamerError(Exception):
    """Base exception for csv-streamer errors."""


class NotCSVError(StreamerError):
    """Source does not appear to be a CSV file."""


class DecodeError(StreamerError):
    """Failed to decode bytes as UTF-8."""


class ParseError(StreamerError):
    """Failed to parse CSV content."""


class SchemaError(StreamerError):
    """Schema validation or casting failed."""


class ColumnError(StreamerError):
    """Requested column not found in CSV."""


# BYTES ITERATORS
def _iter_file_chunks(path: Path, chunk_size: int = 65536) -> Iterator[bytes]:
    """Iterate over file in chunks."""
    try:
        with open(path, "rb") as f:
            while chunk := f.read(chunk_size):
                yield chunk
    except OSError as e:
        raise OSError(f"Failed to read file '{path}': {e}") from e


def _iter_url_chunks(url: str, chunk_size: int = 1048576) -> Iterator[bytes]:
    """Iterate over URL response in chunks."""
    try:
        response = requests.get(url, stream=True, timeout=30)
        response.raise_for_status()
        for chunk in response.iter_content(chunk_size=chunk_size):
            if chunk:
                yield chunk
    except requests.RequestException as e:
        raise RuntimeError(f"Failed to stream URL '{url}': {e}") from e


# ZIP DETECTION
def _is_local_zip(path: Path) -> bool:
    """Check if local file is a ZIP by inspecting magic bytes."""
    if not path.is_file():
        return False
    try:
        with path.open("rb") as f:
            return f.read(4) in ZIP_SIGNATURES
    except OSError:
        return False


def _is_remote_zip(url: str) -> bool:
    """Check if remote URL is a ZIP by inspecting magic bytes via Range request."""
    try:
        headers = {"Range": "bytes=0-3"}
        response = requests.get(url, headers=headers, timeout=10, stream=True)
        response.raise_for_status()
        first_bytes = next(response.iter_content(chunk_size=4), b"")
        return first_bytes in ZIP_SIGNATURES
    except Exception:
        return False


# CSV LOGIC
def _parse_csv_lines(
    text_chunks: Iterator[str],
    columns: Optional[list[str]] = None,
) -> Iterator[list[str]]:
    """
    Parse CSV from text chunks.

    First yield is the header, subsequent yields are row values.

    Args:
        text_chunks: Iterator of text chunks
        columns: Optional list of columns to include (filters output)

    Yields:
        First: header as list[str]
        Then: each row as list[str]
    """
    header = None
    column_indices = None
    partial_line = ""

    for text_chunk in text_chunks:
        text_chunk = partial_line + text_chunk
        lines = text_chunk.split("\n")
        partial_line = lines[-1]
        lines = lines[:-1]

        for line in lines:
            if not line.strip():
                continue

            if header is None:
                header = next(csv.reader([line]))

                if columns:
                    missing = [c for c in columns if c not in header]
                    if missing:
                        raise ColumnError(f"Columns not found in CSV: {missing}")
                    column_indices = [header.index(c) for c in columns]
                    header = [header[i] for i in column_indices]

                yield header
            else:
                try:
                    values = next(csv.reader([line]))
                    if column_indices:
                        values = [values[i] for i in column_indices]
                    yield values
                except (csv.Error, IndexError):
                    continue

    # Handle final partial line
    if partial_line.strip() and header:
        try:
            values = next(csv.reader([partial_line]))
            if column_indices:
                values = [values[i] for i in column_indices]
            yield values
        except (csv.Error, IndexError):
            pass


# ARROW LOGIC
def _rows_to_arrow_table(
    header: list[str],
    rows: list[list[str]],
    schema: Optional[pa.Schema] = None,
) -> pa.Table:
    """Convert rows to an Arrow table."""
    # Build column arrays
    column_data = {col: [] for col in header}
    for row in rows:
        for i, col in enumerate(header):
            column_data[col].append(row[i] if i < len(row) else None)

    match schema:
        case pa.Schema() as s:
            arrays = []
            for field in s:
                if field.name in column_data:
                    try:
                        arr = pa.array(column_data[field.name], type=pa.string())
                        arr = arr.cast(field.type, safe=False)
                    except (pa.ArrowInvalid, pa.ArrowNotImplementedError) as e:
                        raise SchemaError(
                            f"Failed to cast column '{field.name}' to {field.type}: {e}"
                        ) from e
                    arrays.append(arr)
                else:
                    arrays.append(pa.nulls(len(rows), type=field.type))
            return pa.Table.from_arrays(arrays, schema=s)
        case None:
            return pa.Table.from_pydict(column_data)


# STREAM LOGIC
def _stream_csv_direct(
    byte_chunks: Iterable[bytes],
    batch_size: int,
    columns: Optional[list[str]],
    schema: Optional[pa.Schema],
) -> Iterator[pa.Table]:
    """Stream CSV directly from byte chunks."""

    def decode_chunks():
        for chunk in byte_chunks:
            yield chunk.decode("utf-8", errors="ignore")

    lines = _parse_csv_lines(decode_chunks(), columns)
    header = next(lines, None)

    if header is None:
        logger.warning("Empty CSV - no header found")
        return

    logger.debug("CSV columns: %s", header)

    batch_count = 0
    row_buffer = []
    for row in lines:
        row_buffer.append(row)

        if len(row_buffer) >= batch_size:
            batch_count += 1
            table = _rows_to_arrow_table(header, row_buffer, schema)
            logger.debug("Yielding batch %d: %d rows", batch_count, len(row_buffer))
            yield table
            row_buffer = []

    if row_buffer:
        batch_count += 1
        table = _rows_to_arrow_table(header, row_buffer, schema)
        logger.debug("Yielding final batch %d: %d rows", batch_count, len(row_buffer))
        yield table

    logger.info("Completed: %d batches", batch_count)


def _stream_csv_from_zip(
    byte_chunks: Iterable[bytes],
    batch_size: int,
    columns: Optional[list[str]],
    schema: Optional[pa.Schema],
) -> Iterator[pa.Table]:
    """Stream CSV from ZIP archive using zipzip."""

    for file_name, file_size, unzipped_chunks in zipzip(byte_chunks):
        file_name_str = (
            file_name.decode("utf-8") if isinstance(file_name, bytes) else file_name
        )

        # Only process CSV files
        if not str(file_name_str).lower().endswith(".csv"):
            logger.debug("Skipping non-CSV file in ZIP: %s", file_name_str)
            for _ in unzipped_chunks:
                pass
            continue

        logger.info("Processing CSV from ZIP: %s", file_name_str)

        def decode_chunks():
            for chunk in unzipped_chunks:
                yield chunk.decode("utf-8", errors="ignore")

        lines = _parse_csv_lines(decode_chunks(), columns)
        header = next(lines, None)

        if header is None:
            logger.warning("Empty CSV in ZIP: %s", file_name_str)
            continue

        logger.debug("CSV columns: %s", header)

        batch_count = 0
        row_buffer = []
        for row in lines:
            row_buffer.append(row)

            if len(row_buffer) >= batch_size:
                batch_count += 1
                table = _rows_to_arrow_table(header, row_buffer, schema)
                logger.debug("Yielding batch %d: %d rows", batch_count, len(row_buffer))
                yield table
                row_buffer = []

        if row_buffer:
            batch_count += 1
            table = _rows_to_arrow_table(header, row_buffer, schema)
            logger.debug(
                "Yielding final batch %d: %d rows", batch_count, len(row_buffer)
            )
            yield table

        logger.info("Completed %s: %d batches", file_name_str, batch_count)


# SINGLE POINT OF ENTRY
def stream_csv(
    source: Union[str, Path, Iterable[bytes]],
    batch_size: int = 10000,
    columns: Optional[list[str]] = None,
    schema: Optional[pa.Schema] = None,
) -> Iterator[pa.Table]:
    """
    Stream CSV data as Arrow tables.

    Args:
        source: URL, file path, or byte iterator
        batch_size: Number of rows per yielded table
        columns: Optional list of column names to include
        schema: Optional PyArrow schema for type conversion

    Yields:
        PyArrow Tables containing batch_size rows (last batch may be smaller - usually is)

    Example:
        >>> for table in stream_csv("data.csv", batch_size=1000):
        ...     process(table)

        >>> schema = pa.schema([("id", pa.int64()), ("name", pa.string())])
        >>> for table in stream_csv("data.zip", schema=schema, columns=["id", "name"]):
        ...     process(table)
    """
    match source:
        case str() | Path() as s:
            source_str = str(s)
            is_zip = (
                _is_remote_zip(source_str)
                if (is_remote := source_str.startswith(("http://", "https://")))
                else _is_local_zip(Path(source_str))
            )

            if not is_zip and not source_str.lower().endswith(".csv"):
                raise NotCSVError(
                    f"Source does not appear to be a CSV file: {source_str}"
                )

            # 4 paths: local csv, local zip, remote csv, remote zip
            match (is_remote, is_zip):
                case (True, True):
                    logger.info("Streaming remote ZIP: %s", source_str)
                    yield from _stream_csv_from_zip(
                        _iter_url_chunks(source_str), batch_size, columns, schema
                    )
                case (True, False):
                    logger.info("Streaming remote CSV: %s", source_str)
                    yield from _stream_csv_direct(
                        _iter_url_chunks(source_str), batch_size, columns, schema
                    )
                case (False, True):
                    logger.info("Streaming local ZIP: %s", source_str)
                    yield from _stream_csv_from_zip(
                        _iter_file_chunks(Path(source_str)), batch_size, columns, schema
                    )
                case (False, False):
                    logger.info("Streaming local CSV: %s", source_str)
                    yield from _stream_csv_direct(
                        _iter_file_chunks(Path(source_str)), batch_size, columns, schema
                    )

        case _:
            logger.info("Streaming from byte iterator")
            yield from _stream_csv_direct(source, batch_size, columns, schema)
