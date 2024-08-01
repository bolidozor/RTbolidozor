


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
	step = 2000
	start = time.time()
	last_time = time.time()
	db = pymongo.MongoClient("mongodb://localhost:27017/").Bolidozor

	for loop in range(0, 100000000, step):
		print("Start index", loop)
		print(time.time() - last_time, "s")
		print(time.time() - start, "s")

		last_time = time.time()
		data = _sql("Select * FROM MLABvo.bolidozor_met ORDER BY ID LIMIT {} OFFSET {}".format(step, loop+7017))
		#last_time = start

		for row in data:
			print(row)
			#file_type = 0
			#if 'raw' in row['filename']: file_type = 1
			#elif 'met.' in row['filename']: file_type = 2
			#elif 'snap' in row['filename']: file_type = 3
			#elif 'meta' in row['filename']: file_type = 4
			#

			collection = {
				"_id": bson.ObjectId(),
				"fid": row['id'],
				"name": row['name'],
				"name_simple": row['namesimple'],
				"status": row['status'],
				"web": [row['web']],
				"description": row['comment'],
				"station":{"hardware": row['hardware'], 'RTbolidozor':row['RTbolidozor']},
				"description": row['comment'],
				"maintainer":[row['owner']]
			}
			print(collection)
			print(row['observatory'])
			db.observatory.update({'fid': row['observatory']}, {'$addToSet': {'stations': collection}})
			#db.observatory.insert_one(collection)
			#{'filename_original': '20160818210226286_ZVPP-R4_snap.fits', 'id': 2305, 'id_observer': 2, 'filepath': '/storage/bolidozor/ZVPP/ZVPP-R4/snapshots/2016/08/18/21', 'checksum': '139856f4ed6b611c5d07a11374f87e19', 'id_server': 1, 'obstime': datetime.datetime(2016, 8, 18, 21, 5, 2), 'indextime': datetime.datetime(2016, 11, 6, 6, 48, 57), 'filename': '20160818210226286_ZVPP-R4_snap.fits', 'uploadtime': datetime.datetime(2016, 8, 18, 21, 5, 2), 'lastaccestime': datetime.datetime(2016, 8, 18, 21, 5, 7)}


