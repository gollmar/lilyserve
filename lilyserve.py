from hashlib import md5
from tempfile import TemporaryDirectory, NamedTemporaryFile
import subprocess
import os.path
import binascii

from flask import Flask, request, redirect, url_for, send_file

app = Flask(__name__)


def notate_expression(expr):
    '''Generates a PNG preview of the given expression.'''
    expr_hash = md5(expr.encode()).hexdigest()
    expr = expr + '''
\paper {
        indent=0\mm
        line-width=120\mm
        oddFooterMarkup=##f
        oddHeaderMarkup=##f
        bookTitleMarkup = ##f
        scoreTitleMarkup = ##f
        }'''
    with TemporaryDirectory() as tmpdir:
        with open(os.path.join(tmpdir, 'expr.ly'), 'w') as lily:
            lily.write(expr)
            lily.write('''
                \paper {
                    indent=0\mm
                    line-width=120\mm
                    oddFooterMarkup=##f
                    oddHeaderMarkup=##f
                    bookTitleMarkup = ##f
                    scoreTitleMarkup = ##f
                }''')
        subprocess.call(['lilypond', 
                         '-dbackend=eps', 
                         '-dno-gs-load-fonts', 
                         '-dinclude-eps-fonts', 
                         '--png', 
                         '--output=' + os.path.join(tmpdir, 'output'),
                         os.path.join(tmpdir, 'expr.ly')])
        with open(os.path.join(tmpdir, 'output.png'), 'rb') as png:
            with open(os.path.join('output', expr_hash), 'wb') as png_copy:
                png_copy.write(png.read())
    return png_copy + '.png'


@app.route('/', methods=['GET','POST'])
def notate():
    expr = request.args.get('expr')
    return send_file(os.path.join('output', notate_expression(expr)))

@app.route('/expressions/<expr_hash>.png')
def get_expression(expr_hash):
    return expr_hash

if __name__ == '__main__':
    app.run(debug=True)
