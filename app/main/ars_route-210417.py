import os

# import sox
from flask import Blueprint, request, session, jsonify, render_template

from app.model_src.ASR.asr import Question
from app.model import Result, Path, AnswerConfigDB

from .. import db

ars_route = Blueprint('ars_route', __name__)


def delete_audio(audio_path, out_path):
    """如果原音频存在和输出音频同时存在，则删除原音频，保留输出音频"""
    if os.path.exists(audio_path) and os.path.exists(out_path):
        os.remove(audio_path)


def save_file(file, filename, upload_folder):
    """保存上传文件"""
    dir = os.path.abspath(os.path.dirname(__file__)).split('main')[0]
    file_dir = os.path.join(dir, upload_folder)
    audio_path = os.path.join(file_dir, filename)
    file.save(audio_path)
    audio_path = audio_path.replace('\\', '/')
    return audio_path


# def upsample_wav(file):
#     """ 音频转为采样率为16000， 单声道， 位深为16"""
#     tfm = sox.Transformer()
#     tfm.set_output_format(rate=16000, bits=16, channels=1)
#     out_path = file.split('.wav')[0] + "_hr.wav"
#     tfm.build(file, out_path)
#     out_path = out_path.replace('\\', '/')
#     return out_path


# 年份
@ars_route.route('/year', methods=['POST'])
def ars_year():
    if request.method == 'POST':
        filename = request.form['audio-filename']
        file = request.files['audio-blob']
        language = session.get("language")
        filename = str(session.get('name')) +'-' + filename
        upload_folder = 'static/audio'
        # 首先保存音频，方便以后复查
        audio_path = save_file(file, filename, upload_folder)

        # 对音频进行转换处理
        # out_path = upsample_wav(audio_path)
        url_path = audio_path.split('app')[1]
        # 删除原音频
        # delete_audio(audio_path, out_path)

        client = Question(audio_path, language=language)
        # 年份
        result, score = client.match_year()
        ret = str(result) + '(' + str(score) + ')'
        print(ret)
        print('year')
        # 存入数据库
        if session.get('result_id') is not None:
            result = Result.query.filter_by(id=session.get('result_id')).one()
            uri = Path.query.filter_by(result_id=result.id).one()
            if result:
                result.year = ret
                uri.year = url_path
                # db.session.add(result)
                # db.session.add(uri)
                db.session.commit()
                return ret
        return "未保存"


# 季节
@ars_route.route('/reason', methods=['POST'])
def ars_reason():
    if request.method == 'POST':
        filename = request.form['audio-filename']
        file = request.files['audio-blob']
        filename = str(session.get('name')) + '-' + filename
        upload_folder = 'static/audio'
        # 首先保存音频，方便以后复查
        audio_path = save_file(file, filename, upload_folder)

        # 对音频进行转换处理
        # out_path = upsample_wav(audio_path)
        url_path = audio_path.split('app')[1]
        # 删除原音频
        # delete_audio(audio_path, out_path)
        language = session.get("language")
        client = Question(audio_path,language=language)
        # 季节
        result, score = client.match_reason()
        # print(result)
        ret = str(result) + '(' + str(score) + ')'
        print(ret)
        print("reason")
        # 存入数据库
        if session.get('result_id') is not None:
            result = Result.query.filter_by(id=session.get('result_id')).one()
            uri = Path.query.filter_by(result_id=result.id).one()
            if result:
                result.reason = ret
                uri.reason = url_path
                # db.session.add(result)
                # db.session.add(uri)
                db.session.commit()
                return ret
        return "未保存"


# 月份
@ars_route.route('/month', methods=['POST'])
def ars_month():
    if request.method == 'POST':
        filename = request.form['audio-filename']
        file = request.files['audio-blob']
        filename = str(session.get('name')) + '-' + filename
        upload_folder = 'static/audio'
        # 首先保存音频，方便以后复查
        audio_path = save_file(file, filename, upload_folder)

        # 对音频进行转换处理
        # out_path = upsample_wav(audio_path)
        url_path = audio_path.split('app')[1]
        # 删除原音频
        # delete_audio(audio_path, out_path)
        language = session.get("language")
        client = Question(audio_path,language=language)
        # 月份
        result, score = client.match_month()
        # print(result)
        ret = str(result) + '(' + str(score) + ')'
        print(ret)
        # 存入数据库
        if session.get('result_id') is not None:
            result = Result.query.filter_by(id=session.get('result_id')).one()
            uri = Path.query.filter_by(result_id=result.id).one()
            if result:
                result.month = ret
                uri.month = url_path
                # db.session.add(result)
                # db.session.add(uri)
                db.session.commit()
                return ret
        return "未保存"


# 日期
@ars_route.route('/day', methods=['POST'])
def ars_day():
    if request.method == 'POST':
        filename = request.form['audio-filename']
        file = request.files['audio-blob']
        filename = str(session.get('name')) + '-' + filename
        upload_folder = 'static/audio'
        # 首先保存音频，方便以后复查
        audio_path = save_file(file, filename, upload_folder)
        # 对音频进行转换处理
        # out_path = upsample_wav(audio_path)
        url_path = audio_path.split('app')[1]
        # 删除原音频
        # delete_audio(audio_path, out_path)
        language = session.get("language")
        client = Question(audio_path,language=language)
        # 日期
        result, score = client.match_day()
        # print(result)
        ret = str(result) + '(' + str(score) + ')'
        print(ret)
        # 存入数据库
        if session.get('result_id') is not None:
            result = Result.query.filter_by(id=session.get('result_id')).one()
            uri = Path.query.filter_by(result_id=result.id).one()
            if result:
                result.day = ret
                uri.day = url_path
                # db.session.add(result)
                # db.session.add(uri)
                db.session.commit()
                return ret
        return "未保存"


# 星期
@ars_route.route('/week', methods=['POST'])
def ars_week():
    if request.method == 'POST':
        filename = request.form['audio-filename']
        file = request.files['audio-blob']
        filename = str(session.get('name')) + '-' + filename
        upload_folder = 'static/audio'
        # 首先保存音频，方便以后复查
        audio_path = save_file(file, filename, upload_folder)

        # 对音频进行转换处理
        # out_path = upsample_wav(audio_path)
        url_path = audio_path.split('app')[1]
        # 删除原音频
        # delete_audio(audio_path, out_path)
        language = session.get("language")
        client = Question(audio_path,language=language)
        # 星期
        result, score = client.match_week()
        # print(result)
        ret = str(result) + '(' + str(score) + ')'
        print(ret)
        # 存入数据库
        if session.get('result_id') is not None:
            result = Result.query.filter_by(id=session.get('result_id')).one()
            uri = Path.query.filter_by(result_id=result.id).one()
            if result:
                result.week = ret
                uri.week = url_path
                # db.session.add(result)
                # db.session.add(uri)
                db.session.commit()
                return ret
        return "未保存"


# 城市
@ars_route.route('/city', methods=['POST'])
def ars_city():
    if request.method == 'POST':
        filename = request.form['audio-filename']
        file = request.files['audio-blob']
        filename = str(session.get('name')) + '-' + filename
        upload_folder = 'static/audio'
        # 首先保存音频，方便以后复查
        audio_path = save_file(file, filename, upload_folder)

        # 对音频进行转换处理
        # out_path = upsample_wav(audio_path)
        url_path = audio_path.split('app')[1]
        # 删除原音频
        # delete_audio(audio_path, out_path)
        # if session.get('user_id') is not None:
        #     answer_config_db = AnswerConfigDB.query.filter_by(user_id=session.get('user_id')).one()
        # else:
        #     raise Exception("session失效")
        answer_config_db = AnswerConfigDB.query.filter_by(id=1).one()
        language = session.get("language")
        client = Question(audio_path,language=language,answer_config=answer_config_db)
        # 城市
        result, score = client.match_city()
        # print(result)
        ret = str(result) + '(' + str(score) + ')'
        print(ret)
        # 存入数据库
        if session.get('result_id') is not None:
            result = Result.query.filter_by(id=session.get('result_id')).one()
            uri = Path.query.filter_by(result_id=result.id).one()
            if result:
                result.city = ret
                uri.city = url_path
                # db.session.add(result)
                # db.session.add(uri)
                db.session.commit()
                # save_db('year', ret, out_path)
                return ret
        return "未保存"


# 区
@ars_route.route('/area', methods=['POST'])
def ars_area():
    if request.method == 'POST':
        filename = request.form['audio-filename']
        file = request.files['audio-blob']
        filename = str(session.get('name')) + '-' + filename
        upload_folder = 'static/audio'
        # 首先保存音频，方便以后复查
        audio_path = save_file(file, filename, upload_folder)

        # 对音频进行转换处理
        # out_path = upsample_wav(audio_path)
        url_path = audio_path.split('app')[1]
        # 删除原音频

        answer_config_db = AnswerConfigDB.query.filter_by(id=1).one()
        language = session.get("language")
        client = Question(audio_path,language=language,answer_config=answer_config_db)
        # 区
        result, score = client.match_area()
        # print(result)
        ret = str(result) + '(' + str(score) + ')'
        print(ret)
        # 存入数据库
        if session.get('result_id') is not None:
            result = Result.query.filter_by(id=session.get('result_id')).one()
            uri = Path.query.filter_by(result_id=result.id).one()
            if result:
                result.area = ret
                uri.area = url_path
                # db.session.add(result)
                # db.session.add(uri)
                db.session.commit()
                return ret
        return "未保存"


# 街道
@ars_route.route('/street', methods=['POST'])
def ars_street():
    if request.method == 'POST':
        filename = request.form['audio-filename']
        file = request.files['audio-blob']
        filename = str(session.get('name')) + '-' + filename
        upload_folder = 'static/audio'
        # 首先保存音频，方便以后复查
        audio_path = save_file(file, filename, upload_folder)

        # 对音频进行转换处理
        # out_path = upsample_wav(audio_path)
        url_path = audio_path.split('app')[1]
        # 删除原音频
        # delete_audio(audio_path, out_path)

        # if session.get('user_id') is not None:
        #     answer_config_db = AnswerConfigDB.query.filter_by(user_id=session.get('user_id')).one()
        # else:
        #     raise Exception("session失效")
        answer_config_db = AnswerConfigDB.query.filter_by(id=1).one()
        language = session.get("language")
        client = Question(audio_path,language=language,answer_config=answer_config_db)
        # 街道
        result, score = client.match_street()
        # print(result)
        ret = str(result) + '(' + str(score) + ')'
        print(ret)
        # 存入数据库
        if session.get('result_id') is not None:
            result = Result.query.filter_by(id=session.get('result_id')).one()
            uri = Path.query.filter_by(result_id=result.id).one()
            if result:
                result.street = ret
                uri.street = url_path
                # db.session.add(result)
                # db.session.add(uri)
                db.session.commit()
                return ret
        return "未保存"


# 楼层
@ars_route.route('/floor', methods=['POST'])
def ars_floor():
    if request.method == 'POST':
        filename = request.form['audio-filename']
        file = request.files['audio-blob']
        filename = str(session.get('name')) + '-' + filename
        upload_folder = 'static/audio'
        # 首先保存音频，方便以后复查
        audio_path = save_file(file, filename, upload_folder)

        # 对音频进行转换处理
        # out_path = upsample_wav(audio_path)
        url_path = audio_path.split('app')[1]
        # 删除原音频
        # delete_audio(audio_path, out_path)

        # if session.get('user_id') is not None:
        #     answer_config_db = AnswerConfigDB.query.filter_by(user_id=session.get('user_id')).one()
        # else:
        #     raise Exception("session失效")
        answer_config_db = AnswerConfigDB.query.filter_by(id=1).one()
        language = session.get("language")
        client = Question(audio_path,language=language,answer_config=answer_config_db)
        # 年份
        result, score = client.match_floor()
        # print(result)
        ret = str(result) + '(' + str(score) + ')'
        print(ret)
        # 存入数据库
        if session.get('result_id') is not None:
            result = Result.query.filter_by(id=session.get('result_id')).one()
            uri = Path.query.filter_by(result_id=result.id).one()
            if result:
                result.floor = ret
                uri.floor = url_path
                # db.session.add(result)
                # db.session.add(uri)
                db.session.commit()
                # save_db('year', ret, out_path)
                return ret
        return "未保存"


# 地方
@ars_route.route('/location', methods=['POST'])
def ars_location():
    if request.method == 'POST':
        filename = request.form['audio-filename']
        file = request.files['audio-blob']
        filename = str(session.get('name')) + '-' + filename
        upload_folder = 'static/audio'
        # 首先保存音频，方便以后复查
        # filename = str(session.get('name')) + filename
        audio_path = save_file(file, filename, upload_folder)

        # 对音频进行转换处理
        # out_path = upsample_wav(audio_path)
        url_path = audio_path.split('app')[1]
        # 删除原音频

        answer_config_db = AnswerConfigDB.query.filter_by(id=1).one()
        language = session.get("language")
        client = Question(audio_path,language=language,answer_config=answer_config_db)
        # 地方
        result, score = client.match_location()
        # print(result)
        ret = str(result) + '(' + str(score) + ')'
        print(ret)
        # 存入数据库
        if session.get('result_id') is not None:
            result = Result.query.filter_by(id=session.get('result_id')).one()
            uri = Path.query.filter_by(result_id=result.id).one()
            if result:
                result.location = ret
                uri.location = url_path

                db.session.commit()
                # save_db('year', ret, out_path)
                return ret
        return "未保存"


# 回忆
@ars_route.route('/immediateMemory', methods=['POST'])
def ars_immediate_momery():
    if request.method == 'POST':
        filename = request.form['audio-filename']
        file = request.files['audio-blob']
        filename = str(session.get('name')) + '-' + filename
        upload_folder = 'static/audio'
        # 首先保存音频，方便以后复查
        audio_path = save_file(file, filename, upload_folder)

        # 对音频进行转换处理
        # out_path = upsample_wav(audio_path)
        url_path = audio_path.split('app')[1]
        # 删除原音频
        # delete_audio(audio_path, out_path)
        language = session.get("language")
        client = Question(audio_path, language=language)
        # 回忆
        result, score = client.memory()
        # print(result)
        ret = str(result) + '(' + str(score) + ')'
        print(ret)
        # 存入数据库
        if session.get('result_id') is not None:
            result = Result.query.filter_by(id=session.get('result_id')).one()
            uri = Path.query.filter_by(result_id=result.id).one()
            if result:
                result.immediate_memory = ret
                uri.immediate_memory = url_path

                db.session.commit()

                return ret
        return "未保存"


@ars_route.route('/lateMemory', methods=['POST'])
def ars_late_momery():
    if request.method == 'POST':
        filename = request.form['audio-filename']
        file = request.files['audio-blob']
        filename = str(session.get('name')) + '-' + filename
        upload_folder = 'static/audio'
        # 首先保存音频，方便以后复查
        audio_path = save_file(file, filename, upload_folder)

        # 对音频进行转换处理
        # out_path = upsample_wav(audio_path)
        url_path = audio_path.split('app')[1]
        # 删除原音频
        # delete_audio(audio_path, out_path)
        language = session.get("language")
        client = Question(audio_path, language=language)
        # 回忆
        result, score = client.memory()
        # print(result)
        ret = str(result) + '(' + str(score) + ')'
        print(ret)
        # 存入数据库
        if session.get('result_id') is not None:
            result = Result.query.filter_by(id=session.get('result_id')).one()
            uri = Path.query.filter_by(result_id=result.id).one()
            if result:
                result.late_memory = ret
                uri.late_memory = url_path
                # db.session.add(result)
                # db.session.add(uri)
                db.session.commit()
                # save_db('year', ret, out_path)
                return ret
        return "未保存"


# 计算
@ars_route.route('/compute', methods=['POST'])
def ars_compute():
    if request.method == 'POST':
        filename = request.form['audio-filename']
        file = request.files['audio-blob']
        filename = str(session.get('name')) + '-' + filename
        upload_folder = 'static/audio'
        # 首先保存音频，方便以后复查
        audio_path = save_file(file, filename, upload_folder)

        # 对音频进行转换处理
        # out_path = upsample_wav(audio_path)
        url_path = audio_path.split('app')[1]
        # 删除原音频
        # delete_audio(audio_path, out_path)
        language = session.get("language")
        client = Question(audio_path, language=language)
        # 计算
        result, score = client.compute()
        # print(result)
        ret = str(result) + '(' + str(score) + ')'
        print(ret)
        # 存入数据库
        if session.get('result_id') is not None:
            result = Result.query.filter_by(id=session.get('result_id')).one()
            uri = Path.query.filter_by(result_id=result.id).one()
            if result:
                result.compute = ret
                uri.compute = url_path
                # db.session.add(result)
                # db.session.add(uri)
                db.session.commit()
                # save_db('year', ret, out_path)
                return ret
        return "未保存"


# 铅笔命名
@ars_route.route('/namePencil', methods=['POST'])
def ars_pencil():
    if request.method == 'POST':
        filename = request.form['audio-filename']
        file = request.files['audio-blob']
        filename = str(session.get('name')) + '-' + filename
        upload_folder = 'static/audio'
        # 首先保存音频，方便以后复查
        audio_path = save_file(file, filename, upload_folder)

        # 对音频进行转换处理
        # out_path = upsample_wav(audio_path)
        url_path = audio_path.split('app')[1]
        # 删除原音频
        # delete_audio(audio_path, out_path)
        language = session.get("language")
        client = Question(audio_path,language=language)
        # 铅笔
        result, score = client.name_pencil()
        # print(result)
        ret = str(result) + '(' + str(score) + ')'
        print(ret)
        # 存入数据库
        if session.get('result_id') is not None:
            result = Result.query.filter_by(id=session.get('result_id')).one()
            uri = Path.query.filter_by(result_id=result.id).one()
            if result:
                result.name_pencil = ret
                uri.name_pencil = url_path
                # db.session.add(result)
                # db.session.add(uri)
                db.session.commit()
                # save_db('year', ret, out_path)
                return ret
        return "未保存"


# 手表命名
@ars_route.route('/nameWatch', methods=['POST'])
def ars_watch():
    if request.method == 'POST':
        filename = request.form['audio-filename']
        file = request.files['audio-blob']
        filename = str(session.get('name')) + '-' + filename
        upload_folder = 'static/audio'
        # 首先保存音频，方便以后复查
        audio_path = save_file(file, filename, upload_folder)

        # 对音频进行转换处理
        # out_path = upsample_wav(audio_path)
        url_path = audio_path.split('app')[1]
        # 删除原音频
        # delete_audio(audio_path, out_path)
        language = session.get("language")
        client = Question(audio_path,language=language)
        # 铅笔
        result, score = client.name_watch()
        # print(result)
        ret = str(result) + '(' + str(score) + ')'
        print(ret)
        # 存入数据库
        if session.get('result_id') is not None:
            result = Result.query.filter_by(id=session.get('result_id')).one()
            uri = Path.query.filter_by(result_id=result.id).one()
            if result and uri:
                result.name_watch = ret
                uri.name_watch = url_path
                # db.session.add(result)
                # db.session.add(uri)
                db.session.commit()
                # save_db('year', ret, out_path)
                return ret
        return "未保存"


# 复述
@ars_route.route('/repeat', methods=['POST'])
def ars_repeat():
    if request.method == 'POST':
        filename = request.form['audio-filename']
        file = request.files['audio-blob']
        filename = str(session.get('name')) + '-' + filename
        upload_folder = 'static/audio'
        # 首先保存音频，方便以后复查
        audio_path = save_file(file, filename, upload_folder)

        # 对音频进行转换处理
        # out_path = upsample_wav(audio_path)
        url_path = audio_path.split('app')[1]
        # 删除原音频
        # delete_audio(audio_path, out_path)
        language = session.get("language")
        client = Question(audio_path,language=language)
        # 复述
        result, score = client.repeat()
        # print(result)
        ret = str(result) + '(' + str(score) + ')'
        print(ret)
        # 存入数据库
        if session.get('result_id') is not None:
            result = Result.query.filter_by(id=session.get('result_id')).one()
            uri = Path.query.filter_by(result_id=result.id).one()
            if result:
                result.repeat = ret
                uri.repeat = url_path
                # db.session.add(result)
                # db.session.add(uri)
                db.session.commit()
                # save_db('year', ret, out_path)
                return ret
        return "未保存"
