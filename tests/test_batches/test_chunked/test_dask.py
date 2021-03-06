import pytest

import numpy as np

from timeserio.data.mock import mock_dask_fit_data
from timeserio.batches.chunked.dask import (SequenceForecastBatchGenerator)


class TestSequenceForecastBatchGeneratorMultiID:
    @pytest.mark.parametrize('n_customers', [
        1,
        2,
        3,
        4,
        5,
    ])
    def test_n_subgens(self, n_customers):
        ids = np.arange(n_customers)
        periods = 4
        ddf = mock_dask_fit_data(periods=periods, ids=ids)
        generator = SequenceForecastBatchGenerator(
            ddf=ddf,
            sequence_length=2,
            forecast_steps_max=1,
            batch_size=2 ** 10,
        )
        assert len(generator.chunks) == n_customers
        assert len(generator.subgen_lengths) == n_customers
        assert len(generator.subgen_index_bounds) == n_customers + 1

    @pytest.mark.parametrize('n_customers', [
        1,
        2,
    ])
    @pytest.mark.parametrize(
        'batch_size, exp_sg_len', [
            (1, 2),
            (2 ** 10, 1),
        ]
    )
    def test_subgen_lengths(self, n_customers, batch_size, exp_sg_len):
        n_customers = 3
        ids = np.arange(n_customers)
        ddf = mock_dask_fit_data(periods=3, ids=ids)
        generator = SequenceForecastBatchGenerator(
            ddf=ddf,
            sequence_length=1,
            forecast_steps_max=1,
            batch_size=batch_size,
        )
        assert all(sgl == exp_sg_len for sgl in generator.subgen_lengths)

    @pytest.mark.parametrize(
        'batch_size, batch_idx, exp_subgen_idx, exp_idx_in_subgen', [
            (1, 0, 0, 0),
            (1, 1, 0, 1),
            (1, 2, 1, 0),
            (1, 3, 1, 1),
            (2 ** 10, 0, 0, 0),
            (2 ** 10, 1, 1, 0),
            (2 ** 10, 2, 2, 0),
        ]
    )
    def test_find_batch_in_subgens(
        self, batch_size, batch_idx, exp_subgen_idx, exp_idx_in_subgen
    ):
        n_customers = 3
        ids = np.arange(n_customers)
        ddf = mock_dask_fit_data(periods=3, ids=ids)
        generator = SequenceForecastBatchGenerator(
            ddf=ddf,
            sequence_length=1,
            forecast_steps_max=1,
            batch_size=batch_size,
        )
        subgen_idx, idx_in_subgen = generator.find_subbatch_in_subgens(
            batch_idx
        )
        assert subgen_idx == exp_subgen_idx
        assert idx_in_subgen == exp_idx_in_subgen

    def test_find_batch_raises_outside_subgens(self):
        n_customers = 3
        ids = np.arange(n_customers)
        ddf = mock_dask_fit_data(periods=3, ids=ids)
        generator = SequenceForecastBatchGenerator(
            ddf=ddf,
            sequence_length=1,
            forecast_steps_max=1,
            batch_size=2 ** 10,
        )
        batch_idx = 2 ** 10
        with pytest.raises(IndexError):
            generator.find_subbatch_in_subgens(batch_idx)

    def test_aggregate_ids(self):
        n_customers = 2
        ids = np.arange(n_customers)
        ddf = mock_dask_fit_data(periods=3, ids=ids)
        generator = SequenceForecastBatchGenerator(
            ddf=ddf,
            sequence_length=2,
            forecast_steps_max=1,
            batch_size=2,
            batch_aggregator=2
        )
        assert len(generator) == 1
        batch = generator[0]
        assert len(batch) == 2
