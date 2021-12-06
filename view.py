import copy
from flask import Flask, render_template, request, abort, redirect, url_for, make_response

app = Flask(__name__)

BASE = {
    'Name': 'Dish Name',
    'Price': '123$',
    'Quantity': '0',
    # 'Picture': 'www.xxx.com'
}

MENU = {
    'Appetizer': {
        'a': {
            'Price': "1",
            'Quantity': '0',
        },
        'b': {
            'Price': "2",
            'Quantity': '0',
        },
        'c': {
            'Price': "3",
            'Quantity': '0',
        },
    },
    'Main Dish': {
        'd': {
            'Price': "4",
            'Quantity': '0',
        },
        'e': {
            'Price': "5",
            'Quantity': '0',
        },
        'f': {
            'Price': "6",
            'Quantity': '0',
        },
    },
    'Soup': {
        'g': {
            'Price': "7",
            'Quantity': '0',
        },
        'h': {
            'Price': "8",
            'Quantity': '0',
        },
        'i': {
            'Price': "9",
            'Quantity': '0',
        },
    },
    'Dessert': {
        'j': {
            'Price': "10",
            'Quantity': '0',
        },
        'k': {
            'Price': "11",
            'Quantity': '0',
        },
        'l': {
            'Price': "12",
            'Quantity': '0',
        },
    },
    "Beverage": {
        'm': {
            'Price': "13",
            'Quantity': '0',
        },
        'n': {
            'Price': "14",
            'Quantity': '0',
        },
        'o': {
            'Price': "15",
            'Quantity': '0',
        },
    },
}

DISCOUNT = {
    100: 0.9,
    200: 0.8,
    300: 0.7,
}

bill_summary = {
    "AliPay": [0.0, 0, 0],
    "WechatPay": [0.0, 0.0],
    "Cash": [0.0, 0.0],
    "Credit Card": [0.0, 0.0],
}

guest_number = 0


@app.route('/')
def index():
    return redirect(url_for('menu'))


@app.route('/menu', methods=['POST', 'GET'])
def menu():
    if request.method == 'GET':
        resp = make_response(render_template('menu.html', items=MENU["Appetizer"]))
        for item in MENU.values():
            for key in item.keys():
                resp.delete_cookie(key)
        return resp

    data = request.form
    # print(data)
    menu = copy.deepcopy(MENU)
    for item in menu.values():
        for key in item.keys():
            if key in data.keys():
                item[key]['Quantity'] = data[key]
            elif request.cookies.get(key):
                item[key]['Quantity'] = request.cookies.get(key)

    # print(menu)
    page = data.get('page', None)

    if not page:
        return redirect(url_for('order', **data))

    resp = make_response(render_template('menu.html', items=menu[page]))
    for item in menu.values():
        for key in item.keys():
            resp.set_cookie(key, item[key]['Quantity'], max_age=60 * 2)
    return resp


@app.route('/order')
def order():
    menu = copy.deepcopy(MENU)
    table = dict()
    cnt = 1
    total = 0.0
    for item in menu.values():
        for key in item.keys():
            if key in request.args.keys():
                item[key]['Quantity'] = int(request.args[key])
            elif request.cookies.get(key):
                item[key]['Quantity'] = int(request.cookies.get(key))
            if item[key]['Quantity'] and item[key]['Quantity'] != '0':
                table[cnt] = {
                    'Name': key,
                    'Price': int(item[key]['Price']),
                    'Quantity': item[key]['Quantity'],
                }
                total += table[cnt]['Price'] * table[cnt]['Quantity']
                cnt += 1

    discount = 1.0
    for price, dis in DISCOUNT.items():
        if total > price:
            discount = dis
    paid = discount * total

    discount = f"{int(discount*100)} %"
    return render_template("order.html", table=table, total=total, discount=discount, paid=paid)


@app.route('/summary')
def summary():
    total = request.args.get('total')
    paid = request.args.get('paid')
    method = request.args.get('method')
    bill_summary[method][0] += float(total)
    bill_summary[method][1] += float(paid)

    revenue = sum([v[0] for v in bill_summary.values()])
    actual_revenue = sum([v[1] for v in bill_summary.values()])
    global guest_number
    guest_number += 1
    return render_template(
        'summary.html',
        revenue=revenue,
        actual_revenue=actual_revenue,
        guest_number=guest_number,
        alipay=bill_summary['AliPay'][1],
        wechatpay=bill_summary['WechatPay'][1],
        cash=bill_summary['Cash'][1],
        credit=bill_summary['Credit Card'][1],
    )


if __name__ == '__main__':
    app.run(port=5001, debug=True)