from flask import Flask,render_template
app=Flask(__name__)

PRODUCTS=[{
    'name':'Nokia c10',
    'category':'phones',
    'location':'KV',
    'description':'128gb ROM 3gb RAM 4000mah',
    'price':'ksh 13000'
},
{
    'name':'3*6 bed',
    'category':'Furniture',
    'location':'KV',
    'description':'3*6 wooden bed',
    'price':'ksh 3000'
},
{
    'name':'hp 1020 g2',
    'category':'Laptops',
    'location':'Kitui town',
    'description':'i6 10th gen, 8gb ram , 256gb ssd, 14 inch display , windows 11 pro',
    'price':'ksh 34000'
},
{
    'name':'32 inch sony smart tv',
    'category':'TVs',
    'location':'KV',
    'description':'32 inch android 13 2gb ram, 8gb rom,digital tv',
    'price':'ksh 15000'
}

]
@app.route('/')

def home():
    return render_template('home.html')

@app.route('/templates/categories')

def cat_return():
    return render_template('categories.html')

@app.route('/templates/create-seller')
def create_seller():
    return render_template('create-seller.html')
@app.route('/templates/login')
def login():
    return render_template('loginpage.html')
@app.route('/templates/advertise')
def advertise():
    return render_template('advert.html')
@app.route('/templates/phones')
def show_phone():
    return render_template('phones.html',products=PRODUCTS)

if __name__=='__main__':
    app.run(debug=True)