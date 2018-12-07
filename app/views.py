from flask import render_template, flash, redirect, session, url_for, current_app, request, make_response
from flask_admin.contrib.sqla import ModelView
from flask_login import current_user, login_user, login_required
from flask_principal import Identity, AnonymousIdentity,identity_changed
from datetime import datetime
from werkzeug.urls import url_parse
from app import app, db,admin_permission
from .models import User,Post,UserRole,Comment,Tag,posts_tags
from .forms import LoginForm,RegistrationForm,PasswordForm,EditProfileForm,PostForm,CommentForm
from sqlalchemy import func
import os,random
from flask_login import logout_user
from flask_admin import Admin,AdminIndexView,expose


class MyAdminIndexView(AdminIndexView):
    def is_accessible(self):
        return admin_permission

    def inaccessible_callback(self, name, **kwargs):
        flash("You have no authority to access this page!")
        if current_user.is_authenticated:
             app.logger.warning('"%s"is try to access the admin page',current_user.username)
             return redirect(url_for('index', next=request.url))
        else:
            app.logger.warning('Anonymous usr tried to access the background')
            return redirect(url_for('index', next=request.url))

    @expose('/')
    def index(self):
        # Get URL for the test view method
        user = User.query.count()
        posts = Post.query.count()
        tags = Tag.query.count()
        return self.render('admin/welcom.html',
                           users=user,
                           posts=posts,
                           tags=tags,
                           url = '/admin')


admin = Admin(app,template_mode='bootstrap3',
                  index_view=MyAdminIndexView())


class MyViewAll(ModelView):
    def after_model_delete(self, model):
        app.logger.info('Admin "%s" deleted the "%s"',current_user.username, model)

    def after_model_change(self, form, model, is_create):
        app.logger.info('Admin "%s" updated the "%s"', current_user.username, model)


class MyView(MyViewAll):
    column_exclude_list = ('password_hash')
    form_excluded_columns = ('posts', 'comments')


class MyViewpost(MyViewAll):
    form_excluded_columns = ('comments')
    page_size = 6


admin.add_view(MyView(User, db.session))
admin.add_view(MyViewpost(Post, db.session))
admin.add_view(MyViewAll(Comment, db.session))
admin.add_view(MyViewAll(Tag, db.session))



@app.route('/')
@app.route('/index<int:page>')
def index(page=1):
    if current_user.is_anonymous:
        posts = Post.query.order_by(
            Post.timestamp.desc()
        ).paginate(page,3,False)
        recent, top_tags = sidebar_data()

        return render_template('base/index.html',
                               posts=posts,
                               recent=recent,
                               top_tags=top_tags)
    else:
        role = UserRole.query.filter_by(user_id = current_user.id).first()
        posts = Post.query.order_by(
            Post.timestamp.desc()
        ).paginate(page,3,False)
        recent, top_tags = sidebar_data()

        return render_template('base/index.html',
                               posts=posts,
                               recent=recent,
                               top_tags=top_tags,
                               role=role)


@app.route('/login',methods=['GET','POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    # Check the form data
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            # log information
            app.logger.info('"%s" logged in failed', form.username.data)
            return redirect(url_for('login'))
        identity_changed.send(current_app._get_current_object(), identity=Identity(user.id))
        login_user(user, remember=form.remember_me.data)

        #log information
        app.logger.info('"%s" logged in successfully', user.username)

        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('index')
        return redirect(next_page)
    return render_template('user/login.html',title='Login',form=form)


@app.route('/logout')
def logout():
    try:
        # log information
        app.logger.info('"%s" logged out successfully', current_user.username)
        logout_user()
        # Remove session keys set by Flask-Principal
        for key in ('identity.name', 'identity.auth_type'):
            session.pop(key, None)
        # Tell Flask-Principal the user is anonymous
        identity_changed.send(current_app._get_current_object(),
                              identity=AnonymousIdentity())
        return redirect(url_for('index'))
    except Exception as e:
        # log information
        app.logger.info('"%s" logged out failed', current_user.username)
        flash("Logout failed")
        redirect(url_for('index'))


@app.route('/cookies')
def privacy():
    return render_template('base/privacy.html')



@app.route('/register', methods=['GET', 'POST'])
def register():
    # 判断当前用户是否验证，如果通过的话返回首页
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data,email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        userrole = UserRole(user_id=user.id)
        userrole.role_id = 2
        db.session.add(userrole)
        db.session.commit()
        flash('Welcome to join us!')
        # log information
        app.logger.info('"%s" registered successfully', user.username)
        return redirect(url_for('login'))
    return render_template('user/register.html', title='register', form=form)


@app.route('/user/password',methods=['GET','POST'])
@login_required
def security():
    form = PasswordForm()
    if form.validate_on_submit():
        if not current_user.check_password(form.password.data):
            flash('The original password is wrong')
            # log information
            app.logger.info('"%s" changed password failed', current_user.username)
            return redirect(url_for('security'))
        else:
            current_user.set_password(form.passwordnew.data)
            db.session.commit()
            flash('Success! Please login again')
            # log information
            app.logger.info('%s changed password', current_user.username)
            return redirect(url_for('logout'))
    return render_template('user/pawedit.html', title='password_edit',
                           form=form)


@app.route('/user/<username>')
def user(username):
    user = User.query.filter_by(username=username).first_or_404()
    userid = user.id
    posts = Post.query.order_by(
        Post.timestamp.desc()
    ).filter_by(user_id=userid)
    return render_template('user/user.html',user=user,posts=posts)


@app.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm()
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.about_me = form.about_me.data
        db.session.commit()
        flash('Your profile has changed!')

        # log information
        app.logger.info('"%s" has edited profile', current_user.username)

        return redirect(url_for('user', username=current_user.username))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.about_me.data = current_user.about_me
    return render_template('user/edit_profile.html', title='Profile Editor',
                           form=form)


@app.route('/new_post', methods=['GET', 'POST'])
@login_required
def new_post():
    """View function for new_port."""
    form = PostForm()
    if form.validate_on_submit():
        new_post = Post(title=form.title.data)
        new_post.body = form.body.data
        new_post.timestamp = datetime.now()
        new_post.user_id = current_user.id
        new_post.tags.name = form.tags.data
        print("wow")
        for t in form.tags.data:
            tag = Tag.query.get(t)
            new_post.tags.append(tag)
            print(2)
        db.session.add(new_post)
        db.session.commit()
        flash("Create succss!")
        # log information
        app.logger.info('"%s" has post a new post "%s"', current_user.username,new_post.title)
        return redirect(url_for('index'))

    return render_template('post/new_post.html',
                           form=form)


@app.route('/edit/<id>', methods=['GET', 'POST'])
def edit_post(id):
    """View function for edit_post."""
    post = Post.query.get_or_404(id)
    form = PostForm()

    if post.author.id != current_user.id:
        # log information
        app.logger.warning('"%s" tried to edit post "%s" with no authority', current_user.username, post.title)
        flash ("You have no authority to edit")
        return redirect(url_for('index'))

    if form.validate_on_submit():
        post.title = form.title.data
        post.body = form.body.data
        post.tags.name = form.tags.data
        post.timestamp = datetime.now()
        for t  in form.tags.data:
            tag = Tag.query.get(t)
            post.tags.append(tag)

        # Update the post
        db.session.add(post)
        db.session.commit()
        # log information
        app.logger.info('"%s" has deleted post "%s"', current_user.username, post.title)
        return redirect(url_for('post', post_id=post.id))

    form.title.data = post.title
    form.body.data = post.body

    return render_template('post/edit_post .html', form=form, post=post)


@app.route('/delete_post/<id>', methods=['GET'])
def delete_post(id):
    post = Post.query.get(id)
    db.session.delete(post)
    db.session.commit()
    flash("Delete succss!")
    # log information
    app.logger.info('"%s" has deleted post "%s"', current_user.username, post.title)
    return redirect(url_for("user",username=current_user.username))


def sidebar_data():
    """Set the sidebar function."""
    # Get post of recent
    recent = db.session.query(Post).order_by(
            Post.timestamp.desc()
        ).limit(5).all()

    # Get the tags and sort by count of posts.
    top_tags = db.session.query(
            Tag, func.count(posts_tags.c.post_id).label('total')
        ).join(
            posts_tags
        ).group_by(Tag).order_by('total DESC').limit(5).all()
    return recent, top_tags


@app.route('/post/<post_id>', methods=('GET', 'POST'))
def post(post_id):
    """View function for post page"""
    # Form object: `Comment`
    form = CommentForm()
    # form.validate_on_submit() will be true and return the
    # data object to form instance from user enter,
    # when the HTTP request is POST
    if form.validate_on_submit():
        new_comment = Comment(user_id = current_user.id)
        new_comment.text = form.text.data
        new_comment.date = datetime.now()
        new_comment.post_id = post_id
        db.session.add(new_comment)
        db.session.commit()
        # log information
        app.logger.info('"%s" has commented on post "%s"', current_user.username, new_comment.posts.title)

    post = Post.query.get_or_404(post_id)
    tags = post.tags
    comments = post.comments.order_by(Comment.date.desc()).all()
    recent, top_tags = sidebar_data()

    return render_template('post/post.html',
                               post=post,
                               tags=tags,
                               comments=comments,
                               form=form,
                               recent=recent,
                               top_tags=top_tags)


@app.route('/tag/<string:tag_name>')
def tag(tag_name):
    """View function for tag page"""

    tag = Tag.query.filter_by(name=tag_name).first_or_404()
    posts = tag.posts.order_by(Post.timestamp.desc()).all()
    recent, top_tags = sidebar_data()

    return render_template('post/tags.html',
                           tag=tag,
                           posts=posts,
                           recent=recent,
                           top_tags=top_tags)


def gen_rnd_filename():
    filename_prefix = datetime.now().strftime('%Y%m%d%H%M%S')
    return '%s%s' % (filename_prefix, str(random.randrange(1000, 10000)))


@app.route('/ckupload/', methods=['POST', 'OPTIONS'])
def ckupload():
    """CKEditor file upload"""
    error = ''
    url = ''
    callback = request.args.get("CKEditorFuncNum")

    if request.method == 'POST' and 'upload' in request.files:
        fileobj = request.files['upload']
        fname, fext = os.path.splitext(fileobj.filename)
        rnd_name = '%s%s' % (gen_rnd_filename(), fext)

        filepath = os.path.join(app.static_folder, 'upload', rnd_name)

        # 检查路径是否存在，不存在则创建
        dirname = os.path.dirname(filepath)
        if not os.path.exists(dirname):
            try:
                os.makedirs(dirname)
            except:
                error = 'ERROR_CREATE_DIR'
        elif not os.access(dirname, os.W_OK):
            error = 'ERROR_DIR_NOT_WRITEABLE'

        if not error:
            fileobj.save(filepath)
            url = url_for('static', filename='%s/%s' % ('upload', rnd_name))
            print(url)
    else:
        error = 'post error'

    res = """<script type="text/javascript">
  window.parent.CKEDITOR.tools.callFunction(%s, '%s', '%s');
</script>""" % (callback, url, error)

    response = make_response(res)
    response.headers["Content-Type"] = "text/html"
    return response

