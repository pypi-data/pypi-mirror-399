To create a new release:

```
poetry version rc
git commit -am "Release candidate"
git tag v1.2.0-rc.1
git push origin main --tags
```

OR

```
poetry version patch
git commit -am "Stable release"
git tag v1.2.0
git push origin main --tags
```
