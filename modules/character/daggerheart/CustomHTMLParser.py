from html.parser import HTMLParser
import json

class CustomHTMLParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.json_data = None
        self.is_target_script = False

    def handle_starttag(self, tag, attrs):
        # Check if the tag is <script> and has the required attributes
        if tag == "script":
            for attr in attrs:
                if attr == ("id", "__NEXT_DATA__") and ("type", "application/json") in attrs:
                    self.is_target_script = True

    def handle_data(self, data):
        # If inside the target <script>, store the data
        if self.is_target_script:
            self.json_data = data.strip()

    def handle_endtag(self, tag):
        # Reset flag when the script tag ends
        if tag == "script":
            self.is_target_script = False

    def get_json(self):
        return json.loads(self.json_data)
