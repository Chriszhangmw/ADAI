import os
import time
import threading
import pymysql

from flask import Blueprint, request, session, jsonify, render_template

from app.model_src.ASR.asr import Question
from app.model import Result, Path, AnswerConfigDB

from .. import db

ars_route = Blueprint('ars_route', __name__)

#时间：2022/01/17
#作者：王香霖
#更改：将音频以及计算得分的过程在后台进行，保证前端页面流畅

def delete_audio(audio_path, out_path):
    """如果原音频存在和输出音频同时存在，则删除原音频，保留输出音频"""
    if os.path.exists(audio_path) and os.path.exists(out_path):
        os.remove(audio_path)


def save_file(file, filename, upload_folder):
    """保存上传文件"""
    dir = os.path.abspath(os.path.dirname(__file__)).split('main')[0]
    file_dir = os.path.join(dir, upload_folder)
    if not os.path.exists(file_dir):
        os.makedirs(file_dir)
    audio_path = os.path.join(file_dir, filename)
    audio_path = audio_path.replace('\\', '/')
    file.save(audio_path)
    return audio_path


#多线程更新数据库，保存得分，音频文件的路径
def store_res(task,rid,pid,res,path):
    conn = pymysql.connect(
        host='127.0.0.1',  # 连接的数据库服务器主机名
        port=3306,  # 数据库端口号
        user='root',  # 数据库登录用户名
        passwd='159',
        db='db_ad',  # 数据库名称
        charset='utf8',  # 连接编码
        cursorclass=pymysql.cursors.DictCursor
    )
    cur = conn.cursor()
    resultsql = f"update result set {task}='{res}' where id={rid}"
    pathsql = f"update path set {task}='{path}' where id={pid}"

    cur.execute(resultsql)
    cur.execute(pathsql)
    conn.commit()
    conn.close()

# 年份
@ars_route.route('/year', methods=['POST'])
def ars_year():
    if request.method == 'POST':
        filename = request.form['audio-filename']
        file = request.files['audio-blob']
        language = session.get("language")
        filename = str(session.get('name')) +'-' + filename
        upload_folder = f'static/audio/{str(session.get("language")).replace("_nv","").replace("_nan","")}/{time.strftime("%Y.%m.%d")}/{str(session.get("name"))}'
        # 首先保存音频，方便以后复查
        audio_path = save_file(file, filename, upload_folder)
        url_path = audio_path.split('app')[1]
        #多线程保存上下文信息
        rid = session.get('result_id')
        pid = session.get('path_id')
        def thread_year(rid,pid):
            print('thread year start')
            client = Question(audio_path, language=language)
            # 年份
            result, score = client.match_year()
            ret = str(result) + '(' + str(score) + ')'
            print(ret)
            print('year')
            # 存入数据库
            if rid is not None:
                store_res('year',rid,pid,ret,url_path)
            print('thread year end')
        thread_1 = threading.Thread(target=thread_year,args=[rid,pid])
        thread_1.start()
        return "next"


# 季节
@ars_route.route('/reason', methods=['POST'])
def ars_reason():
    if request.method == 'POST':
        filename = request.form['audio-filename']
        file = request.files['audio-blob']
        filename = str(session.get('name')) + '-' + filename
        upload_folder = f'static/audio/{str(session.get("language")).replace("_nv","").replace("_nan","")}/{time.strftime("%Y.%m.%d")}/{str(session.get("name"))}'
        # 首先保存音频，方便以后复查
        audio_path = save_file(file, filename, upload_folder)
        url_path = audio_path.split('app')[1]
        language = session.get("language")
        #多线程保存上下文信息
        rid = session.get('result_id')
        pid = session.get('path_id')
        def thread_reason(rid, pid):
            print('thread reason start')
            client = Question(audio_path, language=language)
            # 季节
            result, score = client.match_reason()
            ret = str(result) + '(' + str(score) + ')'
            print(ret)
            print("reason")
            # 存入数据库
            if rid is not None:
                store_res('reason', rid, pid, ret, url_path)
            print('thread reason end')

        thread_1 = threading.Thread(target=thread_reason, args=[rid, pid])
        thread_1.start()
        return "next"



# 月份
@ars_route.route('/month', methods=['POST'])
def ars_month():
    if request.method == 'POST':
        filename = request.form['audio-filename']
        file = request.files['audio-blob']
        filename = str(session.get('name')) + '-' + filename
        upload_folder = f'static/audio/{str(session.get("language")).replace("_nv","").replace("_nan","")}/{time.strftime("%Y.%m.%d")}/{str(session.get("name"))}'
        # 首先保存音频，方便以后复查
        audio_path = save_file(file, filename, upload_folder)
        url_path = audio_path.split('app')[1]
        language = session.get("language")
        # 多线程保存上下文信息
        rid = session.get('result_id')
        pid = session.get('path_id')
        def thread_month(rid, pid):
            print('thread month start')
            client = Question(audio_path, language=language)
            # 月份
            result, score = client.match_month()
            ret = str(result) + '(' + str(score) + ')'
            print(ret)
            # 存入数据库
            if rid is not None:
                store_res('month', rid, pid, ret, url_path)
            print('thread month end')

        thread_1 = threading.Thread(target=thread_month, args=[rid, pid])
        thread_1.start()
        return "next"


# 日期
@ars_route.route('/day', methods=['POST'])
def ars_day():
    if request.method == 'POST':
        filename = request.form['audio-filename']
        file = request.files['audio-blob']
        filename = str(session.get('name')) + '-' + filename
        upload_folder = f'static/audio/{str(session.get("language")).replace("_nv","").replace("_nan","")}/{time.strftime("%Y.%m.%d")}/{str(session.get("name"))}'
        # 首先保存音频，方便以后复查
        audio_path = save_file(file, filename, upload_folder)
        url_path = audio_path.split('app')[1]
        language = session.get("language")
        # 多线程保存上下文信息
        rid = session.get('result_id')
        pid = session.get('path_id')
        def thread_day(rid, pid):
            print('thread day start')
            client = Question(audio_path, language=language)
            # 日期
            result, score = client.match_day()
            ret = str(result) + '(' + str(score) + ')'
            print(ret)
            # 存入数据库
            if rid is not None:
                store_res('day', rid, pid, ret, url_path)
            print('thread day end')

        thread_1 = threading.Thread(target=thread_day, args=[rid, pid])
        thread_1.start()
        return "next"


# 星期
@ars_route.route('/week', methods=['POST'])
def ars_week():
    if request.method == 'POST':
        filename = request.form['audio-filename']
        file = request.files['audio-blob']
        filename = str(session.get('name')) + '-' + filename
        upload_folder = f'static/audio/{str(session.get("language")).replace("_nv","").replace("_nan","")}/{time.strftime("%Y.%m.%d")}/{str(session.get("name"))}'
        # 首先保存音频，方便以后复查
        audio_path = save_file(file, filename, upload_folder)
        url_path = audio_path.split('app')[1]
        language = session.get("language")
        # 多线程保存上下文信息
        rid = session.get('result_id')
        pid = session.get('path_id')
        def thread_week(rid, pid):
            print('thread week start')
            client = Question(audio_path, language=language)
            # 星期
            result, score = client.match_week()
            ret = str(result) + '(' + str(score) + ')'
            print(ret)
            # 存入数据库
            if rid is not None:
                store_res('week', rid, pid, ret, url_path)
            print('thread week end')

        thread_1 = threading.Thread(target=thread_week, args=[rid, pid])
        thread_1.start()
        return "next"
# 城市
@ars_route.route('/city', methods=['POST'])
def ars_city():
    if request.method == 'POST':
        filename = request.form['audio-filename']
        file = request.files['audio-blob']
        filename = str(session.get('name')) + '-' + filename
        upload_folder = f'static/audio/{str(session.get("language")).replace("_nv","").replace("_nan","")}/{time.strftime("%Y.%m.%d")}/{str(session.get("name"))}'
        # 首先保存音频，方便以后复查
        audio_path = save_file(file, filename, upload_folder)
        url_path = audio_path.split('app')[1]
        answer_config_db = AnswerConfigDB.query.filter_by(id=1).one()
        language = session.get("language")
        # 多线程保存上下文信息
        rid = session.get('result_id')
        pid = session.get('path_id')
        def thread_city(rid, pid):
            print('thread city start')
            client = Question(audio_path, language=language, answer_config=answer_config_db)
            # 城市
            result, score = client.match_city()
            
            ret = str(result) + '(' + str(score) + ')'
            print(ret)
            # 存入数据库
            if rid is not None:
                store_res('city', rid, pid, ret, url_path)
            print('thread city end')

        thread_1 = threading.Thread(target=thread_city, args=[rid, pid])
        thread_1.start()
        return "next"


# 区
@ars_route.route('/area', methods=['POST'])
def ars_area():
    if request.method == 'POST':
        filename = request.form['audio-filename']
        file = request.files['audio-blob']
        filename = str(session.get('name')) + '-' + filename
        upload_folder = f'static/audio/{str(session.get("language")).replace("_nv","").replace("_nan","")}/{time.strftime("%Y.%m.%d")}/{str(session.get("name"))}'
        # 首先保存音频，方便以后复查
        audio_path = save_file(file, filename, upload_folder)
        url_path = audio_path.split('app')[1]
        answer_config_db = AnswerConfigDB.query.filter_by(id=1).one()
        language = session.get("language")
        # 多线程保存上下文信息
        rid = session.get('result_id')
        pid = session.get('path_id')
        def thread_area(rid, pid):
            print('thread area start')
            client = Question(audio_path, language=language, answer_config=answer_config_db)
            # 区
            result, score = client.match_area()
            ret = str(result) + '(' + str(score) + ')'
            print(ret)
            # 存入数据库
            if rid is not None:
                store_res('area', rid, pid, ret, url_path)
            print('thread area end')

        thread_1 = threading.Thread(target=thread_area, args=[rid, pid])
        thread_1.start()
        return "next"


# 街道
@ars_route.route('/street', methods=['POST'])
def ars_street():
    if request.method == 'POST':
        filename = request.form['audio-filename']
        file = request.files['audio-blob']
        filename = str(session.get('name')) + '-' + filename
        upload_folder = f'static/audio/{str(session.get("language")).replace("_nv","").replace("_nan","")}/{time.strftime("%Y.%m.%d")}/{str(session.get("name"))}'
        # 首先保存音频，方便以后复查
        audio_path = save_file(file, filename, upload_folder)
        url_path = audio_path.split('app')[1]
        answer_config_db = AnswerConfigDB.query.filter_by(id=1).one()
        language = session.get("language")
        # 多线程保存上下文信息
        rid = session.get('result_id')
        pid = session.get('path_id')
        def thread_street(rid, pid):
            print('thread street start')
            client = Question(audio_path, language=language, answer_config=answer_config_db)
            # 街道
            result, score = client.match_street()
            
            ret = str(result) + '(' + str(score) + ')'
            print(ret)
            # 存入数据库
            if rid is not None:
                store_res('street', rid, pid, ret, url_path)
            print('thread street end')

        thread_1 = threading.Thread(target=thread_street, args=[rid, pid])
        thread_1.start()
        return "next"

# 楼层
@ars_route.route('/floor', methods=['POST'])
def ars_floor():
    if request.method == 'POST':
        filename = request.form['audio-filename']
        file = request.files['audio-blob']
        filename = str(session.get('name')) + '-' + filename
        upload_folder = f'static/audio/{str(session.get("language")).replace("_nv","").replace("_nan","")}/{time.strftime("%Y.%m.%d")}/{str(session.get("name"))}'
        # 首先保存音频，方便以后复查
        audio_path = save_file(file, filename, upload_folder)
        url_path = audio_path.split('app')[1]
        answer_config_db = AnswerConfigDB.query.filter_by(id=1).one()
        language = session.get("language")
        # 多线程保存上下文信息
        rid = session.get('result_id')
        pid = session.get('path_id')
        def thread_floor(rid, pid):
            print('thread floor start')
            client = Question(audio_path, language=language, answer_config=answer_config_db)
            # 年份
            result, score = client.match_floor()
            
            ret = str(result) + '(' + str(score) + ')'
            print(ret)
            # 存入数据库
            if rid is not None:
                store_res('floor', rid, pid, ret, url_path)
            print('thread floor end')

        thread_1 = threading.Thread(target=thread_floor, args=[rid, pid])
        thread_1.start()
        return "next"


# 地方
@ars_route.route('/location', methods=['POST'])
def ars_location():
    if request.method == 'POST':
        filename = request.form['audio-filename']
        file = request.files['audio-blob']
        filename = str(session.get('name')) + '-' + filename
        upload_folder = f'static/audio/{str(session.get("language")).replace("_nv","").replace("_nan","")}/{time.strftime("%Y.%m.%d")}/{str(session.get("name"))}'
        # 首先保存音频，方便以后复查
        audio_path = save_file(file, filename, upload_folder)
        url_path = audio_path.split('app')[1]
        answer_config_db = AnswerConfigDB.query.filter_by(id=1).one()
        language = session.get("language")
        # 多线程保存上下文信息
        rid = session.get('result_id')
        pid = session.get('path_id')

        def thread_location(rid, pid):
            print('thread location start')
            client = Question(audio_path, language=language, answer_config=answer_config_db)
            # 地方
            result, score = client.match_location()
            ret = str(result) + '(' + str(score) + ')'
            print(ret)
            # 存入数据库
            if rid is not None:
                store_res('location', rid, pid, ret, url_path)
            print('thread location end')

        thread_1 = threading.Thread(target=thread_location, args=[rid, pid])
        thread_1.start()
        return "next"

# 回忆
@ars_route.route('/immediateMemory', methods=['POST'])
def ars_immediate_momery():
    if request.method == 'POST':
        filename = request.form['audio-filename']
        file = request.files['audio-blob']
        filename = str(session.get('name')) + '-' + filename
        upload_folder = f'static/audio/{str(session.get("language")).replace("_nv","").replace("_nan","")}/{time.strftime("%Y.%m.%d")}/{str(session.get("name"))}'
        # 首先保存音频，方便以后复查
        audio_path = save_file(file, filename, upload_folder)
        url_path = audio_path.split('app')[1]
        language = session.get("language")
        # 多线程保存上下文信息
        rid = session.get('result_id')
        pid = session.get('path_id')
        def thread_immediateMemory(rid, pid):
            print('thread immediateMemory start')
            client = Question(audio_path, language=language)
            # 回忆
            result, score = client.memory()
            ret = str(result) + '(' + str(score) + ')'
            ret = ret.replace("'",'"')
            print(ret)
            # 存入数据库
            if rid is not None:
                store_res('immediate_memory', rid, pid, ret, url_path)
            print('thread immediateMemory end')

        thread_1 = threading.Thread(target=thread_immediateMemory, args=[rid, pid])
        thread_1.start()
        return "next"

@ars_route.route('/lateMemory', methods=['POST'])
def ars_late_momery():
    if request.method == 'POST':
        filename = request.form['audio-filename']
        file = request.files['audio-blob']
        filename = str(session.get('name')) + '-' + filename
        upload_folder = f'static/audio/{str(session.get("language")).replace("_nv","").replace("_nan","")}/{time.strftime("%Y.%m.%d")}/{str(session.get("name"))}'
        # 首先保存音频，方便以后复查
        audio_path = save_file(file, filename, upload_folder)
        url_path = audio_path.split('app')[1]
        language = session.get("language")
        # 多线程保存上下文信息
        rid = session.get('result_id')
        pid = session.get('path_id')
        def thread_lateMemory(rid, pid):
            print('thread lateMemory start')
            client = Question(audio_path, language=language)
            # 回忆
            result, score = client.memory()
            ret = str(result) + '(' + str(score) + ')'
            ret = ret.replace("'",'"')
            print(ret)
            # 存入数据库
            if rid is not None:
                store_res('late_memory', rid, pid, ret, url_path)
            print('thread lateMemory end')

        thread_1 = threading.Thread(target=thread_lateMemory, args=[rid, pid])
        thread_1.start()
        return "next"


# 计算
@ars_route.route('/compute', methods=['POST'])
def ars_compute():
    if request.method == 'POST':
        filename = request.form['audio-filename']
        file = request.files['audio-blob']
        filename = str(session.get('name')) + '-' + filename
        upload_folder = f'static/audio/{str(session.get("language")).replace("_nv","").replace("_nan","")}/{time.strftime("%Y.%m.%d")}/{str(session.get("name"))}'
        # 首先保存音频，方便以后复查
        audio_path = save_file(file, filename, upload_folder)
        url_path = audio_path.split('app')[1]
        language = session.get("language")
        # 多线程保存上下文信息
        rid = session.get('result_id')
        pid = session.get('path_id')
        def thread_compute(rid, pid):
            print('thread compute start')
            client = Question(audio_path, language=language)
            # 计算
            result, score = client.compute()
            ret = str(result) + '(' + str(score) + ')'
            print(ret)
            # 存入数据库
            if rid is not None:
                store_res('compute', rid, pid, ret, url_path)
            print('thread compute end')
        thread_1 = threading.Thread(target=thread_compute, args=[rid, pid])
        thread_1.start()
        return "next"

# 铅笔命名
@ars_route.route('/namePencil', methods=['POST'])
def ars_pencil():
    if request.method == 'POST':
        filename = request.form['audio-filename']
        file = request.files['audio-blob']
        filename = str(session.get('name')) + '-' + filename
        upload_folder = f'static/audio/{str(session.get("language")).replace("_nv","").replace("_nan","")}/{time.strftime("%Y.%m.%d")}/{str(session.get("name"))}'
        # 首先保存音频，方便以后复查
        audio_path = save_file(file, filename, upload_folder)
        url_path = audio_path.split('app')[1]
        language = session.get("language")
        # 多线程保存上下文信息
        rid = session.get('result_id')
        pid = session.get('path_id')
        def thread_namePencil(rid, pid):
            print('thread namePencil start')
            client = Question(audio_path, language=language)
            # 铅笔
            result, score = client.name_pencil()
            ret = str(result) + '(' + str(score) + ')'
            print(ret)
            # 存入数据库
            if rid is not None:
                store_res('name_pencil', rid, pid, ret, url_path)
            print('thread namePencil end')
        thread_1 = threading.Thread(target=thread_namePencil, args=[rid, pid])
        thread_1.start()
        return "next"


# 手表命名
@ars_route.route('/nameWatch', methods=['POST'])
def ars_watch():
    if request.method == 'POST':
        filename = request.form['audio-filename']
        file = request.files['audio-blob']
        filename = str(session.get('name')) + '-' + filename
        upload_folder = f'static/audio/{str(session.get("language")).replace("_nv","").replace("_nan","")}/{time.strftime("%Y.%m.%d")}/{str(session.get("name"))}'
        # 首先保存音频，方便以后复查
        audio_path = save_file(file, filename, upload_folder)
        url_path = audio_path.split('app')[1]
        language = session.get("language")
        # 多线程保存上下文信息
        rid = session.get('result_id')
        pid = session.get('path_id')
        def thread_nameWatch(rid, pid):
            print('thread nameWatch start')
            client = Question(audio_path,language=language)
            # 铅笔
            result, score = client.name_watch()
            
            ret = str(result) + '(' + str(score) + ')'
            print(ret)
            # 存入数据库
            if rid is not None:
                store_res('name_watch', rid, pid, ret, url_path)
            print('thread nameWatch end')
        thread_1 = threading.Thread(target=thread_nameWatch, args=[rid, pid])
        thread_1.start()
        return "next"


# 复述
@ars_route.route('/repeat', methods=['POST'])
def ars_repeat():
    if request.method == 'POST':
        filename = request.form['audio-filename']
        file = request.files['audio-blob']
        filename = str(session.get('name')) + '-' + filename
        upload_folder = f'static/audio/{str(session.get("language")).replace("_nv","").replace("_nan","")}/{time.strftime("%Y.%m.%d")}/{str(session.get("name"))}'
        # 首先保存音频，方便以后复查
        audio_path = save_file(file, filename, upload_folder)
        url_path = audio_path.split('app')[1]
        language = session.get("language")
        # 多线程保存上下文信息
        rid = session.get('result_id')
        pid = session.get('path_id')
        def thread_repeat(rid, pid):
            print('thread repeat start')
            client = Question(audio_path, language=language)
            # 复述
            result, score = client.repeat()
            ret = str(result) + '(' + str(score) + ')'
            print(ret)
            # 存入数据库
            if rid is not None:
                store_res('`repeat`', rid, pid, ret, url_path)
            print('thread repeat end')
        thread_1 = threading.Thread(target=thread_repeat, args=[rid, pid])
        thread_1.start()
        return "next"