import copy
from flask import Flask, render_template, request, abort, redirect, url_for, make_response

app = Flask(__name__)

# menu dictionary
# 'Name': {
#     'price': '0',
#     'Quantity': '0',
# }
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

# discount dictionary, 10% off if order is bigger than 100.
DISCOUNT = {
    100: 0.9,
    200: 0.8,
    300: 0.7,
}

# bill summary dictionary, the first element in the list is total paid,
# the second is the actual paid.
bill_summary = {
    "AliPay": [0.0, 0, 0],
    "WechatPay": [0.0, 0.0],
    "Cash": [0.0, 0.0],
    "Credit Card": [0.0, 0.0],
}

# guest number counter.
guest_number = 0


# index page redirect
@app.route('/')
def index():
    return redirect(url_for('menu'))


# menu page.
@app.route('/menu', methods=['POST', 'GET'])
def menu():
    # redirect by index page
    if request.method == 'GET':
        resp = make_response(
            render_template('menu.html', items=MENU["Appetizer"]))

        # delete all cookies.
        for item in MENU.values():
            for key in item.keys():
                resp.delete_cookie(key)
        return resp

    # Post by menu change page.
    # Request form data.
    data = request.form

    # new order dictionary
    menu = copy.deepcopy(MENU)
    for item in menu.values():
        for key in item.keys():
            # newly submitted order
            if key in data.keys():
                item[key]['Quantity'] = data[key]
            # previous submitted order stored in cookies.
            elif request.cookies.get(key):
                item[key]['Quantity'] = request.cookies.get(key)

    # next page parameter.
    page = data.get('page', None)

    # submit all order and redirect to payment page.
    if not page:
        return redirect(url_for('order', **data))

    # render template using new menu dictionary with specific page.
    resp = make_response(render_template('menu.html', items=menu[page]))
    for item in menu.values():
        for key in item.keys():
            # set new cookies using menu dictionary.
            resp.set_cookie(key, item[key]['Quantity'], max_age=60 * 2)
    return resp


# order and payment page.
@app.route('/order')
def order():
    # order dictionary
    menu = copy.deepcopy(MENU)
    # shopping cart dictionary
    table = dict()

    cnt = 1
    total = 0.0

    # create new order dictionary and complete the shopping cart.
    for item in menu.values():
        for key in item.keys():
            # Dishes in the form data.
            if key in request.args.keys():
                item[key]['Quantity'] = int(request.args[key])
            # Dishes stored in cookies.
            elif request.cookies.get(key):
                item[key]['Quantity'] = int(request.cookies.get(key))
            # Add Dishes to shopping cart if the quantity is not 0.
            if item[key]['Quantity'] and item[key]['Quantity'] != '0':
                table[cnt] = {
                    'Name': key,
                    'Price': int(item[key]['Price']),
                    'Quantity': item[key]['Quantity'],
                }
                # compute total payment
                total += table[cnt]['Price'] * table[cnt]['Quantity']
                cnt += 1

    # compute the discount with total payment.
    discount = 1.0
    for price, dis in DISCOUNT.items():
        if total > price:
            discount = dis

    # actual payment
    paid = discount * total

    discount = f"{int(discount*100)} %"
    # render shopping cart template.
    return render_template("order.html",
                           table=table,
                           total=total,
                           discount=discount,
                           paid=paid)


# summary page
@app.route('/summary')
def summary():
    # add total payment, actual payment and payment method to summary.
    total = request.args.get('total')
    paid = request.args.get('paid')
    method = request.args.get('method')
    # update bill_summary
    bill_summary[method][0] += float(total)
    bill_summary[method][1] += float(paid)

    # compute revenue and actual revenue using bill summary dictionary.
    revenue = sum([v[0] for v in bill_summary.values()])
    actual_revenue = sum([v[1] for v in bill_summary.values()])

    # update global guest number
    global guest_number
    guest_number += 1

    # render summary template page
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