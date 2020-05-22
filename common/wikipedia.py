from typing import TYPE_CHECKING, List, Dict
import requests

from .config import logger

if TYPE_CHECKING:
    from .status import Status


class Wikipedia:
    def __init__(self, status: 'Status', start_path: str):
        self.status = status
        self.start_path = start_path

    @property
    def links(self) -> List[str]:
        return self.scrape_page()

    def build_payload(self, json_response=None) -> Dict[str, str]:
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

    def scrape_page(self) -> List[str]:
        payload = self.build_payload()
        all_links = list()

        # Interact with wiki API to get all links on a given page + continued links if any
        while True:
            logger.info("still getting links..")
            json_response = requests.get("https://en.wikipedia.org/w/api.php", payload).json()
            links = json_response.get("query", {}).get("pages", [{}])[0].get("links", [])
            all_links += [link["title"] for link in links if link.get("title")]
            if "batchcomplete" not in json_response:
                payload = self.build_payload(json_response)
            else:
                break

        return all_links
