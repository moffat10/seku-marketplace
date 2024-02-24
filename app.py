from flask import Flask,render_template,request,redirect,url_for,flash
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail,Message
from werkzeug.security import generate_password_hash,check_password_hash
from flask_login import LoginManager,login_required,logout_user,login_user,UserMixin,current_user
from werkzeug.utils import secure_filename
import os
import random

app=Flask(__name__)
app.config['SECRET_KEY']=os.environ.get['SECRET_KEY']
app.config['SQLALCHEMY_DATABASE_URI']='sqlite:///database.db'
app.config['UPLOAD_FOLDER']='static/files'
app.config['MAIL_SERVER']='smtp.gmail.com'
app.config['MAIL_PORT']=465
app.config['MAIL_USE_TLS']=False
app.config['MAIL_USE_SSL']=True
app.config['MAIL_USERNAME']='sekumarket@gmail.com'
app.config['MAIL_PASSWORD']=os.environ.get['PASSWORD']



db=SQLAlchemy(app)
login_manager=LoginManager()
login_manager.init_app(app)
login_manager.login_view="login"
mail=Mail(app)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


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
    
class Products(db.Model,UserMixin):
    id=db.Column(db.Integer,primary_key=True)
    name=db.Column(db.String(50),nullable=False)
    description=db.Column(db.String(100),nullable=False)
    image_url=db.Column(db.String(50),nullable=False)
    category=db.Column(db.String(20),nullable=False)
    product_nature=db.Column(db.String(50),nullable=False)
    price=db.Column(db.String(50),nullable=False)
    price_terms=db.Column(db.String(50),nullable=False)
    seller_name=db.Column(db.String(50),nullable=False)
    seller_contact=db.Column(db.String(50),nullable=False)
    seller_id=db.Column(db.Integer,db.ForeignKey('user.id'))

class Passrecovery(db.Model,UserMixin):
    id=db.Column(db.Integer,primary_key=True)
    email=db.Column(db.String(50),unique=True,nullable=False)
    code=db.Column(db.String(50),unique=True,nullable=False)

@app.route('/')
def home():
    all_products=Products.query.limit(8).all()
    return render_template('home.html',all_products=all_products)

@app.route('/categories')
def cat_return():
    return render_template('categories.html')

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

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('logged out')
    return redirect(url_for('login'))

@app.route('/dashboard',methods=['GET','POST'])
@login_required
def dashboard():
    user_products=Products.query.filter_by(seller_id=current_user.id)
    return render_template('dashboard.html',user_products=user_products)

@app.route('/addproduct',methods=['GET','POST'])
@login_required
def addproduct():
    if request.method=="POST":
        uploaded_file=request.files["product_image"]
        filename=secure_filename(uploaded_file.filename)
        uploaded_file.save(os.path.join(app.config['UPLOAD_FOLDER'],filename))
        image_url='/static/files/'+filename
        name=request.form['product_name']
        description=request.form['Description']
        category=request.form['category']
        product_nature=request.form['product_nature']
        price=request.form['price']
        price_terms=request.form['price_terms']
        seller_id=current_user.id
        seller_name=current_user.username
        seller_contact=current_user.phone_number
        new_product=Products(name=name,description=description,image_url=image_url,category=category,product_nature=product_nature,price=price,price_terms=price_terms,seller_id=seller_id,seller_name=seller_name,seller_contact=seller_contact)
        db.session.add(new_product)
        db.session.commit()
        flash('Product Added successfully')
        return redirect(url_for('dashboard'))
    return render_template('addproduct.html')

@app.route('/advertise')
def advertise():
    return render_template('advert.html')
 
@app.route('/category/<cat>',methods=['POST','GET'])
def cat_view(cat):
    viewed=Products.query.filter_by(category=cat)
    return render_template('category_view.html',viewed=viewed)

@app.route('/product/<id>')
def proview(id):
    product_description=Products.query.filter_by(id=id)
    return render_template('product.html',product_description=product_description)
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
    
                
                



if __name__=='__main__':  
    with app.app_context():
        db.create_all()  
    app.run(host='0.0.0.0',debug=True)