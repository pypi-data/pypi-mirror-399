import bz2
import zlib
from struct import Struct
from typing import Any, Container, Generator, Iterable, NewType, Optional, Tuple

_Encryption = NewType("_Encryption", object)

NO_ENCRYPTION: _Encryption = _Encryption(object())

_ALL_ENCRYPTIONS = (NO_ENCRYPTION,)
_DEFAULT_CHUNK_SIZE = 65536


def zipzip(
    zipfile_chunks: Iterable[bytes],
    password: Optional[bytes] = None,
    chunk_size: int = _DEFAULT_CHUNK_SIZE,
    allow_zip64: bool = True,
    allowed_encryption_mechanisms: Container[_Encryption] = _ALL_ENCRYPTIONS,
) -> Generator[Tuple[bytes, Optional[int], Generator[bytes, Any, None]], Any, None]:
    local_file_header_signature = b"PK\x03\x04"
    local_file_header_struct = Struct("<H2sHHHIIIHH")
    zip64_compressed_size = 0xFFFFFFFF
    zip64_size_signature = b"\x01\x00"
    central_directory_signature = b"PK\x01\x02"
    end_of_central_directory_signature = b"PK\x05\x06"
    unsigned_short = Struct("<H")
    unsigned_long_long = Struct("<Q")

    dd_optional_signature = b"PK\x07\x08"
    dd_struct_32 = Struct("<0sIII4s")
    dd_struct_32_with_sig = Struct("<4sIII4s")
    dd_struct_64 = Struct("<0sIQQ4s")
    dd_struct_64_with_sig = Struct("<4sIQQ4s")

    def next_or_truncated_error(it):
        try:
            return next(it)
        except StopIteration:
            raise TruncatedDataError from None

    def get_byte_readers(iterable):
        chunk = b""
        offset = 0
        offset_from_start = 0
        queue = list()
        it = iter(iterable)

        def _next():
            try:
                return queue.pop(0)
            except IndexError:
                return (next_or_truncated_error(it), 0)

        def _yield_num(num):
            nonlocal chunk, offset, offset_from_start

            while num:
                if offset == len(chunk):
                    chunk, offset = _next()
                to_yield = min(num, len(chunk) - offset, chunk_size)
                offset = offset + to_yield
                num -= to_yield
                offset_from_start += to_yield
                yield chunk[offset - to_yield : offset]

        def _yield_all():
            try:
                yield from _yield_num(float("inf"))
            except TruncatedDataError:
                pass

        def _get_num(num):
            return b"".join(_yield_num(num))

        def _return_num_unused(num_unused):
            nonlocal offset, offset_from_start
            offset -= num_unused
            offset_from_start -= num_unused

        def _return_bytes_unused(bytes_unused):
            nonlocal chunk, offset, offset_from_start
            queue.insert(0, (chunk, offset))
            chunk = bytes_unused
            offset = 0
            offset_from_start -= len(bytes_unused)

        def _get_offset_from_start():
            return offset_from_start

        return (
            _yield_all,
            _get_num,
            _return_num_unused,
            _return_bytes_unused,
            _get_offset_from_start,
        )

    def get_decompressor_none(num_bytes):
        num_decompressed = 0
        num_unused = 0

        def _decompress(compressed_chunk):
            nonlocal num_decompressed, num_unused
            to_yield = min(len(compressed_chunk), num_bytes - num_decompressed)
            num_decompressed += to_yield
            num_unused = len(compressed_chunk) - to_yield
            yield compressed_chunk[:to_yield]

        def _is_done():
            return num_decompressed == num_bytes

        def _num_unused():
            return num_unused

        return _decompress, _is_done, _num_unused

    def get_decompressor_deflate():
        dobj = zlib.decompressobj(wbits=-zlib.MAX_WBITS)

        def _decompress_single(compressed_chunk):
            try:
                return dobj.decompress(compressed_chunk, chunk_size)
            except zlib.error as e:
                raise DeflateError() from e

        def _decompress(compressed_chunk):
            uncompressed_chunk = _decompress_single(compressed_chunk)
            if uncompressed_chunk:
                yield uncompressed_chunk

            while dobj.unconsumed_tail and not dobj.eof:
                uncompressed_chunk = _decompress_single(dobj.unconsumed_tail)
                if uncompressed_chunk:
                    yield uncompressed_chunk

        def _is_done():
            return dobj.eof

        def _num_unused():
            return len(dobj.unused_data)

        return _decompress, _is_done, _num_unused

    def get_decompressor_bz2():
        dobj = bz2.BZ2Decompressor()

        def _decompress_single(compressed_chunk):
            try:
                return dobj.decompress(compressed_chunk, chunk_size)
            except OSError as e:
                raise BZ2Error() from e

        def _decompress(compressed_chunk):
            uncompressed_chunk = _decompress_single(compressed_chunk)
            if uncompressed_chunk:
                yield uncompressed_chunk

            while not dobj.eof:
                uncompressed_chunk = _decompress_single(b"")
                if not uncompressed_chunk:
                    break
                yield uncompressed_chunk

        def _is_done():
            return dobj.eof

        def _num_unused():
            return len(dobj.unused_data)

        return _decompress, _is_done, _num_unused

    def yield_file(
        yield_all,
        get_num,
        return_num_unused,
        return_bytes_unused,
        get_offset_from_start,
    ):
        def get_flag_bits(flags):
            for b in flags:
                for i in range(8):
                    yield (b >> i) & 1

        def parse_extra(extra):
            extra_offset = 0
            while extra_offset <= len(extra) - 4:
                extra_signature = extra[extra_offset : extra_offset + 2]
                extra_offset += 2
                (extra_data_size,) = unsigned_short.unpack(
                    extra[extra_offset : extra_offset + 2]
                )
                extra_offset += 2
                extra_data = extra[extra_offset : extra_offset + extra_data_size]
                extra_offset += extra_data_size
                yield (extra_signature, extra_data)

        def get_extra_value(
            extra,
            if_true,
            signature,
            exception_if_missing,
            min_length,
            exception_if_too_short,
        ):
            value = None

            if if_true:
                try:
                    value = extra[signature]
                except KeyError:
                    if exception_if_missing:
                        raise exception_if_missing()
                else:
                    if len(value) < min_length:
                        raise exception_if_too_short()

            return value

        def decrypt_none_decompress(chunks, decompress, is_done, num_unused):
            while not is_done():
                yield from decompress(next_or_truncated_error(chunks))

            return_num_unused(num_unused())

        def read_data_and_count_and_crc32(chunks):
            offset_1 = None
            offset_2 = None
            crc_32_actual = zlib.crc32(b"")
            l = 0

            def _iter():
                nonlocal offset_1, offset_2, crc_32_actual, l

                offset_1 = get_offset_from_start()
                for chunk in chunks:
                    crc_32_actual = zlib.crc32(chunk, crc_32_actual)
                    l += len(chunk)
                    yield chunk
                offset_2 = get_offset_from_start()

            return (
                _iter(),
                lambda: (offset_2 or 0) - (offset_1 or 0),
                lambda: crc_32_actual,
                lambda: l,
            )

        def checked_from_local_header(
            chunks, get_crc_32, get_compressed_size, get_uncompressed_size
        ):
            yield from chunks

            crc_32_data = get_crc_32()
            compressed_size_data = get_compressed_size()
            uncompressed_size_data = get_uncompressed_size()

            if crc_32_expected != crc_32_data:
                raise CRC32IntegrityError()

            if compressed_size_data != compressed_size:
                raise CompressedSizeIntegrityError()

            if uncompressed_size_data != uncompressed_size:
                raise UncompressedSizeIntegrityError()

        def checked_from_data_descriptor(
            chunks,
            is_sure_zip64,
            get_crc_32,
            get_compressed_size,
            get_uncompressed_size,
        ):
            yield from chunks

            crc_32_data = get_crc_32()
            compressed_size_data = get_compressed_size()
            uncompressed_size_data = get_uncompressed_size()
            best_matches = (False, False, False, False, False)
            must_treat_as_zip64 = (
                is_sure_zip64
                or compressed_size_data > 0xFFFFFFFF
                or uncompressed_size_data > 0xFFFFFFFF
            )

            checks = (
                (
                    (dd_struct_64_with_sig, dd_optional_signature),
                    (dd_struct_64, b""),
                )
                if allow_zip64
                else ()
            ) + (
                (
                    (dd_struct_32_with_sig, dd_optional_signature),
                    (dd_struct_32, b""),
                )
                if not must_treat_as_zip64
                else ()
            )

            if not checks:
                raise UnsupportedZip64Error()

            dd = get_num(checks[0][0].size)
            dd_struct = checks[0][0]
            next_signature = b""

            for dd_struct, expected_signature in checks:
                (
                    signature_dd,
                    crc_32_dd,
                    compressed_size_dd,
                    uncompressed_size_dd,
                    next_signature,
                ) = dd_struct.unpack(dd[: dd_struct.size])
                matches = (
                    signature_dd == expected_signature,
                    crc_32_dd == crc_32_data,
                    compressed_size_dd == compressed_size_data,
                    uncompressed_size_dd == uncompressed_size_data,
                    next_signature
                    in (local_file_header_signature, central_directory_signature),
                )
                best_matches = max(best_matches, matches, key=lambda t: t.count(True))

                if best_matches == (True, True, True, True, True):
                    break

            if not best_matches[0]:
                raise UnexpectedSignatureError()

            if not best_matches[1]:
                raise CRC32IntegrityError()

            if not best_matches[2]:
                raise CompressedSizeIntegrityError()

            if not best_matches[3]:
                raise UncompressedSizeIntegrityError()

            if not best_matches[4]:
                raise UnexpectedSignatureError(next_signature)

            return_bytes_unused(
                dd[dd_struct.size - 4 :]
            )  # 4 is the length of next signature already taken

        (
            version,
            flags,
            compression_raw,
            mod_time,
            mod_date,
            crc_32_expected,
            compressed_size_raw,
            uncompressed_size_raw,
            file_name_len,
            extra_field_len,
        ) = local_file_header_struct.unpack(get_num(local_file_header_struct.size))

        flag_bits = tuple(get_flag_bits(flags))
        if flag_bits[4] or flag_bits[5] or flag_bits[6] or flag_bits[13]:
            raise UnsupportedFlagsError(flag_bits)

        file_name = get_num(file_name_len)
        extra = dict(parse_extra(get_num(extra_field_len)))

        is_encrypted = flag_bits[0]

        if is_encrypted:
            raise UnsupportedFeatureError(
                "Encryption not supported in simplified version"
            )

        if password is not None and NO_ENCRYPTION not in allowed_encryption_mechanisms:
            raise FileIsNotEncrypted()

        compression = compression_raw

        if compression not in (0, 8, 12):
            raise UnsupportedCompressionTypeError(compression)

        has_data_descriptor = flag_bits[3]
        might_be_zip64 = (
            compressed_size_raw == zip64_compressed_size
            and uncompressed_size_raw == zip64_compressed_size
        )
        zip64_extra = get_extra_value(
            extra,
            might_be_zip64,
            zip64_size_signature,
            False,
            16,
            TruncatedZip64ExtraError,
        )
        is_sure_zip64 = bool(zip64_extra)

        if not allow_zip64 and is_sure_zip64:
            raise UnsupportedZip64Error()

        compressed_size = (
            None
            if has_data_descriptor and compression in (8, 12)
            else unsigned_long_long.unpack(zip64_extra[8:16])[0]
            if is_sure_zip64
            else compressed_size_raw
        )

        uncompressed_size = (
            None
            if has_data_descriptor and compression in (8, 12)
            else unsigned_long_long.unpack(zip64_extra[:8])[0]
            if is_sure_zip64
            else uncompressed_size_raw
        )

        if has_data_descriptor and compression == 0 and compressed_size == 0:
            raise NotStreamUnzippable(file_name)

        decompressor = (
            get_decompressor_none(uncompressed_size)
            if compression == 0
            else get_decompressor_deflate()
            if compression == 8
            else get_decompressor_bz2()
        )

        decompressed_bytes = decrypt_none_decompress(yield_all(), *decompressor)

        (
            counted_decompressed_bytes,
            get_compressed_size,
            get_crc_32_actual,
            get_uncompressed_size,
        ) = read_data_and_count_and_crc32(decompressed_bytes)

        checked_bytes = (
            checked_from_data_descriptor(
                counted_decompressed_bytes,
                is_sure_zip64,
                get_crc_32_actual,
                get_compressed_size,
                get_uncompressed_size,
            )
            if has_data_descriptor
            else checked_from_local_header(
                counted_decompressed_bytes,
                get_crc_32_actual,
                get_compressed_size,
                get_uncompressed_size,
            )
        )

        return file_name, uncompressed_size, checked_bytes

    def all():
        (
            yield_all,
            get_num,
            return_num_unused,
            return_bytes_unused,
            get_offset_from_start,
        ) = get_byte_readers(zipfile_chunks)

        while True:
            signature = get_num(len(local_file_header_signature))
            if signature == local_file_header_signature:
                yield yield_file(
                    yield_all,
                    get_num,
                    return_num_unused,
                    return_bytes_unused,
                    get_offset_from_start,
                )
            elif signature in (
                central_directory_signature,
                end_of_central_directory_signature,
            ):
                for _ in yield_all():
                    pass
                break
            else:
                raise UnexpectedSignatureError(signature)

    for file_name, file_size, unzipped_chunks in all():
        yield file_name, file_size, unzipped_chunks
        for _ in unzipped_chunks:
            raise UnfinishedIterationError()


class UnzipError(Exception):
    pass


class InvalidOperationError(UnzipError):
    pass


class UnfinishedIterationError(InvalidOperationError):
    pass


class UnzipValueError(UnzipError, ValueError):
    pass


class DataError(UnzipValueError):
    pass


class UncompressError(UnzipValueError):
    pass


class DeflateError(UncompressError):
    pass


class BZ2Error(UncompressError):
    pass


class UnsupportedFeatureError(DataError):
    pass


class UnsupportedFlagsError(UnsupportedFeatureError):
    pass


class UnsupportedCompressionTypeError(UnsupportedFeatureError):
    pass


class UnsupportedZip64Error(UnsupportedFeatureError):
    pass


class NotStreamUnzippable(UnsupportedFeatureError):
    pass


class TruncatedDataError(DataError):
    pass


class UnexpectedSignatureError(DataError):
    pass


class MissingExtraError(DataError):
    pass


class TruncatedExtraError(DataError):
    pass


class TruncatedZip64ExtraError(TruncatedExtraError):
    pass


class InvalidExtraError(TruncatedExtraError):
    pass


class IntegrityError(DataError):
    pass


class CRC32IntegrityError(IntegrityError):
    pass


class SizeIntegrityError(IntegrityError):
    pass


class UncompressedSizeIntegrityError(SizeIntegrityError):
    pass


class CompressedSizeIntegrityError(SizeIntegrityError):
    pass


class PasswordError(UnzipValueError):
    pass


class MissingPasswordError(UnzipValueError):
    pass


class IncorrectPasswordError(PasswordError):
    pass


class EncryptionMechanismNotAllowed(PasswordError):
    pass


class FileIsNotEncrypted(EncryptionMechanismNotAllowed):
    pass
