# -*- coding: utf-8 -*-
"""
    Flask Database-admin
"""

from flask import Flask, request, render_template, abort, session, g, url_for, \
                  redirect, flash

from flask.ext.sqlalchemy import SQLAlchemy

from sqlalchemy import exc
from functools import wraps

"""
    Initialize Flask & SQLAlchemy
"""

app = Flask(__name__)
db = SQLAlchemy(app)


"""
    Database Configuration
"""
DB_USER = 'dbuser'
DB_PASS = 'dbpass'
DB_NAME = 'dbname'
DB_HOST = 'localhost'
DB_CHARSET = '?charset=utf8'
SQLALCHEMY_DATABASE_URI = 'mysql://' + DB_USER + ':' + DB_PASS + '@' + DB_HOST + ':3306/' + DB_NAME + DB_CHARSET
SQLALCHEMY_ECHO = False

"""
    App Configuration
"""
app.config['HOST'] = '0.0.0.0'
app.config['PORT']= 8088
app.config['DEBUG'] = True
app.config['SECRET_KEY'] = 'Banana!'


"""
    Place Database Models in models.py
"""

import models

"""
    get_client_ip - Returns the remote IP address, checks the headers for
    X-Forwarded-For as well (if the application sits behind a proxy or similar).
"""
def get_client_ip():
    if 'X-Forwarded-For' in request.headers:
        return request.headers.get('X-Forwarded-For')
    else:
        return request.remote_addr

"""
    requires_admin - Decorate the routes that requires administrator
    authentication, checks the session dictionary for 'is_admin', should be True
"""
def requires_admin(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        is_admin = session.get('is_admin')

        if not is_admin:
            flash(u'Requires Admin Access', 'warning')
            #### 
            # Uncomment this and create the admin-login route for 
            # some protection. This decorator does nothing but whining for now.
            #return redirect( url_for('admin_login') )

        return f(*args, **kwargs)

    return decorated

"""
    Start
"""
@app.route('/')
def admin_index():
    return render_template('database.html')

"""
    Database Management
"""
@app.route('/admin/db/init')
@requires_admin
def init_db():
    db.create_all()
    app.logger.info('{ip} created database tables'.format(ip=get_client_ip()))
    flash(u'Database created', 'success')
    return redirect( url_for('show_tables') )

@app.route('/admin/db/drop')
@requires_admin
def drop_db():
    db.drop_all()
    app.logger.info('{ip} dropped database tables'.format(ip=get_client_ip()))
    flash(u'Database dropped', 'success')
    return redirect( url_for('show_tables') )

"""
    Admin DB Table-Creation Helper methods
"""
def is_model(tbl):
    model = eval('models.{t}'.format(t=tbl))
    return hasattr(model, '__tablename__')

def table_exists(tbl):
    model = eval('models.{t}.__tablename__'.format(t=tbl))
    return db.engine.dialect.has_table(db.engine, model)

def create_table(tbl):
    model = eval('models.{t}'.format(t=tbl))
    return model.__table__.create(db.engine, checkfirst=True)

def delete_table(tbl):
    model = eval('models.{t}'.format(t=tbl))
    return model.__table__.drop(db.engine)

@app.route('/admin/db/tables')
@app.route('/admin/db/tables/<tbl>')
@requires_admin
def show_tables(tbl=None):
    import inspect
    classes = inspect.getmembers(models, inspect.isclass)
    rows = None
    if tbl:
        if not table_exists(tbl):
            flash(u'Table {tbl} does not exist'.format(tbl=tbl), 'warning')
        else:
            model = eval('models.{t}'.format(t=tbl))
            rows = model.query.all()
    return render_template('database.html', cls=classes, rows=rows)

@app.route('/admin/db/create/<tbl>')
@requires_admin
def create_single_table(tbl):
    if table_exists(tbl):
        flash(u'Table already exists', 'info')
    else:
        try:
            create_table(tbl)
        except (exc.ProgrammingError, exc.OperationalError, exc.IntegrityError) as err:
            flash(u'Could not create table {tbl}, error was {err}'.format(tbl=tbl, err=err), 'warning')

        flash(u'Table {tbl} created'.format(tbl=tbl), 'success')
    return redirect( url_for('show_tables') )

@app.route('/admin/db/delete/<tbl>')
@requires_admin
def delete_single_table(tbl):
    print table_exists(tbl)
    if not table_exists(tbl):
        flash(u'Table {tbl} does not exist'.format(tbl=tbl), 'info')
    else:
        try:
            delete_table(tbl)
            flash(u'Table {tbl} deleted successfully'.format(tbl=tbl), 'success')
        except (exc.ProgrammingError, exc.OperationalError, exc.IntegrityError) as err:
            flash(u'Could not delete table {tbl}, error was {err}'.format(tbl=tbl, err=err), 'warning')

    return redirect( url_for('show_tables') )

"""
    Admin helper(s)
"""

app.jinja_env.globals.update(table_exists=table_exists)
app.jinja_env.globals.update(is_model=is_model)

from logging import FileHandler, Formatter

if __name__ == '__main__':
    """
        Setup logging format and files
    """
    app.run(host=app.config['HOST'], port=app.config['PORT'],
            debug=app.config['DEBUG'], use_reloader=True)

"""
EOF
"""
