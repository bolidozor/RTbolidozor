import MySQLdb as mdb
import pymysql.cursors

import pymongo
import bson

import time
import datetime
import csv
import time
import os
import hashlib
import glob


def _sql(query, read=False, db="MLABvo"):
        print("#>", query)
        connection = pymysql.connect(host="localhost", user="root", passwd="root", db=db, use_unicode=True, charset="utf8", cursorclass=pymysql.cursors.DictCursor)
        try:
            cursorobj = connection.cursor()
            cursorobj.execute(query)
            result = cursorobj.fetchall()
            if not read:
                connection.commit()
        except Exception as e:
                print("Err", e)
        connection.close()
        return result



def get_files_and_put_them_in_mongodb():
	print("start")




if __name__ == '__main__':
	get_files_and_put_them_in_mongodb()
	step = 1000
	start = time.time()
	last_time = time.time()
	db = pymongo.MongoClient("mongodb://localhost:27017/").Bolidozor

	for loop in range(0, 100000000, step):
		print("Start index", loop)
		print("Loop", time.time() - last_time, "s")
		print("Loop", (time.time() - last_time)/step, "s/row")
		print("All", time.time() - start, "s")
		print("All", (time.time() - start)/(loop+0.1), "s/row")
		last_time = time.time()

		data = _sql("Select * FROM MLABvo.bolidozor_fileindex ORDER BY ID LIMIT {} OFFSET {}".format(step, loop))
		#last_time = start

		for row in data:
			file_type = 0
			if 'raw' in row['filename']: file_type = 1
			elif 'met.' in row['filename']: file_type = 2
			elif 'snap' in row['filename']: file_type = 3
			elif 'meta' in row['filename']: file_type = 4
			elif 'freq' in row['filename']: file_type = 5

			collection = {
				'filename_original': row['filename_original'],
				'filename': row['filename'],
				'server_file_path': row['filepath'],
				'server_id': row['id_server'],
				'observer_id': row['id_observer'],
				'time_obs': row['obstime'],
				'time_indexed': row['indextime'],
				'time_uploaded': row['uploadtime'],
				'checksum': row['checksum'],
				'type': file_type,

			}

			#print(collection)
			db.file_index.insert_one(collection)
			#{'filename_original': '20160818210226286_ZVPP-R4_snap.fits', 'id': 2305, 'id_observer': 2, 'filepath': '/storage/bolidozor/ZVPP/ZVPP-R4/snapshots/2016/08/18/21', 'checksum': '139856f4ed6b611c5d07a11374f87e19', 'id_server': 1, 'obstime': datetime.datetime(2016, 8, 18, 21, 5, 2), 'indextime': datetime.datetime(2016, 11, 6, 6, 48, 57), 'filename': '20160818210226286_ZVPP-R4_snap.fits', 'uploadtime': datetime.datetime(2016, 8, 18, 21, 5, 2), 'lastaccestime': datetime.datetime(2016, 8, 18, 21, 5, 7)}


		if len(data) == 0:
			print("Konec")
			break;
