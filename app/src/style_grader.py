from flask import Flask
from todoView import TodoView, TodoAdd, TodoRetrieve
import pdb

app = Flask(__name__)
app.add_url_rule('/', view_func=TodoView.as_view('todo_view'),
    methods=['GET'])
app.add_url_rule('/todoAdd', view_func=TodoAdd.as_view('todo_add'),
    methods=['POST'])
app.add_url_rule('/todoRetrieve/<int:n>',
    view_func=TodoRetrieve.as_view('todo_retrieve'), methods=['GET'])

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='Development Server Help')
    parser.add_argument("-d", "--debug", action="store_true", dest="debug_mode",
                  help="run in debug mode (for use with PyCharm)", default=False)
    parser.add_argument("-p", "--port", dest="port",
                  help="port of server (default:%(default)s)", type=int, default=5000)

    cmd_args = parser.parse_args()
    app_options = {"port": cmd_args.port }

    if cmd_args.debug_mode:
        app_options["debug"] = True
        app_options["use_debugger"] = False
        app_options["use_reloader"] = False
    app.run(**app_options)
