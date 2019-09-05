import requests, json, zipfile, os, threading, io

s = requests.session()
def get(url):
	while True:
		try: return s.get(url).text
		except Exception as e: print(e)

hyea_url = 'https://bms.kyouko.moe/'
bms2zip_url = hyea_url + 'BMS2ZIP.json'
zip2bms_url = hyea_url + 'ZIP2BMS.json'
download_url = hyea_url + 'zip/'
download_path = 'Songs'
bms2zip = json.loads(get(bms2zip_url))
zip2bms = json.loads(get(zip2bms_url))
normallist = []
for normallist_url in ['https://lite.stellabms.xyz/score.json', 'https://stellabms.xyz/score.json']:
	normallist += json.loads(get(normallist_url))
normallist.reverse()

if not os.path.exists(download_path):
	os.mkdir(download_path)

lock = threading.Lock()

def Do():
	while True:
		lock.acquire()
		if not normallist:
			lock.release()
			return
		song = normallist.pop()
		lock.release()
		bms = 'BMS_' + song['md5']
		try:
			filename = download_path + '/' + bms2zip[bms][-1]
			tmp_url = download_url + bms2zip[bms][-1] + '.zip'
		except KeyError:
			print('No bms in server :', song)
		if os.path.exists(filename):
			print(song['title'], 'exists')
			continue
		r = s.get(tmp_url)
		if r.status_code != 200:
			print('\033[91m', song['title'], 'download failed\033[00m')
			continue
		r = r.content
		print('\033[92m', song['title'], 'download finish\033[00m')
		with zipfile.ZipFile(io.BytesIO(r), 'r') as zip_ref:
			zip_ref.extractall(filename)
		print('\033[92m', song['title'], 'extract finish\033[00m')

th = [threading.Thread(target = Do, daemon = True) for _ in range(8)]
for t in th: t.start()
for t in th: t.join()
