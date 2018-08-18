import code
import os
import sys
from io import StringIO
from flask import Flask, escape, request

app = Flask(__name__)
interpreter = code.InteractiveInterpreter(locals=locals())

class Capturing(list):
    def __enter__(self):
        self._stdout = sys.stdout
        self._stderr = sys.stderr
        sys.stdout = self._stringio = StringIO()
        sys.stderr = self._stringio
        return self
    def __exit__(self, *args):
        self.extend(self._stringio.getvalue().splitlines())
        del self._stringio # free some memory
        sys.stdout = self._stdout
        sys.stderr = self._stderr

@app.route("/")
def homepage():
    return "Hello world"

@app.route("/shell", methods=["GET", "POST"])
def web_shell():
    if request.method == "POST":
        error = False
        with Capturing() as output:
            try:
                interpreter.runsource(request.form["command"])
            except Exception as e:
                result = str(e)
        if not error:
            result = "\n".join(output)
        
        return '''
            <pre style="max-width:90%; overflow: auto">
                {}
            </pre>
            <form method="POST">
                <textarea name=command></textarea>
                <input type=submit value="Execute">
            </form>
        '''.format(escape(result))
            
    else:
        return '''
            <form method="POST">
                <textarea name=command></textarea>
                <input type=submit value="Execute">
            </form>
        '''

@app.route("/healthz")
def health():
    return "Ok", 200
