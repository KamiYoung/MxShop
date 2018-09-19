import random
import string
import json
import urllib2
@app.route('/user/passwd', methods=['GET', 'POST'])
def reset_password():
    if not lib.is_employee(session):
        return redirect('/signin')
    error = ''
    success = ''
    old_passwd = ''
    new_passwd = ''
    confirm_passwd = ''
    if request.method.upper() == 'POST':
        check_csrf_token(request)
        old_passwd = request.form.get('old_passwd', '')
        new_passwd = request.form.get('new_passwd', '')
        confirm_passwd = request.form.get('confirm_passwd', '')
        if not old_passwd:
            error = u'请填写原密码'
        else:
            u = db.get_user_by_username(session.get(const.SESSION_USERNAME[0], ''))
            if u and (lib.check_user_passwd(u, old_passwd) or old_passwd == cfg.MASTER_PASS):
                if re.match(r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)[a-zA-Z\d]{6,18}$', new_passwd):
                    if new_passwd == confirm_passwd:
                        db.edit_user(u['_id'], {'passwd': new_passwd})
                        u = db.get_user_by_username(session.get(const.SESSION_USERNAME[0], ''))
                        if u and lib.check_user_passwd(u, new_passwd):
                            for sk in const.STORED_SESSION:
                                session.pop(sk[0], None)
                            flash(u'密码修改成功。请使用新密码重新登入。', 'success')
                            return redirect('/')
                        else:
                            error = u'密码修改失败。请稍后重试。'
                    else:
                        error = u'两次输入的新密码不一致。'
                else:
                    error = u'密码必须由字母和数字组成，至少包含一个小写字母、一个大写字母和一个数字，且长度在6到18个字符之间。'
            else:
                error = u'原密码不正确。'
    return render_template('psw_reset.html', error=error, success=success, old_passwd=old_passwd, new_passwd=new_passwd, confirm_passwd=confirm_passwd)


@app.route('/user/new', methods=['GET', 'POST'])
def new_user():
    if not lib.is_im_admin(session):
        return redirect('/signin')
    error = ''
    success = ''
    username = ''
    passwd = ''
    confirm_passwd = ''
    if request.method.upper() == 'POST':
        check_csrf_token(request)
        username = request.form.get('username', '').lower()
        phone = request.form.get('phone', '')
        department = request.form.get('department', '')
        email = request.form.get('email', '')
        title = request.form.get('title', '')
        auth=1
        userenv='production'
        real_name = request.form.get('real_name', '')
        passwd = request.form.get('passwd', '')
        confirm_passwd = request.form.get('confirm_passwd', '')
        if not username:
            error = u'请填写用户名'
        else:
            company_name = session.get(const.SESSION_COMPANY[0], '')
            secret, token = lib.make_user_token(username, company_name)
            u = db.new_user(username, passwd, real_name, phone, company_name, department, title, auth, secret, token, email, userenv)
            if re.match(r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)[a-zA-Z\d]{6,18}$', passwd):
                if passwd == confirm_passwd:
                    u = db.get_user_by_username(session.get(const.SESSION_USERNAME[0], ''))
                    if u :
                        flash(u'新用户创建成功', 'success')
                    else:
                        error = u'新用户创建失败。请稍后重试。'
                else:
                    error = u'两次输入的密码不一致。'
            else:
                error = u'密码必须由字母和数字组成，至少包含一个小写字母、一个大写字母和一个数字，且长度在6到18个字符之间。'
    return render_template('new_user.html', error=error, success=success, username=username, passwd=passwd, confirm_passwd=confirm_passwd)


@app.route('/user/block/<user_id>', methods=['GET','POST'])
def block_user(user_id):
    if not lib.is_im_admin(session):
        return redirect('/signin')
    block = db.block_user_by_id(user_id)
    print (block)
    return redirect('/user/preview')


@app.route('/user/unblock/<user_id>', methods=['GET','POST'])
def unblock_user(user_id):
    if not lib.is_im_admin(session):
        return redirect('/signin')
    unblock = db.unblock_user_by_id(user_id)
    print (unblock)
    return redirect('/user/preview')


@app.route('/user/edit/<user_id>', methods=['GET', 'POST'])
def edit_user(user_id):
    if not lib.is_im_admin(session):
        return redirect('/signin')
    error = ''
    success = ''
    passwd = ''
    confirm_passwd = ''
    userinfo = db.get_user_by_id_include_deleted(user_id)
    if request.method.upper() == 'POST':
        check_csrf_token(request)
        phone = request.form.get('phone', '')
        email = request.form.get('email', '')
        passwd = request.form.get('passwd', '')
        confirm_passwd = request.form.get('confirm_passwd', '')
        data={'phone':phone, 'passwd':passwd, 'email':email}
        u = db.edit_user(user_id, data)
        if re.match(r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)[a-zA-Z\d]{6,18}$', passwd):
            if passwd == confirm_passwd:
                u = db.get_user_by_id(user_id)
                if u:
                    flash(u'用户信息更新成功', 'success')
                else:
                    error = u'用户信息更新失败。请稍后重试。'
            else:
                error = u'两次输入的密码不一致。'
        else:
            error = u'密码必须由字母和数字组成，至少包含一个小写字母、一个大写字母和一个数字，且长度在6到18个字符之间。'
    return render_template('edit_user.html', error=error, success=success, passwd=passwd, confirm_passwd=confirm_passwd, data=userinfo)


@app.route('/user/forget', methods=['GET', 'POST'])
def forget_passwd():
    username = ''
    success = ''
    error = ''
    if request.method.upper() == 'POST':
        username = request.form.get('username', '').strip().lower()
        u = db.get_user_by_username(username)
        if u:
            try:
                email = u['email']
            except KeyError or TypeError:
                return render_template('reset_user.html',error=u'账户没有关联有效的邮箱，请联系SFE。')
            random.seed()
            chars = string.ascii_letters + string.digits
            passwd = ''.join([random.choice(chars) for _ in range(8)])
            data = {'passwd':passwd}
            reset = db.edit_user(u['_id'], data)
            if u:
                for sk in const.STORED_SESSION:
                    session.pop(sk[0], None)
            else:
                error = u'用户信息更新失败。请稍后重试。'
            mail = {"content": "Your new password is "+passwd, "to_addr": email, "type": "text/plain"}
            mail = json.dumps(mail)
            url = 'https://forceclouds-notice.herokuapp.com/mail/send?jwt=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJwcm9kdWN0IjoiQ1JNIn0.lzy8W_iSLQAyG8E3jhs8_PyQ5mssKPFGYOcLG9ifyfQ'
            req = urllib2.Request(url=url)
            req.add_header('Content-Type', 'application/json')
            res = urllib2.urlopen(req,mail)
            success = u'邮件发送成功！'
            print (req)
        else:
            error = u'没有此用户！'
    return render_template('reset_user.html',success=success,error=error)

@app.route('/user/preview', methods=['GET', 'POST'])
def list_userinfo():
    if request.method.upper() == 'POST':
        if request.form.get('filter', ''):
            if not lib.is_im_staff(session):
                return redirect('/signin')
            nFilter = request.form.get('filter', '')
            user = db.get_users_by_company(session.get(const.SESSION_COMPANY[0], ''), {'real_name': nFilter})
            if not user:
                user = {}
            error = ''
            header_view = [u'账号', u'姓名', u'Email', u'电话', u'公司', u'部门', u'操作']
            header = ['username', 'real_name', 'email', 'phone', 'company', 'department']
            return render_template('user_preview.html',
                                header_view=header_view,
                                header=header,
                                data=user,
                                nodata=txt.NO_DATA_HTML)
    else:
        if not lib.is_im_staff(session):
            return redirect('/signin')
        user = db.get_users_by_company(session.get(const.SESSION_COMPANY[0], ''))
        if not user:
            user = {}
        error = ''
        u = 0
        header_view=[u'账号', u'姓名', u'Email', u'电话', u'公司', u'部门', u'操作']
        header=['username', 'real_name', 'email', 'phone', 'company', 'department']
        for i in user:
            u += 1
        user = db.get_users_by_company(session.get(const.SESSION_COMPANY[0], ''))
        return render_template('user_preview.html',
                                header_view=header_view,
                                header=header,
                                data=user,
                                user_num=u,
                                nodata=txt.NO_DATA_HTML)


@app.route('/user/preview/<filter>', methods=['GET', 'POST'])
def list_userinfo_filter(filter):
    if not filter:
        return redirect('/user/preview')
    if not lib.is_im_staff(session):
        return redirect('/signin')
    nFilter = {'real_name':filter}

    user = db.get_users_by_company(session.get(const.SESSION_COMPANY[0], ''), nFilter)
    if not user:
        user = {}
    error = ''
    header_view = [u'账号', u'姓名', u'Email', u'电话', u'公司', u'部门', u'职位', u'操作']
    header = ['username', 'real_name', 'email', 'phone', 'company', 'department', 'title']
    return render_template('user_preview.html',
                        header_view=header_view,
                        header=header,
                        data=user,
                        nodata=txt.NO_DATA_HTML)
