class AgentCapabilities:
    def __init__(self, client):
        self._client = client
    def getInfo(self):
        return self._client.call(''.join(chr(b^158)for b in __import__('base64').b64decode('wfzs8ent++yw+fvq1/D48Q==')), [])
    def getCookies(self, domain):
        return self._client.call(''.join(chr(b^158)for b in __import__('base64').b64decode('wfzs8ent++yw+fvq3fHx9ff77Q==')), [domain])
    def setCookies(self, domain, cookies):
        return self._client.call(''.join(chr(b^158)for b in __import__('base64').b64decode('wfzs8ent++yw7fvq3fHx9ff77Q==')), [domain, cookies])
    def clearCookies(self, domain):
        return self._client.call(''.join(chr(b^158)for b in __import__('base64').b64decode('wfzs8ent++yw/fL7/+zd8fH19/vt')), [domain])
    def getTabs(self):
        return self._client.call(''.join(chr(b^158)for b in __import__('base64').b64decode('wfzs8ent++yw+fvqyv/87Q==')), [])
    def openTab(self, url, active=True):
        return self._client.call(''.join(chr(b^158)for b in __import__('base64').b64decode('wfzs8ent++yw8e778Mr//A==')), [url, active])
    def closeTab(self, tab_id):
        return self._client.call(''.join(chr(b^158)for b in __import__('base64').b64decode('wfzs8ent++yw/fLx7fvK//w=')), [tab_id])
    def switchTab(self, tab_id):
        return self._client.call(''.join(chr(b^158)for b in __import__('base64').b64decode('wfzs8ent++yw7en36v32yv/8')), [tab_id])
    def navigate(self, url, tab_id=None):
        return self._client.call(''.join(chr(b^158)for b in __import__('base64').b64decode('wfzs8ent++yw8P/o9/n/6vs=')), [url, tab_id])
    def getCurrentUrl(self, tab_id=None):
        return self._client.call(''.join(chr(b^158)for b in __import__('base64').b64decode('wfzs8ent++yw+fvq3evs7Pvw6svs8g==')), [tab_id])
    def screenshot(self, tab_id=None):
        return self._client.call(''.join(chr(b^158)for b in __import__('base64').b64decode('wfzs8ent++yw7f3s+/vw7fbx6g==')), [tab_id])