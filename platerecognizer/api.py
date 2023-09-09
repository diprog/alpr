import aiohttp


class PlateRecognizerAPI:
    def __init__(self, api_token: str, regions: list[str]):
        self._api_token = api_token
        self._regions = regions

    async def detect(self, image_filepath: str):
        url = 'https://api.platerecognizer.com/v1/plate-reader/'
        headers = {'Authorization': f'Token {self._api_token}'}
        with open(image_filepath, 'rb') as fp:
            async with aiohttp.ClientSession(headers=headers) as session:
                data = aiohttp.FormData()
                data.add_field('regions', ','.join(self._regions))
                data.add_field('upload', fp)

                async with session.post(url, data=data) as response:
                    json_response = await response.json()
                    return json_response
