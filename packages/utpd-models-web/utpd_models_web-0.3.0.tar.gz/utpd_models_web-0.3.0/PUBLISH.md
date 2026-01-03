# This is a PyPi package

## PyPi publish command

```bash
uv lock -U && uv export --frozen --no-editable --no-dev -o requirements.txt > /tmp/uv.txt && \
      rm -rf dist/* && uv build && uv publish --token $PYPI_TOKEN
```

> Note: comment out any local path sources in pyproject.toml before publishing.
