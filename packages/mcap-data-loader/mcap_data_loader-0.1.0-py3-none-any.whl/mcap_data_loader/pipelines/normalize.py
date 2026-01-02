from pydantic import BaseModel, ConfigDict, field_validator, field_serializer
from weakref import WeakValueDictionary
from mcap_data_loader.utils.array_like import Array
from mcap_data_loader.utils.basic import (
    ForceSetAttr,
    DictDataStamped,
    copy_dict_data_stamped,
)
from mcap_data_loader.utils.extra_itertools import (
    recursive_map_reusable,
    first_recursive,
)
from mcap_data_loader.pipelines.basis import Pipe, T
from typing import Optional, Dict, Set, Generic, TypeVar
from collections.abc import Mapping, Sequence, Iterable


StatValueT = TypeVar("StatValueT", bound=Array)
StatisticsT = Optional[Dict[str, StatValueT]]


class NormalizeConfigBasis(BaseModel, Generic[StatValueT], frozen=True):
    model_config = ConfigDict(extra="forbid", validate_assignment=True)

    name: str = ""
    """Unique name of the pipeline. Used for caching configs as the default values."""
    statistics: StatisticsT[StatValueT] = None
    """Statistic values corresponding to each key."""
    inverse: bool = False
    """Whether to perform inverse normalization."""
    include: Set[str] = set()
    """List of keys to include for normalization. If empty, all keys are included."""
    exclude: Set[str] = set()
    """List of keys to exclude from normalization."""
    depth: int = 0
    """Depth of recursion for nested iterable. 0 means no recursion.
    < 0 means recursion until a `Mapping` is encountered."""
    replace: bool = False
    """Whether to replace the original values with normalized values."""
    strict: bool = True
    """Whether to raise an error if a specified key is not found in the data item."""


ConfigT = TypeVar("ConfigT", bound=NormalizeConfigBasis)


class NormalizeBasis(Pipe[DictDataStamped[T]], Generic[StatValueT, T]):
    _configs: WeakValueDictionary[str, ConfigT] = WeakValueDictionary()

    def __init__(self, config: NormalizeConfigBasis[StatValueT]):
        self.config = config

    def _prepare_stats(self, iterable):
        config = self.config
        name = config.name
        if name in self._configs:
            self.get_logger().info("Reusing existing config for name: %s", name)
            update = {}
            for field in config.model_fields_set - {"name"}:
                update[field] = getattr(config, field)
            config = self._configs[name].model_copy(update=update)
            self.get_logger().info("Reused config fields: %s", update.keys())
        else:
            self._configs[name] = config
        config: ConfigT
        self.config = config
        if config.statistics is None:
            self._process_none_stat(iterable)
        # TODO: The implicit type hint for statistics based on the `config` is incorrect in the subclass, so we explicitly declare it here. This requires an additional generic parameter to be passed in when defining the subclass. Perhaps we can find a better way later.
        self._statistics = config.statistics
        self._replace = config.replace
        self._inverse = config.inverse

    def _process_none_stat(self, iterable):
        method = "statistics"
        if hasattr(iterable, method):
            with ForceSetAttr(self.config) as cfg:
                cfg.statistics = getattr(iterable, method)()
        else:
            raise ValueError(
                "The `statistics` field must be provided in the config or "
                "the iterable must have a `statistics` method: "
                f"{iterable=}, iterable_type={type(iterable)}"
            )

    def transform(self, item: DictDataStamped) -> DictDataStamped:
        return self.on_transform(item, self._statistics, self._inverse)

    def on_transform(
        self, item: DictDataStamped, statistics: StatisticsT[StatValueT], inverse: bool
    ) -> DictDataStamped:
        return item


class MeanStd(BaseModel, frozen=True):
    """Class to hold mean and standard deviation values."""

    model_config = ConfigDict(validate_assignment=True, extra="allow")

    mean: Optional[Array]
    """Mean value for standardization."""
    std: Optional[Array]
    """Standard deviation for standardization."""

    @field_validator("mean", "std", mode="before")
    def validate_mean_std(cls, v):
        if isinstance(v, Sequence):
            import numpy as np

            return np.array(v)
        return v

    @field_serializer("mean", "std", when_used="json")
    def serialize_mean_std(self, v: Optional[Array]) -> Optional[list]:
        if v is not None:
            return v.tolist()
        return v


class StandardizeConfig(NormalizeConfigBasis[MeanStd]):
    """Configuration for Standardize pipeline."""


class Standardize(NormalizeBasis[MeanStd, T]):
    # class Transform:
    #     def __init__(self):
    #         self._first_call = True

    #     def __call__(self, iterable: Iterable[dict]):

    #     def __iter__(self):
    #         for item in iterable:
    #             yield self._transform(item)

    def __init__(self, config: StandardizeConfig):
        self.config = config

    def on_transform(self, item, statistics, inverse) -> DictDataStamped:
        """Transform a single data item by standardizing or inverse standardizing specified keys."""
        new_item = item if self._replace else copy_dict_data_stamped(item)
        for key in self._used_keys:
            stat = statistics[key]
            mean = stat.mean
            std = stat.std
            value = item[key]["data"]
            if inverse:
                new_item[key]["data"] = value * std + mean
            else:
                new_item[key]["data"] = (value - mean) / std
        return new_item

    def on_call(self, iterable):
        self._prepare_stats(iterable)
        config = self.config
        all_keys = self._statistics.keys()
        if config.include - all_keys:
            raise ValueError(
                f"Included keys {config.include} are not present in statistics keys {all_keys}."
            )
        self._used_keys = (config.include or all_keys) - config.exclude
        self.get_logger().info("Keys to be standardized: %s", self._used_keys)

        first_item: dict = first_recursive(iterable, config.depth + 1)
        if not config.strict:
            self._used_keys &= first_item.keys()
        else:
            missing_keys = self._used_keys - first_item.keys()
            if missing_keys:
                raise KeyError(
                    f"Keys {missing_keys} specified for standardization are not found in the data item."
                )
        if self._used_keys:
            return recursive_map_reusable(
                self._transform, iterable, self.config.depth, base_type=Mapping
            )
        return iterable


if __name__ == "__main__":
    import numpy as np
    import logging
    import json
    from pprint import pprint

    logging.basicConfig(level=logging.INFO)

    config = StandardizeConfig(
        statistics={
            "a": MeanStd(mean=np.array(5.0), std=np.array(2.0)),
            "b": MeanStd(mean=np.array([1.0, 2.0]), std=np.array([0.5, 0.5])),
            "c": MeanStd(mean=np.array(0.0), std=np.array(1.0)),
            "d": MeanStd(mean=np.array(10.0), std=np.array(2.0)),
        },
        include={"a", "b", "d"},
        exclude={"c", "d"},
    )
    pipeline = Standardize(config)
    print("---- Pipeline Config ----")
    pprint(json.dumps(pipeline.dump("json"), indent=4))
    data = [
        {
            "a": np.array(7.0),
            "b": [2.0, 3.0],
            "c": np.array(0.0),
            "d": np.array(12.0),
        },
        {
            "a": np.array(3.0),
            "b": np.array([0.0, 1.0]),
            "c": np.array(0.0),
            "d": np.array(8.0),
        },
    ]
    for item in data:
        for key, value in item.items():
            item[key] = {"data": value}
    print("---- Original Data ----")
    for item in data:
        pprint(item)
    # Standardization
    standardized = pipeline(data)
    print("---- Standardized Data ----")
    for item in standardized:
        pprint(item)
    # Inverse standardization
    inverse_config = StandardizeConfig(inverse=True)
    inverse_pipeline = Standardize(inverse_config)
    inversed = inverse_pipeline(standardized)
    print("---- Inversed Data ----")
    for item in inversed:
        pprint(item)
