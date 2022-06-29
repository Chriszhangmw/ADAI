from flask import Blueprint, request, render_template, url_for
from sqlalchemy import and_

from .. import db
from ..model import User, Result, Path
import re

query = Blueprint('query', __name__)

def get_model_dict(model):
    return dict((column.name, getattr(model, column.name)) for column in model.__table__.columns)

'''
查询页面
'''
@query.route('/name', methods=['POST'])
def query_name():
    if request.method == 'POST':
        name = request.form['name']
        test_date = request.form['test_date']

        if name and test_date:
            result_user = db.session.query(Result, User).join(User).filter(User.username == name).filter(Result.date == test_date).all()
            paths = []
            results = []
            users = []
            for result, user in result_user:
                path = db.session.query(Path).filter_by(result=result).one()
                result = get_model_dict(result)
                path = get_model_dict(path)
                results.append(result)
                paths.append(path)
                users.append(get_model_dict(user))

            print(paths)
            keys = ['year', 'reason', 'month', 'day', 'week', 'city', 'area', 'street', 'floor', 'location',
                   'immediate_memory', 'compute', 'late_memory', 'name_pencil', 'name_watch', 'repeat',
                   'sentence', 'wink', 'paper', 'draw']
            for result in results:
                for key in keys[:-3]:
                    res = re.findall('\(.*\)',str(result[key]))
                    res = 'None' if len(res)==0 else res[0]
                    result[key] = res
            return render_template('query.html', results=results, paths=paths, users=users, keys=keys)
        else:
            return render_template("query.html", message="输入信息有误！！")

