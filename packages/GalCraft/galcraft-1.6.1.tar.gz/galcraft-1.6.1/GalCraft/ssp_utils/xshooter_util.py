import glob, re

import numpy as np
from scipy import interpolate
from astropy.io import fits


def age_metal(filename):
    """
    Extract age (T) and metallicity (Z or MH) values from the given filename.
    Supports formats:
    - 'XSL_SSP_logT<logT>_MH<MH>_Kroupa_PC.fits'
    - 'XSL_SSP_T<age>_Z<Z>_Kroupa_P00.fits'
    """
    pattern1 = r'XSL_SSP_logT(?P<logT>[-+]?[0-9]*\.?[0-9]+)_MH(?P<MH>[-+]?[0-9]*\.?[0-9]+)_.+\.fits'
    pattern2 = r'XSL_SSP_T(?P<T>[-+]?[0-9]*\.?[0-9]+e?[+-]?[0-9]*)_Z(?P<Z>[-+]?[0-9]*\.?[0-9]+)_.+\.fits'

    match1 = re.search(pattern1, filename)
    match2 = re.search(pattern2, filename)

    if match1:
        return 10 ** float(match1.group('logT')) / 1e9, float(match1.group('MH'))
    elif match2:
        return float(match2.group('T')) / 1e9, float(match2.group('Z'))
    else:
        return None


class ssp:

    def __init__(self, path_library, FWHM_tem='lsf_xshooter',
                 age_range=None, metal_range=None, alpha_range=None):

        files = glob.glob(path_library)
        assert len(files) > 0, "Files not found %s" % path_library

        # Read data
        hdu = fits.open(files[0])
        ssp = hdu[0].data
        h2 = hdu[0].header
        lam = 10 ** (h2['CRVAL1'] + np.arange(h2['NAXIS1']) * h2['CDELT1']) * 10

        # Extract ages, metallicities and alpha from the templates
        all = [age_metal(f) for f in files]
        all_ages, all_metals = np.array(all).T
        ages, metals = np.unique(all_ages), np.unique(all_metals)
        alphas = np.array([0])
        nAges, nMetal, nAlpha = len(ages), len(metals), len(alphas)

        # Arrays to store templates
        templates          = np.zeros((ssp.size, nAges, nMetal, nAlpha))
        templates[:,:,:,:] = np.nan

        # Arrays to store properties of the models
        age_grid    = np.empty((nAges, nMetal, nAlpha))
        metal_grid  = np.empty((nAges, nMetal, nAlpha))
        alpha_grid  = np.empty((nAges, nMetal, nAlpha))

        # Determine the flux factor
        if '_KU_' in files[0]:
            flux_factor = 5567946.09
        elif '_SA_' in files[0]:
            flux_factor = 9799552.50
        else:
            raise ValueError('initial-mass function is unknown, can not calculate flux unit factor')

        # This sorts for ages
        for j, age in enumerate(ages):
            # This sorts for metals
            for k, mh in enumerate(metals):
                p = all.index((age, mh))
                hdu = fits.open(files[p])
                ssp = hdu[0].data
                age_grid[j, k, 0] = age
                metal_grid[j, k, 0] = mh
                alpha_grid[j, k, 0] = alphas[0]
                templates[:, j, k, 0] = ssp

        # Interpolate templates into linear wave grid
        new_wave = np.arange(lam[0], lam[-1], np.min(np.diff(lam)))
        new_templates = np.zeros([len(new_wave), templates.shape[1], templates.shape[2], templates.shape[3]])
        for i in range(templates.shape[1]):
            for j in range(templates.shape[2]):
                interpolator = interpolate.interp1d(lam, templates[:, i, j, 0])
                new_templates[:, i, j, 0] = interpolator(new_wave)
        new_templates = new_templates * flux_factor

        lam = new_wave
        templates = new_templates
        new_wave = None
        new_templates = None

        if age_range is not None:
            w = (age_range[0] <= age_grid[:, 0, 0]) & (age_grid[:, 0, 0] <= age_range[1])
            templates = templates[:, w, :, :]
            age_grid = age_grid[w, :, :]
            metal_grid = metal_grid[w, :, :]
            alpha_grid = alpha_grid[w, :, :]
            nAges, nMetal, nAlpha = age_grid.shape

        if metal_range is not None:
            w = (metal_range[0] <= metal_grid[0, :, 0]) & (metal_grid[0, :, 0] <= metal_range[1])
            templates = templates[:, :, w, :]
            age_grid = age_grid[:, w, :]
            metal_grid = metal_grid[:, w, :]
            alpha_grid = alpha_grid[:, w, :]
            nAges, nMetal, nAlpha = age_grid.shape

        if alpha_range is not None:
            w = (alpha_range[0] <= alpha_grid[0, 0, :]) & (alpha_grid[0, 0, :] <= alpha_range[1])
            templates = templates[:, :, :, w]
            age_grid = age_grid[:, :, w]
            metal_grid = metal_grid[:, :, w]
            alpha_grid = alpha_grid[:, :, w]
            nAges, nMetal, nAlpha = age_grid.shape

        self.templates = templates
        self.lam_temp = lam
        self.age_grid = age_grid
        self.metal_grid = metal_grid
        self.alpha_grid = alpha_grid
        self.n_ages = nAges
        self.n_metal = nMetal
        self.n_alpha = nAlpha
        self.FWHM_tem = FWHM_tem
