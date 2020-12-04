def b(text=None):
    return '<strong>' + str(text) + '</strong>'


def h3(text=None):
    return '<h3>' + str(text) + '</h3>'


def h4(text=None):
    return '<h4>' + str(text) + '</h4>'


def link(text=None, url='#'):
    return '<a href="' + str(url) + '">' + str(text) + '</a>'
