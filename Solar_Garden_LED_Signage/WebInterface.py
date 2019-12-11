#!/usr/bin/python3
"""
author: Tyler Thompson
date: October 26th 2019
"""
import os, random
from flask import Flask, render_template, request, session, redirect, send_from_directory
from flask_menu import Menu, register_menu
from resources.config import Git, Config
from resources import logging
from resources.DataStores import DataSync

config = Config()
data_sync = DataSync.DataSync()
logger = logging.get_logger(__name__)
app = Flask(__name__)
Menu(app=app)
app.secret_key = os.urandom(12)


def main():
    app.run(
        debug=config.config['interfaces']['web']['debug'],
        host='0.0.0.0',
        port=config.config['interfaces']['web']['port'],
        threaded=True
    )


def allowed_file(filename):
    """
    Tell whether or not a file extension is allowed
    :param filename: any string that is a filename
    :return: True | False
    """
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in config.config['interfaces']['web']['extensions']


@app.route("/")
@register_menu(app, '.', "Home")
def home():
    """
    The main route of the site
    :return: main_page.html or login.html
    """
    # session['logged_in'] = True  # comment this line out to enable login
    if not session.get('logged_in'):
        return render_template('login.html')

    config.read_config()
    return render_template('main_page.html', config=config.config)


@app.route("/login", methods=['POST'])
def login():
    """
    Processes a user login
    :return: an error message or redirect to /
    """
    session['client_ip'] = request.remote_addr
    session['username'] = request.form['username']
    password = request.form['password']
    if password == "" or not password:
        return render_template('message.html', alertLevel="error", message="Password cannot be blank.", returnurl="/")

    if session.get('username') == config.config['interfaces']['web']['username']:
        if password == config.config['interfaces']['web']['password']:
            session['logged_in'] = True
            session['name'] = "Administrator"
        else:
            return render_template('message.html', alertLevel="error", message="Bad Password.", returnurl="/")
    else:
        return render_template('message.html', alertLevel="error", message="Bad Username.", returnurl="/")
    return redirect("/")


@app.route("/frames")
@register_menu(app, '.frames', 'Frames', order=1)
def frames():
    """
    The frame summary page
    :return: frames.html
    """
    if not session.get('logged_in'):
        return redirect("/")
    return render_template('frames/frames.html', summaryview='read', config=config.config)


@app.route("/add_frame", methods=['POST', 'GET'])
@register_menu(app, '.frames.add_frame', 'Add Frame', order=1)
def add_frame():
    """
    The add frame page
    :return: add_frame.html
    """
    if not session.get('logged_in'):
        return redirect("/")

    frame_template = None
    if "load_template" in request.form:
        frame_template = config.config['frame_templates'][request.form.to_dict()['type']]
        session['frame_type'] = request.form.to_dict()['type']

    elif "add_frame" in request.form:
        new_frame_config = request.form.to_dict()
        new_frame_config.pop('add_frame')
        new_frame_config['index'] = len(config.config['frames'])

        if "image" in request.files:
            if not request.files['image'].filename:
                return render_template('message.html',
                                       alertLevel='error',
                                       return_url='/add_frame',
                                       message='No file selected to upload')
            elif not allowed_file(request.files['image'].filename):
                return render_template('message.html',
                                       alertLevel='error',
                                       return_url='/add_frame',
                                       message='Unsupported file format')
            else:
                new_frame_config['image'] = request.files['image'].filename

        for key in new_frame_config:
            if not new_frame_config[key] and key != 'index':
                return render_template('message.html',
                                       alertLevel='error',
                                       return_url='/add_frame',
                                       message='{0} cannot be left empty'.format(key))

        if "image" in request.files:
            request.files['image'].save(os.path.join(config.image_dir, request.files['image'].filename))

        config.add_frame(new_config=new_frame_config)

        return redirect('/frames')

    return render_template('frames/add_frame.html', config=config.config, frame_template=frame_template)


@app.route("/edit_frame", methods=['POST', 'GET'])
@register_menu(app, '.frames.edit_frame', 'Edit Frame', order=0)
def edit_frame():
    """
    The edit frame page
    :return: edit_frame.html
    """
    if not session.get('logged_in'):
        return redirect("/")

    if "edit" in request.form:
        session['edit_frame'] = config.config['frames'][int(request.form['index'])]

    elif "save" in request.form:
        frame = request.form.to_dict()
        frame.pop('save')
        config.update_frame(frame=frame)
        session['edit_frame'] = config.config['frames'][int(frame['index'])]
    else:
        session['edit_frame'] = None

    return render_template('frames/edit_frame.html', summaryview='edit', config=config.config)


@app.route("/delete_frame", methods=['POST', 'GET'])
@register_menu(app, '.frames.delete_frame', 'Delete Frame', order=2)
def delete_frame():
    """
    The delete frame page
    :return: delete_frame.html
    """
    if not session.get('logged_in'):
        return redirect("/")

    if "delete" in request.form:
        global config
        delete_index = request.form['index']
        config.del_frame(int(delete_index))

    return render_template('frames/delete_frame.html', summaryview='delete', config=config.config)


@app.route("/available_data", methods=['GET'])
@register_menu(app, '.available_data', 'Available Data', order=2)
def available_data():
    """
    The available data page
    :return: available_data.html
    """
    if not session.get('logged_in'):
        return redirect("/")

    status = data_sync.connection_status()
    if status:
        data_sync.sync_all_data()
        config.read_config()
    return render_template('available_data.html', config=config.config, connection_status=status)


@app.route("/settings", methods=['POST', 'GET'])
@register_menu(app, '.settings', 'Settings', order=3)
def settings():
    """
    The settings page
    :return: settings.html
    """
    if not session.get('logged_in'):
        return redirect("/")

    '''Save settings'''
    if "save_settings" in request.form:
        new_settings = request.form.to_dict()
        config.config['displays']['led_matrix']['brightness'] = int(new_settings['brightness'])
        config.config['interfaces']['web']['username'] = new_settings['username']
        if new_settings['password']:
            config.config['interfaces']['web']['password'] = new_settings['password']
        config.config['interfaces']['web']['port'] = int(new_settings['port'])
        config.config['interfaces']['web']['debug'] = True if new_settings['debug'] == 'on' else False

        if config.config['data_stores']['location']['name'] != new_settings['data_location']:
            config.config['data_stores']['location']['name'] = new_settings['data_location']

            # enable/disable frames based on new location
            for frame in config.config['frames']:
                if "data" in frame['type']:
                    if frame['location'] == config.config['data_stores']['location']['name']:
                        frame['enabled'] = True
                    else:
                        frame['enabled'] = False
        config.write_config()

    return render_template('settings.html', config=config.config)


@app.route("/about")
@register_menu(app, '.about', 'About', order=4)
def about():
    """
    The about page
    :return: about.html
    """
    if not session.get('logged_in'):
        return redirect("/")
    return render_template('about.html', git=Git(), config=config)


@app.route("/logout")
@register_menu(app, '.logout', 'Logout', order=5)
def logout():
    """
    Logs a user out
    :return: redirect to /
    """
    session['logged_in'] = False
    session.clear()
    return redirect("/")


@app.route('/uploads/<filename>')
def uploaded_file(filename):
    """
    Makes uploaded images available to be displayed on the site
    :param filename: file name of the image
    :return: the image
    """
    if not session.get('logged_in'):
        return redirect("/")
    return send_from_directory(config.image_dir, filename)


@app.template_filter(name='normalize')
def normalize(value):
    """
    Replace underscores with spaces
    :param value: any string
    :return: the input string with spaces
    """
    try:
        return value.replace('_', ' ')
    except AttributeError:
        return value


@app.template_filter(name='all_upper')
def all_upper(value):
    """
    Make all the characters in a string uppercase
    :param value: any string
    :return: the input sting in uppercase
    """
    value = str(value)
    new_value = ""
    for character in value:
        new_value += character.upper()
    return new_value


@app.template_filter(name='random_color')
def random_color(value=0):
    """
    Generate a random hex color code
    :param value: optional reference value
    :return: a hex color code as a string
    """
    r = random.randint(0, value)
    g = random.randint(value, 255)
    b = random.randint(0, 255-value)
    rgbl = [r, g, b]
    random.shuffle(rgbl)
    return '#%02x%02x%02x' % tuple(rgbl)


@app.template_filter(name='log')
def message_log(msg):
    """
    Log a message from the front end
    :param msg: any string
    :return: the input message
    """
    logger.info(msg=msg)
    msg.strip()
    return msg


if __name__ == '__main__':
    main()
