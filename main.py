import requests
from dotenv import load_dotenv
import os
import sys
import textwrap
load_dotenv()


# Exceptions
class RequestFailure(Exception):
    pass


class InvalidSearch(Exception):
    pass


class BadReturn(Exception):
    pass


def api_call(endpoint=None, query=None):
    """Makes the API call to The Movie Database

    :param endpoint: The Movie Database API endpoint
    :type endpoint: str
    :param query: Search Term
    :type query: str
    :return: None
    """

    if endpoint is None or query is None:
        raise InvalidSearch
    url = f'https://api.themoviedb.org/3/{endpoint}'
    params = {'api_key': os.getenv('API_KEY'), 'query': query}

    try:
        # make the call!
        response = requests.get(url, params=params, allow_redirects=True)
        return response.json()
    except requests.exceptions.RequestException:
        raise RequestFailure


def movie_search(search_str=None):
    """Checks for valid search input and makes call to API method, then
    collects API return in to list of movie objects

    :param search_str: String to be used in search query
    :type search_str: str
    :rtype: list
    :return: Movie object list
    """

    if search_str is None or len(search_str) == 0:
        raise InvalidSearch
    movie_list = []
    api_return = api_call('search/movie', search_str)
    if api_return is None:
        raise BadReturn
    # get the part of the return that we want
    data = api_return.get('results')
    if data is None or len(data) == 0:
        raise BadReturn
    # create movie objects and store in lists
    for item in data:
        movie = {'title': item.get('title'),
                 'overview': item.get('overview'),
                 'release_date': item.get('release_date')}
        movie_list.append(movie)

    return movie_list


def parse_data(movie_list=None):
    """Parses lists of movies to extract title, year, and overview, then collects
       movies into output string

    :param movie_list: List of movie objects
    :rtype: str
    :return: String of movie data
    """
    if isinstance(movie_list, list) and len(movie_list) > 0:
        output = []
        for movie in movie_list:
            # some trivial data manipulation: extract only the year from the release_date ('yyyy-mm-dd')
            date = movie.get('release_date')
            year = ''
            if date is not None:
                date_arr = date.split('-')
                year = date_arr[0] if date_arr[0] != '' else 'No Data'
            # create string for each movie, and set output width
            wrapper = textwrap.TextWrapper(width=50)
            entry = f'Title: {movie.get("title", "No Data")}\n' \
                    f'Year: {year}\n' \
                    f'Overview: {wrapper.fill(text=movie.get("overview", "No Data"))}'
            output.append(entry)

        return '\n-------------------------\n'.join(output)  # join all movie strings together
    else:
        raise BadReturn


if __name__ == '__main__':
    try:
        search_str = input('Enter a movie title or franchise (case sensitive!): ')
        movie_list = movie_search(search_str)
        print(parse_data(movie_list))
        sys.exit(0)
    except RequestFailure:
        print('Request failed!')
        sys.exit(1)
    except InvalidSearch:
        print('Invalid Search!')
        sys.exit(1)
    except BadReturn:
        print('Bad Return!')
        sys.exit(1)
