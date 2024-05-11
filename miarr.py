import arrapi
from arrapi import RadarrAPI,SonarrAPI
import difflib
import asyncio

class MiarrAPI:
    radarr = None
    sonarr = None
    added_content = []
    searched_movies = []
    searched_shows = []

    def __init__(self, radarr: tuple[str, str], sonarr: tuple[str,str]):
        self.radarr = RadarrAPI(radarr[0],radarr[1])
        self.sonarr = SonarrAPI(sonarr[0],sonarr[1])
        self.added_content = self.radarr.all_movies()
        self.added_content += self.sonarr.all_series()
        self.radarr.respect_list_exclusions_when_adding()
        self.sonarr.respect_list_exclusions_when_adding()

    def search_content(self, content: str):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(asyncio.gather(
                self._radarr_search(content),
                self._sonarr_search(content)
            ))
        loop.close()
        search = self.searched_movies[:5] + self.searched_shows[:5]
        return self._sort_content(search, content)

    def search_added_content(self, content: str):
        result = self._sort_content(self.added_content, content)
        return result

    def add_content(self, content):
        if content in self.added_content:
            return False
        if isinstance(content,arrapi.objs.reload.Movie):
            content.add("/Data/media/movies","HD-1080p")
            return True
        if isinstance(content,arrapi.objs.reload.Series):
            content.add("/Data/media/shows","HD-1080p")
            return True
        else:
            return False

    def delete_content(self,content):
        if content not in self.added_content:
            return False
        content.delete(deleteFiles = True)
        return True

    def redownload_content(self,content):
        #TODO: Delete Files and block release (may not be possible with API)
        return None

    async def _radarr_search(self, content:str):
        self.searched_movies = self.radarr.search_movies(content)
    async def _sonarr_search(self, content:str):
        self.searched_shows = self.sonarr.search_series(content)

    def _sort_content(self, content: list, content_name: str):
        weighted_results = []
        for result in content:
            ratio = difflib.SequenceMatcher(None, result.title,content_name).ratio()
            weighted_results.append((result,ratio))
        sorted_tuples = sorted(weighted_results, key=lambda x: x[1], reverse=True)[:10]
        sorted_content = []
        for content in sorted_tuples:
            sorted_content.append(content[0])
        return sorted_content
