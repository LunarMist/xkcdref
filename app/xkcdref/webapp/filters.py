from xkcdref.webapp import app


@app.template_filter('format_int')
def format_integer_filter(value):
    return '{:,}'.format(value)
