import os
import re

from flask import Flask, request, jsonify, render_template

# create an instance of the Flask class
app = Flask(__name__)

# list if items
items = [{"item": "item1"}, {"item": "item2"}]

@app.route('/')
def index():
    """Render the index page."""
    # Main page
    return jsonify({
                "status": "success",
                "message": "Hello, world!"
             })

@app.route('/items', methods=['GET', 'POST'])
def items_route():
    """Items route."""
    if request.method == 'POST':
        # push the item to the list
        items.append(request.get_json())
        # return the created item
        return jsonify({
            "status": "success",
            "item": request.get_json()
        })
        # return jsonify({"status": "success", "message": "Post item!"})
    elif request.method == 'GET':
        # return the list of items
        return jsonify({"status": "success", "items": items})
        # return jsonify({"status": "sucess", "message": "Get Route for items!"})

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 33507))
    app.run(host='0.0.0.0', debug=True, port=port)