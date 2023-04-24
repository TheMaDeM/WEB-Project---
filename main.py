from datetime import date
from datetime import datetime as dt

from flask import Flask, render_template, redirect, request, abort
from flask_login import LoginManager, login_user, login_required, logout_user, current_user

from data import db_session
from data.ads import Ad
from data.users import User
from forms.ad import AdsForm1, AdsForm2
from forms.user import RegisterForm, LoginForm, EditForm, DataForm

app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'
login_manager = LoginManager()
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


@app.route("/")
def index():
    db_sess = db_session.create_session()
    ads = db_sess.query(Ad)
    return render_template("index.html", ads=ads, title='Главная страница')


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
                                   message="Эта почта уже использована")
        if db_sess.query(User).filter(User.name == form.name.data).first():
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Пользователь с таким именем уже есть")
        if db_sess.query(User).filter(User.phone_num == form.phone_num.data).first():
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Этот номер телефона уже использован")
        user = User(
            name=form.name.data,
            email=form.email.data,
            about=form.about.data,
            phone_num=form.phone_num.data
        )
        user.set_password(form.password.data)
        db_sess.add(user)
        db_sess.commit()
        return redirect('/login')
    return render_template('register.html', title='Регистрация', form=form)


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


@app.route('/profile')
def my_profile():
    return render_template('profile.html', title='Мой профиль', user=current_user)


@app.route('/profile/<int:id>')
def profile(id):
    db_sess = db_session.create_session()
    user = db_sess.query(User).filter(User.id == id).first()
    if user:
        return render_template('profile.html', title='Профиль пользователя', user=user)
    else:
        abort(404)


@app.route('/profile/edit', methods=['GET', 'POST'])
def edit_my_profile():
    form = EditForm()
    if request.method == "GET":
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.name == current_user.name).first()
        if user:
            form.name.data = user.name
            form.phone_num.data = user.phone_num
            form.about.data = user.about
        else:
            abort(404)
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.name == current_user.name).first()
        if db_sess.query(User).filter(User.name == form.name.data).first()\
                and db_sess.query(User).filter(User.name == form.name.data).first() != current_user:
            return render_template('edit.html', title='Регистрация',
                                   form=form,
                                   message="Пользователь с таким именем уже есть")
        if db_sess.query(User).filter(User.phone_num == form.phone_num.data).first()\
                and db_sess.query(User).filter(User.phone_num == form.phone_num.data).first() != current_user:
            return render_template('edit.html', title='Регистрация',
                                   form=form,
                                   message="Этот номер телефона уже использован")
        if user:
            user.name = form.name.data
            user.phone_num = form.phone_num.data
            user.about = form.about.data
            db_sess.commit()
            return redirect('/')
        else:
            abort(404)
    return render_template('edit.html', title='Изменение профиля', form=form)


@app.route('/profile/edit/data', methods=['GET', 'POST'])
def edit_data():
    form = DataForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.email == current_user.email).first()
        if form.password.data != form.password_again.data:
            return render_template('data.html', title='Регистрация',
                                   form=form,
                                   message="Пароли не совпадают")
        if db_sess.query(User).filter(User.email == form.email.data).first()\
                and db_sess.query(User).filter(User.email == form.email.data).first() != current_user:
            return render_template('data.html', title='Регистрация',
                                   form=form,
                                   message="Эта почта уже использована")
        user.email = form.email.data
        user.set_password(form.password.data)
        db_sess.commit()
        return redirect('/')
    return render_template('data.html', title='Изменение данных', form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")


@app.route('/ad',  methods=['GET', 'POST'])
@login_required
def add_ad():
    form = AdsForm1()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        f = form.image.data
        filename = f'{date.today().year}{date.today().month}{date.today().day}' \
                   f'{dt.now().time().hour}{dt.now().time().minute}{dt.now().time().second}'
        f.save(f'static/img/{filename}.png')
        ad = Ad(title=form.title.data,
                price=form.price.data,
                content=form.content.data,
                image=filename)
        current_user.ad.append(ad)
        db_sess.merge(current_user)
        db_sess.commit()
        return redirect('/')
    return render_template('ad.html', title='Добавление новости', form=form, file=True)


@app.route('/ad/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_ad(id):
    form = AdsForm2()
    if request.method == "GET":
        db_sess = db_session.create_session()
        ad = db_sess.query(Ad).filter(Ad.id == id, Ad.user == current_user).first()
        if ad:
            form.title.data = ad.title
            form.price.data = ad.price
            form.content.data = ad.content
        else:
            abort(404)
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        ad = db_sess.query(Ad).filter(Ad.id == id, Ad.user == current_user).first()

        if ad:
            ad.title = form.title.data
            ad.price = form.price.data
            ad.content = form.content.data
            db_sess.commit()
            return redirect('/')
        else:
            abort(404)
    return render_template('ad.html', title='Редактирование новости', form=form, file=False, id=id)


@app.route('/ad/file/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_file(id):
    form = AdsForm1()
    if request.method == "GET":
        db_sess = db_session.create_session()
        ad = db_sess.query(Ad).filter(Ad.id == id, Ad.user == current_user).first()
        if ad:
            form.title.data = ad.title
            form.price.data = ad.price
            form.content.data = ad.content
        else:
            abort(404)
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        ad = db_sess.query(Ad).filter(Ad.id == id, Ad.user == current_user).first()
        if ad:
            f = form.image.data
            filename = f'{date.today().year}{date.today().month}{date.today().day}' \
                       f'{dt.now().time().hour}{dt.now().time().minute}{dt.now().time().second}'
            f.save(f'static/img/{filename}.png')
            ad.title = form.title.data
            ad.price = form.price.data
            ad.content = form.content.data
            ad.image = filename
            db_sess.commit()
            return redirect('/')
        else:
            abort(404)
    return render_template('ad.html', title='Редактирование новости', form=form, file=True)


@app.route('/ad_delete/<int:id>', methods=['GET', 'POST'])
@login_required
def ad_delete(id):
    db_sess = db_session.create_session()
    ad = db_sess.query(Ad).filter(Ad.id == id, Ad.user == current_user).first()
    if ad:
        db_sess.delete(ad)
        db_sess.commit()
    else:
        abort(404)
    return redirect('/')


@app.route('/ad/detail/<int:id>')
def ad_detail(id):
    db_sess = db_session.create_session()
    ad = db_sess.query(Ad).filter(Ad.id == id).first()
    if ad:
        return render_template('detail.html', title='Подробности объявления', ad=ad)
    else:
        abort(404)


def main():
    db_session.global_init("db/blogs.db")
    app.run()


if __name__ == '__main__':
    main()