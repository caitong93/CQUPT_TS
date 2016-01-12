# -*- coding:utf-8 -*-

from threading import Thread

from flask import render_template, session, redirect, url_for, flash
from flask.ext.login import login_user, logout_user, login_required, current_user

from . import main
from .forms import AddNameForm
from .. import db
from ..models import Submission, User, ToolTempUser
from ..crawl_submits import Crawler


OJ = ['Total', 'POJ', 'HDU', 'ZOJ', 'CodeForces']
OJ_ = OJ[1:]


def calc_rows(cls):
    global OJ, OJ_

    all_user = cls.query.all()

    count_by_user = {}
    for u in all_user:
        cnt2 = {}
        for oj in OJ:
            cnt2[oj] = 0
        count_by_user[u.username] = cnt2

    for submission in Submission.query.filter_by(result=1):
        if submission.username in count_by_user:
            cnt = count_by_user[submission.username]
            if submission.oj in cnt:
                cnt[submission.oj] += 1
            cnt['Total'] += 1

    rows = []
    for username, cnt in count_by_user.items():
        row = [username]
        for k in OJ:
            row.append(cnt[k])
        rows.append(row)
    rows = sorted(rows, key=lambda x: x[1], reverse=True)
    return rows


@main.route('/', methods=['GET', 'POST'])
def index():
    rows = calc_rows(User)
    return render_template('index.html', OJ=OJ, rows=rows)


@main.route('/setting', methods=['GET', 'POST'])
@login_required
def setting():
    all_user = User.query.all()
    return render_template('setting.html', all_user=all_user)


@main.route('/tools', methods=['GET', 'POST'])
@login_required
def tools():
    form = AddNameForm()
    if form.validate():
        name = form.name.data.strip()
        if not ToolTempUser.query.filter_by(username=name).first():
            db.session.add(ToolTempUser(username=name))
            db.session.commit()

            #  如果以前没有爬过 则开始爬取
            # todo: 实现一个后台进程 定时更新
            if not Submission.query.filter_by(username=name).first():
                c = Crawler()
                c.run([name])
        else:
            flash(u'This username already exists.')
        return redirect(url_for('main.tools'))
    return render_template('tools.html', form=form, all_temp_user=ToolTempUser.query.all(), OJ=OJ, rows=calc_rows(ToolTempUser))


@main.route('/tools_remove/<username>')
@login_required
def tools_remove(username):
    tmp = ToolTempUser.query.filter_by(username=username).first()
    if tmp:
        db.session.delete(tmp)
        db.session.commit()
    return redirect(url_for('main.tools'))