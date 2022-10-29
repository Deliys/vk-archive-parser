import json
from multiprocessing.pool import ThreadPool

from alive_progress import alive_bar

import requests
from os import listdir , mkdir
from os.path import isfile, isdir, join, basename, dirname, splitext
from bs4 import BeautifulSoup

BASE_DIR = 'Archive/messages'
OUT_DIR_IMG_ALL = join('result')

__current_id = ''


def get_attachment_image_links_from_document(html_doc: str) -> list:
	soup = BeautifulSoup(html_doc, 'html.parser')
	link_tags = soup.find_all("a", class_="attachment__link")
	links = [tag['href'] for tag in link_tags if tag['href'].find('.jpg') != -1]
	return links


def get_all_files_from_directory(path: str, ext: list) -> list:
	return [join(path, f) for f in listdir(path) if isfile(join(path, f)) and splitext(join(path, f))[1] in ext]


def get_all_dirs_from_directory(path: str) -> list:
	return [join(path, f) for f in listdir(path) if isdir(join(path, f))]


def walk_dialog_directory(dir_path: str) -> list:
	files = get_all_files_from_directory(dir_path, ['.html'])
	result = []
	for file in files:
		f = open(file, encoding='windows-1251')
		try:
			content = '\n'.join(f.readlines())
			result.extend(get_attachment_image_links_from_document(content))
		except Exception as e:
			print('Error in file ' + file)
		finally:
			f.close()
	return result


def walk_messages_directory(base_dir: str) -> dict:
	result = {}
	dirs = get_all_dirs_from_directory(base_dir)
	with alive_bar(len(mylist)) as bar:
		for i in mylist:
			bar()
			time.sleep(1)
	
	for i, path in enumerate(dirs):
		print('Processing dialog ' + str(i) + ' out of ' + str(len(dirs)))
		id = basename(dirname(path + '/'))
		imgs = walk_dialog_directory(path)
		if len(imgs) > 0:
			result[id] = imgs
	return result


def download_file(url: str):
	file_name_start_pos = url.rfind("/") + 1
	file_name = url[file_name_start_pos:]
	file_name = join(OUT_DIR_IMG_ALL, __current_id +"\\"+__current_id+ '_' + file_name)

	try:
		mkdir((OUT_DIR_IMG_ALL+"/"+__current_id))
	except Exception as e:

		pass

	r = requests.get(url, stream=True)
	if r.status_code == requests.codes.ok:
		with open(file_name, 'wb') as f:
			for data in r:
				f.write(data)
	return url


def download_images(obj: dict):
	global __current_id
	total_count = len(obj)
	i = 1
	pool = ThreadPool(8)
	for key, urls in obj.items():
		__current_id = key
		print('скачено ' + str(i) + ' чатов из ' + str(total_count))
		result = list(pool.imap_unordered(download_file, urls))
		# print(result)
		i += 1
	pool.close()


def main():
	print('1:архив \n2:result.json')
	mode = input("введите режим")
	if mode == '1':
		try:
			print('***************** MODE 1************************')
			result = walk_messages_directory(BASE_DIR)
			f = open('result.json', 'w')
			json.dump(result, f)
			f.close()
		except Exception as e:
			print(e)

	elif mode == '2':

		print('***************** MODE 2************************')
		


		f = open('result.json')
		result = json.load(f)
		f.close()
		try:
			mkdir("result")
		except Exception as e:
			pass


		for i in result:
			for url in result[i]:
				print(i , len(result[i]))
				input()


		print('в {} чатах всего {} фотографий'.format(len(result) ,len_photo))
		
		# if old_photo >0:
		#   print("ого , так ты уже использывал этот режим?\nТогда вычеркиваем уже скаченные {} фотографии из общего списка".format(old_photo))
		

		download_images(result)
	else:
		print('нет такого режима')



if __name__ == '__main__':
	main()
