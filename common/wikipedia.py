from typing import TYPE_CHECKING, List, Dict
import requests
from .config import logger

if TYPE_CHECKING:
    from .status import Status


class Wikipedia:
    def __init__(self, status: "Status", start_path: str):
        """Wikipedia interacts with the wiki API.

        Wikipedia interacts with MediaWiki through requests.
        MediaWiki is used to obtain the links on each Wikipedia page.

        Args:
            status: Status of current search.
            start_path: History of current query.
        """
        self.status = status
        self.start_path = start_path

    @property
    def links(self) -> List[str]:
        """The links on the queried wikipedia page."""
        return self.scrape_page()

    def build_payload(self, json_response=None) -> Dict[str, str]:
        """Creates a payload for the API request.

        This function takes care of setting "plcontinue" based on request received.

        Args:
            json_response: Response obtained from querying MediaWiki API.

        Returns: Payload for request to MediaWiki API.

        """
        payload = {
            "action": "query",
            "titles": self.start_path,
            "format": "json",
            "formatversion": "2",
            "prop": "links",
            "pllimit": "max",
        }
        if json_response:
            payload["plcontinue"] = json_response.get("continue").get("plcontinue")
        return payload

    @staticmethod
    def get_request(params):
        """Sends a request to MediaWiki API.

        Args:
            params: The parameters of the request.

        Returns: Response obtained from MediaWiki API.

        """
        return requests.get("https://en.wikipedia.org/w/api.php", params).json()

    def scrape_page(self) -> List[str]:
        """Scrape links from Wikipedia page queried.

        Incomplete responses have a continue clause pointing to the rest of the data.
        To get rest of data: send a new request using the "plcontinue" from the response.

        Returns: List of links on wikipedia page queried.

        """
        params = self.build_payload()
        all_links = list()

        # Interact with wiki API to get all links on a given page + continued links if any
        while True:
            logger.info("still getting links..")
            json_response = requests.get(
                "https://en.wikipedia.org/w/api.php", params
            ).json()
            links = (
                json_response.get("query", {}).get("pages", [{}])[0].get("links", [])
            )
            all_links += [link["title"] for link in links if link.get("title")]
            if "batchcomplete" not in json_response and len(json_response.keys()) > 1:
                params = self.build_payload(json_response)
            else:
                break

        return all_links
