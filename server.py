import datetime

from flask import Flask, render_template, redirect, url_for, request
from flask_bootstrap import Bootstrap5
from flask_ckeditor import CKEditor, CKEditorField
from flask_wtf import FlaskForm
from sqlalchemy import select, String, Text, create_engine, update, delete
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, Session
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired

DATA_ENDPOINT = 'https://api.npoint.io/0cf2baa2b063e8a67ce3'
app = Flask(__name__)
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'
bootstrap = Bootstrap5(app)
ckeditor = CKEditor(app)


class Base(DeclarativeBase):
    pass


class BlogPost(Base):
    __tablename__ = 'blog_post'
    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(250))
    date: Mapped[str] = mapped_column(String(250))
    body: Mapped[str] = mapped_column(Text)
    author: Mapped[str] = mapped_column(String(250))
    img_url: Mapped[str] = mapped_column(String(250))
    subtitle: Mapped[str] = mapped_column(String(250))


engine = create_engine('sqlite:///posts.db')
Base.metadata.create_all(engine)


class NewPostForm(FlaskForm):
    title = StringField(validators=[DataRequired()])
    subtitle = StringField(validators=[DataRequired()])
    author = StringField(validators=[DataRequired()])
    img_URL = StringField(validators=[DataRequired()])
    body = CKEditorField(validators=[DataRequired()])
    submit = SubmitField('Submit Post')


@app.route('/')
def get_homepage():
    with Session(engine) as session:
        stmt = select(BlogPost)
        data = session.execute(stmt).scalars().all()
    return render_template('index.html', posts=data)


@app.route('/new-post', methods=['GET', 'POST'])
def make_post():
    make_post_form = NewPostForm()
    if request.method == 'POST' and make_post_form.validate_on_submit():
        date_now = datetime.date.today().strftime('%B %d, %G')
        data = BlogPost(title=make_post_form.title.data,
                        date=date_now, body=make_post_form.body.data,
                        author=make_post_form.author.data,
                        img_url=make_post_form.img_URL.data,
                        subtitle=make_post_form.subtitle.data)
        with Session(engine) as session:
            session.add(data)
            session.commit()

    return render_template('make-post.html', form=make_post_form)


@app.route('/posts/<int:post_id>')
def get_post(post_id):
    with Session(engine) as session:
        stmt = select(BlogPost).where(BlogPost.id == post_id)
        data = session.execute(stmt).scalar_one()
    return render_template('post.html', post=data)


@app.route('/edit_post/<int:post_id>', methods=['GET', 'POST'])
def edit_post(post_id):
    date_now = datetime.date.today().strftime('%B %d, %G')
    req = request.args.get(post_id)
    with Session(engine) as session:
        stmt = select(BlogPost).where(BlogPost.id == post_id)
        data = session.execute(stmt).scalar_one()
    form_data = NewPostForm(title=data.title,
                            body=data.body,
                            author=data.author,
                            img_URL=data.img_url,
                            subtitle=data.subtitle)

    if request.method == 'POST' and form_data.validate_on_submit():
        with Session(engine) as session:
            stmt = update(BlogPost).where(BlogPost.id == post_id).values(title=form_data.title.data,
                                                                         body=form_data.body.data,
                                                                         author=form_data.author.data,
                                                                         img_url=form_data.img_URL.data,
                                                                         subtitle=form_data.subtitle.data)
            session.execute(stmt)
            session.commit()
        return redirect(url_for('get_post', post_id=post_id))

    return render_template('make-post.html', form=form_data, rule='edit')


@app.route('/delete/<post_id>')
def delete_post(post_id):
    req = request.args.get(post_id)
    with Session(engine) as session:
        stmt = delete(BlogPost).where(BlogPost.id == post_id)
        data = session.execute(stmt)
        session.commit()
    return redirect(url_for('get_homepage'))


@app.route('/get_contact', methods=['POST'])
def get_contact():
    name = request.form['name']
    email = request.form['email']
    message = request.form['message']
    return f"<h1> name is: {name}\n email is: {email}\n and the message is:\n {message} </h1>"


@app.route('/about')
def about():
    return render_template('about.html')


@app.route('/contact')
def contact():
    return render_template('contact.html')


if __name__ == '__main__':
    app.run(debug=True)
