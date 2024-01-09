import requests.cookies
from database import *
import smtplib, random, datetime, jdatetime, jwt, os, mimetypes, re

mimetypes.init()
app.app_context().push()
db.create_all()

path = './static/files'

def send_email(email):
    email_host = 'smtp.gmail.com'
    email_host_user = 'seyedparsaarabi8824@gmail.com'
    email_port_ssl = 465
    email_host_password = '****************'
    code = str(random.randint(100000, 999999))
    with smtplib.SMTP_SSL(email_host, email_port_ssl) as server:
        server.login(email_host_user, email_host_password)
        server.sendmail(email_host_password, email,
                        'hello! Welcom to our site! \n your confirmation code: ' + code)
    return code


@app.route('/')
@limiter.limit("3 per seconds")
def index():
    if request.cookies.get("cookie"):
        try:
            name = jwt.decode(request.cookies.get('cookie'), app.secret_key, algorithms=["HS256"])
        except:
            flash("دوباره وارد شوید", "danger")
            resp = make_response(redirect("/login"))
            resp.delete_cookie("cookie")
            return resp
        return render_template("index.html", name=name['username'], files=Files.query.all(), page='index')
    else:
        return render_template("index.html")

@app.route("/login", methods=['GET', 'POST'])
@limiter.limit("3 per seconds")
def login():
    if request.cookies.get("cookie"):
        flash("شما در حساب کاربری خود وارد هستید", "danger")
        return redirect("/")
    else:
        if request.method == 'GET':
            return render_template("login.html")
        if request.method == 'POST':
            username = request.form.get('username')
            password = request.form.get('password')
            if User.query.filter_by(username=username).first():
                for users_for in range(len(User.query.all())):
                    if User.query.all()[users_for].password == password:
                        if User.query.all()[users_for].username == username:
                            if User.query.all()[users_for].email_status == True:
                                token = jwt.encode(
                                    {'username': username,
                                     'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=10)},
                                    app.config['SECRET_KEY'])
                                response = make_response(redirect("/"))
                                response.set_cookie("cookie", token, 60*24)
                                return response
                            if User.query.all()[users_for].email_status == False:
                                user = User.query.filter_by(username=username).first()
                                random_code = send_email(user.email)
                                user.email_code = random_code
                                db.session.commit()
                                flash("شما هنوز ایمیل خود را تایید نکردید!", "danger")
                                flash("ایمیل خود را چک کنید. کد را ارسال کردیم. ممکن است ایمیل به هرزنامه ها رفته باشد. برای تایید 3 دقیقه فرصت دارید",
                                      "info")
                                response = make_response(render_template("accept-email.html"))
                                response.set_cookie("temporary-cookie", username, 100)
                                return response
                else:
                    flash("این نام کاربری یا رمز درست نیست", "danger")
                    return redirect("/login")
            else:
                flash("کاربری با این مشخصات وجود ندارد", "warning")
                return redirect("/login")



@app.route("/new_file/<string:for_folder>", methods=['POST', 'GET'])
@limiter.limit("3 per seconds")
def new_file(for_folder):
    if request.cookies.get("cookie"):
        if request.method == 'GET':
            try:
                name = jwt.decode(request.cookies.get('cookie'), app.secret_key, algorithms=["HS256"])
            except:
                flash("دوباره وارد شوید", "danger")
                resp = make_response(redirect("/login"))
                resp.delete_cookie("cookie")
                return resp
            return render_template("new-file.html", name=name['username'], for_folder=for_folder)


        else:
            flash("شما ابتدا باید وارد شوید", "danger")
            return redirect("/login")

@app.route("/register_file", methods=['POST', 'GET'])
@limiter.limit("3 per seconds")
def register_file():
    if request.cookies.get("cookie"):
        if request.method == 'POST':
            try:
                name = jwt.decode(request.cookies.get('cookie'), app.secret_key, algorithms=["HS256"])
            except:
                flash("دوباره وارد شوید", "danger")
                resp = make_response(redirect("/login"))
                resp.delete_cookie("cookie")
                return resp
            file = request.files.get("file")
            for_folder_ = request.form.get("for_folder")
            file_extension = os.path.splitext(path + "(" + request.cookies.get("cookie") + ")" + file.filename)[1]
            print(file.filename)
            print(file_extension)
            mimestart = mimetypes.guess_type(path + "(" + name['username'] + ")" + file.filename)[0]

            if mimestart != None:
                mimestart = mimestart.split('/')[0]

            if mimestart == None:
                mimestart = 'Undefined'

            print("before")
            print(mimestart)
            print("after")

            if file:
                text_to_remove = file_extension
                filename_ = file.filename
                new_text = filename_.replace(text_to_remove, "")
                if Files.query.filter_by(name=file.filename, for_user=name['username']).first():
                    num = 1
                    while (True):
                        new_name = new_text + "(" + str(num) + ")" + file_extension
                        if Files.query.filter_by(name=new_name, for_user=name['username']).first():
                            num += 1
                        if not Files.query.filter_by(name=new_name, for_user=name['username']).first():
                            break

                if not Files.query.filter_by(name=file.filename, for_user=name['username']).first():
                    new_name = file.filename
                file.save(os.path.join(path, "(" + name['username'] + ")" + new_name))
                now = jdatetime.datetime.today()
                mm = str(now.month)
                dd = str(now.day)
                yyyy = str(now.year)
                hour = str(now.hour)
                mi = str(now.minute)
                ss = str(now.second)
                admin = Files(name=new_text,
                              url="./static/files/(" + name['username'] + ")" + new_name,
                              for_user=name['username'],
                              type=mimestart,
                              time=yyyy + "/" + mm + "/" + dd + " " + hour + ":" + mi,
                              format_=file_extension,
                              for_folder=for_folder_,
                              )
                db.session.add(admin)
                db.session.commit()
                return redirect("/in_folder/" + for_folder_)
    else:
        flash("شما اول باید وارد شوید", "warning")
        return redirect('/login')

@app.route("/delete/<int:post_id>", methods=['POST','GET'])
@limiter.limit("3 per seconds")
def delete(post_id):
    if request.cookies.get("cookie"):

        try:
            name = jwt.decode(request.cookies.get('cookie'), app.secret_key, algorithms=["HS256"])
        except:
            flash("توکن شما منقضی شده است . دوباره وارد شوید", "danger")
            resp = make_response(redirect("/login"))
            resp.delete_cookie("cookie")
            return resp

        file = Files.query.filter_by(id=post_id).first()
        if file.url == None:
            if file.delete_files_in == None:
                for files_list in Files.query.all():
                    if files_list.for_folder == file.name and files_list.for_user == name['username']:
                        folder = file.for_folder
                        files_list.for_folder = folder
            if file.delete_files_in != None:
                for files_list in Files.query.all():
                    if files_list.for_folder == file.name and files_list.for_user == name['username']:
                        if files_list.url != None:
                            if os.path.exists(files_list.url):
                                os.remove(files_list.url)
                        myfile = Files.query.filter_by(name=files_list.name, for_user=name['username']).first()
                        db.session.delete(myfile)
                        db.session.commit()
            db.session.delete(file)
            db.session.commit()
        if file.url != None:

            if os.path.exists(file.url):
                os.remove(file.url)
            db.session.delete(file)
            db.session.commit()
        return redirect("/in_folder/" + file.for_folder)
    else:
        flash("شما اول باید وارد شوید", "warning")
        return redirect('/login')

@app.route("/new_folder/<string:for_folder>", methods=['POST', 'GET'])
@limiter.limit("3 per seconds")
def new_folder(for_folder):
    if request.cookies.get("cookie"):
        try:
            name = jwt.decode(request.cookies.get('cookie'), app.secret_key, algorithms=["HS256"])
        except:
            flash("دوباره وارد شوید", "danger")
            resp = make_response(redirect("/login"))
            resp.delete_cookie("cookie")
            return resp

        now = jdatetime.datetime.today()
        mm = str(now.month)
        dd = str(now.day)
        yyyy = str(now.year)
        hour = str(now.hour)
        mi = str(now.minute)
        if Files.query.filter_by(name="New Folder", for_user=name['username']).first():
            num = 1
            while (True):
                new_name = "New Folder" + "(" + str(num) + ")"
                if Files.query.filter_by(name=new_name, for_user=name['username']).first():
                    num += 1
                if not Files.query.filter_by(name=new_name, for_user=name['username']).first():
                    break

        if not Files.query.filter_by(name="New Folder", for_user=name['username']).first():
            new_name = "New Folder"
        new_folder = Files(for_user=name['username'],
                           name=new_name,
                           for_folder=for_folder,
                           type='folder',
                           time=yyyy + "/" + mm + "/" + dd + " " + hour + ":" + mi,
                           delete_files_in=None
                           )
        db.session.add(new_folder)
        db.session.commit()
        return redirect("/in_folder/" + for_folder)
    else:
        flash("شما ابتدا باید وارد شوید", "danger")
        return redirect("/login")

@app.route("/register", methods=['GET', 'POST'])
@limiter.limit("3 per seconds")
def register():
    if request.cookies.get("cookie"):
        flash("شما در حساب کاربری خود وارد هستید", "danger")
        return redirect("/")
    else:
        if request.method == 'GET':
            if request.cookies.get("temporary-cookie"):
                return render_template("accept-email.html")
            return render_template("register.html")
        if request.method == 'POST':
            username = request.form.get('username')
            email = request.form.get('email')
            password = request.form.get('password')
            for users_list in range(len(User.query.all())):
                if User.query.all()[users_list].username == username:

                    if User.query.filter_by(username=username).first().email_status != True:
                        user = User.query.filter_by(username=username).first()
                        random_code = send_email(user.email)
                        user.email_code = random_code
                        db.session.commit()
                        flash("شما هنوز ایمیل خود را تایید نکردید!", "danger")
                        flash(
                            "ایمیل خود را چک کنید. کد را ارسال کردیم. ممکن است ایمیل به هرزنامه ها رفته باشد. برای تایید 3 دقیقه فرصت دارید",
                            "info")
                        flash("جدید ترین کد را بنویسید", "warning")
                        response = make_response(render_template("accept-email.html"))
                        response.set_cookie("temporary-cookie", username, 100)
                        return response
                    else:
                        flash("این نام کاربری قابل استفاده نیست", "warning")
                        return redirect("/register")
                if User.query.all()[users_list].email == email:
                    flash("این ایمیل قابل استفاده نیست", "warning")
                    return redirect("/register")
            else:

                random_code = send_email(email)
                new = User(username=username,
                           email=email,
                           password=password,
                           email_status=False,
                           email_code_expiration=datetime.datetime.utcnow() + datetime.timedelta(minutes=10),
                           email_code=random_code
                           )
                db.session.add(new)
                db.session.commit()



                flash("ایمیل خود را چک کنید. کد را ارسال کردیم. ممکن است ایمیل به هرزنامه ها رفته باشد.برای تایید 3 دقیقه فرصت دارید.", "info")

                response = make_response(render_template("accept-email.html"))
                response.set_cookie("temporary-cookie", username, 100)
                return response


@app.route("/email_checker", methods=['POST', 'GET'])
@limiter.limit("3 per seconds")
def email_checker():
    if request.cookies.get("temporary-cookie"):
        if request.method == 'POST':
            received_code = request.form.get("code")
            user = User.query.filter_by(username=request.cookies.get("temporary-cookie")).first()
            code = user.email_code
            token = jwt.encode(
                {'username': request.cookies.get("temporary-cookie"), 'exp': datetime.datetime.utcnow() + datetime.timedelta(days=1)},
                app.config['SECRET_KEY'])
            if received_code == code:
                user.email_status = True
                db.session.commit()
                flash("ایمیل تایید شد", "success")
                response = make_response(redirect("/"))
                response.set_cookie("cookie", token, 60 * 24)
                return response
            else:
                flash("کد اشتباه است", "danger")
                return render_template("accept-email.html")
    else:
        flash("شما کوکی موقت ندارید", "danger")
        return redirect("/")

@app.route("/edit_file/<int:id>")
@limiter.limit("3 per seconds")
def edit_file(id):
    if request.cookies.get("cookie"):
        try:
            name = jwt.decode(request.cookies.get('cookie'), app.secret_key, algorithms=["HS256"])
        except:
            flash("توکن شما منقضی شده است . دوباره وارد شوید", "danger")
            resp = make_response(redirect("/login"))
            resp.delete_cookie("cookie")
            return resp
        file = Files.query.filter_by(id=id).first()
        return render_template("edit-file.html", name=name['username'], btn_status=file.delete_files_in, id=id, for_folder=file.for_folder, name_=file.name, files=Files.query.all(), type=file.type)
    else:
        flash("شما ابتدا باید وارد شوید", "danger")
        return redirect("/login")

@app.route("/accept_edit_file", methods=['POST', 'GET'])
@limiter.limit("3 per seconds")
def accept_edit_file():
    if request.cookies.get("cookie"):
        if request.method == 'POST':
            try:
                name = jwt.decode(request.cookies.get('cookie'), app.secret_key, algorithms=["HS256"])
            except:
                flash("توکن شما منقضی شده است . دوباره وارد شوید", "danger")
                resp = make_response(redirect("/login"))
                resp.delete_cookie("cookie")
                return resp
            id = request.form.get("id")
            file_name = request.form.get("name")
            for_folder_ = request.form.get("for_folder")
            delete_check = request.form.get("delete_check")
            file = Files.query.filter_by(id=id).first()
            numbers_in_parentheses = re.findall(r'\((\d+)\)', file_name)
            for number in numbers_in_parentheses:
                text_without_numbers = re.sub(r'\(\d+\)', '', file_name)
                file_name = text_without_numbers
            if file.name != file_name:
                if Files.query.filter_by(name=file_name, for_user=name['username']).first():
                    num = 1
                    while (True):
                        new_name = file_name + "(" + str(num) + ")"
                        if Files.query.filter_by(name=new_name, for_user=name['username']).first():
                            num += 1
                        if not Files.query.filter_by(name=new_name, for_user=name['username']).first():
                            break
                if not Files.query.filter_by(name=file_name, for_user=name['username']).first():
                    new_name = file_name
            if file.name == file_name:
                new_name = file_name
            if file.type == 'folder':

                for files in Files.query.all():
                    if files.for_user == name['username'] and files.for_folder == file.name:
                        file2 = Files.query.filter_by(for_user=name['username'], for_folder=files.for_folder).first()
                        file2.for_folder = new_name
                        db.session.commit()

                file.name = new_name
                file.for_folder = for_folder_
                file.delete_files_in = delete_check
                db.session.commit()
            else:
                file_extension = os.path.splitext(file.url)
                format_ = str(file_extension[1])
                os.rename(file.url, path + "/(" + name['username'] + ")" + new_name + format_)
                file.url = path + "/(" + name['username'] + ")" + new_name + format_
                file.name = new_name
                file.for_folder = for_folder_
                db.session.commit()

            return redirect("/in_folder/" + for_folder_)

        else:
            flash("متود اشتباه بود", "danger")
    else:
        flash("شما ابتدا باید وارد شوید", "danger")
        return redirect("/")

@app.route("/in_folder/<string:folder>")
@limiter.limit("3 per seconds")
def in_folder(folder):
    if request.cookies.get("cookie"):
        if request.cookies.get("cookie"):
            try:
                name = jwt.decode(request.cookies.get('cookie'), app.secret_key, algorithms=["HS256"])
            except:
                flash("توکن شما منقضی شده است . دوباره وارد شوید", "danger")
                resp = make_response(redirect("/login"))
                resp.delete_cookie("cookie")
                return resp
            get_path = Files.query.filter_by(for_user=name['username'], name=folder).first()
            text = []
            if folder == "index":
                return redirect("/")
            else:
                if get_path.for_folder == "index":
                    for_append = folder
                    text.append(for_append)
                if get_path.for_folder != "index":
                    text.append(folder)
                    text.append(get_path.for_folder)

            parentfolder = get_path.for_folder
            while(True):
                if Files.query.filter_by(for_user=name['username'], name=parentfolder).first():
                    parentfolder = Files.query.filter_by(for_user=name['username'], name=parentfolder).first()
                    parentfolder = parentfolder.for_folder

                    text.append(parentfolder)

                if not Files.query.filter_by(for_user=name['username'], name=parentfolder).first():
                    break
            for_back_btn = Files.query.filter_by(for_user=name['username'], name=folder).first()
        finally_path = []
        print(text)
        lenght = len(text)
        print(lenght)
        for _ in range(len(text)):
            lenght = int(lenght) - 1
            print(text[lenght])
            finally_path.append(text[lenght])


        print(text)
        print(finally_path)

        return render_template("index.html",
                               name=name['username'],
                               files=Files.query.all(),
                               page=folder,
                               lenght=len(text),
                               path=finally_path,
                               back_btn=for_back_btn.for_folder)
    else:
        flash("شما کوکی ندارید", "danger")
        return redirect("/login")

@app.route("/logout")
def logout():
    if request.cookies.get("cookie"):
        flash("از حساب خارج  شدید", "success")
        resp = make_response(redirect("/"))
        resp.delete_cookie("cookie")
        return resp
    else:
        flash("شما کوکی ندارید", "danger")
        return redirect("/login")

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
