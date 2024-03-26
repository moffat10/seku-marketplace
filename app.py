from flask import Flask,render_template,request,redirect,url_for,flash
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail,Message
from werkzeug.security import generate_password_hash,check_password_hash
from flask_login import LoginManager,login_required,logout_user,login_user,UserMixin,current_user
from werkzeug.utils import secure_filename
import os
import random
from datetime import datetime
import time
import requests
from requests.auth import HTTPBasicAuth
import base64

import string
app=Flask(__name__)

#configure app and mail server

app.config['SECRET_KEY']=os.environ.get('SECRET_KEY')
app.config['SQLALCHEMY_DATABASE_URI']='sqlite:///database.db'
app.config['UPLOAD_FOLDER']='static/files'
app.config['MAIL_SERVER']='smtp.gmail.com'
app.config['MAIL_PORT']=465
app.config['MAIL_USE_TLS']=False
app.config['MAIL_USE_SSL']=True
app.config['MAIL_USERNAME']='sekumarket@gmail.com'
app.config['MAIL_PASSWORD']=os.environ.get('PASSWORD')


#create db object

db=SQLAlchemy(app)
login_manager=LoginManager()
login_manager.init_app(app)
login_manager.login_view="login"

#create mail object
mail=Mail(app)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

#define user table
class User(db.Model,UserMixin):
    id=db.Column(db.Integer,primary_key=True)
    username=db.Column(db.String(50),unique=True,nullable=False)
    email=db.Column(db.String(50),unique=True,nullable=False)
    location=db.Column(db.String(50),nullable=False)
    phone_number=db.Column(db.Integer,unique=True,nullable=False)
    password=db.Column(db.String(50),nullable=False)
    products=db.relationship('Products')
    
    def is_active(self):
        return True
#create products table
class Products(db.Model,UserMixin):
    id=db.Column(db.Integer,primary_key=True)
    name=db.Column(db.String(50),nullable=False)
    description=db.Column(db.String(100),nullable=False)
    image_url=db.Column(db.String(50),nullable=False)
    category=db.Column(db.String(20),nullable=False)
    product_nature=db.Column(db.String(50),nullable=False)
    price=db.Column(db.String(50),nullable=False)
    seller_name=db.Column(db.String(50),nullable=False)
    seller_contact=db.Column(db.String(50),nullable=False)
    seller_id=db.Column(db.Integer,db.ForeignKey('user.id'))

#create password recovery table
class Passrecovery(db.Model,UserMixin):
    id=db.Column(db.Integer,primary_key=True)
    email=db.Column(db.String(50),unique=True,nullable=False)
    code=db.Column(db.String(50),unique=True,nullable=False)

#define shopping kart table
class Shoppingkart(db.Model,UserMixin):
    id=db.Column(db.Integer,primary_key=True)
    name=db.Column(db.String(50),nullable=False)
    description=db.Column(db.String(100),nullable=False)
    image_url=db.Column(db.String(50),nullable=False)
    category=db.Column(db.String(20),nullable=False)
    product_nature=db.Column(db.String(50),nullable=False)
    price=db.Column(db.String(50),nullable=False)
    seller_name=db.Column(db.String(50),nullable=False)
    seller_contact=db.Column(db.String(50),nullable=False)
    buyer_id=db.Column(db.Integer,nullable=False)

#define sold items table
class Solditems(db.Model,UserMixin):
    id=db.Column(db.Integer,primary_key=True)
    order_number=db.Column(db.String(50),unique=True,nullable=False)
    name=db.Column(db.String(50),nullable=False)
    price=db.Column(db.String(50),nullable=False)
    seller_name=db.Column(db.String(50),nullable=False)
    seller_contact=db.Column(db.String(50),nullable=False)
    buyer_id=db.Column(db.Integer,nullable=False)

#chats table
class Chatstable(db.Model,UserMixin):
    id=db.Column(db.Integer,primary_key=True)
    message=db.Column(db.String(50),nullable=False)
    buyer_id=db.Column(db.String(50),nullable=False)
    seller_id=db.Column(db.String(50),nullable=False)
    seller_name=db.Column(db.String(50),nullable=False)
    buyer_name=db.Column(db.String(50),nullable=False)
    time=db.Column(db.String(50),nullable=False)
    order_number=db.Column(db.String(50),nullable=False)

#transaction table
class Transactions(db.Model,UserMixin):
    id=db.Column(db.Integer,primary_key=True)
    delivery=db.Column(db.String(50),nullable=False)
    buyer_id=db.Column(db.String(50),nullable=False)
    seller_id=db.Column(db.String(50),nullable=False)
    seller_name=db.Column(db.String(50),nullable=False)
    buyer_name=db.Column(db.String(50),nullable=False)
    seller_contact=db.Column(db.String(50),nullable=False)
    product_name=db.Column(db.String(50),nullable=False)
    mpesaref=db.Column(db.String(50),nullable=False)
    
#home route
@app.route('/',methods=['POST','GET'])
def home():
    all_products=Products.query.limit(8).all()
    if request.method=='POST':
        flash('Login first!')
        return redirect(url_for('login'))
    return render_template('home.html',all_products=all_products)

#categories route
@app.route('/categories')
def cat_return():
    return render_template('categories.html')

#create account route
@app.route('/create-seller',methods=['GET','POST'])
def create_seller():
    if request.method=='POST':
        username=request.form['username']
        email=request.form['email']
        location=request.form['location']
        phone_number=request.form['phone_number']
        password=request.form['password']
        hashed_password=generate_password_hash(password)
        new_user=User(username=username,email=email,password=hashed_password,phone_number=phone_number,location=location)
        existing_username=User.query.filter_by(username=username).first()
        existing_phone=User.query.filter_by(phone_number=phone_number).first()
        if existing_username:
            flash('username already exists','danger')
            return redirect(url_for('create_seller'))
        elif existing_phone:
            flash('phone number already in use','danger')
            return redirect(url_for('create_seller'))
        else:
            db.session.add(new_user)
            db.session.commit()
            flash('account created sucessfully','success')
            return redirect(url_for('login'))
    return render_template('create-seller.html')


#login route
@app.route('/login',methods=['GET','POST'])
def login():
    if request.method=='POST':
        username=request.form['username']
        password=request.form['password']
        user=User.query.filter_by(username=username).first()
        if user:
           if check_password_hash(user.password,password):
                login_user(user)
                return redirect(url_for('dashboard')) 
           else:
               flash('Wrong username or password, please check and try again!')
        else:
            flash('Wrong username or password, please check and try again!','danger')
    return render_template('login.html')

#logout user
@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('logged out')
    return redirect(url_for('login'))

#user dashboard
@app.route('/dashboard',methods=['GET','POST'])
@login_required
def dashboard():
    all_products=Products.query.all()
    if request.method=='POST':
        name=request.form['product-name']
        image_url=request.form['product-image']
        condition=request.form['product-condition']
        price=request.form['product-price']
        category=request.form['product-category']
        seller_contact=request.form['seller-contact']
        seller_name=request.form['seller-name']
        description=request.form['product-description']
        buyer_id=current_user.id
        newcart=Shoppingkart(name=name,image_url=image_url,description=description,category=category,price=price,product_nature=condition,seller_contact=seller_contact,seller_name=seller_name,buyer_id=buyer_id)
        db.session.add(newcart)
        db.session.commit()
        flash('Added to your cart, proceed to checkout!')
        return redirect(url_for('dashboard'))
    return render_template('dashboard.html',user_products=all_products)

#add product
@app.route('/addproduct',methods=['GET','POST'])
@login_required
def addproduct():
    if request.method=="POST":
        uploaded_file=request.files["product_image"]
        code=random.randint(1000,9999)
        filename=secure_filename(str(code) + uploaded_file.filename)
        uploaded_file.save(os.path.join(app.config['UPLOAD_FOLDER'],filename ))
        image_url='/static/files/'+filename
        name=request.form['product_name']
        description=request.form['Description']
        category=request.form['category']
        product_nature=request.form['product_nature']
        price=request.form['price']
        seller_id=current_user.id
        seller_name=current_user.username
        seller_contact=current_user.phone_number
        new_product=Products(name=name,description=description,image_url=image_url,category=category,product_nature=product_nature,price=price,seller_id=seller_id,seller_name=seller_name,seller_contact=seller_contact)
        db.session.add(new_product)
        db.session.commit()
        flash('Product Added successfully')
        return redirect(url_for('dashboard'))
    return render_template('addproduct.html')

#advertise
@app.route('/advertise')
def advertise():
    return render_template('advert.html')

#filter by category
@app.route('/category/<cat>',methods=['POST','GET'])
def cat_view(cat):
    viewed=Products.query.filter_by(category=cat)
    return render_template('category_view.html',viewed=viewed)

#view product details
@app.route('/product/<id>')
def proview(id):
    product_description=Products.query.filter_by(id=id)
    return render_template('product.html',product_description=product_description)

#reset password
@app.route('/reset',methods=['POST','GET'])
def reset():
    if request.method=='POST':
        email=request.form['email']
        user=User.query.filter_by(email=email).first()
        if user:
            code=random.randint(1000,9999)
            new_recovery=Passrecovery(email=email,code=str(code))
            db.session.add(new_recovery)
            db.session.commit()
            msg=Message(subject='Password Reset',sender='sekumarket@gmail.com',recipients=[email])
            msg.body='Your code is '+str(code)
            mail.send(msg)
            flash('Reset code sent, Check your email')
            return redirect(url_for('newpass'))
    return render_template('resetpass.html')

#update password
@app.route('/new_pass',methods=['POST','GET'])
def newpass():
    if request.method=='POST':
        email=request.form['email']
        code=request.form['code']
        password=request.form['password']
        passwordc=request.form['passwordc']
        email_check=Passrecovery.query.filter_by(email=email).first()
        if password==passwordc:
            if email_check.code==code:
                hashed_password=generate_password_hash(password)
                user=User.query.filter_by(email=email).first()
                user.password=hashed_password
                db.session.commit()
                flash('Password reset successfully')
                if user.password==hashed_password:
                    code_delete=Passrecovery.query.filter_by(email=email).first()
                    db.session.delete(code_delete)
                    db.session.commit()
                    return redirect(url_for('login'))
        else:
            flash("Password did not match, try again !")
    return render_template('newpass.html')
    
                
@app.route('/mycart',methods=['POST','GET'])
@login_required
def mycart():
    usershopping=Shoppingkart.query.filter_by(buyer_id=current_user.id)
    return render_template('cart.html',usershopping=usershopping)

@app.route('/myproducts',methods=['POST','GET'])
@login_required
def myproducts():
    myproduct=Products.query.filter_by(seller_contact=current_user.phone_number)
    return render_template('myproducts.html',myproduct=myproduct)

@app.route('/profile',methods=['POST','GET'])
@login_required
def profile():
    return render_template('profile.html')

@app.route('/history')
@login_required
def history():
    return render_template('history.html')

@app.route('/remove/<proid>')
@login_required
def remove(proid):
    cart=Shoppingkart.query.filter_by(buyer_id=current_user.id,id=proid).first()
    db.session.delete(cart)
    db.session.commit()
    return redirect(url_for('mycart'))

@app.route('/delete/<proid>')
@login_required
def delete(proid):
    prod=Products.query.filter_by(seller_id=current_user.id,id=proid).first()
    db.session.delete(prod)
    db.session.commit()
    flash('Deleted!')
    return redirect(url_for('dashboard'))

@app.route('/deletemsg/<msgid>')
@login_required
def deletemsg(msgid):
    del_message=Chatstable.query.filter_by(id=msgid).first()
    db.session.delete(del_message)
    db.session.commit()
    flash('Deleted!')
    return redirect(url_for('sent'))


@app.route('/messages')
@login_required
def messages():
    my_recieved_messages=Chatstable.query.filter_by(seller_id=current_user.id).order_by(Chatstable.id.desc())
    
    return render_template('messages.html',my_recieved_messages=my_recieved_messages)
@app.route('/sent')
@login_required
def sent():
    my_sent_messages=Chatstable.query.filter_by(buyer_id=current_user.id).order_by(Chatstable.id.desc())
    return render_template('sent.html',my_sent_messages=my_sent_messages)
@app.route('/chat/<product>',methods=['POST','GET'])
@login_required
def chat(product): 
    product_details=Products.query.filter_by(id=product).first()
    name=product_details.seller_name
    if request.method=="POST":
        product_details=Products.query.filter_by(id=product).first()
        message=request.form['message']
        buyer_id=current_user.id
        seller_id=product_details.seller_id
        buyer_name=current_user.username
        seller_name=product_details.seller_name
        timestamp=datetime.now()
        time=timestamp.strftime("%H:%M")
        new_message=Chatstable(message=message,buyer_id=buyer_id,seller_id=seller_id,buyer_name=buyer_name,seller_name=seller_name,time=time)
        db.session.add(new_message)
        db.session.commit()
        flash('Sent!')
        return redirect(url_for('sent'))
    return render_template('compose.html',name=name)

@app.route('/replymsg/<id>',methods=['POST','GET'])
@login_required
def replymsg(id): 
    reciever_details=Chatstable.query.filter_by(id=id).first()
    name=reciever_details.buyer_name
    mesg=reciever_details.message
    if request.method=="POST":
        reciever_details=Chatstable.query.filter_by(id=id).first()
        message=request.form['message']
        buyer_id=current_user.id
        seller_id=reciever_details.buyer_id
        buyer_name=current_user.username
        seller_name=reciever_details.buyer_name
        timestamp=datetime.now()
        time=timestamp.strftime("%H:%M")
        new_message=Chatstable(message=message,buyer_id=buyer_id,seller_id=seller_id,buyer_name=buyer_name,time=time,seller_name=seller_name)
        db.session.add(new_message)
        db.session.commit()
        flash('Message sent successfully!')
        return redirect(url_for('sent'))
    return render_template('reply.html',name=name,mesg=mesg)

@app.route('/pay/<proid>', methods=['POST','GET'])
@login_required
def pay(proid):
    getAccesstoken()
    cart=Shoppingkart.query.filter_by(id=proid)
    
    endpoint = "https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest"
    if request.method=='POST':
        access_token = getAccesstoken()
        headers = {"Authorization": "Bearer %s" % access_token}
        Timestamp = datetime.now()
        passkey = "bfb279f9aa9bdbcf158e97dd71a467cd2e0c893059b10f78e6b72ada1ed2c919"
        times = Timestamp.strftime("%Y%m%d%H%M%S")
        password = "174379" + passkey + times
        password1 = base64.b64encode(password.encode("utf-8")).decode("utf-8")
        number=request.form['number']
        delivery=request.form['dlocation']
        address=request.form['address']
        product_name=request.form['productname']
        seller_id=request.form['seller_id']
        seller_name=request.form['seller_name']
        buyer_id=current_user.id 
        buyer_name=current_user.name
        seller_contact=request.form['seller_contact']
        global dlocation
        global address1
        global productname
        global sellerid
        global sellername
        global sellercontact
        global buyerid 
        global buyername
        dlocation=delivery
        address1=address
        productname=product_name
        sellerid=seller_id
        sellername=seller_name
        sellercontact=seller_contact
        buyerid=buyer_id
        buyername=buyer_name
        data = {
            "BusinessShortCode": "174379",
            "Password": password1,
            "Timestamp": times,
            "TransactionType": "CustomerPayBillOnline",
            "PartyA": "254759187700",
            "PartyB": "174379",
            "PhoneNumber": "254" + str(number),
            "CallBackURL":"https://sekuvirtualmarket.onrender.com/lnmocallback",
            "AccountReference": "SekuVm",
            "TransactionDesc": "HelloTest",
            "Amount": "1"
        }
        res = requests.post(endpoint, json=data, headers=headers).json()
        if res['ResponseCode']=='0':
            return redirect(url_for('incoming'))
        else:
            flash('Request Unsuccessful!')
            return redirect(url_for('pay',proid=proid))
    return render_template('pay.html',cart=cart)

#callback url
@app.route('/lnmocallback', methods=['POST'])
def lnmocallback():
    data = request.get_json()
    time.sleep(1)
    if data['ResultCode']=='1032':
        flash('Transaction cancelled!')
        return redirect(url_for("mycart"))
    elif data['ResultCode']=='0':
        flash('Transaction successful!')
        mpesaref=data['MpesaReceiptNumber']
        return redirect(url_for('paid',mpesaref=mpesaref))
    return render_template('redirect.html')


#process transaction
@app.route('/paid/<mpesaref>')
@login_required
def paid(mpesaref):
    delivery=str(dlocation)
    buyer_id=buyerid
    buyer_name=str(buyername)
    seller_id=str(sellerid)
    seller_name=str(sellername)
    seller_contact=str(sellercontact)
    product_name=str(productname)
    
    code= ''.join(random.choices(string.ascii_uppercase + string.digits, k=5))
    integ=random.randint(1000,9999)

    order_number=str(code) + str(integ)
    mpesaref=mpesaref
    if mpesaref:
        new_order=Transactions(delivery=delivery,buyer_id=buyer_id,buyer_name=buyer_name,seller_contact=seller_contact,seller_id=seller_id,seller_name=seller_name,product_name=product_name,mpesaref=mpesaref,order_number=order_number)
        db.session.add(new_order)
        db.session.commit()
        flash("Order placed successfully, wait for delivery.")
        return redirect(url_for('myorders'))
    return render_template('paid.html',mpesaref=mpesaref,order_number=order_number)

@app.route('/myorders')
@login_required
def myorders():
    myorders=Transactions.query.filter_by(buyer_id=current_user.id).all()
    return render_template('myorders.html',myorders=myorders)
#get mpesa access token
def getAccesstoken():
    consumer_key = "2F1rXrdxPotCuFTl3tNpQqoy0mFAiZlbZ2Gb4IiOOXwXoCHc"
    consumer_secret = "PltOtNCa4odKGGz8mC1ZssdvDaCbz2w1SK1jpEE3MZ506DoAHo32ssoTBzE5hO7g"
    endpoint = "https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials"
    r = requests.get(endpoint, auth=HTTPBasicAuth(consumer_key, consumer_secret))
    access_token = r.json()['access_token']
    time.sleep(3)
    return access_token
#start app
if __name__=='__main__':  
    with app.app_context():
        db.create_all()  
    app.run(host='0.0.0.0',debug=True)