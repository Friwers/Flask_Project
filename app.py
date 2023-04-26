from flask import Flask, url_for, request, render_template, redirect, abort
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from flask_restful import Api
from sqlalchemy import and_

from data import db_session, product_resources
from data.cart import Cart
from data.category import Category
from data.products import Product
from data.users import User
from forms.login_forms import LoginForm
from forms.product import ProductForm
from forms.search import SearchForm
from forms.user import RegisterForm, UserEditForm
from image import byte_img_to_html

app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'
api = Api(app)

login_manager = LoginManager()
login_manager.init_app(app)



@app.route('/')
def index():
    db_sess = db_session.create_session()
    products = db_sess.query(Product)
    lst = []
    for i in products:
        s = []
        for j in i.categories:
            s.append(j.name)
        lst.append((i, ' '.join(s)))
    return render_template('index.html', title='Товары', products=lst)


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.email == form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect("/")
        return render_template('login.html',
                               message="Неправильный логин или пароль",
                               form=form)
    return render_template('login.html', title='Авторизация', form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Пароли не совпадают")
        db_sess = db_session.create_session()
        if db_sess.query(User).filter(User.email == form.email.data).first():
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Такой пользователь уже есть")
        user = User(
            name=form.name.data,
            surname=form.surname.data,
            email=form.email.data,
            age=form.age.data,
            address=form.address.data,
            is_admin=False
        )
        user.set_password(form.password.data)
        db_sess.add(user)
        db_sess.commit()

        return redirect('/login')
    return render_template('register.html', title='Регистрация', form=form)


@app.route('/user/ed/<int:user_id>', methods=['GET', 'POST'])
@login_required
def edit_user(user_id):
    form = UserEditForm()
    db_sess = db_session.create_session()
    if request.method == "GET":
        if current_user.id == user_id or current_user.is_admin:
            user = db_sess.query(User).filter(User.id == user_id).first()
            if user:
                form.email.data = user.email
                form.name.data = user.name
                form.surname.data = user.surname
                form.age.data = user.age
                form.address.data = user.address
                form.is_admin.data = user.is_admin
            else:
                abort(404)
        else:
            abort(404)
    if form.validate_on_submit():
        user = db_sess.query(User).filter(User.id == user_id).first()
        if user:
            user.email = form.email.data
            user.name = form.name.data
            user.surname = form.surname.data
            user.age = form.age.data
            user.address = form.address.data
            user.is_admin = form.is_admin.data
            if form.password.data:
                user.set_password(form.password.data)
            db_sess.commit()
            return redirect('/')
        else:
            abort(404)
    return render_template('register.html', edit=True, title='Редактирование', form=form)


@app.route('/user/<int:user_id>', methods=['GET', 'POST'])
@login_required
def user(user_id):
    db_sess = db_session.create_session()
    user = db_sess.query(User).filter(User.id == user_id).first()
    return render_template('user.html', title='Страница', user=user)


@app.route('/addproduct', methods=['GET', 'POST'])
@login_required
def add_product():
    form = ProductForm()
    db_sess = db_session.create_session()
    categories = db_sess.query(Category).all()
    form.category.choices = [(i.id, i.name) for i in categories]
    if request.method == 'POST':
        product = Product()
        product.title = form.title.data
        product.price = form.price.data
        product.about = form.about.data
        product.count = form.count.data
        product.categories.extend(
            db_sess.query(Category).filter(Category.id.in_(form.category.data)).all())

        if request.files['img']:
            product.image = byte_img_to_html(request.files['img'])

        product.manufacturer = current_user
        db_sess.merge(product)

        db_sess.commit()
        return redirect('/')
    return render_template('product.html', title='Добавление продукта',
                           form=form)


@app.route('/editproduct/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_product(id):
    form = ProductForm()
    db_sess = db_session.create_session()
    categories = db_sess.query(Category).all()
    form.category.choices = [(i.id, i.name) for i in categories]
    if request.method == "GET":
        product = db_sess.query(Product).filter(Product.id == id, Product.manufacturer == current_user).first()
        if product:
            form.title.data = product.title
            form.price.data = product.price
            form.about.data = product.about
            form.count.data = product.count
            form.category.data = [i.id for i in categories]
        else:
            abort(404)
    if form.validate_on_submit():
        product = db_sess.query(Product).filter(Product.id == id, Product.manufacturer == current_user).first()
        if product:
            form.title.data = product.title
            form.price.data = product.price
            form.about.data = product.about
            product.count = form.count.data
            product.categories = []
            product.categories.extend(
                db_sess.query(Category).filter(Category.id.in_(form.category.data)).all())
            db_sess.commit()
            return redirect('/')
        else:
            abort(404)
    return render_template('product.html',
                           title='Редактирование продукта',
                           form=form
                           )


@app.route('/product_delete/<int:product_id>', methods=['GET', 'POST'])
@login_required
def product_delete(product_id):
    db_sess = db_session.create_session()
    if current_user.is_admin:
        product = db_sess.query(Product).filter(Product.id == product_id,
                                                Product.manufacturer == current_user).first()
    else:
        product = None
    if product:
        db_sess.delete(product)
        db_sess.commit()
    else:
        abort(404)
    return redirect('/')


@app.route('/sort_increase')
def sort_increase():
    db_sess = db_session.create_session()
    products = db_sess.query(Product).order_by(Product.price)
    lst = []
    for i in products:
        s = []
        for j in i.categories:
            s.append(j.name)
        lst.append((i, ' '.join(s)))
    return render_template('index.html', title='Товары', products=lst)


@app.route('/sort_descending')
def sort_descending():
    db_sess = db_session.create_session()
    products = db_sess.query(Product).order_by(Product.price)
    lst = []
    for i in products:
        s = []
        for j in i.categories:
            s.append(j.name)
        lst.append((i, ' '.join(s)))
    return render_template('index.html', title='Товары', products=reversed(lst))


@app.route('/sort_recent')
def sort_recent():
    db_sess = db_session.create_session()
    products = db_sess.query(Product).order_by(Product.modified_date)
    lst = []
    for i in products:
        s = []
        for j in i.categories:
            s.append(j.name)
        lst.append((i, ' '.join(s)))
    return render_template('index.html', title='Товары', products=reversed(lst))


@app.route('/sort_old')
def sort_old():
    db_sess = db_session.create_session()
    products = db_sess.query(Product).order_by(Product.modified_date)
    lst = []
    for i in products:
        s = []
        for j in i.categories:
            s.append(j.name)
        lst.append((i, ' '.join(s)))
    return render_template('index.html', title='Товары', products=(lst))


@app.route('/cart_fill/<int:product_id>', methods=['GET', 'POST'])
@login_required
def cart_fill(product_id):
    db_sess = db_session.create_session()
    product = db_sess.query(Product).get(product_id)
    user_cart = Cart()
    user_cart.product = product
    user_cart.customer = current_user.email
    db_sess.merge(user_cart)
    db_sess.commit()
    return redirect('/')


@app.route('/clean', methods=['GET', 'POST'])
@login_required
def clean():
    db_sess = db_session.create_session()
    products = db_sess.query(Cart).filter(Cart.customer == current_user.email).all()
    for i in products:
        db_sess.delete(i)
    db_sess.commit()
    return redirect('/cart')


@app.route('/del_product/<int:product_id>', methods=['GET', 'POST'])
@login_required
def del_product(product_id):
    db_sess = db_session.create_session()
    product = db_sess.query(Cart).filter(Cart.id == product_id, Cart.customer == current_user.email).first()
    db_sess.delete(product)
    db_sess.commit()
    return redirect('/cart')


@app.route('/cart', methods=['GET', 'POST'])
@login_required
def cart():
    db_sess = db_session.create_session()
    products = db_sess.query(Cart).filter(Cart.customer == current_user.email).all()
    return render_template('cart.html', title='Корзина', products=products)


@app.route('/buy', methods=['GET', 'POST'])
@login_required
def buy():
    db_sess = db_session.create_session()
    cart = db_sess.query(Cart).filter(Cart.customer == current_user.email).all()
    for i in cart:
        i.product.count -= 1
    db_sess.commit()
    return redirect('/clean')

@app.route('/buy_one/<int:product_id>', methods=['GET', 'POST'])
@login_required
def buy_one(product_id):
    db_sess = db_session.create_session()
    cart = db_sess.query(Cart).filter(Cart.id == product_id, Cart.customer == current_user.email).first()
    cart.product.count -= 1
    db_sess.delete(cart)
    db_sess.commit()
    return redirect('/cart')


@app.route('/category', methods=['GET', 'POST'])
@login_required
def category():
    form = ProductForm()
    db_sess = db_session.create_session()
    if request.method == 'POST':
        print(form.title.data)
        category = Category()
        category.name = form.title.data

        db_sess.add(category)
        db_sess.commit()
        return redirect('/')
    return render_template('category.html', title='Добавление категории',
                           form=form)


if __name__ == '__main__':
    db_session.global_init("db/store.db")
    app.run(port=8080, host='127.0.0.1')
