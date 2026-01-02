# =============================================================================
# Docstring
# =============================================================================

"""
Mimetype Sniff Utility Module
===============================================

Best-effort magic-number based MIME type detection.

"""


# =============================================================================
# Imports
# =============================================================================

# Import | Future
from __future__ import annotations

BytesLike = bytes | bytearray | memoryview


# =============================================================================
# Helper Functions
# =============================================================================


def _check_fixed_signatures(mv: memoryview) -> str | None:
    """Check fixed magic number signatures."""
    if mv[:8] == b"\x89PNG\r\n\x1a\n":
        return "image/png"
    if mv[:3] == b"\xff\xd8\xff":
        return "image/jpeg"
    if mv[:6] in (b"GIF87a", b"GIF89a"):
        return "image/gif"
    if mv[:5] == b"%PDF-":
        return "application/pdf"
    if mv[:4] == b"PK\x03\x04":
        return "application/zip"
    if mv[:3] == b"\x1f\x8b\x08":
        return "application/gzip"
    if mv[:3] == b"ID3" or (
        len(mv) >= 2 and mv[0] == 0xFF and (mv[1] & 0xE0) == 0xE0
    ):
        return "audio/mpeg"
    if mv[:4] == b"fLaC":
        return "audio/flac"
    return None


def _check_riff_container(mv: memoryview) -> str | None:
    """Check RIFF container format (WebP, WAV)."""
    if len(mv) >= 12 and mv[:4] == b"RIFF":
        if mv[8:12] == b"WEBP":
            return "image/webp"
        if mv[8:12] == b"WAVE":
            return "audio/wav"
    return None


def _check_ogg_container(mv: memoryview) -> str | None:
    """Check Ogg container format (Opus, Vorbis, Theora)."""
    if mv[:4] == b"OggS":
        tail = bytes(mv[:64])
        if b"OpusHead" in tail:
            return "audio/opus"
        if b"\x01vorbis" in tail:
            return "audio/vorbis"
        if b"\x80theora" in tail:
            return "video/theora"
        return "application/ogg"
    return None


def _check_iso_bmff(mv: memoryview) -> str | None:
    """Check ISO BMFF format (MP4, AVIF, HEIF) via ftyp brand."""
    if len(mv) >= 12 and mv[4:8] == b"ftyp":
        brand = bytes(mv[8:12])
        mp4_brands = {b"isom", b"iso2", b"mp41", b"mp42", b"MSNV", b"avc1"}
        if brand in mp4_brands:
            return "video/mp4"
        if brand in {b"avif", b"avis"}:
            return "image/avif"
        if brand in {b"heic", b"heix", b"hevc", b"hevx"}:
            return "image/heif"
        return "application/octet-stream"
    return None


# =============================================================================
# Functions
# =============================================================================


def mimetype_sniff(
    buf: BytesLike,
    *,
    max_probe: int = 512,
) -> str | None:
    """
    Best-effort MIME sniffing from magic numbers.

    Returns None if no known signature is found. Only inspects the first
    `max_probe` bytes (default 512). Supports common formats: PNG, JPEG,
    GIF, WebP, PDF, ZIP, GZIP, MP3/ID3, MP4 (ftyp brands), WAV,
    Ogg/Opus/Vorbis, FLAC, AVIF/HEIF.

    Args:
    ----
        buf: Bytes-like object to sniff.
        max_probe: Maximum bytes to inspect. Defaults to 512.

    Returns:
    -------
        str | None: MIME type string or None if unrecognized.
    """
    if not buf:
        return None

    mv = memoryview(buf)[:max_probe]

    result = _check_fixed_signatures(mv)
    if result:
        return result

    result = _check_riff_container(mv)
    if result:
        return result

    result = _check_ogg_container(mv)
    if result:
        return result

    result = _check_iso_bmff(mv)
    if result:
        return result

    return None


# =============================================================================
# Test Classes
# =============================================================================


# class TestMimetypeSniffPNG(unittest.TestCase):
#     """Test PNG image detection."""

#     def test_png_signature(self):
#         """Test PNG magic number detection."""
#         png_header = b"\x89PNG\r\n\x1a\n" + b"\x00" * 100
#         result = mimetype_sniff(png_header)
#         assert result == "image/png"

#     def test_png_complete_signature(self):
#         """Test PNG with typical IHDR chunk."""
#         png_with_ihdr = (
#             b"\x89PNG\r\n\x1a\n"
#             b"\x00\x00\x00\x0dIHDR"
#             b"\x00\x00\x00\x10\x00\x00\x00\x10"
#             b"\x08\x02\x00\x00\x00"
#         )
#         result = mimetype_sniff(png_with_ihdr)
#         assert result == "image/png"

#     def test_png_minimal(self):
#         """Test minimal PNG signature."""
#         result = mimetype_sniff(b"\x89PNG\r\n\x1a\n")
#         assert result == "image/png"


# class TestMimetypeSniffJPEG(unittest.TestCase):
#     """Test JPEG image detection."""

#     def test_jpeg_signature(self):
#         """Test JPEG magic number detection."""
#         jpeg_header = b"\xff\xd8\xff" + b"\xe0" + b"\x00" * 100
#         result = mimetype_sniff(jpeg_header)
#         assert result == "image/jpeg"

#     def test_jpeg_with_jfif(self):
#         """Test JPEG with JFIF marker."""
#         jpeg_jfif = b"\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x00"
#         result = mimetype_sniff(jpeg_jfif)
#         assert result == "image/jpeg"

#     def test_jpeg_with_exif(self):
#         """Test JPEG with EXIF marker."""
#         jpeg_exif = b"\xff\xd8\xff\xe1\x00\x10Exif\x00\x00"
#         result = mimetype_sniff(jpeg_exif)
#         assert result == "image/jpeg"

#     def test_jpeg_minimal(self):
#         """Test minimal JPEG signature."""
#         result = mimetype_sniff(b"\xff\xd8\xff")
#         assert result == "image/jpeg"


# class TestMimetypeSniffGIF(unittest.TestCase):
#     """Test GIF image detection."""

#     def test_gif87a_signature(self):
#         """Test GIF87a magic number detection."""
#         gif87a_header = b"GIF87a" + b"\x00" * 100
#         result = mimetype_sniff(gif87a_header)
#         assert result == "image/gif"

#     def test_gif89a_signature(self):
#         """Test GIF89a magic number detection."""
#         gif89a_header = b"GIF89a" + b"\x00" * 100
#         result = mimetype_sniff(gif89a_header)
#         assert result == "image/gif"

#     def test_gif_with_logical_screen_descriptor(self):
#         """Test GIF with logical screen descriptor."""
#         gif_with_lsd = b"GIF89a\x0a\x00\x0a\x00\x80\x00\x00"
#         result = mimetype_sniff(gif_with_lsd)
#         assert result == "image/gif"


# class TestMimetypeSniffPDF(unittest.TestCase):
#     """Test PDF document detection."""

#     def test_pdf_signature(self):
#         """Test PDF magic number detection."""
#         pdf_header = b"%PDF-1.4\n" + b"test content" * 10
#         result = mimetype_sniff(pdf_header)
#         assert result == "application/pdf"

#     def test_pdf_version_17(self):
#         """Test PDF 1.7 signature."""
#         pdf_header = b"%PDF-1.7\n%\xe2\xe3\xcf\xd3\n"
#         result = mimetype_sniff(pdf_header)
#         assert result == "application/pdf"

#     def test_pdf_version_20(self):
#         """Test PDF 2.0 signature."""
#         pdf_header = b"%PDF-2.0\n"
#         result = mimetype_sniff(pdf_header)
#         assert result == "application/pdf"

#     def test_pdf_minimal(self):
#         """Test minimal PDF signature."""
#         result = mimetype_sniff(b"%PDF-")
#         assert result == "application/pdf"


# class TestMimetypeSniffZIP(unittest.TestCase):
#     """Test ZIP archive detection."""

#     def test_zip_signature(self):
#         """Test ZIP magic number detection."""
#         zip_header = b"PK\x03\x04" + b"\x00" * 100
#         result = mimetype_sniff(zip_header)
#         assert result == "application/zip"

#     def test_zip_with_local_file_header(self):
#         """Test ZIP with local file header structure."""
#         zip_with_header = (
#             b"PK\x03\x04"  # Local file header signature
#             b"\x14\x00"  # Version
#             b"\x00\x00"  # Flags
#             b"\x00\x00"  # Compression method
#         )
#         result = mimetype_sniff(zip_with_header)
#         assert result == "application/zip"


# class TestMimetypeSniffGZIP(unittest.TestCase):
#     """Test GZIP compression detection."""

#     def test_gzip_signature(self):
#         """Test GZIP magic number detection."""
#         gzip_header = b"\x1f\x8b\x08" + b"\x00" * 100
#         result = mimetype_sniff(gzip_header)
#         assert result == "application/gzip"

#     def test_gzip_with_flags(self):
#         """Test GZIP with various flags."""
#         gzip_with_flags = b"\x1f\x8b\x08\x08\x00\x00\x00\x00\x00\x03"
#         result = mimetype_sniff(gzip_with_flags)
#         assert result == "application/gzip"


# class TestMimetypeSniffMP3(unittest.TestCase):
#     """Test MP3 audio detection."""

#     def test_mp3_id3_signature(self):
#         """Test MP3 with ID3 header detection."""
#         id3_header = b"ID3\x03\x00\x00\x00\x00\x00\x00"
#         result = mimetype_sniff(id3_header)
#         assert result == "audio/mpeg"

#     def test_mp3_mpeg_frame_sync(self):
#         """Test MP3 MPEG frame sync detection."""
#         mpeg_sync = b"\xff\xe0" + b"\x00" * 100
#         result = mimetype_sniff(mpeg_sync)
#         assert result == "audio/mpeg"

#     def test_mp3_different_mpeg_versions(self):
#         """Test MP3 with different MPEG frame sync patterns."""
#         # MPEG sync patterns (0xFF followed by 0xEx)
#         for second_byte in [
#             0xE0,
#             0xE2,
#             0xE4,
#             0xE6,
#             0xE8,
#             0xEA,
#             0xEC,
#             0xEE,
#             0xF0,
#         ]:
#             mpeg_sync = bytes([0xFF, second_byte]) + b"\x00" * 100
#             result = mimetype_sniff(mpeg_sync)
#             assert result == "audio/mpeg"


# class TestMimetypeSniffFLAC(unittest.TestCase):
#     """Test FLAC audio detection."""

#     def test_flac_signature(self):
#         """Test FLAC magic number detection."""
#         flac_header = b"fLaC" + b"\x00" * 100
#         result = mimetype_sniff(flac_header)
#         assert result == "audio/flac"

#     def test_flac_with_metadata_block(self):
#         """Test FLAC with STREAMINFO metadata block."""
#         flac_with_metadata = (
#             b"fLaC"  # Magic number
#             b"\x00\x00\x00\x22"  # Metadata block header
#             b"\x00" * 34  # STREAMINFO data (34 bytes)
#         )
#         result = mimetype_sniff(flac_with_metadata)
#         assert result == "audio/flac"


# class TestMimetypeSniffWebP(unittest.TestCase):
#     """Test WebP image detection (RIFF container)."""

#     def test_webp_signature(self):
#         """Test WebP magic number detection."""
#         webp_header = b"RIFF\x00\x00\x00\x00WEBP"
#         result = mimetype_sniff(webp_header)
#         assert result == "image/webp"

#     def test_webp_with_vp8(self):
#         """Test WebP with VP8 chunk."""
#         webp_with_vp8 = b"RIFF\x1a\x00\x00\x00WEBPVP8 "
#         result = mimetype_sniff(webp_with_vp8)
#         assert result == "image/webp"

#     def test_webp_with_vp8l(self):
#         """Test WebP with VP8L (lossless) chunk."""
#         webp_with_vp8l = b"RIFF\x1a\x00\x00\x00WEBPVP8L"
#         result = mimetype_sniff(webp_with_vp8l)
#         assert result == "image/webp"


# class TestMimetypeSniffWAV(unittest.TestCase):
#     """Test WAV audio detection (RIFF container)."""

#     def test_wav_signature(self):
#         """Test WAV magic number detection."""
#         wav_header = b"RIFF\x00\x00\x00\x00WAVE"
#         result = mimetype_sniff(wav_header)
#         assert result == "audio/wav"

#     def test_wav_with_fmt_chunk(self):
#         """Test WAV with fmt chunk."""
#         wav_with_fmt = b"RIFF\x24\x00\x00\x00WAVE" b"fmt \x10\x00\x00\x00"
#         result = mimetype_sniff(wav_with_fmt)
#         assert result == "audio/wav"


# class TestMimetypeSniffOgg(unittest.TestCase):
#     """Test Ogg container and codec detection."""

#     def test_ogg_opus_signature(self):
#         """Test Ogg Opus audio detection."""
#         ogg_opus = b"OggS\x00\x02\x00\x00\x00\x00\x00\x00\x00\x00OpusHead"
#         result = mimetype_sniff(ogg_opus)
#         assert result == "audio/opus"

#     def test_ogg_vorbis_signature(self):
#         """Test Ogg Vorbis audio detection."""
#         ogg_vorbis = b"OggS\x00\x02\x00\x00\x00\x00\x00\x00\x00\x00\x01vorbis"
#         result = mimetype_sniff(ogg_vorbis)
#         assert result == "audio/vorbis"

#     def test_ogg_theora_signature(self):
#         """Test Ogg Theora video detection."""
#         ogg_theora = b"OggS\x00\x02\x00\x00\x00\x00\x00\x00\x00\x00\x80theora"
#         result = mimetype_sniff(ogg_theora)
#         assert result == "video/theora"

#     def test_ogg_generic_signature(self):
#         """Test generic Ogg container without known codec."""
#         ogg_generic = b"OggS\x00\x02\x00\x00\x00\x00\x00\x00\x00\x00unknown"
#         result = mimetype_sniff(ogg_generic)
#         assert result == "application/ogg"

#     def test_ogg_opus_in_middle(self):
#         """Test Ogg Opus with OpusHead marker not at start."""
#         ogg_opus_offset = b"OggS" + b"\x00" * 20 + b"OpusHead" + b"\x00" * 10
#         result = mimetype_sniff(ogg_opus_offset)
#         assert result == "audio/opus"


# class TestMimetypeSniffMP4(unittest.TestCase):
#     """Test MP4 video detection (ISO BMFF)."""

#     def test_mp4_isom_brand(self):
#         """Test MP4 with isom brand."""
#         mp4_isom = b"\x00\x00\x00\x20ftypisom" + b"\x00" * 100
#         result = mimetype_sniff(mp4_isom)
#         assert result == "video/mp4"

#     def test_mp4_iso2_brand(self):
#         """Test MP4 with iso2 brand."""
#         mp4_iso2 = b"\x00\x00\x00\x20ftypiso2" + b"\x00" * 100
#         result = mimetype_sniff(mp4_iso2)
#         assert result == "video/mp4"

#     def test_mp4_mp41_brand(self):
#         """Test MP4 with mp41 brand."""
#         mp4_mp41 = b"\x00\x00\x00\x20ftypmp41" + b"\x00" * 100
#         result = mimetype_sniff(mp4_mp41)
#         assert result == "video/mp4"

#     def test_mp4_mp42_brand(self):
#         """Test MP4 with mp42 brand."""
#         mp4_mp42 = b"\x00\x00\x00\x20ftypmp42" + b"\x00" * 100
#         result = mimetype_sniff(mp4_mp42)
#         assert result == "video/mp4"

#     def test_mp4_avc1_brand(self):
#         """Test MP4 with avc1 brand."""
#         mp4_avc1 = b"\x00\x00\x00\x20ftypavc1" + b"\x00" * 100
#         result = mimetype_sniff(mp4_avc1)
#         assert result == "video/mp4"

#     def test_mp4_msnv_brand(self):
#         """Test MP4 with MSNV brand."""
#         mp4_msnv = b"\x00\x00\x00\x20ftypMSNV" + b"\x00" * 100
#         result = mimetype_sniff(mp4_msnv)
#         assert result == "video/mp4"


# class TestMimetypeSniffAVIF(unittest.TestCase):
#     """Test AVIF image detection (ISO BMFF)."""

#     def test_avif_brand(self):
#         """Test AVIF with avif brand."""
#         avif_header = b"\x00\x00\x00\x20ftypavif" + b"\x00" * 100
#         result = mimetype_sniff(avif_header)
#         assert result == "image/avif"

#     def test_avif_sequence_brand(self):
#         """Test AVIF with avis (sequence) brand."""
#         avif_sequence = b"\x00\x00\x00\x20ftypavis" + b"\x00" * 100
#         result = mimetype_sniff(avif_sequence)
#         assert result == "image/avif"


# class TestMimetypeSniffHEIF(unittest.TestCase):
#     """Test HEIF/HEIC image detection (ISO BMFF)."""

#     def test_heic_brand(self):
#         """Test HEIC with heic brand."""
#         heic_header = b"\x00\x00\x00\x20ftypheic" + b"\x00" * 100
#         result = mimetype_sniff(heic_header)
#         assert result == "image/heif"

#     def test_heix_brand(self):
#         """Test HEIF with heix brand."""
#         heix_header = b"\x00\x00\x00\x20ftypheix" + b"\x00" * 100
#         result = mimetype_sniff(heix_header)
#         assert result == "image/heif"

#     def test_hevc_brand(self):
#         """Test HEIF with hevc brand."""
#         hevc_header = b"\x00\x00\x00\x20ftyphevc" + b"\x00" * 100
#         result = mimetype_sniff(hevc_header)
#         assert result == "image/heif"

#     def test_hevx_brand(self):
#         """Test HEIF with hevx brand."""
#         hevx_header = b"\x00\x00\x00\x20ftyphevx" + b"\x00" * 100
#         result = mimetype_sniff(hevx_header)
#         assert result == "image/heif"


# class TestMimetypeSniffUnknownBMFF(unittest.TestCase):
#     """Test unknown ISO BMFF brands."""

#     def test_unknown_ftyp_brand(self):
#         """Test ISO BMFF with unknown brand."""
#         unknown_bmff = b"\x00\x00\x00\x20ftypunko" + b"\x00" * 100
#         result = mimetype_sniff(unknown_bmff)
#         assert result == "application/octet-stream"

#     def test_ftyp_with_qt_brand(self):
#         """Test ISO BMFF with QuickTime brand."""
#         qt_header = b"\x00\x00\x00\x20ftypqt  " + b"\x00" * 100
#         result = mimetype_sniff(qt_header)
#         assert result == "application/octet-stream"


# class TestMimetypeSniffEdgeCases(unittest.TestCase):
#     """Test edge cases and boundary conditions."""

#     def test_empty_buffer(self):
#         """Test with empty buffer."""
#         result = mimetype_sniff(b"")
#         assert result is None

#     def test_none_buffer(self):
#         """Test with None-like empty buffer."""
#         result = mimetype_sniff(b"")
#         assert result is None

#     def test_very_short_buffer(self):
#         """Test with very short buffer (1 byte)."""
#         result = mimetype_sniff(b"\x00")
#         assert result is None

#     def test_two_byte_buffer(self):
#         """Test with two-byte buffer."""
#         result = mimetype_sniff(b"\x00\x00")
#         assert result is None

#     def test_unknown_signature(self):
#         """Test with unknown signature."""
#         unknown = b"UNKN\x00\x00\x00\x00" + b"\x00" * 100
#         result = mimetype_sniff(unknown)
#         assert result is None

#     def test_max_probe_parameter(self):
#         """Test max_probe parameter limits inspection."""
#         # PNG signature at start
#         png_at_start = b"\x89PNG\r\n\x1a\n" + b"\x00" * 1000
#         result = mimetype_sniff(png_at_start, max_probe=512)
#         assert result == "image/png"

#     def test_max_probe_short(self):
#         """Test very short max_probe."""
#         png_header = b"\x89PNG\r\n\x1a\n" + b"\x00" * 100
#         # Even with short max_probe, PNG should be detected (needs 8 bytes)
#         result = mimetype_sniff(png_header, max_probe=10)
#         assert result == "image/png"

#     def test_max_probe_insufficient_for_ogg_codec(self):
#         """Test Ogg detection with insufficient probe length for codec."""
#         ogg_short = b"OggS\x00\x02"  # Only OggS signature, no codec marker
#         result = mimetype_sniff(ogg_short, max_probe=6)
#         assert result == "application/ogg"  # Falls back to generic ogg

#     def test_bytearray_input(self):
#         """Test with bytearray instead of bytes."""
#         png_bytearray = bytearray(b"\x89PNG\r\n\x1a\n")
#         result = mimetype_sniff(png_bytearray)
#         assert result == "image/png"

#     def test_memoryview_input(self):
#         """Test with memoryview input."""
#         png_bytes = b"\x89PNG\r\n\x1a\n"
#         png_memoryview = memoryview(png_bytes)
#         result = mimetype_sniff(png_memoryview)
#         assert result == "image/png"

#     def test_large_buffer_with_signature(self):
#         """Test with large buffer containing signature."""
#         large_buffer = b"\xff\xd8\xff" + (b"\x00" * 10000)
#         result = mimetype_sniff(large_buffer)
#         assert result == "image/jpeg"


# class TestMimetypeSniffRIFFEdgeCases(unittest.TestCase):
#     """Test RIFF container edge cases."""

#     def test_riff_insufficient_length(self):
#         """Test RIFF with insufficient length for type identification."""
#         riff_short = b"RIFF\x00\x00\x00\x00"  # Only 8 bytes, no type
#         result = mimetype_sniff(riff_short)
#         assert result is None

#     def test_riff_unknown_type(self):
#         """Test RIFF with unknown type."""
#         riff_unknown = b"RIFF\x00\x00\x00\x00UNKN"
#         result = mimetype_sniff(riff_unknown)
#         assert result is None

#     def test_riff_almost_webp(self):
#         """Test RIFF with typo in WebP identifier."""
#         riff_typo = b"RIFF\x00\x00\x00\x00WEBQ"  # WEBQ instead of WEBP
#         result = mimetype_sniff(riff_typo)
#         assert result is None


# class TestMimetypeSniffMPEGFrameSyncVariants(unittest.TestCase):
#     """Test MPEG frame sync pattern edge cases."""

#     def test_mpeg_sync_boundary_low(self):
#         """Test MPEG sync at lower boundary (0xE0)."""
#         mpeg_sync = b"\xff\xe0"
#         result = mimetype_sniff(mpeg_sync)
#         assert result == "audio/mpeg"

#     def test_mpeg_sync_boundary_high(self):
#         """Test MPEG sync at upper boundary (0xFF)."""
#         mpeg_sync = b"\xff\xff"
#         result = mimetype_sniff(mpeg_sync)
#         assert result == "audio/mpeg"

#     def test_mpeg_sync_just_below_threshold(self):
#         """Test byte just below MPEG sync threshold (0xDF)."""
#         not_mpeg = b"\xff\xdf"
#         result = mimetype_sniff(not_mpeg)
#         assert result is None

#     def test_single_ff_byte(self):
#         """Test single 0xFF byte without second byte."""
#         single_byte = b"\xff"
#         result = mimetype_sniff(single_byte)
#         assert result is None


# =============================================================================
# Exports
# =============================================================================

__all__: list[str] = ["mimetype_sniff"]
