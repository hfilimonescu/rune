allowed_tags = ['a', 'p',
                'i', 'strong',
                'ol', 'ul', 'li',
                'h1', 'h2', 'h3', 'h4', 'h5', 'h6',
                'img']

allowed_attrs = {
    'a': ['href'],
    'h1': ['id'],
    'h2': ['id'],
    'h3': ['id'],
    'h4': ['id'],
    'h5': ['id'],
    'h6': ['id'],
    'img': ['src', 'data-src',
            'alt', 'title',
            'width', 'height',
            'align', 'class'],
    'li': ['id'],
    'p': ['id', 'class'],
    'ol': ['id'],
    'ul': ['id'],
}

allowed_extensions = [
    'abbr',
    'admonition',
    'attr_list',
    # 'codehilite',
    'def_list',
    'footnotes',
    'meta',
    'nl2br',
    # 'tables',
    # 'toc',
    # 'wikilinks',
]
