######################################################################################
#
#	MovieGo.co - v1.00
#
######################################################################################

from DumbTools import DumbKeyboard

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
ICON_OPTIONS = "icon-options.png"
ICON_ENABLED = "icon-enabled.png"
ICON_DISABLED = "icon-disabled.png"
BASE_URL = "http://moviego.cc"

# SSL Web Proxy
PROXY_URL = "https://ssl-proxy.my-addr.org/myaddrproxy.php/"
PROXY_PART1A = "/myaddrproxy.php/https/moviego.cc/"
PROXY_PART1B = "/myaddrproxy.php/http/moviego.cc/"
PROXY_PART1_REPLACE = "/"
PROXY_PART2A = "/myaddrproxy.php/https/"
PROXY_PART2B = "/myaddrproxy.php/http/"
PROXY_PART2_REPLACE = "//"

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
	
	oc.add(DirectoryObject(key = Callback(MenuCategory), title = 'Menu Category', summary='Menu with categories'))
			
	if UsingOption(key='ToggleDumbKeyboard'):
		DumbKeyboard(PREFIX, oc, Search,
				dktitle = 'Search',
				dkthumb = R(ICON_SEARCH)
		)
	else:
		oc.add(InputDirectoryObject(key = Callback(Search), title='Search', summary='Search MovieGo', prompt='Search for...'))
		
	oc.add(DirectoryObject(key = Callback(Options), title = 'Options', thumb = R(ICON_OPTIONS), summary='Options that can be accessed from a Client, includes Enabling DumbKeyboard & Redirector'))
	
	return oc
	
######################################################################################	
@route(PREFIX + "/menucategory")
def MenuCategory():

	oc = ObjectContainer(title='Menu')
	try:
		page = GetPageElements(BASE_URL)
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
	except:
		pass
			
	return oc

######################################################################################
# Creates page url from category and creates objects from that page

@route(PREFIX + "/showcategory")
def ShowCategory(title, category, page_count):

	oc = ObjectContainer(title1 = title)
	thistitle = title
	if page_count == "1":
		page = GetPageElements(BASE_URL + str(category))
	else:
		page = GetPageElements(BASE_URL + str(category) + '/page/' + str(page_count) + '/')

	for each in page.xpath("//div[@class='short_content']"):
		url = each.xpath("./a/@href")[0]
		title = each.xpath("./a/div/text()")[0].strip()
		thumb = each.xpath("./a/img/@src")[0]
		thumb = GetThumb(BASE_URL + str(thumb))
		
		oc.add(DirectoryObject(
			key = Callback(EpisodeDetail, title = title, url = url),
			title = title,
			thumb = thumb
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
	
	url = url.replace('http://moviego.cchttp://moviego.cc','http://moviego.cc')
	page = GetPageElements(url)
	
	title = page.xpath("//h1[@id='news-title']/text()")[0].strip()
	description = page.xpath("//div[@itemprop='description']/text()")[0].strip()
	thumb = page.xpath("//div[@class='poster cf']/img/@src")[0]
	thumb = GetThumb(BASE_URL + str(thumb))
	
	try:
		oc.add(VideoClipObject(
			title = title,
			summary = description,
			thumb = thumb,
			url = url
			)
		)
	except:
		pass
	#try:
	useRedirector = 'false'
	redStat = ''
	if UsingOption('ToggleRedirector'):
		useRedirector = 'true'
		redStat = ' (via Redirector)'
		
	gdUrl = GetGoogleLink(url=url)
	durl = "mvg2://" + E(JSON.StringFromObject({"apilink":('http://api.getlinkdrive.com/getlink?url='+gdUrl),"url":url, "title":title, "thumb": str(thumb), "useRedirector":useRedirector}))
	oc.add(VideoClipObject(
		title=title + ' (via API)' + redStat,
		thumb= str(thumb),
		url=durl
		))
	#except:
	#	pass
		
	return oc

####################################################################################################
@route(PREFIX + "/search")
def Search(query):

	oc = ObjectContainer(title2='Search Results')
	page = GetPageElements(BASE_URL + '/index.php?do=search&subaction=search&search_start=0&full_search=0&result_from=1&story=%s' % String.Quote(query, usePlus=True))

	for each in page.xpath("//div[@class='short_content']"):
		url = each.xpath("./a/@href")[0]
		title = each.xpath("./a/div/text()")[0].strip()
		thumb = each.xpath("./a/img/@src")[0]
		thumb = GetThumb(BASE_URL + str(thumb))

		oc.add(DirectoryObject(
			key = Callback(EpisodeDetail, title = title, url = url),
			title = title,
			thumb = str(thumb)
			)
		)
	return oc

	
####################################################################################################
# Gets a client specific identifier
@route(PREFIX + '/getsession')
def getSession():

	session = 'UnknownPlexClientSession'
	if 'X-Plex-Client-Identifier' in str(Request.Headers):
		session = str(Request.Headers['X-Plex-Client-Identifier'])
	elif 'X-Plex-Target-Client-Identifier' in str(Request.Headers):
		session = str(Request.Headers['X-Plex-Target-Client-Identifier'])
	elif 'User-Agent' in str(Request.Headers) and 'X-Plex-Token' in str(Request.Headers):
		session = 'UnknownClient-'+E(str(Request.Headers['User-Agent']) + str(Request.Headers['X-Plex-Token'][:3]))[:10]
	
	return E(session)

######################################################################################
@route(PREFIX + "/options")
def Options():
	oc = ObjectContainer(title2='Options')
	
	session = getSession()
	if Dict['ToggleDumbKeyboard'+session] == None or Dict['ToggleDumbKeyboard'+session] == 'disabled':
		oc.add(DirectoryObject(key=Callback(setDictVal,key='ToggleDumbKeyboard',session=session, val='enabled'), title = 'Enable DumbKeyboard', summary='Click here to Enable DumbKeyboard for this Device', thumb=R(ICON_ENABLED)))
	else:
		oc.add(DirectoryObject(key=Callback(setDictVal,key='ToggleDumbKeyboard',session=session, val='disabled'), title = 'Disable DumbKeyboard', summary='Click here to Disable DumbKeyboard for this Device', thumb=R(ICON_DISABLED)))
		
	if Dict['ToggleRedirector'+session] == None or Dict['ToggleRedirector'+session] == 'disabled':
		oc.add(DirectoryObject(key=Callback(setDictVal,key='ToggleRedirector',session=session, val='enabled'), title = 'Enable Redirector', summary='Click here to Enable Redirector method when using API link for this Device', thumb=R(ICON_ENABLED)))
	else:
		oc.add(DirectoryObject(key=Callback(setDictVal,key='ToggleRedirector',session=session, val='disabled'), title = 'Disable Redirector', summary='Click here to Disable Redirector method when using API link for this Device', thumb=R(ICON_DISABLED)))
	
	return oc
	
######################################################################################
@route(PREFIX + "/setDictVal")
def setDictVal(key, session, val):
	Dict[key+session] = val
	Dict.Save()
	return ObjectContainer(header=key, message=key.replace('Toggle','') + ' has been ' + Dict[key+session] + ' for this device.', title1=key)

@route(PREFIX + "/UsingOption")
def UsingOption(key):
	session = getSession()
	if Dict[key+session] == None or Dict[key+session] == 'disabled':
		return False
	else:
		return True
		
######################################################################################
@route(PREFIX + "/GetPageElements")
def GetPageElements(url, headers=None):

	page_data_elems = None
	try:
		page_data_string = GetPageAsString(url=url, headers=headers)
		#Log(page_data_string)
		page_data_elems = HTML.ElementFromString(page_data_string)
	except:
		pass
		
	return page_data_elems
	
######################################################################################
@route(PREFIX + "/GetPageAsString")
def GetPageAsString(url, headers=None, timeout=15):

	page_data_string = None
	try:
		if Prefs["use_web_proxy"]:
			Log("Using SSL Web-Proxy Option")
			Log("Url: " + url)
				
			if headers == None:
				page_data_string = HTTP.Request(PROXY_URL + url, timeout=timeout).content
			else:
				page_data_string = HTTP.Request(PROXY_URL + url, headers=headers, timeout=timeout).content
				
			page_data_string = page_data_string.replace(PROXY_PART1A, PROXY_PART1_REPLACE)
			page_data_string = page_data_string.replace(PROXY_PART1B, PROXY_PART1_REPLACE)
			page_data_string = page_data_string.replace(PROXY_PART2A, PROXY_PART2_REPLACE)
			page_data_string = page_data_string.replace(PROXY_PART2B, PROXY_PART2_REPLACE)
		else:
			if headers == None:
				page_data_string = HTTP.Request(url, timeout=timeout).content
			else:
				page_data_string = HTTP.Request(url, headers=headers, timeout=timeout).content
	except Exception as e:
		Log('ERROR GetPageAsString: %s URL: %s' % (e.args,url))
		pass
		
	return page_data_string

######################################################################################
@route(PREFIX + "/GetThumb")
def GetThumb(url):

	thumb = url

	if Prefs["use_web_proxy"]:
		thumb = PROXY_URL + url
		
	return thumb
	
######################################################################################
def find_between( s, first, last ):
    try:
        start = s.index( first ) + len( first )
        end = s.index( last, start )
        return s[start:end]
    except ValueError:
        return ""

######################################################################################
@route(PREFIX + "/GetGoogleLink")
def GetGoogleLink(url):

	html = GetPageElements(url)
	iframe = html.xpath('//iframe/@src')
	for url in iframe:
		if 'youtube' not in url:
			furl = url
			break
	
	html2 = GetPageAsString(furl)
	driveid = find_between(html2, '2Cexpire|','|driveid')
	
	googleLink = 'https://drive.google.com/file/d/%s/view' % driveid

	return googleLink
	
def test():
	ret = GetGoogleLink('http://213.183.51.36/play/zRUPCcZyvER5oAm/')
	
	print ret
	
#test()