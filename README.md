# Overview

This interface layer hadles the ```provides``` end of the WSGate relation.

# Usage

A simple example:

```python
@reactive.when('wsgate.available')
@reactive.when_any(
    'config.complete',
    'ssl.enabled')
def wsgate_connected(wsgate):
    with charm.provide_charm_instance() as wsgate_charm:
        wsgate_charm.set_wsgate_info(wsgate)
```

And your ```set_wsgate_info()``` function:

```python
def set_wsgate_info(self, wsgate):
    is_ready = reactive.flags.is_flag_set('config.complete')
    has_ssl = reactive.flags.get_state('ssl.enabled')
    ha_available = reactive.flags.is_flag_set('ha.available')
    proto = "https" if has_ssl is True else "http"
    local_ip = ch_ip.get_relation_ip("internal")
    addr = self.config["vip"] if ha_available else local_ip
    allowed_user = self._get_allowed_user()

    if not allowed_user:
        # We don't have AD credentials yet. Defer for later
        return

    relation_data = {
        "enabled": is_ready,
        "html5_proxy_base_url": "%(proto)s://%(address)s:%(port)s/" % {
            "proto": proto,
            "address": addr,
            "port": self.api_ports["wsgate"][os_ip.PUBLIC],
        },
        "allow_user": allowed_user,
    }
    for unit in wsgate.all_joined_units:
        wsgate.set_wsgate_info(
            unit.relation.relation_id,
            relation_data)

```
