import json
import os
import sys
from glob import *
from api.models import *
from api import db
import urllib2
from time import *
import datetime

party_name_overrides = {
	"DEMOCRATIC ALLIANCE/DEMOKRATIESE ALLIANSIE": "DEMOCRATIC ALLIANCE",
	"CONGRESS  OF THE PEOPLE": "CONGRESS OF THE PEOPLE",
	"VRYHEIDSFRONT \\ FREEDOM FRONT": "FREEDOM FRONT",
	"CAPE PARTY/ KAAPSE PARTY": "CAPE PARTY",
}

province_keys = {
	"LIMPOPO": "LIM",
	"MPUMALANGA": "MP",
	"NORTH WEST": "NW",
	"GAUTENG": "GT",
	"KWAZULU-NATAL": "KZN",
	"EASTERN CAPE": "EC",
	"FREE STATE": "FS",
	"NORTHERN CAPE": "NC",
	"WESTERN CAPE": "WC",
}

province_order = { "EC": 1, "FS": 2, "GT": 3, "KZN": 4, "MP": 5, "NC": 6, "LIM": 7, "NW": 8, "WC": 9 }

municipality_codes = {
	"EC": json.loads('[{"ProvinceID":1,"MunicipalityID":1117,"Municipality":"BUF - Buffalo City Metropolitan Municipality [East London]"},{"ProvinceID":1,"MunicipalityID":1102,"Municipality":"EC101 - Camdeboo [Graaff-Reinet]"},{"ProvinceID":1,"MunicipalityID":1103,"Municipality":"EC102 - Blue Crane Route [Somerset East]"},{"ProvinceID":1,"MunicipalityID":1104,"Municipality":"EC103 - Ikwezi [Jansenville]"},{"ProvinceID":1,"MunicipalityID":1105,"Municipality":"EC104 - Makana [Grahamstown]"},{"ProvinceID":1,"MunicipalityID":1106,"Municipality":"EC105 - Ndlambe [Port Alfred]"},{"ProvinceID":1,"MunicipalityID":1107,"Municipality":"EC106 - Sundays River Valley [Kirkwood]"},{"ProvinceID":1,"MunicipalityID":1108,"Municipality":"EC107 - Baviaans [Willowmore]"},{"ProvinceID":1,"MunicipalityID":1109,"Municipality":"EC108 - Kouga [Humansdorp]"},{"ProvinceID":1,"MunicipalityID":1110,"Municipality":"EC109 - Kou-Kamma [Kareedouw]"},{"ProvinceID":1,"MunicipalityID":1113,"Municipality":"EC121 - Mbhashe [Idutywa]"},{"ProvinceID":1,"MunicipalityID":1114,"Municipality":"EC122 - Mnquma [Butterworth]"},{"ProvinceID":1,"MunicipalityID":1115,"Municipality":"EC123 - Great Kei [Komga]"},{"ProvinceID":1,"MunicipalityID":1116,"Municipality":"EC124 - Amahlathi [Stutterheim]"},{"ProvinceID":1,"MunicipalityID":1118,"Municipality":"EC126 - Ngqushwa [Peddie]"},{"ProvinceID":1,"MunicipalityID":1119,"Municipality":"EC127 - Nkonkobe [Alice]"},{"ProvinceID":1,"MunicipalityID":1120,"Municipality":"EC128 - Nxuba [Adelaide]"},{"ProvinceID":1,"MunicipalityID":1122,"Municipality":"EC131 - Inxuba Yethemba [Cradock]"},{"ProvinceID":1,"MunicipalityID":1123,"Municipality":"EC132 - Tsolwana [Tarkastad]"},{"ProvinceID":1,"MunicipalityID":1124,"Municipality":"EC133 - Inkwanca [Molteno]"},{"ProvinceID":1,"MunicipalityID":1125,"Municipality":"EC134 - Lukhanji [Queenstown]"},{"ProvinceID":1,"MunicipalityID":1126,"Municipality":"EC135 - Intsika Yethu [Cofimvaba]"},{"ProvinceID":1,"MunicipalityID":1127,"Municipality":"EC136 - Emalahleni [Lady Frere]"},{"ProvinceID":1,"MunicipalityID":1128,"Municipality":"EC137 - Engcobo [Engcobo]"},{"ProvinceID":1,"MunicipalityID":1129,"Municipality":"EC138 - Sakhisizwe [Elliot]"},{"ProvinceID":1,"MunicipalityID":1131,"Municipality":"EC141 - Elundini [Mount Fletcher]"},{"ProvinceID":1,"MunicipalityID":1132,"Municipality":"EC142 - Senqu [Lady Grey]"},{"ProvinceID":1,"MunicipalityID":1133,"Municipality":"EC143 - Maletswai [Aliwal North]"},{"ProvinceID":1,"MunicipalityID":1134,"Municipality":"EC144 - Gariep [Burgersdorp]"},{"ProvinceID":1,"MunicipalityID":1138,"Municipality":"EC153 - Ngquza Hill [Flagstaff]"},{"ProvinceID":1,"MunicipalityID":1139,"Municipality":"EC154 - Port St Johns [Port St Johns]"},{"ProvinceID":1,"MunicipalityID":1140,"Municipality":"EC155 - Nyandeni [Libode]"},{"ProvinceID":1,"MunicipalityID":1141,"Municipality":"EC156 - Mhlontlo [Qumbu]"},{"ProvinceID":1,"MunicipalityID":1142,"Municipality":"EC157 - King Sabata Dalindyebo [Umtata]"},{"ProvinceID":1,"MunicipalityID":4034,"Municipality":"EC441 - Matatiele [Matatiele]"},{"ProvinceID":1,"MunicipalityID":1031,"Municipality":"EC442 - Umzimvubu [Mount Ayliff]"},{"ProvinceID":1,"MunicipalityID":1136,"Municipality":"EC443 - Mbizana [Bizana]"},{"ProvinceID":1,"MunicipalityID":1137,"Municipality":"EC444 - Ntabankulu [Ntabankulu]"},{"ProvinceID":1,"MunicipalityID":1001,"Municipality":"NMA - Nelson Mandela Bay [Port Elizabeth]"}]'),
	"FS": json.loads('[{"ProvinceID":2,"MunicipalityID":2202,"Municipality":"FS161 - Letsemeng [Koffiefontein]"},{"ProvinceID":2,"MunicipalityID":2203,"Municipality":"FS162 - Kopanong [Trompsburg]"},{"ProvinceID":2,"MunicipalityID":2204,"Municipality":"FS163 - Mohokare [Zastron]"},{"ProvinceID":2,"MunicipalityID":2206,"Municipality":"FS164 - Naledi [Dewetsdorp]"},{"ProvinceID":2,"MunicipalityID":2210,"Municipality":"FS181 - Masilonyana [Theunissen]"},{"ProvinceID":2,"MunicipalityID":2211,"Municipality":"FS182 - Tokologo [Dealesville]"},{"ProvinceID":2,"MunicipalityID":2212,"Municipality":"FS183 - Tswelopele [Hoopstad]"},{"ProvinceID":2,"MunicipalityID":2213,"Municipality":"FS184 - Matjhabeng [Welkom]"},{"ProvinceID":2,"MunicipalityID":2214,"Municipality":"FS185 - Nala [Bothaville]"},{"ProvinceID":2,"MunicipalityID":2216,"Municipality":"FS191 - Setsoto [Senekal]"},{"ProvinceID":2,"MunicipalityID":2217,"Municipality":"FS192 - Dihlabeng [Bethlehem]"},{"ProvinceID":2,"MunicipalityID":2218,"Municipality":"FS193 - Nketoana [Reitz]"},{"ProvinceID":2,"MunicipalityID":2219,"Municipality":"FS194 - Maluti a Phofung [Qwa-Qwa]"},{"ProvinceID":2,"MunicipalityID":2220,"Municipality":"FS195 - Phumelela [Vrede]"},{"ProvinceID":2,"MunicipalityID":2208,"Municipality":"FS196 - Mantsopa [Ladybrand]"},{"ProvinceID":2,"MunicipalityID":2222,"Municipality":"FS201 - Moqhaka [Kroonstad]"},{"ProvinceID":2,"MunicipalityID":2223,"Municipality":"FS203 - Ngwathe [Parys]"},{"ProvinceID":2,"MunicipalityID":2224,"Municipality":"FS204 - Metsimaholo [Sasolburg]"},{"ProvinceID":2,"MunicipalityID":2225,"Municipality":"FS205 - Mafube [Frankfort]"},{"ProvinceID":2,"MunicipalityID":2207,"Municipality":"MAN - Mangaung Metropolitan Municipality [Bloemfontein]"}]'),
	"GT": json.loads('[{"ProvinceID":3,"MunicipalityID":3002,"Municipality":"EKU - Ekurhuleni [East Rand]"},{"ProvinceID":3,"MunicipalityID":3302,"Municipality":"GT421 - Emfuleni [Vereeniging]"},{"ProvinceID":3,"MunicipalityID":3303,"Municipality":"GT422 - Midvaal [Meyerton]"},{"ProvinceID":3,"MunicipalityID":3304,"Municipality":"GT423 - Lesedi [Heidelberg]"},{"ProvinceID":3,"MunicipalityID":3040,"Municipality":"GT481 - Mogale City [Krugersdorp]"},{"ProvinceID":3,"MunicipalityID":3041,"Municipality":"GT482 - Randfontein [Randfontein]"},{"ProvinceID":3,"MunicipalityID":3042,"Municipality":"GT483 - Westonaria [Westonaria]"},{"ProvinceID":3,"MunicipalityID":3039,"Municipality":"GT484 - Merafong City [Carletonville]"},{"ProvinceID":3,"MunicipalityID":3003,"Municipality":"JHB - City of Johannesburg [Johannesburg]"},{"ProvinceID":3,"MunicipalityID":3004,"Municipality":"TSH - Tshwane Metro [Pretoria]"}]'),
	"KZN": json.loads('[{"ProvinceID":4,"MunicipalityID":4005,"Municipality":"ETH - eThekwini [Durban Metro]"},{"ProvinceID":4,"MunicipalityID":4402,"Municipality":"KZN211 - Vulamehlo [Dududu]"},{"ProvinceID":4,"MunicipalityID":4403,"Municipality":"KZN212 - Umdoni [Scottburgh]"},{"ProvinceID":4,"MunicipalityID":4404,"Municipality":"KZN213 - Umzumbe [Umzumbe]"},{"ProvinceID":4,"MunicipalityID":4405,"Municipality":"KZN214 - UMuziwabantu [Harding]"},{"ProvinceID":4,"MunicipalityID":4406,"Municipality":"KZN215 - Ezinqoleni [Izinqolweni]"},{"ProvinceID":4,"MunicipalityID":4407,"Municipality":"KZN216 - Hibiscus Coast [Port Shepstone]"},{"ProvinceID":4,"MunicipalityID":4409,"Municipality":"KZN221 - uMshwathi [Wartburg]"},{"ProvinceID":4,"MunicipalityID":4410,"Municipality":"KZN222 - uMngeni [Howick]"},{"ProvinceID":4,"MunicipalityID":4411,"Municipality":"KZN223 - Mooi Mpofana [Mooirivier]"},{"ProvinceID":4,"MunicipalityID":4412,"Municipality":"KZN224 - Impendle [Impendle]"},{"ProvinceID":4,"MunicipalityID":4413,"Municipality":"KZN225 - Msunduzi [Pietermaritzburg]"},{"ProvinceID":4,"MunicipalityID":4414,"Municipality":"KZN226 - Mkhambathini [Camperdown]"},{"ProvinceID":4,"MunicipalityID":4415,"Municipality":"KZN227 - Richmond [Richmond]"},{"ProvinceID":4,"MunicipalityID":4418,"Municipality":"KZN232 - Emnambithi/Ladysmith [Ladysmith]"},{"ProvinceID":4,"MunicipalityID":4419,"Municipality":"KZN233 - Indaka [Waaihoek]"},{"ProvinceID":4,"MunicipalityID":4420,"Municipality":"KZN234 - Umtshezi [Estcourt]"},{"ProvinceID":4,"MunicipalityID":4421,"Municipality":"KZN235 - Okhahlamba [Bergville]"},{"ProvinceID":4,"MunicipalityID":4422,"Municipality":"KZN236 - Imbabazane [Loskop]"},{"ProvinceID":4,"MunicipalityID":4426,"Municipality":"KZN241 - Endumeni [Dundee]"},{"ProvinceID":4,"MunicipalityID":4427,"Municipality":"KZN242 - Nqutu [Nqutu]"},{"ProvinceID":4,"MunicipalityID":4429,"Municipality":"KZN244 - Msinga [Pomeroy]"},{"ProvinceID":4,"MunicipalityID":4430,"Municipality":"KZN245 - Umvoti [Greytown]"},{"ProvinceID":4,"MunicipalityID":4432,"Municipality":"KZN252 - Newcastle [Newcastle]"},{"ProvinceID":4,"MunicipalityID":4433,"Municipality":"KZN253 - eMadlangeni [Utrecht]"},{"ProvinceID":4,"MunicipalityID":4434,"Municipality":"KZN254 - Dannhauser [Durnacol]"},{"ProvinceID":4,"MunicipalityID":4436,"Municipality":"KZN261 - eDumbe [Paulpietersburg]"},{"ProvinceID":4,"MunicipalityID":4437,"Municipality":"KZN262 - UPhongolo [Pongola]"},{"ProvinceID":4,"MunicipalityID":4438,"Municipality":"KZN263 - Abaqulusi [Vryheid]"},{"ProvinceID":4,"MunicipalityID":4439,"Municipality":"KZN265 - Nongoma [Nongoma]"},{"ProvinceID":4,"MunicipalityID":4440,"Municipality":"KZN266 - Ulundi [Ulundi]"},{"ProvinceID":4,"MunicipalityID":4442,"Municipality":"KZN271 - Umhlabuyalingana [Emangusi]"},{"ProvinceID":4,"MunicipalityID":4443,"Municipality":"KZN272 - Jozini [Mkuze]"},{"ProvinceID":4,"MunicipalityID":4444,"Municipality":"KZN273 - The Big 5 False Bay [Hluhluwe]"},{"ProvinceID":4,"MunicipalityID":4445,"Municipality":"KZN274 - Hlabisa [Somkele]"},{"ProvinceID":4,"MunicipalityID":4446,"Municipality":"KZN275 - Mtubatuba [Mtubatuba]"},{"ProvinceID":4,"MunicipalityID":4449,"Municipality":"KZN281 - Mfolozi [KwaMbonambi]"},{"ProvinceID":4,"MunicipalityID":4450,"Municipality":"KZN282 - uMhlathuze [Richards Bay]"},{"ProvinceID":4,"MunicipalityID":4451,"Municipality":"KZN283 - Ntambana [Ntambana]"},{"ProvinceID":4,"MunicipalityID":4452,"Municipality":"KZN284 - uMlalazi [Eshowe]"},{"ProvinceID":4,"MunicipalityID":4453,"Municipality":"KZN285 - Mthonjaneni [Melmoth]"},{"ProvinceID":4,"MunicipalityID":4454,"Municipality":"KZN286 - Nkandla [Nkandla]"},{"ProvinceID":4,"MunicipalityID":4456,"Municipality":"KZN291 - Mandeni [Mandeni]"},{"ProvinceID":4,"MunicipalityID":4457,"Municipality":"KZN292 - KwaDukuza [Stanger]"},{"ProvinceID":4,"MunicipalityID":4458,"Municipality":"KZN293 - Ndwedwe [Ndwedwe]"},{"ProvinceID":4,"MunicipalityID":4459,"Municipality":"KZN294 - Maphumulo [Maphumulo]"},{"ProvinceID":4,"MunicipalityID":4032,"Municipality":"KZN431 - Ingwe [Creighton]"},{"ProvinceID":4,"MunicipalityID":4033,"Municipality":"KZN432 - Kwa Sani [Underberg]"},{"ProvinceID":4,"MunicipalityID":4035,"Municipality":"KZN433 - Greater Kokstad [Kokstad]"},{"ProvinceID":4,"MunicipalityID":4036,"Municipality":"KZN434 - Ubuhlebezwe [Ixopo]"},{"ProvinceID":4,"MunicipalityID":1030,"Municipality":"KZN435 - Umzimkhulu [Umzimkulu]"}]'),
	"MP": json.loads('[{"ProvinceID":5,"MunicipalityID":5502,"Municipality":"MP301 - Albert Luthuli [Elukwatini/Carolina]"},{"ProvinceID":5,"MunicipalityID":5503,"Municipality":"MP302 - Msukaligwa [Ermelo]"},{"ProvinceID":5,"MunicipalityID":5504,"Municipality":"MP303 - Mkhondo [Piet Retief]"},{"ProvinceID":5,"MunicipalityID":5505,"Municipality":"MP304 - Pixley Ka Seme [Volksrust]"},{"ProvinceID":5,"MunicipalityID":5506,"Municipality":"MP305 - Lekwa [Standerton]"},{"ProvinceID":5,"MunicipalityID":5507,"Municipality":"MP306 - Dipaleseng [Balfour]"},{"ProvinceID":5,"MunicipalityID":5508,"Municipality":"MP307 - Govan Mbeki [Highveld Ridge]"},{"ProvinceID":5,"MunicipalityID":5510,"Municipality":"MP311 - Delmas [Delmas]"},{"ProvinceID":5,"MunicipalityID":5511,"Municipality":"MP312 - Emalahleni [Witbank]"},{"ProvinceID":5,"MunicipalityID":5512,"Municipality":"MP313 - Steve Tshwete [Middelburg]"},{"ProvinceID":5,"MunicipalityID":5513,"Municipality":"MP314 - Emakhazeni [Belfast]"},{"ProvinceID":5,"MunicipalityID":5514,"Municipality":"MP315 - Thembisile [KwaMhlanga]"},{"ProvinceID":5,"MunicipalityID":5515,"Municipality":"MP316 - Dr JS Moroka [Mdutjana]"},{"ProvinceID":5,"MunicipalityID":5517,"Municipality":"MP321 - Thaba Chweu [Sabie]"},{"ProvinceID":5,"MunicipalityID":5518,"Municipality":"MP322 - Mbombela [Nelspruit]"},{"ProvinceID":5,"MunicipalityID":5519,"Municipality":"MP323 - Umjindi [Barberton]"},{"ProvinceID":5,"MunicipalityID":5520,"Municipality":"MP324 - Nkomazi [Nkomazi]"},{"ProvinceID":5,"MunicipalityID":7027,"Municipality":"MP325 - Bushbuckridge [Bushbuckridge]"}]'), 
	"NC": json.loads('[{"ProvinceID":6,"MunicipalityID":6602,"Municipality":"NC061 - RICHTERSVELD [Port Nolloth]"},{"ProvinceID":6,"MunicipalityID":6603,"Municipality":"NC062 - NAMA KHOI [Springbok]"},{"ProvinceID":6,"MunicipalityID":6604,"Municipality":"NC064 - KAMIESBERG [Garies]"},{"ProvinceID":6,"MunicipalityID":6605,"Municipality":"NC065 - HANTAM [Calvinia]"},{"ProvinceID":6,"MunicipalityID":6606,"Municipality":"NC066 - KAROO HOOGLAND [Fraserburg]"},{"ProvinceID":6,"MunicipalityID":6607,"Municipality":"NC067 - KHI-MA [Pofadder]"},{"ProvinceID":6,"MunicipalityID":6610,"Municipality":"NC071 - UBUNTU [Victoria West]"},{"ProvinceID":6,"MunicipalityID":6611,"Municipality":"NC072 - UMSOBOMVU [Colesberg]"},{"ProvinceID":6,"MunicipalityID":6612,"Municipality":"NC073 - EMTHANJENI [De Aar]"},{"ProvinceID":6,"MunicipalityID":6613,"Municipality":"NC074 - KAREEBERG [Carnarvon]"},{"ProvinceID":6,"MunicipalityID":6614,"Municipality":"NC075 - RENOSTERBERG [Phillipstown]"},{"ProvinceID":6,"MunicipalityID":6615,"Municipality":"NC076 - THEMBELIHLE [Hopetown]"},{"ProvinceID":6,"MunicipalityID":6616,"Municipality":"NC077 - SIYATHEMBA [Prieska]"},{"ProvinceID":6,"MunicipalityID":6617,"Municipality":"NC078 - SIYANCUMA [Griekwastad]"},{"ProvinceID":6,"MunicipalityID":6620,"Municipality":"NC081 - MIER [Mier]"},{"ProvinceID":6,"MunicipalityID":6621,"Municipality":"NC082 - KAI !GARIB [Keimoes]"},{"ProvinceID":6,"MunicipalityID":6622,"Municipality":"NC083 - KHARA HAIS [Upington]"},{"ProvinceID":6,"MunicipalityID":6623,"Municipality":"NC084 - !KHEIS [Groblershoop]"},{"ProvinceID":6,"MunicipalityID":6624,"Municipality":"NC085 - TSANTSABANE [Postmasburg]"},{"ProvinceID":6,"MunicipalityID":6625,"Municipality":"NC086 - KGATELOPELE [Danielskuil]"},{"ProvinceID":6,"MunicipalityID":6046,"Municipality":"NC091 - Sol Plaatje [Kimberley]"},{"ProvinceID":6,"MunicipalityID":6047,"Municipality":"NC092 - Dikgatlong [Barkley West]"},{"ProvinceID":6,"MunicipalityID":6048,"Municipality":"NC093 - Magareng [Warrenton]"},{"ProvinceID":6,"MunicipalityID":6045,"Municipality":"NC094 - Phokwane [Hartswater]"},{"ProvinceID":6,"MunicipalityID":6015,"Municipality":"NC451 - Joe Morolong [Kgalagadi]"},{"ProvinceID":6,"MunicipalityID":6012,"Municipality":"NC452 - GA-SEGONYANA [Kuruman]"},{"ProvinceID":6,"MunicipalityID":6013,"Municipality":"NC453 - GAMAGARA [Kathu]"}]'), 
	"LIM": json.loads('[{"ProvinceID":7,"MunicipalityID":7702,"Municipality":"LIM331 - Greater Giyani [Giyani]"},{"ProvinceID":7,"MunicipalityID":7703,"Municipality":"LIM332 - Greater Letaba [Duiwelskloof]"},{"ProvinceID":7,"MunicipalityID":7704,"Municipality":"LIM333 - Greater Tzaneen [Tzaneen]"},{"ProvinceID":7,"MunicipalityID":7705,"Municipality":"LIM334 - Ba-Phalaborwa [Phalaborwa]"},{"ProvinceID":7,"MunicipalityID":7028,"Municipality":"LIM335 - Maruleng [Hoedspruit]"},{"ProvinceID":7,"MunicipalityID":7707,"Municipality":"LIM341 - Musina [Messina]"},{"ProvinceID":7,"MunicipalityID":7708,"Municipality":"LIM342 - Mutale [Mutale-Masisi]"},{"ProvinceID":7,"MunicipalityID":7709,"Municipality":"LIM343 - Thulamela [Thohoyandou]"},{"ProvinceID":7,"MunicipalityID":7710,"Municipality":"LIM344 - Makhado [Louis Trichardt]"},{"ProvinceID":7,"MunicipalityID":7712,"Municipality":"LIM351 - Blouberg [Bochum/My Darling]"},{"ProvinceID":7,"MunicipalityID":7713,"Municipality":"LIM352 - Aganang [Moletji/Matlala]"},{"ProvinceID":7,"MunicipalityID":7714,"Municipality":"LIM353 - Molemole [Dendron/Dikgale]"},{"ProvinceID":7,"MunicipalityID":7715,"Municipality":"LIM354 - Polokwane [Pietersburg]"},{"ProvinceID":7,"MunicipalityID":7716,"Municipality":"LIM355 - Lepele-Nkumpi [Lebowakgomo]"},{"ProvinceID":7,"MunicipalityID":7718,"Municipality":"LIM361 - Thabazimbi [Thabazimbi]"},{"ProvinceID":7,"MunicipalityID":7719,"Municipality":"LIM362 - Lephalale [Ellisras]"},{"ProvinceID":7,"MunicipalityID":7720,"Municipality":"LIM364 - Mookgopong [Naboomspruit]"},{"ProvinceID":7,"MunicipalityID":7721,"Municipality":"LIM365 - Modimolle [Nylstroom]"},{"ProvinceID":7,"MunicipalityID":7722,"Municipality":"LIM366 - Bela-Bela [Warmbad]"},{"ProvinceID":7,"MunicipalityID":7723,"Municipality":"LIM367 - Mogalakwena [Potgietersrus]"},{"ProvinceID":7,"MunicipalityID":5020,"Municipality":"LIM471 - Ephraim Mogale [Marble Hall]"},{"ProvinceID":7,"MunicipalityID":5021,"Municipality":"LIM472 - Elias Motsoaledi [Groblersdal]"},{"ProvinceID":7,"MunicipalityID":7023,"Municipality":"LIM473 - Makhuduthamaga [Ngwaritsi]"},{"ProvinceID":7,"MunicipalityID":7024,"Municipality":"LIM474 - Fetakgomo [Fetakgomo ]"},{"ProvinceID":7,"MunicipalityID":5022,"Municipality":"LIM475 - Greater Tubatse [Burgersfort/Ohrigstad/Eastern Tubatse]"}]'),
	"NW": json.loads('[{"ProvinceID":8,"MunicipalityID":8802,"Municipality":"NW371 - Moretele [Makapanstad]"},{"ProvinceID":8,"MunicipalityID":8803,"Municipality":"NW372 - Madibeng [Brits]"},{"ProvinceID":8,"MunicipalityID":8804,"Municipality":"NW373 - Rustenburg [Rustenburg]"},{"ProvinceID":8,"MunicipalityID":8805,"Municipality":"NW374 - Kgetlengrivier [Koster]"},{"ProvinceID":8,"MunicipalityID":8806,"Municipality":"NW375 - Moses Kotane [Mogwase]"},{"ProvinceID":8,"MunicipalityID":8808,"Municipality":"NW381 - Ratlou [Setlagole]"},{"ProvinceID":8,"MunicipalityID":8809,"Municipality":"NW382 - Tswaing [Delareyville]"},{"ProvinceID":8,"MunicipalityID":8810,"Municipality":"NW383 - Mafikeng [Mahikeng]"},{"ProvinceID":8,"MunicipalityID":8811,"Municipality":"NW384 - Ditsobotla [Lichtenburg]"},{"ProvinceID":8,"MunicipalityID":8812,"Municipality":"NW385 - Ramotshere Moiloa [Zeerust]"},{"ProvinceID":8,"MunicipalityID":8815,"Municipality":"NW392 - Naledi [Vryburg]"},{"ProvinceID":8,"MunicipalityID":8816,"Municipality":"NW393 - Mamusa [Schweizer-Reneke]"},{"ProvinceID":8,"MunicipalityID":8817,"Municipality":"NW394 - Greater Taung [Reivilo]"},{"ProvinceID":8,"MunicipalityID":8819,"Municipality":"NW396 - Lekwa-Teemane [Christiana]"},{"ProvinceID":8,"MunicipalityID":8825,"Municipality":"NW397 - NW397 Local Municipality [Ganyesa/Pomfret]"},{"ProvinceID":8,"MunicipalityID":8821,"Municipality":"NW401 - Ventersdorp [Ventersdorp]"},{"ProvinceID":8,"MunicipalityID":8822,"Municipality":"NW402 - Tlokwe [Potchefstroom]"},{"ProvinceID":8,"MunicipalityID":8823,"Municipality":"NW403 - Matlosana [Klerksdorp]"},{"ProvinceID":8,"MunicipalityID":8824,"Municipality":"NW404 - Maquassi Hills [Wolmaransstad]"}]'), 
	"WC": json.loads('[{"ProvinceID":9,"MunicipalityID":9006,"Municipality":"CPT - City of Cape Town [Cape Town]"},{"ProvinceID":9,"MunicipalityID":9902,"Municipality":"WC011 - Matzikama [Vredendal]"},{"ProvinceID":9,"MunicipalityID":9903,"Municipality":"WC012 - Cederberg [Citrusdal]"},{"ProvinceID":9,"MunicipalityID":9904,"Municipality":"WC013 - Bergrivier [Velddrif]"},{"ProvinceID":9,"MunicipalityID":9905,"Municipality":"WC014 - Saldanha Bay [West Coast Peninsula]"},{"ProvinceID":9,"MunicipalityID":9906,"Municipality":"WC015 - Swartland [Malmesbury]"},{"ProvinceID":9,"MunicipalityID":9909,"Municipality":"WC022 - Witzenberg [Ceres]"},{"ProvinceID":9,"MunicipalityID":9910,"Municipality":"WC023 - Drakenstein [Paarl]"},{"ProvinceID":9,"MunicipalityID":9911,"Municipality":"WC024 - Stellenbosch [Stellenbosch]"},{"ProvinceID":9,"MunicipalityID":9912,"Municipality":"WC025 - Breede Valley [Worcester]"},{"ProvinceID":9,"MunicipalityID":9913,"Municipality":"WC026 - Langeberg [Robertson]"},{"ProvinceID":9,"MunicipalityID":9916,"Municipality":"WC031 - Theewaterskloof [Caledon]"},{"ProvinceID":9,"MunicipalityID":9917,"Municipality":"WC032 - Overstrand [Greater Hermanus]"},{"ProvinceID":9,"MunicipalityID":9918,"Municipality":"WC033 - Cape Agulhas [Bredasdorp]"},{"ProvinceID":9,"MunicipalityID":9919,"Municipality":"WC034 - Swellendam [Barrydale/Swellendam ]"},{"ProvinceID":9,"MunicipalityID":9922,"Municipality":"WC041 - Kannaland [Ladismith]"},{"ProvinceID":9,"MunicipalityID":9923,"Municipality":"WC042 - Hessequa [Heidelberg/Riversdale]"},{"ProvinceID":9,"MunicipalityID":9924,"Municipality":"WC043 - Mossel Bay [Mossel Bay]"},{"ProvinceID":9,"MunicipalityID":9925,"Municipality":"WC044 - George [George]"},{"ProvinceID":9,"MunicipalityID":9926,"Municipality":"WC045 - Oudtshoorn [Oudtshoorn]"},{"ProvinceID":9,"MunicipalityID":9927,"Municipality":"WC047 - Bitou [Greater Plettenberg Bay]"},{"ProvinceID":9,"MunicipalityID":9928,"Municipality":"WC048 - Knysna [Knysna]"},{"ProvinceID":9,"MunicipalityID":9931,"Municipality":"WC051 - Laingsburg [Laingsburg]"},{"ProvinceID":9,"MunicipalityID":9932,"Municipality":"WC052 - Prince Albert [Prins Albert]"},{"ProvinceID":9,"MunicipalityID":9933,"Municipality":"WC053 - Beaufort West [Beaufort West]"}]')
}

def find_municipal_code(munic_id):
	for prov in municipality_codes:
		# print prov
		for munic in municipality_codes[prov]:
			# print munic["Municipality"], munic_id
			if (str(munic["Municipality"]).find(str(munic_id)) == 0):
				return str(munic["MunicipalityID"])
	return False

def download_latest_results(id, vdlist = False):
	jdata = urllib2.urlopen("http://localhost:8082/latest/" + str(id)).read()
	data = json.loads(jdata)
	max_time = highest_time = 0
	fname = "/tmp/iec-api-national-" + str(id)
	if (os.path.exists(fname)):
		f = open(fname, "r")
		max_time = f.readline()
		if (max_time == ""):
			max_time = 0
		else:
			max_time = int(max_time)
		f.close()
	for item in data:
		try:
			dt = strptime(item["ReleasedDate"], '%Y-%m-%dT%H:%M:%S.%f')
		except:
			dt = strptime(item["ReleasedDate"], '%Y-%m-%dT%H:%M:%S')
	 	t = datetime.datetime(*(dt[0:6]))
	 	ut = int(t.strftime("%s"))
	 	if (ut > highest_time):
	 		highest_time = ut
	 	if (ut > max_time):
	 		download_vd(id, item["VDNumber"], dt.tm_year)
	calculate_ward(set(ward_queue), dt.tm_year, "national")
	calculate_municipality(set(municipality_queue), dt.tm_year, id)
	calculate_province(set(province_queue), dt.tm_year, id)
	calculate_national(dt.tm_year, id)
	f = open(fname, "w")
	# print "Max time", max_time
	f.write(str(highest_time))
	f.close()

ward_queue = []
municipality_queue = []
province_queue = []

def download_provincial_results(id, vdlist = False):
	jdata = urllib2.urlopen("http://localhost:8082/latest/" + str(id)).read()
	data = json.loads(jdata)
	max_time = highest_time = 0
	fname = "/tmp/iec-api-provincial-" + str(id)
	if (os.path.exists(fname)):
		f = open(fname, "r")
		max_time = f.readline()
		if (max_time == ""):
			max_time = 0
		else:
			max_time = int(max_time)
		f.close()
	for item in data:
		try:
			dt = strptime(item["ReleasedDate"], '%Y-%m-%dT%H:%M:%S.%f')
		except:
			dt = strptime(item["ReleasedDate"], '%Y-%m-%dT%H:%M:%S')
		t = datetime.datetime(*(dt[0:6]))
	 	ut = int(t.strftime("%s"))
	 	if (ut > highest_time):
	 		highest_time = ut
	 	if (ut > max_time):
			download_vd(id, item["VDNumber"], dt.tm_year)
	calculate_ward(set(ward_queue), dt.tm_year, "provincial")
	calculate_municipality(set(municipality_queue), dt.tm_year, id)
	calculate_province(set(province_queue), dt.tm_year, id)
	f = open(fname, "w")
	f.write(str(highest_time))
	f.close()
	# calculate_national(dt.tm_year, id)

def download_vd(id, voting_district_id, year):
	query = db.session.query(VotingDistrict).filter(VotingDistrict.year == int(year), VotingDistrict.voting_district_id == int(voting_district_id))
	check_result = query.first()
	if (id == 291):
		check_field = json.loads(check_result.results_national)
	else:
		check_field = json.loads(check_result.results_provincial)
	province = db.session.query(Province).filter(Province.pk == check_result.province_pk).first()
	province_id = province_order[province.province_id]
	municipality = db.session.query(Municipality).filter(Municipality.pk == check_result.municipality_pk).first()
	municipality_id = find_municipal_code(municipality.municipality_id)
	uri = "http://localhost:8082/result/" + str(id) + "/province/" + str(province_id) + "/municipality/" + str(municipality_id) + "/voting_district/"+ str(voting_district_id)
	print uri
	jvddata = urllib2.urlopen(uri).read()
	vddata = json.loads(jvddata)
	if int(id) == int(vddata["ElectoralEventID"]):
		print "Looks valid for " + str(vddata["ElectoralEvent"])
		data_dict = {'meta': {}, 'vote_count': {}}
		data_dict["meta"]["num_registered"] = vddata['RegisteredVoters']
		data_dict["meta"]["turnout_percentage"] = vddata['PercVoterTurnout']
		data_dict["meta"]["vote_count"] = vddata['TotalValidVotes']
		data_dict["meta"]["spoilt_votes"] = vddata['SpoiltVotes']
		data_dict["meta"]["total_votes"] = vddata['TotalVotesCast']
		data_dict["meta"]["section_24a_votes"] = vddata['Section24AVotes']
		data_dict["meta"]["special_votes"] = vddata['SpecialVotes']
		if (vddata['bResultsComplete']):
			data_dict["meta"]["vote_complete"] = 100
		else:
			data_dict["meta"]["vote_complete"] = round(float(vddata['VDWithResultsCaptured']) / float(vddata['VDCount']) * 100, 2)
		for party_data in vddata["PartyBallotResults"]:
			data_dict["vote_count"][party_data["Name"]] = party_data["ValidVotes"]
		if (str(vddata["ElectoralEvent"]).lower().find("national") > -1):
			query.update({ 'results_national': json.dumps(data_dict) })
		else:
			query.update({ 'results_provincial': json.dumps(data_dict) })
		db.session.commit()
		ward_queue.append(check_result.ward_pk)
		municipality_queue.append(check_result.municipality_pk)
		province_queue.append(check_result.province_pk)
	
def calculate_ward(queue, year, type):
	for ward_pk in queue:
		query = db.session.query(VotingDistrict).filter(VotingDistrict.year == int(year), VotingDistrict.ward_pk == int(ward_pk))
		vds = query.all()
		data_dict = {'meta': {}, 'vote_count': {}}
		data_dict["meta"]["num_registered"] = 0
		data_dict["meta"]["turnout_percentage"] = 0
		data_dict["meta"]["vote_count"] = 0
		data_dict["meta"]["spoilt_votes"] = 0
		data_dict["meta"]["total_votes"] = 0
		data_dict["meta"]["section_24a_votes"] = 0
		data_dict["meta"]["special_votes"] = 0
		data_dict["meta"]["vote_complete"] = 0
		count = 0;
		tmp = []
		for vd in vds:
			if (type == "national"):
				data = json.loads(vd.results_national)
			else: 
				data = json.loads(vd.results_provincial)
			for key in data["meta"]:
				data_dict["meta"][key] = int(data_dict["meta"].get(key, 0)) + int(data["meta"][key])
				if (key == "total_votes"):
					tmp.append(data["meta"][key])
			for key in data["vote_count"]:
				data_dict["vote_count"][key] = int(data_dict["vote_count"].get(key, 0)) + int(data["vote_count"][key])
			count = count + 1
		data_dict["meta"]["vote_complete"] = round(float(data_dict["meta"]["vote_complete"]) / float(count) * 100, 2)
		if (type=="national"):
			db.session.query(Ward).filter(Ward.pk == ward_pk).update({ 'results_national': json.dumps(data_dict) })
		else:
			db.session.query(Ward).filter(Ward.pk == ward_pk).update({ 'results_provincial': json.dumps(data_dict) })
		# print tmp
		# print ward_pk
		# print count
		db.session.commit()

def calculate_municipality(queue, year, id):
	for pk in queue:
		query = db.session.query(Municipality).filter(Municipality.pk == pk, Municipality.year == int(year))
		municipality = query.first()
		print municipality
		province = db.session.query(Province).filter(Province.pk == municipality.province_pk).first()
		province_id = province_order[province.province_id]
		print find_municipal_code(str(municipality.municipality_id))
		uri = "http://localhost:8082/result/" + str(id) + "/province/" + str(province_id) + "/municipality/"+ find_municipal_code(str(municipality.municipality_id))
		print uri
		jdata = urllib2.urlopen(uri).read()
		data = json.loads(jdata)
		data_dict = {'meta': {}, 'vote_count': {}}
		data_dict["meta"]["num_registered"] = data['RegisteredVoters']
		data_dict["meta"]["turnout_percentage"] = data['PercVoterTurnout']
		data_dict["meta"]["vote_count"] = data['TotalValidVotes']
		data_dict["meta"]["spoilt_votes"] = data['SpoiltVotes']
		data_dict["meta"]["total_votes"] = data['TotalVotesCast']
		data_dict["meta"]["section_24a_votes"] = data['Section24AVotes']
		data_dict["meta"]["special_votes"] = data['SpecialVotes']
		if (data['bResultsComplete']):
			data_dict["meta"]["vote_complete"] = 100
		else:
			data_dict["meta"]["vote_complete"] = round(float(data['VDWithResultsCaptured']) / float(data['VDCount']) * 100, 2)
		for party_data in data["PartyBallotResults"]:
			data_dict["vote_count"][party_data["Name"]] = party_data["ValidVotes"]
		if (str(data["ElectoralEvent"]).lower().find("national") > -1):
			query.update({ 'results_national': json.dumps(data_dict) })
		else:
			query.update({ 'results_provincial': json.dumps(data_dict) })
		db.session.commit()

def calculate_province(queue, year, id):
	for pk in queue:
		query = db.session.query(Province).filter(Province.pk == pk, Province.year == year)
		province = query.first()
		uri = "http://localhost:8082/result/" + str(id) + "/province/"+ str(province_order[province.province_id])
		print uri
		jdata = urllib2.urlopen(uri).read()
		data = json.loads(jdata)
		data_dict = {'meta': {}, 'vote_count': {}}
		data_dict["meta"]["num_registered"] = data['RegisteredVoters']
		data_dict["meta"]["turnout_percentage"] = data['PercVoterTurnout']
		data_dict["meta"]["vote_count"] = data['TotalValidVotes']
		data_dict["meta"]["spoilt_votes"] = data['SpoiltVotes']
		data_dict["meta"]["total_votes"] = data['TotalVotesCast']
		data_dict["meta"]["section_24a_votes"] = data['Section24AVotes']
		data_dict["meta"]["special_votes"] = data['SpecialVotes']
		if (data['bResultsComplete']):
			data_dict["meta"]["vote_complete"] = 100
		else:
			data_dict["meta"]["vote_complete"] = round(float(data['VDWithResultsCaptured']) / float(data['VDCount']) * 100, 2)
		for party_data in data["PartyBallotResults"]:
			data_dict["vote_count"][party_data["Name"]] = party_data["ValidVotes"]
		if (str(data["ElectoralEvent"]).lower().find("national") > -1):
			query.update({ 'results_national': json.dumps(data_dict) })
		else:
			query.update({ 'results_provincial': json.dumps(data_dict) })
		db.session.commit()

def calculate_national(year, id):
	uri = "http://localhost:8082/result/" + str(id)
	print uri
	query = db.session.query(Country).filter(Country.year == year)
	check_result = query.first()
	check_field_national = json.loads(check_result.results_national)
	check_field_provincial = json.loads(check_result.results_provincial)
	if (int(check_field_national["meta"]["vote_complete"]) + int(check_field_provincial["meta"]["vote_complete"]) < 200):
		print "Calculating national totals"
		jdata = urllib2.urlopen(uri).read()
		data = json.loads(jdata)
		data_dict = {'meta': {}, 'vote_count': {}}
		data_dict["meta"]["num_registered"] = data['RegisteredVoters']
		data_dict["meta"]["turnout_percentage"] = data['PercVoterTurnout']
		data_dict["meta"]["vote_count"] = data['TotalValidVotes']
		data_dict["meta"]["spoilt_votes"] = data['SpoiltVotes']
		data_dict["meta"]["total_votes"] = data['TotalVotesCast']
		data_dict["meta"]["section_24a_votes"] = data['Section24AVotes']
		data_dict["meta"]["special_votes"] = data['SpecialVotes']
		if (data['bResultsComplete']):
			data_dict["meta"]["vote_complete"] = 100
		else:
			data_dict["meta"]["vote_complete"] = round(float(data['VDWithResultsCaptured']) / float(data['VDCount']) * 100, 2)
		for party_data in data["PartyBallotResults"]:
			data_dict["vote_count"][party_data["Name"]] = party_data["ValidVotes"]
		if (str(data["ElectoralEvent"]).lower().find("national") > -1):
			query.update({ 'results_national': json.dumps(data_dict) })
		else:
			query.update({ 'results_provincial': json.dumps(data_dict) })
		db.session.commit()

def test(vd):
	data_dict = {'meta': {}, 'vote_count': {}}
	data_dict["meta"]["num_registered"] = 0
	data_dict["meta"]["turnout_percentage"] = 0
	data_dict["meta"]["vote_count"] = 0
	data_dict["meta"]["spoilt_votes"] = 0
	data_dict["meta"]["total_votes"] = 0
	data_dict["meta"]["section_24a_votes"] = 0
	data_dict["meta"]["special_votes"] = 0
	data_dict["meta"]["vote_complete"] = 0
	db.session.query(VotingDistrict).filter(VotingDistrict.voting_district_id == vd).update({ 'results_national': json.dumps(data_dict) })
	db.session.commit()

def refresh_item(ballot, demarc, uid):
	if (ballot == "national"):
		id = 291
	else:
		id = 292
	if (demarc == "voting_district"):
		download_vd(id, uid, "2014")
	if (demarc == "ward"):
		ward = db.session.query(Ward).filter(Ward.ward_id == uid).first()
		vds = db.session.query(VotingDistrict).filter(VotingDistrict.ward_pk == ward.pk, VotingDistrict.year == "2014").all()
		print "Number of voting districts", len(vds)
		for vd in vds:
			try:
				download_vd(id, vd.voting_district_id, "2014")
			except:
				print "Failed to download vd " + str(vd.voting_district_id)
	if (demarc == "municipality"):
		municipality = db.session.query(Municipality).filter(Municipality.municipality_id == uid).first()
		vds = db.session.query(VotingDistrict).filter(VotingDistrict.municipality_pk == municipality.pk, VotingDistrict.year == "2014").all()
		for vd in vds:
			try:
				download_vd(id, vd.voting_district_id, "2014")
			except:
				print "Failed to download vd " + str(vd.voting_district_id)
	if (demarc == "province"):
		province = db.session.query(Province).filter(Province.province_id == uid).first()
		vds = db.session.query(VotingDistrict).filter(VotingDistrict.province_pk == province.pk, VotingDistrict.year == "2014").all()
		for vd in vds:
			try:
				download_vd(id, vd.voting_district_id, "2014")
			except:
				print "Failed to download vd " + str(vd.voting_district_id)
	calculate_ward(set(ward_queue), "2014", ballot)

if __name__ == "__main__":
	if (len(sys.argv) == 4):
		ballot = sys.argv[1]
		demarc = sys.argv[2]
		uid = sys.argv[3]
		refresh_item(ballot, demarc, uid)
	elif (len(sys.argv) == 2):
		if (sys.argv[1] == "national"):
			calculate_national("2014", 291)
	elif (len(sys.argv) == 3):
		if (sys.argv[1] == "province"):
			calculate_province([sys.argv[2]], "2014", 291)
			calculate_province([sys.argv[2]], "2014", 292)
		if (sys.argv[1] == "municipality"):
			municipality = db.session.query(Municipality).filter(Municipality.municipality_id == sys.argv[2]).first()
			calculate_municipality([municipality.pk], "2014", 291)
			calculate_municipality([municipality.pk], "2014", 292)
	else:
		download_latest_results(291)
		download_provincial_results(292)
	# calculate_province
	# download_latest_results(292)
	# test(32862595)
	# download_latest_results(146)
	# calculate_national(2014, 291)