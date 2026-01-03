from collections.abc import Callable
import numpy as np
import scipy
from tqdm.auto import tqdm

from .recording import Recording
from .processing import _get_spectral_function_from_name
from .constants import CLASSIC_BANDWIDTHS
from .errors import BreesyError, BreesyInternalError, protect_from_lib_error
from .type_hints import enforce_type_hints


@enforce_type_hints
def get_mean_power(epochs: np.ndarray, freq_range: str | tuple[int | float, int | float],
                   sample_rate: int | float, method: str = 'welch') -> np.ndarray:
    """Extract mean power of a given frequency range from epoched EEG data.

    :param epochs: 3D array of epoched data (n_epochs, n_channels, n_samples)
    :param sample_rate: Sampling rate in Hz
    :param freq_range: Either a name of a classical band (e.g. "alpha"), or a frequency range (low, high) in Hz
    :param method: The method to determine the spectral function used to extract features; such as "welch" (faster, default) or "periodogram" (has better resolution)

    :return: 1D array of mean power values for each epoch
    """

    # TODO: instead of np.ndarray, epochs should be Recording type

    if isinstance(freq_range, str):
        freq_range = _get_freq_range_from_name(band_name=freq_range)

    spectral_func = _get_spectral_function_from_name(method)
    mean_power = _get_power_feature(epochs=epochs, freq_range=freq_range, sample_rate=sample_rate,
                                    spectral_func=spectral_func, mode='mean')
    return mean_power


@enforce_type_hints
def get_mean_power_per_channel(epochs: np.ndarray,
                               freq_range: str | tuple[int | float, int | float],
                               sample_rate: int | float,
                               method: str = 'welch') -> np.ndarray:
    """Extract mean power per channel of a given frequency range from epoched EEG data.

    :param epochs: 3D array of epoched data (n_epochs, n_channels, n_samples)
    :param sample_rate: Sampling rate in Hz
    :param freq_range: Either a name of a classical band (e.g. "alpha"), or a frequency range (low, high) in Hz
    :param method: The method to determine the spectral function used to extract features; such as "welch" (faster, default) or "periodogram" (has better resolution)

    :return: 2D array of mean power values with shape (n_epochs, n_channels)
    """
    if isinstance(freq_range, str):
        freq_range = _get_freq_range_from_name(band_name=freq_range)

    spectral_func = _get_spectral_function_from_name(method)
    mean_power_per_channel = _get_power_feature(
        epochs=epochs,
        freq_range=freq_range,
        sample_rate=sample_rate,
        spectral_func=spectral_func,
        mode='mean',
        per_channel=True
    )
    return mean_power_per_channel


@enforce_type_hints
def get_normalized_covariance_matrix(epochs: list[Recording]) -> np.ndarray:
    """Compute normalized covariance matrix from epoched EEG data.

    :param epochs: List of Recording objects representing one epoched Recording data

    :return: Normalized covariance matrix of shape (n_channels, n_channels)
    """
    if not epochs:
        raise BreesyError(
            "Cannot compute covariance from an empty list of epochs.",
            "Make sure that the epochs list is not empty. "
        )

    n_channels = epochs[0].number_of_channels
    for i, epoch in enumerate(epochs):
        if epoch.number_of_channels != n_channels:
            raise BreesyError(
                f"All epochs must have the same number of channels. "
                f"Epoch 0 has {n_channels} channels, but epoch {i} has {epoch.number_of_channels} channels.",
                "Ensure all epochs come from the same recording."
            )

    eeg_data = np.array([epoch.data for epoch in epochs])

    cov = []
    for i in range(eeg_data.shape[0]):
        epoch_cov = eeg_data[i] @ eeg_data[i].T
        cov.append(epoch_cov / np.trace(epoch_cov))

    return np.mean(np.array(cov), axis=0)


@enforce_type_hints
def get_csp_features(spatial_filter: np.ndarray, epochs: list[Recording], n_components: int = 2) -> np.ndarray:
    """Extract CSP features from epochs using a spatial filter.

    :param spatial_filter: Spatial filter matrix from get_spatial_filter_from_covariances()
    :param epochs: List of Recording objects representing epoched data
    :param n_components: Number of CSP components to use (default: 2, uses first and last n_components)

    :return: Feature matrix of shape (n_epochs, 2*n_components) containing log-variance features
    """
    if not epochs:
        raise BreesyError(
            "Cannot extract features from an empty list of epochs.",
            "Make sure that the epochs list is not empty."
        )

    if n_components < 1:
        raise BreesyError(
            f"n_components must be at least 1, got {n_components}.",
            "Set n_components to a positive integer (typically 2-4 for CSP)."
        )

    n_channels = epochs[0].number_of_channels
    if spatial_filter.shape[1] != n_channels:
        raise BreesyError(
            f"Spatial filter has {spatial_filter.shape[1]} columns but epochs have {n_channels} channels.",
            "Ensure the spatial filter was computed from epochs with the same number of channels."
        )

    # Stack epochs into 3D array
    eeg_data = np.array([epoch.data for epoch in epochs])

    return _get_Z_features(spatial_filter, eeg_data, n_components)

@enforce_type_hints
def get_spatial_filter_from_covariances(cov_class1: np.ndarray, cov_class2: np.ndarray) -> np.ndarray:
    """Compute spatial filter from two class covariance matrices using CSP.

    :param cov_class1: Covariance matrix for class 1 (e.g., left hand imagery)
    :param cov_class2: Covariance matrix for class 2 (e.g., right hand imagery)

    :return: Spatial filter matrix W of shape (n_channels, n_channels)
    """
    if cov_class1.shape != cov_class2.shape:
        raise BreesyError(
            f"Covariance matrices must have the same shape. "
            f"Got {cov_class1.shape} and {cov_class2.shape}.",
            "Ensure both classes have the same number of channels."
        )

    if cov_class1.ndim != 2 or cov_class1.shape[0] != cov_class1.shape[1]:
        raise BreesyError(
            f"Covariance matrices must be square 2D arrays. Got shape {cov_class1.shape}.",
            "Use get_normalized_covariance_matrix() to compute covariance matrices from epochs."
        )

    # decompose covariance matrices
    cov_comp = cov_class1 + cov_class2
    eigval, eigvec = _decompose_cov(cov_comp)

    # get whitening matrix
    P = _white_matrix(eigval, eigvec)

    # get and decompose S matrix
    s_left = _compute_S(cov_class1, P)
    s_left_eigvec, _ = _decompose_S(s_left, order='descending')

    # getting spatial filter W - we only need one of two!
    W = _spatial_filter(s_left_eigvec, P)

    return W


@protect_from_lib_error("numpy")
def _get_power_feature(epochs: np.ndarray, freq_range: tuple[int | float, int | float],
                       sample_rate: int | float, spectral_func: Callable, mode: str, per_channel: bool = False) -> np.ndarray:
    axis = None
    if per_channel:
        axis = -1

    # TODO: vectorize
    power_feature = []
    epoch_iter = tqdm(epochs, desc="Processing epochs", disable=len(epochs) < 10)

    for epoch in epoch_iter:
        spectral_piece = _get_spectral_epoch_piece(epoch=epoch, freq_range=freq_range, spectral_func=spectral_func, sample_rate=sample_rate)

        if mode == 'mean':
            result = np.mean(spectral_piece, axis=axis)
        elif mode == 'max':
            result = np.max(spectral_piece, axis=axis)
        else:
            raise BreesyInternalError(f'Aggregation mode "{mode}" is not supported.', ex=None)

        power_feature.append(result)

    return np.array(power_feature)

@protect_from_lib_error("numpy")
def _get_spectral_epoch_piece(epoch: np.ndarray, freq_range: tuple[int | float, int | float], spectral_func: Callable,
                              sample_rate: int | float):
    freqs, spectral = spectral_func(epoch, sample_rate=sample_rate)
    start_idx = np.searchsorted(freqs, freq_range[0])
    end_idx = np.searchsorted(freqs, freq_range[1])
    return spectral[:, start_idx:end_idx]


def _get_freq_range_from_name(band_name: str) -> tuple[int | float, int | float]:
    if band_name in CLASSIC_BANDWIDTHS.keys():
        return CLASSIC_BANDWIDTHS[band_name]
    else:
        supported_bands_str = ', '.join(f'"{x}"' for x in [CLASSIC_BANDWIDTHS.keys()])
        raise BreesyError(f'The provided name of the band - "{band_name}" - is unknown to Breesy.',
                            f"Use one of supported names: {supported_bands_str} "
                            'or provide frequency range as two numbers: (low, high).')


@protect_from_lib_error("numpy")
def _decompose_cov(avg_cov: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    lam, V = np.linalg.eig(avg_cov)
    lam_dsc = np.sort(lam)[::-1] # Sort eigenvalue descending order, default is ascending order sort
    idx_dsc = np.argsort(lam)[::-1] # Find index in descending order
    V_dsc = V[:, idx_dsc] # Sort eigenvectors descending order
    lam_dsc = np.diag(lam_dsc) # Diagonalize lam_dsc
    return lam_dsc, V_dsc


@protect_from_lib_error("scipy")
def _white_matrix(lam_dsc: np.ndarray, V_dsc: np.ndarray) -> np.ndarray:
    inv = scipy.linalg.inv(lam_dsc)
    lam_dsc_sqr = scipy.linalg.sqrtm(inv)
    return lam_dsc_sqr @ V_dsc.T


@protect_from_lib_error("numpy")
def _compute_S(avg_cov: np.ndarray, white: np.ndarray) -> np.ndarray:
    return white @ avg_cov @ white.T


@protect_from_lib_error("numpy")
def _decompose_S(S_one_class: np.ndarray, order: str = 'descending') -> tuple[np.ndarray, np.ndarray]:
    # Decompose S
    lam, B = np.linalg.eig(S_one_class)
    # Sort eigenvalues either descending or ascending
    if order == 'ascending':
        idx = lam.argsort()
    else:
        idx = lam.argsort()[::-1]
    return B[:, idx], lam[idx]


@protect_from_lib_error("numpy")
def _spatial_filter(B: np.ndarray, P: np.ndarray) -> np.ndarray:
    return B.T @ P

def _get_Z_features(spatial_filter, epochs_stacked, n_components: int) -> np.ndarray:
  Z = _compute_Z(spatial_filter, epochs_stacked, n_components)
  return _feat_vector(Z)


@protect_from_lib_error("numpy")
def _compute_Z(W: np.ndarray, E: np.ndarray, m: int) -> np.ndarray:
    Z = []
    W = np.delete(W, np.s_[m:-m:], 0)
    for i in range(E.shape[0]):
        Z.append(W @ E[i])
    return np.array(Z)


@protect_from_lib_error("numpy")
def _feat_vector(Z: np.ndarray) -> np.ndarray:
    feat = []
    for i in range(Z.shape[0]):
        var = np.var(Z[i], ddof=1, axis=1)
        varsum = np.sum(var)
        feat.append(np.log10(var / varsum))
    return np.array(feat)