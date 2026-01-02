from ._BaseHandler import BaseHandler
from typing import Any


class TimeSeriesManager(BaseHandler):
    def __init__(self):
        self.time_series = {}

    @property
    def _COMMAND_RULES(self) -> dict[str, dict[str, Any]]:
        return {
            # timeSeries(typeName, tag, *args)
            "timeSeries": {
                "positional": ["typeName", "tag", "args*"],
            },
        }

    def handles(self):
        return ["timeSeries"]

    def handle(self, func_name: str, arg_map: dict[str, Any]):
        args, kwargs = arg_map.get("args"), arg_map.get("kwargs")
        if func_name == "timeSeries":
            self._handle_time_series(*args, **kwargs)

    def _handle_time_series(self, *args: Any, **kwargs: Any):
        arg_map = self._parse("timeSeries", *args, **kwargs)
        
        tag = arg_map.get("tag")
        if not tag:
            return

        series_type = arg_map.get("typeName")
        if not series_type:
            return

        series_args = arg_map.get("args", [])

        # Save time series information
        self.time_series[tag] = {"type": series_type, "args": series_args}

    def get_time_series(self, tag: int) -> dict:
        """Get time series by tag"""
        return self.time_series.get(tag, {})

    def get_time_series_by_type(self, series_type: str) -> list[int]:
        """Get all time series tags of a specific type"""
        return [tag for tag, info in self.time_series.items() 
                if info.get("type") == series_type]

    def clear(self):
        """Clear all time series data"""
        self.time_series.clear()
