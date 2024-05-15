import os

from flask import Flask
from applications.common.flask_uploads import configure_uploads

from applications.common.utils.upload import photos
from applications.configs import common
from applications.extensions import init_plugs
from applications.view import init_view
from applications.api import init_api
from applications.configs import config


def create_app(config_name=None):
    app = Flask('pear-admin-flask')

    if not config_name:
        # 尝试从本地环境中读取
        config_name = os.getenv('FLASK_CONFIG', 'development')

    # 引入数据库配置
    app.config.from_object(common)
    app.config.from_object(config[config_name])

    # 注册各种插件
    init_plugs(app)

    # 注册路由
    init_view(app)

    # 注册接口（restful api）
    init_api(app)

    # 文件上传
    configure_uploads(app, photos)

    if os.environ.get('WERKZEUG_RUN_MAIN') == 'true':
        pass

    return app


def logo():
    print('''
 _____                              _           _         ______ _           _    
|  __ \                    /\      | |         (_)       |  ____| |         | |   
| |__) |__  __ _ _ __     /  \   __| |_ __ ___  _ _ __   | |__  | | __ _ ___| | __
|  ___/ _ \/ _` | '__|   / /\ \ / _` | '_ ` _ \| | '_ \  |  __| | |/ _` / __| |/ /
| |  |  __/ (_| | |     / ____ \ (_| | | | | | | | | | | | |    | | (_| \__ \   < 
|_|   \___|\__,_|_|    /_/    \_\__,_|_| |_| |_|_|_| |_| |_|    |_|\__,_|___/_|\_\\

    ''')
