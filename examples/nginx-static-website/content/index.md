# Nginx Docker Example

Sample page

[Link sample](./deep/other/page.md)

## Markdown improved !!

```python

def parse_md(path):
    """
    Recursive function to create html file from markdown file
    with the same directory tree
    """
    src_abs = os.path.join(SOURCE_DIR, path)
    if not os.path.exists(src_abs):
        raise SyntaxError("Path {path} doesn't exist".format(path=src_abs))

    target_abs = os.path.join(TARGET_DIR, path)
    if os.path.isdir(src_abs):
        if not os.path.exists(target_abs):
            os.mkdir(target_abs)
        return [parse_md(os.path.join(path, f)) for f in os.listdir(src_abs)]

    with open(src_abs, 'ro') as stream:
        content = stream.read()

    if src_abs.endswith('.md'):
        target_abs = os.path.splitext(target_abs)[0] + '.html'
        content = markdown2.markdown(content, extras=["fenced-code-blocks"])
        content = TEMPLATE.render(
            title=os.path.basename(target_abs),
            content=content
        )

    with open(target_abs, 'wb') as stream:
        stream.write(content)
```

