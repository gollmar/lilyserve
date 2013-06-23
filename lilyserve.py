from hashlib import md5
from tempfile import TemporaryDirectory, NamedTemporaryFile
import subprocess
import os.path
import binascii

from flask import Flask, request, redirect, url_for, send_file, render_template

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
        command = ['lilypond', 
                   '-dbackend=eps', 
                   '-dno-gs-load-fonts', 
                   '-dinclude-eps-fonts', 
                   '--png', 
                   '--output=' + os.path.join(tmpdir, 'output'),
                   os.path.join(tmpdir, 'expr.ly')]
        subprocess.call(command)
        with open(os.path.join(tmpdir, 'output.png'), 'rb') as png:
            with open(os.path.join('output', expr_hash + '.png'), 'wb') as png_copy:
                png_copy.write(png.read())
    return expr_hash + '.png'

@app.route('/')
def notate():
    return render_template('index.html')

@app.route('/expressions', methods=['GET','POST'])
def expressions():
    if request.method == 'GET':
        ls = [os.path.splitext(p)[0] for p in os.listdir('output')]
        return render_template('list_expressions.html', expr_list=ls)
    elif request.method == 'POST':
        expr =  request.form.get('expr', request.args.get('expr'))
        expr_hash = md5(expr.encode()).hexdigest()
        if not os.path.exists(os.path.join('output', expr_hash + '.png')):
            notate_expression(expr)
        return json.dumps({'img_src': url_for('expressions',expr_hash=expr_hash)})
            

@app.route('/expressions/<expr_hash>')
def get_expression(expr_hash):
    return send_file(os.path.join('output', expr_hash + '.png'))

if __name__ == '__main__':
    app.run(debug=True)
