import copy
from flask import Flask, render_template, request, abort, redirect, url_for, make_response

app = Flask(__name__)

BASE = {
    'Name': 'Dish Name',
    'Price': '123$',
    'Quantity': '0',
    # 'Picture': 'www.xxx.com',
}

MENU = {
    'Appetizer': {
        'a': {
            'Price': "123",
            'Quantity': '0',
        },
        'b': {
            'Price': "123",
            'Quantity': '0',
        },
        'c': {
            'Price': "123",
            'Quantity': '0',
        },
    },
    'Main Dish': {
        'd': {
            'Price': "123",
            'Quantity': '0',
        },
        'e': {
            'Price': "123",
            'Quantity': '0',
        },
        'f': {
            'Price': "123",
            'Quantity': '0',
        },
    },
    'Soup': {
        'g': {
            'Price': "123",
            'Quantity': '0',
        },
        'h': {
            'Price': "123",
            'Quantity': '0',
        },
        'i': {
            'Price': "123",
            'Quantity': '0',
        },
    },
    'Dessert': {
        'j': {
            'Price': "123",
            'Quantity': '0',
        },
        'k': {
            'Price': "123",
            'Quantity': '0',
        },
        'l': {
            'Price': "123",
            'Quantity': '0',
        },
    },
    "Beverage": {
        'm': {
            'Price': "123",
            'Quantity': '0',
        },
        'n': {
            'Price': "123",
            'Quantity': '0',
        },
        'o': {
            'Price': "123",
            'Quantity': '0',
        },
    },
}


@app.route('/')
def index():
    return redirect(url_for('menu'))


@app.route('/menu', methods=['POST', 'GET'])
def menu():
    if request.method == 'GET':
        return render_template('menu.html', items=MENU["Appetizer"])

    data = request.form
    print(data)
    menu = copy.deepcopy(MENU)
    for item in menu.values():
        for key in item.keys():
            if key in data.keys():
                item[key]['Quantity'] = data[key]
            elif request.cookies.get(key):
                item[key]['Quantity'] = request.cookies.get(key)

    # print(menu)
    page = data.get('page', None)

    # if not page:
    #     return redirect()

    resp = make_response(render_template('menu.html', items=menu[page]))
    for item in menu.values():
        for key in item.keys():
            resp.set_cookie(key, item[key]['Quantity'])
    return resp


if __name__ == '__main__':
    app.run(port=5001, debug=True)