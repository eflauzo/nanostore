import data_interface
import os

from flask import Flask, app, request, jsonify
app = Flask(__name__, static_url_path='', static_folder='web/static')

THIS_DIR = os.path.dirname(os.path.realpath(__file__))
DATA_DIR = os.path.join(THIS_DIR, 'data')

def get_data_interface():
    return data_interface.DataRoot(DATA_DIR)

@app.route('/')
def root():
    print("xxx")
    return app.send_static_file('index.html')

@app.route('/get_datasets')
def get_datasets():
    print("111")
    filter_str = request.args.get('filter', default = '*', type = str)
    print(filter_str)
    return jsonify(get_data_interface().list_datasets(filter_str))

@app.route('/get_channels')
def get_channels():
    print("111")
    datasets_str = request.args.get('datasets', type = str)
    filter_str = request.args.get('filter', default = '*', type = str)
    datasets = datasets_str.split(",")
    #print(datasets_str)
    #result = []
    #for ds in datasets:
    #    get_data_interface().list_channels(ds, filter_str)
    #return jsonify(get_data_interface().list_datasets(filter_str))
    #return jsonify(['a', 'b', 'c'])
    return jsonify(get_data_interface().list_channels(datasets, filter_str))

@app.route('/get_range/<dataset>/<channel_id>')
def get_range(dataset, channel_id):
    #db = data_interface.channel_db_from_channel_id(DATA_DIR, channel_id)
    print("!!!!!!!!!!!!!!!!!", dataset, channel_id)
    db = data_interface.ChannelDatabase(DATA_DIR, dataset, channel_id)
    #print(db.get_all_data())
    start, end = db.get_range()
    response = {"start":start, "end":end}
    print("range response ", response)
    return jsonify(response)

@app.route('/get_multi_range')
def get_multi_range():
    channels = request.args.get('channels', type = str)
    ch_list = channels.split(',')
    result = {
        "channels":{},
        "total":{},
    }
    vals = []
    print(channels)
    for ch in ch_list:
        dataset, channel_id = ch.split('/')
        db = data_interface.ChannelDatabase(DATA_DIR, dataset, channel_id)
        start, end = db.get_range()
        vals.append(start)
        vals.append(end)
        result["channels"][ch] = {'start': start, 'end': end}
    result["total"] = {'start': min(vals), 'end': max(vals)}
    print(result)
    return jsonify(result)

@app.route('/get_data_for_plot/<dataset>/<channel_id>/<start>/<end>/<number_of_points>')
def get_data_for_plot(dataset, channel_id, start, end, number_of_points):
    #db = data_interface.channel_db_from_channel_id(DATA_DIR, channel_id)
    #print("!!!!!!!!!!!!!!!!!", dataset, channel_id)
    db = data_interface.ChannelDatabase(DATA_DIR, dataset, channel_id)
    #print(db.get_all_data())
    #start, end = db.get_range()
    #response = {"start":start, "end":end}
    #print("range response ", response)
    ix, val = db.get_data_for_plotting(float(start), float(end), int(number_of_points))
    result = {
        "last_loaded":{
            "start": start,
            "end": end,
            "number_of_points":number_of_points, 
        },
        "buffer":{
            "index": ix,
            "values": val
        }
    }
    return jsonify(result)



if __name__ == "__main__":
    app.run()