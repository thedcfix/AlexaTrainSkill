from urllib.request import urlopen
import re
import datetime

trains = {"06:05" : 612, "06:35" : 1614, "07:05" : 618, "07:35" : 1622, "08:05" : 624, "08:35" : 2626, "09:05" : 628, "10:05" : 632, "11:05" : 636, "12:05" : 640, "13:05" : 644, 
			"13:35" : 1646, "14:05" : 648, "14:35" : 1650, "15:05" : 652, "15:35" : 2654, "16:05" : 656, "16:35" : 2660, "17:05" : 662, "17:35" : 2666, "18:05" : 668, "18:35" : 1670}
			
non_existing = ["09:35", "10:35", "11:35", "12:35"]

hour = datetime.datetime.now().hour
minute = datetime.datetime.now().minute

# i treni passano alle :35 o alle :05. Così facendo scelgo il prossimo treno, con un po' di margine
if minute >= 50:
	minute = 5
	hour += 1
elif minute >= 20 and minute < 50:
	minute = 35
elif minute >=0 and minute <20: 
	minute = 5

time = str(hour).zfill(2) + ':' + str(minute).zfill(2)

if time not in non_existing and time in trains:
	train = trains[time]

	html = urlopen("http://mobile.my-link.it/mylink/mobile/scheda?numeroTreno=" + str(train) + "&codLocOrig=N00079&tipoRicerca=stazione&lang=IT").read().decode('utf-8')

	beginning = html.find('<div  class="evidenziato"><strong>') + len('<div  class="evidenziato"><strong>')
	end = html.find('<!--c:if test="$') - 23
	content = html[beginning:end]

	content = re.sub("\s\s+", " ", str(content))[1:]
	content = content.replace("e&#039;", 'è')
	content = str(content).strip()
	
	print(content)
else:
	print("Nessun treno previsto a breve nella fascia oraria 6.05 - 18.05. Per gli orari degli altri treni consultare il sito di Trenord.")