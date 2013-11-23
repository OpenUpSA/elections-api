import requests

class IEC(object):
    def __init__(self, base_url):
        self.base_url = base_url

    def _paginate(self, url, params=None):
        params = params or {}
        url = self.base_url + "/" + url
        while url:
            r = requests.get(url, params=params)
            js =  r.json
            for result in js["results"]:
                yield result
            url = js["next"]

    def parties(self):
        return self._paginate("parties")

    def events(self):
        return self._paginate("events")

    def provinces(self):
        return self._paginate("provinces")

    def municipalities(self, **kwargs):
        return self._paginate("municipalities", kwargs)

    def wards(self, **kwargs):
        return self._paginate("wards", kwargs)

    def voting_districts(self, **kwargs):
        return self._paginate("voting_districts", kwargs)

    def results(self, **kwargs):
        return self._paginate("results", kwargs)

    def resultsummaries(self, **kwargs):
        return self._paginate("result_summaries", kwargs)

#iec = IEC("http://iec.code4sa.org")
iec = IEC("http://localhost:8000")
#print list(iec.parties())
#print list(iec.events())
#print list(iec.provinces())
#print list(iec.municipalities(province="Gauteng"))
#print list(iec.wards(province="Gauteng"))
#print list(iec.voting_districts(ward="41602001"))
#print list(iec.results(ward="41602001"))
print list(iec.resultsummaries(ward="41602001"))
