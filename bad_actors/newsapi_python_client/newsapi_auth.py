from requests.auth import AuthBase


class NewsApiAuth(AuthBase):
    # Provided by newsapi: https://newsapi.org/docs/authentication
    def __init__(self, keys, cur_request_counter):
        self._keys_list = keys
        self._cur_request_counter = cur_request_counter

    def __call__(self, request):
        request.headers.update(get_auth_headers(self.get_key(self._cur_request_counter)))
        return request

    def set_request_counter(self, cur_request_counter):
        self._cur_request_counter = cur_request_counter

    def get_key(self, num_of_requests):
        return self._keys_list[(num_of_requests-1)/1000]  # todo: const for 1000 max requests number.


def get_auth_headers(api_key):
    return {
        'Content-Type': 'Application/JSON',
        'Authorization': api_key
    }


