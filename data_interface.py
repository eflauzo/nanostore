import os
import glob
import shutil
import sqlite3
import math

#class Dataset 

EXTENSION = '.chan_db'

#def channel_db_from_channel_id(db_path, channel_id):
#    dataset, channel = channel_id.split('/')
#    return ChannelDatabase(db_path, dataset, channel)

class ChannelDatabase:
    def __init__(self, db_path, dataset, channel_name):
        self.filename = os.path.join(db_path, dataset, channel_name + EXTENSION)
        print('******* self.filename', self.filename)
        self.conn = sqlite3.connect(self.filename)
        self.create_table()
    
    def create_table(self):
        cursor = self.conn.cursor()
        cursor.execute('PRAGMA journal_mode=WAL')
        cursor.execute("CREATE TABLE IF NOT EXISTS data (ix REAL PRIMARY KEY ASC NOT NULL, vals REAL) ")

    def write(self, index, values):
        values = str(list(zip(index, values)))[1:-1]
        cursor = self.conn.cursor()
        cursor.execute('BEGIN TRANSACTION')
        cursor.execute('INSERT INTO data (ix, vals) VALUES %s' % values)
        cursor.execute('COMMIT')

    def get_range(self):
        cursor = self.conn.cursor()
        cursor.execute('SELECT (SELECT min(ix) FROM data), (SELECT max(ix) FROM data); ')
        output = cursor.fetchall()[0]
        print("get range got",output )
        return output
        

    def get_data_for_plotting(self, start, end, num_of_points):
        cursor = self.conn.cursor()
        
        #cur = cursor.execute('SELECT ix, vals FROM data').fetchall()
        
        step = (end - start) / num_of_points

        ix = []
        vals = []

        row = cursor.execute('SELECT ix, vals FROM data WHERE (ix <= %2.10f) LIMIT 1 ' % start).fetchall()
        if len(row) != 0:
            #print ("whoopsie")
            #return [],[]    
            ix_i, vals_i = row[0]
            ix.append(ix_i)
            vals.append(vals_i)
            last_index = ix_i
        else:
            last_index = start

        for i in range(num_of_points):
            #print (">>> ")
            #print(i)
            #last_index = ix_i
            row = cursor.execute('SELECT ix, vals FROM data  WHERE (ix >= %2.10f) LIMIT 1' % last_index).fetchall()
            if len(row) == 0:
                #print("fall")
                return ix, vals
            ix_i, vals_i = row[0]
            last_index = ix_i + step
            ix.append(ix_i)
            vals.append(vals_i)
            if ix_i > end:
                break
        #print(ix)
        #print(vals)
        return (ix, vals)

        '''
        cnt = 0
        for row in cur:
            print(row)
            cnt += 1
        '''

        #print("count = ", cnt)

    def get_all_data(self):
        cursor = self.conn.cursor()
        cur = cursor.execute('SELECT ix, vals FROM data').fetchall()
        cnt = 0
        for row in cur:
            print(row)
            cnt += 1

        print("count = ", cnt)


class DataRoot:
    def __init__(self, db_path):
        self.db_path = db_path
    
    def list_datasets(self, glob_filter, limit=1000):
        rez = []
        for name in glob.glob(os.path.join(self.db_path, glob_filter)):
            rez.append(os.path.basename(name))
        return rez
    
    def list_channels(self, datasets, glob_filter, limit=1000):
        rez = []
        for ds in datasets:
            print("scammomg", ds)
            data_path = os.path.join(self.db_path, self.db_path,ds, glob_filter+EXTENSION)
            print(data_path)
            for name in glob.glob(data_path):
                name_wo_ext = os.path.splitext(name)[0]
                rez.append(ds+"/"+os.path.basename(name_wo_ext))
        print(rez)
        return rez
    
    def delete_dataset(self, name):
        shutil.rmtree(os.path.join(self.db_path, name))
    
    def create_dataset(self, name, error_if_exists=False):
        new_dir = os.path.join(self.db_path, name)
        if error_if_exists:
            if os.path.isdir(new_dir):
                raise RuntimeError("Dataset already exists")
        os.makedirs(new_dir)

    def get_channel_db(self, dataset_name, channel_name):
        return ChannelDatabase(self.db_path, dataset_name, channel_name)


        
if __name__ == "__main__":
    import numpy as np
    from scipy import signal as sg
    import matplotlib.pyplot as plt

    test_root = '/Users/eflauzo/prj/dirt/data'
    data = DataRoot(test_root)
    
    def make_test_dataset(name):
        if len(data.list_datasets(name)) != 0:
            print(name)
            data.delete_dataset(name)
        data.create_dataset(name)

    make_test_dataset('test_data')
    make_test_dataset('test_data1')
    make_test_dataset('test_data2')

    time_1hz = np.linspace(0, 10, 10*1000)
    time_1khz = np.linspace(0, 10, 10*1000*100)
    time_1mhz = np.linspace(0, 10, 10*1000*1000)

    freq = 1
    amp = 1.5
    sin_signal_1hz = amp*np.sin(2*np.pi*freq*time_1hz)
    sin_signal_1khz = amp*np.sin(2*np.pi*freq*time_1khz)
    sin_signal_1mhz = amp*np.sin(2*np.pi*freq*time_1mhz)

    square_signal_1khz = amp*sg.square(2*np.pi*freq*time_1khz, duty=0.3)

    data.get_channel_db('test_data', "sin_1hz").write(time_1hz, sin_signal_1hz)
    data.get_channel_db('test_data', "sin_1khz").write(time_1khz, sin_signal_1khz)
    data.get_channel_db('test_data', "square_1khz").write(time_1khz, square_signal_1khz)
    





'''
if __name__ == "__main__":
    data = DataRoot('/Users/eflauzo/prj/dirt/data')
    
    if len(data.list_datasets('test_data')) != 0:
        print('deleted')
        data.delete_dataset('test_data')

    data.create_dataset('test_data')
    chdb = data.get_channel_db('test_data', "gamma 1hz")
    index = []
    values = []
    start_tm = 1615079361
    
    for i in range(360):
        index.append(i + start_tm)
        values.append(math.sin(i/360.0 * (2*3.14)))
    chdb.write(
        index,
        values
    )
    print(chdb.get_range())

    index = []
    values = []

    square_index = []
    square_value = []

    chdb = data.get_channel_db('test_data', "res 1khz")
    last = 0
    for i in range(36000):
        index.append(i + start_tm)
        square_index(i + start_tm)

        values.append(math.sin(i/36000.0 * (2*3.14)))
        if last = 0:
            new_val = 1

            square_value
    chdb.write(
        index,
        values
    )
    chdb.get_range()
    print(chdb.get_range())

    
    if len(data.list_datasets('test_data2')) != 0:
        print('deleted')
        data.delete_dataset('test_data2')

    data.create_dataset('test_data2')

    chdb = data.get_channel_db('test_data2', "gamma 1Mhz")
    index = []
    values = []
    for i in range(360000):
        index.append(i + start_tm)
        values.append(math.sin(i/36000000.0 * (2*3.14)))
    chdb.write(
        index,
        values
    )
    
    print('old:')
    chdb.get_range()
    
    chdb = data.get_channel_db('test_data2', "gamma 1Mhz")
    print('new:')
    s, e = chdb.get_range()
    print(chdb.get_range())

    ix, v = chdb.get_data_for_plotting(s,e,10)
    xx = list(zip(ix, v))
    for i in xx:
        print(i)




    #chdb.get_all_data()

'''