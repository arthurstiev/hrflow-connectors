from jinja2 import Template

CONNECTOR_README_TEMPLATE = Template(
    """
# {{ connector_name }} Connector
{% if description %}
> {{ description }}
{% endif %}

🔗 {{ url }}

| Actions |
| ------- |
{% for action in actions %}| [**{{ action.name | title | replace("_", " ")}}**](docs/{{ action.name }}.md) |
{% endfor %}
"""
)
ACTION_DOCUMENTATION_TEMAPLTE = Template(
    """
# {{ action_name | title | replace("_", " ") }}
`{{ origin_name }}` :arrow_right: `{{ target_name }}`

{{ description }}

{% if origin_endpoints %}
**{{ origin_name }} endpoints used :**
| Endpoints | Description |
| --------- | ----------- |
{%- for endpoint in origin_endpoints %}
| [**{{ endpoint.name}}**]({{ endpoint.url }}) | {{ endpoint.description }} |
{%- endfor %}

{% endif %}
{% if target_endpoints %}
**{{ target_name }} endpoints used :**
| Endpoints | Description |
| --------- | ----------- |
{%- for endpoint in target_endpoints %}
| [**{{ endpoint.name}}**]({{ endpoint.url }}) | {{ endpoint.description }} |
{%- endfor %}

{% endif %}
## Action Parameters

| Field | Type | Default | Description |
| ----- | ---- | ------- | ----------- |
{%- for field in action_fields %}
| `{{ field.name }}` {% if field.required %}:red_circle:{% endif %} | `{{ field.type }}` | {{ field.default }} | {{ field.description }} |
{%- endfor %}

## Source Parameters

| Field | Type | Default | Description |
| ----- | ---- | ------- | ----------- |
{%- for field in origin_fields %}
| `{{ field.name }}` {% if field.required %}:red_circle:{% endif %} | `{{ field.type }}` | {{ field.default }} | {{ field.description }} |
{%- endfor %}

## Destination Parameters

| Field | Type | Default | Description |
| ----- | ---- | ------- | ----------- |
{%- for field in target_fields %}
| `{{ field.name }}` {% if field.required %}:red_circle:{% endif %} | `{{ field.type }}` | {{ field.default }} | {{ field.description }} |
{%- endfor %}

:red_circle: : *required*

## Example

```python
import logging
from hrflow_connectors import {{ connector_name }}
from hrflow_connectors.core import ReadMode


logging.basicConfig(level=logging.INFO)


{{ connector_name }}.{{ action_name }}(
    workflow_id="some_string_identifier",
    action_parameters=dict(
        {%- for field in action_fields %}
        {{ field.name }}={{ field.example }},
        {%- endfor %}
    ),
    origin_parameters=dict(
        {%- for field in origin_fields %}
        {{ field.name }}={{ field.example }},
        {%- endfor %}
    ),
    target_parameters=dict(
        {%- for field in target_fields %}
        {{ field.name }}={{ field.example }},
        {%- endfor %}
    )
)
```
"""
)

WORKFLOW_TEMPLATE = Template(
    """
import typing as t

from hrflow_connectors import {{ connector_name }}
from hrflow_connectors.core.connector import ActionInitError, Reason

ORIGIN_SETTINGS_PREFIX = "{{ origin_settings_prefix }}"
TARGET_SETTINGS_PREFIX = "{{ target_settings_prefix }}"

{{ format_placeholder }}

{{ logics_placeholder }}
{% if type == "catch" %}
{{ event_parser_placeholder }}
{% endif %}

def workflow(
        {% if type == "catch" %}
        _request: t.Dict,
        {% endif %}
        settings: t.Dict
    ) -> None:
    actions_parameters = dict()
    try:
        format
    except NameError:
        pass
    else:
        actions_parameters["format"] = format

    try:
        logics
    except NameError:
        pass
    else:
        actions_parameters["logics"] = logics

    if "{{ workflow_id_settings_key }}" not in settings:
        return {{ connector_name }}.{{ action_name }}(
            workflow_id="",
            action_parameters=dict(),
            origin_parameters=dict(),
            target_parameters=dict(),
            init_error=ActionInitError(
                reason=Reason.workflow_id_not_found,
                data=dict(error="{{ workflow_id_settings_key }} not found in settings", settings_keys=list(settings.keys())),
            )
        )
    workflow_id = settings["{{ workflow_id_settings_key }}"]

    {% if type == "catch" %}
    try:
        event_parser
        _event_parser = event_parser
    except NameError as e:
        action = {{ connector_name }}.model.action_by_name("{{ action_name }}")
        # Without this trick event_parser is always only fetched from the local scope
        # meaning that try block always raises NameError even if the function is
        # defined in the placeholder
        _event_parser = action.parameters.__fields__["event_parser"].default

    if _event_parser is not None:
        try:
            _request = _event_parser(_request)
        except Exception as e:
            return {{ connector_name }}.{{ action_name }}(
                workflow_id=workflow_id,
                action_parameters=dict(),
                origin_parameters=dict(),
                target_parameters=dict(),
                init_error=ActionInitError(
                    reason=Reason.event_parsing_failure,
                    data=dict(error=e, event=_request),
                )
            )
    {% endif %}

    origin_parameters = dict()
    for parameter in {{ origin_parameters }}:
        if "{}{}".format(ORIGIN_SETTINGS_PREFIX, parameter) in settings:
            origin_parameters[parameter] = settings["{}{}".format(ORIGIN_SETTINGS_PREFIX, parameter)]
        {% if type == "catch" %}
        if parameter in _request:
            origin_parameters[parameter] = _request[parameter]
        {% endif %}

    target_parameters = dict()
    for parameter in {{ target_parameters }}:
        if "{}{}".format(TARGET_SETTINGS_PREFIX, parameter) in settings:
            target_parameters[parameter] = settings["{}{}".format(TARGET_SETTINGS_PREFIX, parameter)]
        {% if type == "catch" %}
        if parameter in _request:
            target_parameters[parameter] = _request[parameter]
        {% endif %}

    return {{ connector_name }}.{{ action_name }}(
        workflow_id=workflow_id,
        action_parameters=actions_parameters,
        origin_parameters=origin_parameters,
        target_parameters=target_parameters,
    )
"""
)
