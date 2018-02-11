"""Tests for ``$ rio ds-mask`` plugin."""


import numpy as np
import rasterio as rio
from rasterio.enums import Compression
from rasterio.rio.main import main_group as rio_main

from rio_ds_mask import _norm_gdal_mask, rio_ds_mask


def test_compare_rasterio_dataset_mask(
        path_alpha_tif, path_alpha_16bit_tif, runner, tmpdir):

    """Compare against Rasterio's ``src.dataset_mask()``."""

    outfile = str(tmpdir.join('compare_rasterio_dataset_mask.tif'))

    for path in (path_alpha_tif, path_alpha_16bit_tif):
        with rio.open(path) as src:
            expected = _norm_gdal_mask(src.dataset_mask(), src.dtypes)

        result = runner.invoke(rio_ds_mask, [
            path, outfile,
            '--co', 'COMPRESS=DEFLATE'])

        assert result.exit_code == 0

        with rio.open(outfile) as src:
            assert src.compression == Compression.deflate
            assert not src.is_tiled
            actual = src.read(1)

        assert np.array_equal(expected, actual)


def test_dtype(runner, tmpdir, path_alpha_16bit_tif):

    """Set output datatype and driver."""

    outfile = str(tmpdir.join('test_dtype_driver.jpg'))

    result = runner.invoke(rio_ds_mask, [
        path_alpha_16bit_tif, outfile,
        '--dtype', 'uint8',
        '--driver', 'JPEG'])

    assert result.exit_code == 0, result.output

    with rio.open(outfile) as src:
        assert src.dtypes[0] == rio.uint8
        assert src.driver == 'JPEG'


def test_16bit_uses_255(runner, tmpdir, path_alpha_16bit_tif):

    """For 16 bit images GDAL produces masks with transparent values as 1's
    rather than 255's.  Verify this plugin is translating those values to
    255's.
    """

    outfile = str(tmpdir.join('test_16bit_uses_255.tif'))

    result = runner.invoke(rio_ds_mask, [
        path_alpha_16bit_tif, outfile])
    assert result.exit_code == 0

    with rio.open(outfile) as src:
        mask = src.read(1)
        assert mask.dtype == np.uint8
        assert mask.min() == 0
        assert mask.max() == 255


def test_plugin_registered(runner):

    """Make sure plugin is registered."""

    result = runner.invoke(rio_main, ['--help'])
    assert result.exit_code == 0
    assert 'ds-mask' in result.output
    assert rio_ds_mask.short_help in result.output
