######################################################################################
#
#	MovieGo.co - v1.00
#
######################################################################################

TITLE = "MovieGo"
PREFIX = "/video/moviego"
ART = "art-default.jpg"
ICON = "icon-default.png"
ICON_LIST = "icon-list.png"
ICON_COVER = "icon-cover.png"
ICON_SEARCH = "icon-search.png"
ICON_NEXT = "icon-next.png"
ICON_MOVIES = "icon-movies.png"
ICON_SERIES = "icon-tv.png"
ICON_CINEMA = "icon-cinema.png"
ICON_QUEUE = "icon-queue.png"
BASE_URL = "http://moviego.cc"

import updater, os, sys
from lxml import html
try:
	path = os.getcwd().split("?\\")[1].split('Plug-in Support')[0]+"Plug-ins/View47.bundle/Contents/Code/Modules/MovieGo"
except:
	path = os.getcwd().split("Plug-in Support")[0]+"Plug-ins/View47.bundle/Contents/Code/Modules/MovieGo"
if path not in sys.path:
	sys.path.append(path)

updater.init(repo = '/jwsolve/MovieGo.bundle', branch = 'master')

######################################################################################
# Set global variables

def Start():

	ObjectContainer.title1 = TITLE
	ObjectContainer.art = R(ART)
	DirectoryObject.thumb = R(ICON_LIST)
	DirectoryObject.art = R(ART)
	VideoClipObject.thumb = R(ICON_MOVIES)
	VideoClipObject.art = R(ART)

	HTTP.CacheTime = CACHE_1HOUR
	HTTP.Headers['User-Agent'] = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_8_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/31.0.1650.63 Safari/537.36'
	HTTP.Headers['Referer'] = BASE_URL + '/'

######################################################################################
# Menu hierarchy

@handler(PREFIX, TITLE, art=ART, thumb=ICON)
def MainMenu():

	oc = ObjectContainer()
	#updater.add_button_to(oc, PerformUpdate)
	page = HTML.ElementFromURL(BASE_URL)
	oc.add(InputDirectoryObject(key = Callback(Search), title='Search', summary='Search MovieGo', prompt='Search for...'))
	for each in page.xpath("//ul[@class='cf']/li"):
		try:
			title = each.xpath("./a/text()")[0].strip()
			category = each.xpath("./a/@href")[0]
			oc.add(DirectoryObject(
				key = Callback(ShowCategory, title = title, category = category, page_count = 1),
				title = title,
				thumb = R(ICON_LIST)
				)
			)
		except:
			pass
	return oc

######################################################################################
@route(PREFIX + "/performupdate")
def PerformUpdate():
	return updater.PerformUpdate()

######################################################################################
# Creates page url from category and creates objects from that page

@route(PREFIX + "/showcategory")
def ShowCategory(title, category, page_count):

	oc = ObjectContainer(title1 = title)
	thistitle = title
	if page_count == "1":
		page = HTML.ElementFromURL(BASE_URL + str(category))
	else:
		page = HTML.ElementFromURL(BASE_URL + str(category) + '/page/' + str(page_count) + '/')

	for each in page.xpath("//div[@class='short_content']"):
		url = each.xpath("./a/@href")[0]
		title = each.xpath("./a/div/text()")[0].strip()
		thumb = each.xpath("./a/img/@src")[0]

		oc.add(DirectoryObject(
			key = Callback(EpisodeDetail, title = title, url = url),
			title = title,
			thumb = BASE_URL + str(thumb)
			)
		)

	oc.add(NextPageObject(
		key = Callback(ShowCategory, title = thistitle, category = category, page_count = int(page_count) + 1),
		title = "More...",
		thumb = R(ICON_NEXT)
			)
		)

	return oc

######################################################################################
# Gets metadata and google docs link from episode page. Checks for trailer availablity.

@route(PREFIX + "/episodedetail")
def EpisodeDetail(title, url):

	oc = ObjectContainer(title1 = title)
	page = HTML.ElementFromURL(url)
	title = page.xpath("//h1[@id='news-title']/text()")[0].strip()
	description = page.xpath("//div[@itemprop='description']/text()")[0].strip()
	thumb = page.xpath("//div[@class='poster cf']/img/@src")[0]

	oc.add(VideoClipObject(
		title = title,
		summary = description,
		thumb = BASE_URL + str(thumb),
		url = url
		)
	)

	return oc

####################################################################################################
@route(PREFIX + "/search")
def Search(query):

	oc = ObjectContainer(title2='Search Results')
	page = HTML.ElementFromURL(BASE_URL + '/index.php?do=search&subaction=search&search_start=0&full_search=0&result_from=1&story=%s' % String.Quote(query, usePlus=True))

	for each in page.xpath("//div[@class='short_content']"):
		url = each.xpath("./a/@href")[0]
		title = each.xpath("./a/div/text()")[0].strip()
		thumb = each.xpath("./a/img/@src")[0]

		oc.add(DirectoryObject(
			key = Callback(EpisodeDetail, title = title, url = url),
			title = title,
			thumb = BASE_URL + str(thumb)
			)
		)
	return oc
