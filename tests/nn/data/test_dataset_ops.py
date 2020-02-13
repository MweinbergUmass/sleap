import numpy as np
import tensorflow as tf

tf.config.experimental.set_visible_devices([], device_type="GPU")  # hide GPUs for test

from sleap.nn.data import dataset_ops


def test_batcher():
    ds = tf.data.Dataset.from_tensors({"a": tf.reshape(tf.range(3 * 2), [3, 2])})
    ds = ds.unbatch()

    batcher = dataset_ops.Batcher(batch_size=2, drop_remainder=False)
    ds_batched = batcher.transform_dataset(ds)
    examples = list(iter(ds_batched))
    np.testing.assert_array_equal(examples[0]["a"], [[0, 1], [2, 3]])
    np.testing.assert_array_equal(examples[1]["a"], [[4, 5]])

    batcher = dataset_ops.Batcher(batch_size=2, drop_remainder=True)
    ds_batched = batcher.transform_dataset(ds)
    examples = list(iter(ds_batched))
    np.testing.assert_array_equal(examples[0]["a"], [[0, 1], [2, 3]])
    assert len(examples) == 1

    # Ragged batch
    ds = tf.data.Dataset.range(2)
    ds = ds.map(lambda i: {"a": tf.ones([2 + i, 2], tf.float32)})
    examples_gt = list(iter(ds))
    assert len(examples_gt) == 2
    assert examples_gt[0]["a"].shape == (2, 2)
    assert examples_gt[1]["a"].shape == (3, 2)

    ds_batched = dataset_ops.Batcher(batch_size=2).transform_dataset(ds)
    examples_batched = list(iter(ds_batched))
    assert len(examples_batched) == 1
    assert examples_batched[0]["a"].shape == (2, 3, 2)
    assert np.isnan(examples_batched[0]["a"][0, 2, :]).all()


def test_preloader():
    preloader = dataset_ops.Preloader()
    ds = tf.data.Dataset.from_tensors({"a": tf.range(3)}).unbatch()
    ds = preloader.transform_dataset(ds)

    np.testing.assert_array_equal(preloader.examples, [{"a": 0}, {"a": 1}, {"a": 2}])
    np.testing.assert_array_equal(list(iter(ds)), [{"a": 0}, {"a": 1}, {"a": 2}])
