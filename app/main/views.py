import base64
import threading

import numpy as np
import json
from ..script import execute, draw
import os
import re
import time
from datetime import datetime

from flask import render_template, request, jsonify, session
import pymysql
from . import main
from .. import db
from ..model import User, Result, Path, AnswerConfigDB
from ..model_src.ASR.asr import AnswerConfig
from ..model_src.albert.ltp_parser import LTP
# from ..model_src.albert.model import albert_model, SenModel
from ..model_src.paper.paper_folding1 import paper_p
from ..model_src.openpose.video2json import video_json
from ..model_src.zhayan.zhayan import Detect

from ..videoprocess import transfer

base_dir = os.path.abspath(os.path.dirname(__file__)).split('main')[0]


@main.route('/')
def home():
    init_global_fold()
    return render_template('home.html')


@main.route('/index')
def index():
    return render_template('index.html')


@main.route('/home/handle', methods=['GET', 'POST'])
def home_handle():
    if request.method == 'POST':
        username = request.form['username']
        birthday = request.form['birthday']
        date = time.strftime("%Y-%m-%d", time.localtime())
        language = request.form['language']
        if username and birthday:
            user = User.query.filter_by(username=username, birthday=birthday).first()
            if user is None:
                user = User(username=username, birthday=birthday)
            result = Result(user=user, date=date)
            result.username = username
            path = Path(result=result)
            path.username = username

            db.session.add(user)
            db.session.add(result)
            db.session.add(path)
            db.session.commit()

            session['user_id'] = user.id
            session['name'] = username
            session['result_id'] = result.id
            session['path_id'] = path.id
            session["language"] = language
            session.permanent = True
            answer_config = AnswerConfig()
            answer_config_db = AnswerConfigDB.query.filter_by(id=1).one_or_none()
            if answer_config_db is None:
                answer_config_db = AnswerConfigDB(id=1,
                                                  city=answer_config.city,
                                                  area=answer_config.area,
                                                  street=answer_config.street,
                                                  floor=answer_config.floor,
                                                  location=answer_config.location)
                db.session.add(answer_config_db)
                db.session.commit()
            return render_template('ars.html',language=language)
        else:
            return render_template('home.html')


@main.route('/answer/login')
def answer_login():
    return render_template('answerLogin.html')


@main.route('/answer/config', methods=["POST"])
def answer_config():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username == "admin" and password == "admin":
            answer_config_db = AnswerConfigDB.query.filter_by(id=1).one_or_none()
            if answer_config_db is None:
                answer_config = AnswerConfig()
                answer_config_db = AnswerConfigDB(id=1,
                                                  city=answer_config.city,
                                                  area=answer_config.area,
                                                  street=answer_config.street,
                                                  floor=answer_config.floor,
                                                  location=answer_config.location)
                db.session.add(answer_config_db)
                db.session.commit()
            answer_config_db = AnswerConfigDB.query.filter_by(id=1).one_or_none()
            answer_config = AnswerConfig(city=answer_config_db.city, area=answer_config_db.area,
                                         street=answer_config_db.street, floor=answer_config_db.floor,
                                         location=answer_config_db.location)
            return render_template('answerConfig.html', answer_config=answer_config)
        else:
            return render_template('answerLogin.html', text="?????????????????????")


@main.route('/answer/handle', methods=['POST'])
def answer_handle():
    if request.method == 'POST':
        answer_config = {"city": request.form['city'], "area": request.form['area'], "street": request.form['street'],
                         "floor": request.form['floor'], "location": request.form['location']}

        answer_config_db = AnswerConfigDB.query.filter_by(id=1).one()
        if answer_config_db:
            for key in answer_config.keys():
                if answer_config[key] != getattr(answer_config_db, key) and answer_config[key] != '':
                    setattr(answer_config_db, key, answer_config[key])
            db.session.commit()
            return render_template('home.html')
        else:
            raise Exception("?????????????????????")
    return "scuess"


@main.route('/ars/')
def ars():
    return render_template('ars.html')


@main.route('/semantic')
def semantic():
    language = session.get("language")
    if language is None:
        language = "chongqing"
    return render_template('semantic.html', language=language)


@main.route('/query/')
def query():
    return render_template('query.html', user=None)


@main.route('/semantic/handle', methods=['GET', 'POST'])
def semantic_handle():
    if request.method == 'POST':
        filename = request.form['video-filename']
        file = request.files['video-blob']
        sentence = request.form['sentence']

        # ????????????
        UPLOAD_FOLDER = 'static/video/semantic'
        filename = str(session.get('name')) + "-" + filename
        file_dir = os.path.join(base_dir, UPLOAD_FOLDER)
        file.save(os.path.join(file_dir, filename))

        # ?????????????????????
        rid = session.get('result_id')
        pid = session.get('path_id')
        def process_and_store(rid, pid):
            fast_model = albert_model()
            ltp_model = LTP(os.path.join(base_dir, r'D:\flask_project\LTP\ltp_data_v3.4.0'))
            sen_model = SenModel(ltp_model, fast_model)
            res = sen_model.predict(sentence)
            res = sentence + '(' + str(res) + ')'
            conn = pymysql.connect(
                host='127.0.0.1',  # ????????????????????????????????????
                port=3306,  # ??????????????????
                user='root',  # ????????????????????????
                passwd='159',
                db='db_ad',  # ???????????????
                charset='utf8',  # ????????????
                cursorclass=pymysql.cursors.DictCursor
            )
            video_path = '/' + UPLOAD_FOLDER + '/' + filename
            cur = conn.cursor()
            resultsql = "update result set sentence=%s where id=%s"
            pathsql = "update path set sentence=%s where id=%s"

            cur.execute(resultsql, (str(res), int(rid)))
            cur.execute(pathsql, (video_path, int(pid)))
            conn.commit()
            conn.close()

        thread_1 = threading.Thread(target=process_and_store, args=[rid, pid])
        thread_1.start()

        return "success"


@main.route('/wink')
def wink():
    language = session.get("language")
    if language is None:
        language = "chongqing"
    return render_template('wink.html', language=language)


@main.route('/wink/handle', methods=['POST'])
def wink_handle():
    if request.method == 'POST':
        filename = request.form['video-filename']
        file = request.files['video-blob']
        # ??????????????????
        UPLOAD_FOLDER = 'static/video/up_wink'

        filename = str(session.get('name')) + '-' + filename
        file_dir = os.path.join(base_dir, UPLOAD_FOLDER)
        video_path = os.path.join(file_dir, filename)
        file.save(video_path)

        rid = session.get('result_id')
        pid = session.get('path_id')
        stored_video_path = '/' + UPLOAD_FOLDER + '/' + filename
        def process_and_store(rid,pid):
            detect = Detect(video_path)
            total = detect.count()
            total = 1 if total > 0 else 0
            conn = pymysql.connect(
                host='127.0.0.1',  # ????????????????????????????????????
                port=3306,  # ??????????????????
                user='root',  # ????????????????????????
                passwd='159',
                db='db_ad',  # ???????????????
                charset='utf8',  # ????????????
                cursorclass=pymysql.cursors.DictCursor
            )
            cur = conn.cursor()
            resultsql = "update result set wink=%s where id=%s"
            pathsql = "update path set wink=%s where id=%s"

            cur.execute(resultsql, (total, int(rid)))
            cur.execute(pathsql, (stored_video_path, int(pid)))
            conn.commit()
            conn.close()
        thread_1 = threading.Thread(target=process_and_store, args=[rid,pid])
        thread_1.start()
        # ?????????????????????
        # detect = Detect(video_path)
        # total = detect.count()
        # print(total)
        # total = 1 if total > 0 else 0
        # video_path = '/' + UPLOAD_FOLDER + '/' + filename
        # if session.get('result_id') is not None:
        #     result = Result.query.filter_by(id=session.get('result_id')).one()
        #     path = Path.query.filter_by(result_id=result.id).one()
        #     if result:
        #         result.wink = total
        #         path.wink = video_path
        #         db.session.commit()
        #         return '???????????????{}'.format(total)
        return "?????????"


@main.route('/paper')
def paper():
    language = session.get("language")
    if language is None:
        language = "chongqing"
    return render_template('paper.html', language=language)


@main.route('/paper/handle', methods=['POST'])
def paper_handle():
    if request.method == 'POST':
        filename = str(session.get('name')) + '-' + request.form['video-filename']
        file = request.files['video-blob']  # ????????????????????????

        file_dir = os.path.join(base_dir, 'static/video/up_paper')

        video_path = os.path.join(file_dir, filename)

        file.save(video_path)

        t_video_path = video_path.split('.mp4')[0] + '_paper.mp4'

        _, color, mo_fold, t_fold = init_own_fold(file_dir, filename)
        #   init_own_fold?????????????????? dir1??? color??? out??? temp
        #   dir1: 'F:/flask_project/app/static/video/up_paper/xx-xxxx'
        #   color: ??????????????????????????????????????????????????? dir1 + '/color'
        #   out: ??????json?????? dir1 + '/out'
        #   temp: ???????????????????????????????????? 'F:/flask_project/app/static/video/up_paper/temp' ??????????????????????????????

        rid = session.get('result_id')
        pid = session.get('path_id')

        stored_video_path = '/static/video/up_paper/' + filename

        def process_and_store(rid, pid):
            transfer(video_path, t_video_path, t_fold)
            os.chdir('D:/flask_project/app/model_src/openpose')
            # video_json(t_video_path, mo_fold)

            s1, s2, s3 = paper_p(t_video_path, mo_fold, color)

            pf_r = str(s1) + str(s2) + str(s3)
            clear_fold(mo_fold, t_fold)
            conn = pymysql.connect(
                host='127.0.0.1',  # ????????????????????????????????????
                port=3306,  # ??????????????????
                user='root',  # ????????????????????????
                passwd='159',
                db='db_ad',  # ???????????????
                charset='utf8',  # ????????????
                cursorclass=pymysql.cursors.DictCursor
            )
            cur = conn.cursor()
            resultsql = "update result set paper=%s where id=%s"
            pathsql = "update path set paper=%s where id=%s"

            cur.execute(resultsql, (str(pf_r), int(rid)))
            cur.execute(pathsql, (stored_video_path, int(pid)))
            conn.commit()
            conn.close()

        thread_1 = threading.Thread(target=process_and_store, args=[rid,pid])
        thread_1.start()

        return "next"


@main.route('/pentagon')
def pentagon():
    language = session.get("language")
    if language is None:
        language = "chongqing"
    return render_template('draw.html', language=language)


@main.route('/pentagon_handle', methods=['POST'])
def pentagon_handle():
    if request.method == "POST":
        base_dir = os.path.dirname(__file__).split('\main')[0]
        filename = str(session.get('name')) + re.sub(r':|\s|\.', '-', str(datetime.now()))
        picture_path = base_dir + '/static/video/up_draw/' + filename + '.jpg'
        point_path = base_dir + '/static/video/up_draw/' + filename + '.npy'

        recv_data = request.get_json()
        if recv_data is None:
            recv_data = request.get_data()

        json_re = json.loads(recv_data)
        imgRes = json_re['uploadImg']
        point = json_re['uploadPoint']
        imgdata = base64.b64decode(imgRes)

        file = open(picture_path, "wb")
        file.write(imgdata)
        file.close()

        np.save(point_path, np.array(point))
        # draw(point)
        if execute(point):
            _r = 1
        else:
            _r = 0
        print("?????????????????????:", _r)

        if session.get('result_id') is not None:
            result = Result.query.filter_by(id=session.get('result_id')).one()
            path = Path.query.filter_by(result_id=result.id).one()
            if result:
                result.draw = _r
                path.draw = '/static/video/up_draw/' + filename + '.jpg'
                db.session.commit()
                return render_template("thank.html")
        else:
            return render_template("thank.html")
    # base_dir = os.path.dirname(__file__).split('\main')[0]
    # os.chdir(base_dir)
    # filename = str(session.get('name')) + re.sub(r':|\s|\.', '-', str(datetime.now()))
    #
    # _bat = 'python ' + base_dir + '/script.py ' + filename
    #
    # picture_path = '/static/video/up_draw/' + filename + '.jpg'
    # # print(_bat)
    # # os.system('conda activate tf113')
    # _r = os.popen(_bat).read()
    # print("?????????????????????:", _r)
    #
    # # html = "<body> <div style='width:40%;margin:auto;'>" + "???????????????????????????: " + _r +"<br>"
    # #        + "<input type='butto' class='btn' id='next' value='????????????' onclick='location.href='" + "/pentagon_handle/></div> </body>"
    # b1 = "<body> <div style='width:40%;margin:auto;'>"
    # r1 = "???????????????????????????: " + _r + "<br>"
    # i1 = "?????????????????????<br><a href='/'>????????????</a>"
    # b2 = "</div></body>"
    # html = b1 + r1 + i1 + b2
    # if session.get('result_id') is not None:
    #     result = Result.query.filter_by(id=session.get('result_id')).one()
    #     path = Path.query.filter_by(result_id=result.id).one()
    #     if result:
    #         result.draw = int(_r.split('\n')[0] == 'True')
    #         path.draw = picture_path
    #         db.session.commit()
    #         return html
    # else:
    #     return html


@main.route('/thank')
def thank():
    return render_template('thank.html')


def summary_result(total_score,education):
    '''
    ????????????????????????????????????????????????????????????????????????
    :param total_score: ?????????
    :param education: ??????????????????????????????????????????????????????????????????????????????
    :return:
    '''

    pass




@main.route('/result/handle', methods=['POST'])
def result_dispaly():
    result_id = None
    if request.method == 'POST':
        result_id = request.get_data()
    print(result_id)

    result = Result()
    if result_id is not None:
        result = Result.query.filter_by(id=result_id).one()
        print(result)



    def get_score(text):
        if text is None:
            return 0
        text = text.split("(")[1]
        score = text.split(")")[0]
        return score

    def get_score1(text, key):
        if text is None:
            return 0
        text = text.split("(")[1]
        text = text.split(")")[0]
        text = eval(text)
        return text[key]

    def get_score2(res, idx):
        if res is None:
            return 0
        else:
            return res[idx]

    def get_score3(text, idx):
        if text is None:
            return 0
        text = text.split("(")[1]
        text = text.split(")")[0]
        text = eval(text)
        res = []
        for val in text.values():
            res.append(val)
        if idx > len(res) - 1:
            return 0
        else:
            return res[idx]
    def get_score4(text):
        if text is None:
            return 0
        else:
            return text
    # dict = {
    #     '1.?????????????????????': get_score(result.year),
    #     '2.????????????????????????': get_score(result.reason),
    #     '3.??????????????????': get_score(result.month),
    #     '4.??????????????????': get_score(result.day),
    #     '5.?????????????????????': get_score(result.week),
    #     '6.???????????????????????????': get_score(result.city),
    #     '7.??????????????????': get_score(result.area),
    #     '8.?????????????????????': get_score(result.street),
    #     '9.??????????????????????????????': get_score(result.floor),
    #     '10.????????????????????????': get_score(result.location),
    #     '11.????????? ??????': get_score1(result.immediate_memory, '??????'),
    #     '12.      ??????': get_score1(result.immediate_memory, '??????'),
    #     '13.      ??????': get_score1(result.immediate_memory, '??????'),
    #     '14.?????????100-7????????????': get_score3(result.compute, 0),
    #     '15.          93-7': get_score3(result.compute, 1),
    #     '16.          86-7': get_score3(result.compute, 2),
    #     '17.          79-7': get_score3(result.compute, 3),
    #     '18.          72-7': get_score3(result.compute, 4),
    #     '19.????????? ??????': get_score1(result.late_memory, '??????'),
    #     '20.      ??????': get_score1(result.late_memory, '??????'),
    #     '21.      ??????': get_score1(result.late_memory, '??????'),
    #     '22.????????? ??????': get_score(result.name_pencil),
    #     '23.      ??????': get_score(result.name_watch),
    #     '24.????????????????????????????????????': get_score(result.repeat),
    #     '25.?????????????????????????????????': get_score4(result.wink),
    #     '26.????????????????????????': get_score2(result.paper, 0),
    #     '27.     ????????????': get_score2(result.paper, 1),
    #     '28.     ???????????????': get_score2(result.paper, 2),
    #     '29.???????????????????????????': get_score(result.sentence),
    #     '30.?????????': get_score4(result.draw),
    #     '??????': 0
    # }
    values = list(dict.values())
    def get_total_scor(scors):
        if isinstance(scors,type(list())):
            scor = 0
            for i in scors:
                scor+=int(i)
        else:
            scor = scors
        return scor

    dict = {
        '1.?????????(10)':get_total_scor(values[:10]),
        '2.????????????(3)':get_total_scor(values[10:13]),
        '3.???????????????(5)':get_total_scor(values[13:18]),
        '4.????????????(3)':get_total_scor(values[18:21]),
        '5.??????(2)':get_total_scor(values[21:23]),
        '6.??????(1)':get_total_scor(values[23]),
        '7.??????(1)':get_total_scor(values[24]),
        '8.??????(3)':get_total_scor(values[25:28]),
        '9.??????(1)':get_total_scor(values[28]),
        '10.?????????(1)':get_total_scor(values[29]),
    }
    print(dict)
    total = 0
    for i in dict.values():
        total += int(i)
    print(total)
    dict['??????(30)'] = total
    return render_template('result.html', result=dict)
    # return dict



def init_global_fold():
    cpath = os.path.join(os.path.abspath(os.path.dirname(__file__)).split('main')[0], 'static/video')

    path1 = os.path.join(cpath, 'up_draw')
    path2 = os.path.join(cpath, 'up_paper')
    path3 = os.path.join(cpath, 'up_wink')
    path4 = os.path.join(cpath, 'semantic')
    if not os.path.exists(path1):
        os.mkdir(path1)
    if not os.path.exists(path2):
        os.mkdir(path2)
    if not os.path.exists(path3):
        os.mkdir(path3)
    if not os.path.exists(path4):
        os.mkdir(path4)


def init_own_fold(file_dir, filename):
    name_list = filename.split('.')[0].split('-')
    fold_name = name_list[-2] + '-' + name_list[-1]

    dir1 = os.path.join(file_dir, fold_name)
    dir2 = os.path.join(dir1, 'color')
    dir3 = os.path.join(dir1, 'out')
    dir_temp = os.path.join(file_dir, 'temp')

    if not os.path.exists(dir1):
        os.mkdir(dir1)
    if not os.path.exists(dir2):
        os.mkdir(dir2)
    if not os.path.exists(dir3):
        os.mkdir(dir3)
    if not os.path.exists(dir_temp):
        os.mkdir(dir_temp)

    return dir1, dir2, dir3, dir_temp


def clear_fold(meidia_out, temp):
    clear(meidia_out)
    clear(temp)
    os.rmdir(meidia_out)
    os.rmdir(temp)


def clear(pth):
    jsf = os.listdir(pth)
    for file in jsf:
        os.remove(pth + '/' + file)
