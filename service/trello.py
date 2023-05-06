import aiohttp

class Trello:
    def __init__(self):
        pass
        
    async def get_board_tasks(self, api_key, token, board_id):
        url = f"https://api.trello.com/1/boards/{board_id}/cards"
        querystring = {"key": api_key, "token": token}
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=querystring) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    raise Exception("Failed to get Trello tasks.")
    