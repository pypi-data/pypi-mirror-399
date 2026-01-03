# bilibili_api_c

## Areas
### 创作中心 Creative Center
### 个人空间 Space

## Development

### Release
Don't forget to update the version in `pyproject.toml`
1. Build wheel
```shell
python -m build
```
2. Upload to PyPI
```shell
python -m pip install --upgrade twine
python -m twine upload dist/*
```


