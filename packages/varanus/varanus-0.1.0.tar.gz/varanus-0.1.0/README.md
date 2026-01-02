# Varanus

## Installation

```
pip install varanus
```

## Quickstart for Django

In your `settings.py`:

```python
try:
    import varanus.client
    varanus.client.setup(
        "https://APIKEY@varanus.example.com",
        environment=os.getenv("VARANUS_ENV", "local"),
        install=MIDDLEWARE,
    )
except ImportError:
    pass
```

For more information about how to configure the Varanus client, see [the configuration docs](docs/configuration.md). If nothing else, note that when using uWSGI, you'll need to enable threads with the [enable-threads](https://uwsgi-docs.readthedocs.io/en/latest/Options.html#enable-threads) option.
