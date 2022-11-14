
# Catch profile
`Monster Profiles` :arrow_right: `HrFlow.ai Profile Parsing`

catches a Monster profile to Hrflow.ai


**Monster Profiles endpoints used :**
| Endpoints | Description |
| --------- | ----------- |
| [**Post Candidate**](https://partner.monster.com/apply-with-monster-implementing) | Endpoint to catch a profile and assign it to a source in hrflow |



## Action Parameters

| Field | Type | Default | Description |
| ----- | ---- | ------- | ----------- |
| `logics`  | `typing.List[typing.Callable[[typing.Dict], typing.Optional[typing.Dict]]]` | [] | List of logic functions |
| `format`  | `typing.Callable[[typing.Dict], typing.Dict]` | [`format_profile`](../connector.py#L248) | Formatting function |
| `read_mode`  | `str` | ReadMode.sync | If 'incremental' then `read_from` of the last run is given to Origin Warehouse during read. **The actual behavior depends on implementation of read**. In 'sync' mode `read_from` is neither fetched nor given to Origin Warehouse during read. |

## Source Parameters

| Field | Type | Default | Description |
| ----- | ---- | ------- | ----------- |
| `profile`  | `Any` | None | Optional profile for testing |

## Destination Parameters

| Field | Type | Default | Description |
| ----- | ---- | ------- | ----------- |
| `api_secret` :red_circle: | `str` | None | X-API-KEY used to access HrFlow.ai API |
| `api_user` :red_circle: | `str` | None | X-USER-EMAIL used to access HrFlow.ai API |
| `source_key` :red_circle: | `str` | None | HrFlow.ai source key |
| `only_insert`  | `bool` | False | When enabled the profile is written only if it doesn't exist in the source |

:red_circle: : *required*

## Example

```python
import logging
from hrflow_connectors import Monster
from hrflow_connectors.core import ReadMode


logging.basicConfig(level=logging.INFO)


Monster.catch_profile(
    workflow_id="some_string_identifier",
    action_parameters=dict(
        logics=[],
        format=lambda *args, **kwargs: None # Put your code logic here,
        read_mode=ReadMode.sync,
    ),
    origin_parameters=dict(
        profile=***,
    ),
    target_parameters=dict(
        api_secret="your_api_secret",
        api_user="your_api_user",
        source_key="your_source_key",
        only_insert=False,
    )
)
```