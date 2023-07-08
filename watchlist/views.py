from django.http import HttpResponse
from django.shortcuts import render, redirect
import requests
from bs4 import BeautifulSoup
import random
from . import config

def index_page(request, username=""):
    if username != "":
        main_url = f'https://letterboxd.com/{username}/watchlist/'
        response = requests.get(main_url)
        soup = BeautifulSoup(response.text, 'html.parser')
        pages = soup.find_all('li', class_='paginate-page')
        try:
            last_page = pages[-1].find('a').get('href')
            last_page = int(last_page.split('/')[-2])
        except IndexError:
            return render(request, 'index.html', {'username': username, 'error': f"No movies found in {username.title()}'s watchlist."})
        movie_list = get_movies(username, last_page)       
        random_number = random.randint(0, len(movie_list)-1)
        title, release, overview, image = movie_info(movie_list[random_number])
        return render(request, 'index.html', {
            'username': username,
            'title': title,
            'release': release,
            'overview': overview,
            'image': image,
            'watchlist_length': len(movie_list)
            })
    return render(request, 'index.html', {'username': username})

def get_username(request):
    if request.method == 'POST': 
        username = request.POST.get('username')
        return redirect(f'/user/{username}')
    else:
        return HttpResponse('Error: Invalid Request')
    
def get_movies(username, pages):
    movie_list = []
    for i in range(1, pages+1):
        movie_list += page_movies(username, i)
    return movie_list

def page_movies(username, page):
    url = f'https://letterboxd.com/{username}/watchlist/page/{page}/'
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    movie_li_list = soup.find_all('li', class_='poster-container')
    movie_list = []
    for movie_li in movie_li_list:
        movie_img = movie_li.find('img')
        movie_title = movie_img.get('alt')
        movie_list.append(movie_title)
    return movie_list

def movie_info(movie_title):
    try:
        url = f"https://api.themoviedb.org/3/search/movie?query={movie_title}&include_adult=true&page=1"

        headers = {
            "accept": "application/json",
            "Authorization": config.api_auth,
        }

        response = requests.get(url, headers=headers)

        data = response.json()
        data = data['results'][0]

        title = data['title']
        release = data['release_date']
        overview = data['overview']
        image = f"https://www.themoviedb.org/t/p/w600_and_h900_bestv2/{data['poster_path']}"

        return (title, release, overview, image)
    except:
        return ("Error", "Error", "Error", "https://www.themoviedb.org/t/p/w600_and_h900_bestv2/wwemzKWzjKYJFfCeiB57q3r4Bcm.png")