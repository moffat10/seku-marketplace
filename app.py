from flask import Flask,render_template,request,redirect,url_for,flash
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash,check_password_hash
from flask_login import LoginManager,login_required,logout_user,login_user,UserMixin,current_user
from werkzeug.utils import secure_filename
import os

app=Flask(__name__)
app.config['SECRET_KEY']='saystheking'
app.config['SQLALCHEMY_DATABASE_URI']='sqlite:///database.db'
app.config['UPLOAD_FOLDER']='static/files'
db=SQLAlchemy(app)
login_manager=LoginManager()
login_manager.init_app(app)
login_manager.login_view="login"

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class User(db.Model,UserMixin):
    id=db.Column(db.Integer,primary_key=True)
    username=db.Column(db.String(50),unique=True,nullable=False)
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
    seller_id=db.Column(db.Integer,db.ForeignKey('user.id'))

@app.route('/')

def home():
    all_products=Products.query.all()
    return render_template('home.html',all_products=all_products)

@app.route('/templates/categories')
def cat_return():
    return render_template('categories.html')

@app.route('/templates/create-seller',methods=['GET','POST'])
def create_seller():
    if request.method=='POST':
        username=request.form['username']
        location=request.form['location']
        phone_number=request.form['phone_number']
        password=request.form['password']
        hashed_password=generate_password_hash(password,method='sha256')
        new_user=User(username=username,password=hashed_password,phone_number=phone_number,location=location)
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



@app.route('/templates/login',methods=['GET','POST'])
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
        new_product=Products(name=name,description=description,image_url=image_url,category=category,product_nature=product_nature,price=price,price_terms=price_terms,seller_id=seller_id)
        db.session.add(new_product)
        db.session.commit()
        flash('Product Added successfully')
        return redirect(url_for('dashboard'))
    return render_template('addproduct.html')

@app.route('/templates/advertise')
def advertise():
    return render_template('advert.html')
def proadd():
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
    new_product=Products(name=name,description=description,image_url=image_url,category=category,product_nature=product_nature,price=price,price_terms=price_terms,seller_id=seller_id)
    db.session.add(new_product)
    db.session.commit()
    return redirect(url_for('dashboard'))
app.jinja_env.globals.update(proadd=proadd)

if __name__=='__main__':
    with app.app_context():
        db.create_all()
    app.run(host='0.0.0.0',debug=True)