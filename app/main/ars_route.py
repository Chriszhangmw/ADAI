import os
import time
import threading
import pymysql

from flask import Blueprint, request, session, jsonify, render_template

from app.model_src.ASR.asr import Question
from app.model import Result, Path, AnswerConfigDB
import pandas as pd
import datetime
import traceback

from .. import db

ars_route = Blueprint('ars_route', __name__)

#时间：2022/04/14
#作者：王香霖
#更改：增加全称录音功能

import pyaudio
import wave
from pydub import AudioSegment

#全程录音标志
record_flag = True
# Excel文件的数据，每次测试后自动生成一个excel文件，保存语音转写的信息，得分
excel_title = ['问题', '得分', '语音识别']  # Excel文件的表头
excel_data = []


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


@ars_route.route('/StartRecord', methods=['GET'])
def StartRecord():
    return jsonify({'status': record_flag})

# 年份
@ars_route.route('/year', methods=['POST'])
def ars_year():
    if request.method == 'POST':
        filename = request.form['audio-filename']
        file = request.files['audio-blob']
        language = session.get("language")
        tester_name = str(session.get('name'))
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
            global  excel_data
            excel_data = []
            item = ['year', score, result]
            excel_data.append(item)

            # 全称录音
        def record_all():
            global record_flag

            CHUNK = 1024  # 块大小
            FORMAT = pyaudio.paInt16  # 每次采集的位数
            CHANNELS = 1  # 声道数
            RATE = 16000  # 采样率：每秒采集数据的次数
            RECORD_SECONDS = 300  # 最大录音时间5分钟
            WAVE_OUTPUT_FILENAME = os.getcwd().split('app')[0].replace('flask_project\\','flask_project')+"/app/"+upload_folder+f'/{tester_name}的全程录音.wav'  # 文件存放位置
            p = pyaudio.PyAudio()
            stream = p.open(format=FORMAT,
                            channels=CHANNELS,
                            rate=RATE,
                            input=True,
                            frames_per_buffer=CHUNK)
            try:
                print('try:',os.getcwd())
                record_flag = True
                frames = []
                wf = wave.open(WAVE_OUTPUT_FILENAME, 'wb')
                # raise Exception('抛出异常测试')
                print("全称录音开始")
                record_num = 0
                # 最长录5分钟
                while record_flag and record_num<int(RATE / CHUNK * RECORD_SECONDS):
                    record_num += 1
                    data = stream.read(CHUNK)
                    frames.append(data)
            except:# 保存错误日志
                print('AfterError:',os.getcwd())
                with open(os.path.join(os.getcwd().split('app')[0].replace('flask_project\\','flask_project'),'app', upload_folder, '错误日志.txt'), 'w', encoding='utf-8') as SaveLog:
                    SaveLog.write(str(traceback.format_exc()))
            finally:
                print("全称录音结束")
                record_flag = True

                stream.stop_stream()
                stream.close()
                p.terminate()

                wf.setnchannels(CHANNELS)
                wf.setsampwidth(p.get_sample_size(FORMAT))
                wf.setframerate(RATE)
                wf.writeframes(b''.join(frames))
                wf.close()

                # 将第一个问题的回答与全程录音合并，这样全程录音才完整
                # upload_folder = r'static\audio\mandarin\2022.04.11\王香霖041101'
                audio_dirs = os.listdir(os.path.join(os.getcwd().split('app')[0].replace('flask_project\\','flask_project'),'app', upload_folder))
                # 音频合并
                record_file1 = [i for i in audio_dirs if 'year' in i][0]  # 年份音频的文件名
                record_file2 = [i for i in audio_dirs if '全程录音' in i][0]  # 全程录音的文件名
                input_music_1 = AudioSegment.from_wav(os.path.join(os.getcwd().split('app')[0].replace('flask_project\\','flask_project'),'app', upload_folder, record_file1))  # 加载音频
                input_music_2 = AudioSegment.from_wav(os.path.join(os.getcwd().split('app')[0].replace('flask_project\\','flask_project'),'app', upload_folder, record_file2))
                output_music = input_music_1 + input_music_2  # 音频拼接
                output_music.export(os.path.join(os.getcwd().split('app')[0].replace('flask_project\\','flask_project'),'app', upload_folder, record_file2), format="wav")  # 保存音频

        thread_1 = threading.Thread(target=thread_year,args=[rid,pid])
        thread_1.start()

        thread_2 = threading.Thread(target=record_all)
        thread_2.start()

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

            global excel_data
            item = ['reason', score, result]
            excel_data.append(item)


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

            global excel_data
            item = ['month', score, result]
            excel_data.append(item)

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

            global excel_data
            item = ['day', score, result]
            excel_data.append(item)

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

            global excel_data
            item = ['week', score, result]
            excel_data.append(item)

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

            global excel_data
            item = ['city', score, result]
            excel_data.append(item)

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

            global excel_data
            item = ['area', score, result]
            excel_data.append(item)

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

            global excel_data
            item = ['street', score, result]
            excel_data.append(item)

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

            global excel_data
            item = ['floor', score, result]
            excel_data.append(item)

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

            global excel_data
            item = ['location', score, result]
            excel_data.append(item)

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

            global excel_data
            for i in score.keys():
                item = ['immediateMemory' + str(i), score[i], result]
                excel_data.append(item)

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

            global excel_data
            for i in score.keys():
                item = ['lateMemory' + str(i), score[i], result]
                excel_data.append(item)

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

            global excel_data
            for i in score.keys():
                item = ['compute' + str(i), score[i], result]
                excel_data.append(item)

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

            global excel_data
            item = ['namePencil', score, result]
            excel_data.append(item)

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

            global excel_data
            item = ['nameWatch', score, result]
            excel_data.append(item)

        thread_1 = threading.Thread(target=thread_nameWatch, args=[rid, pid])
        thread_1.start()
        return "next"


# 复述
@ars_route.route('/repeat', methods=['POST'])
def ars_repeat():
    #停止录制音频
    global record_flag
    record_flag = False

    if request.method == 'POST':
        filename = request.form['audio-filename']
        file = request.files['audio-blob']
        name = str(session.get('name'))
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

            global excel_data
            global excel_title
            item = ['repeat', score, result]
            excel_data.append(item)

            dir = os.getcwd().split('app')[0].replace('flask_project\\','flask_project')+r'\app'
            print(dir)
            path = os.path.join(dir,upload_folder, name + '-' + datetime.datetime.today().strftime('%Y-%m-%d-%H-%M-%S') + '.xlsx')  # 文件路径及文件名
            print(path)
            writer = pd.ExcelWriter(path)  # 保存成excel格式
            df = pd.DataFrame(excel_data, columns=excel_title)
            df.to_excel(writer, index=None)
            writer.save()
            writer.close()
            print('Excel文件已保存')


        thread_1 = threading.Thread(target=thread_repeat, args=[rid, pid])
        thread_1.start()


        return "next"