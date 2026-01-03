from collections.abc import Callable
import numpy as np
from tqdm.auto import tqdm

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


