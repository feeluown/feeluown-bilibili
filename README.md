# FeelUOwn-TEMPLATE

FeelUOwn plugin for TEMPLATE

## About this template repository 

This template is used for creating a FeelUOwn plugin. Follow the steps to initialize
your project.

1. Rename file from `*TEMPLATE*` to `*YOUR_PLUGIN_NAME*`.
1. Replace the *string* `TEMPLATE` in all files with your plugin name.

For example, if your plugin name is bilibili, you can do it by following commands

```sh
git grep -l 'TEMPLATE' | xargs sed -i 's/TEMPLATE/bilibili/g'
# macOS
# git grep -l 'TEMPLATE' | xargs sed -i '' -e 's/TEMPLATE/bilibili/g'

git grep -l 'AUTHOR' | xargs sed -i 's/AUTHOR/your-name/g'
git grep -l 'EMAIL' | xargs sed -i 's/EMAIL/your-email/g'

find . -type f -name '*TEMPLATE*' | grep -v .git/ | xargs -I{} sh -c 'mv {} $(echo {} | sed -e "s/TEMPLATE/bilibili/g")'
```

## Installation

```sh
pip3 install fuo-TEMPLATE
```

## Changelog

### 0.1 (2021-11-06)
-
