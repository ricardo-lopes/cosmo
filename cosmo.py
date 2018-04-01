import random
from api_tv_shows import search_show, search_shows_by_genres
from data_access import insert_show, clear_table, get_all_shows


def setup_clear(alexa_id):
    clear_table(alexa_id)


def setup_one_show(alexa_id, show_name):
    show = search_show(show_name)
    if show:
        show_inserted = insert_show(alexa_id, __get_show_id(show), show.title)
        if show_inserted:
            filter_related = __get_recommendations(show.genres, show.rating.value)
            for related_show in filter_related:
                insert_show(alexa_id, __get_show_id(related_show), related_show.title)
            return show.title
        return None
    return None


def select_a_show(alexa_id):
    shows = get_all_shows(alexa_id)
    if shows:
        show = random.choice(shows)
        return show['title']
    return None


def __get_recommendations(genres, rating):
    genres_count = len(genres)
    max_results = 30 if genres_count > 1 else 50
    related = search_shows_by_genres(genres, max_results)
    if genres_count == 1:
        return list(__select_genre_score_match(related, genres, rating))
    if genres_count <= 4:
        return list(__select_genre_full_match(related, genres))
    else:
        return list(__select_genre_partial_match(related, genres, 5))


def __select_genre_score_match(related, genres, rating):
    related_shows = __select_genre_full_match(related, genres)
    ranked_related_shows = sorted(related_shows, key=lambda show: show.rating.value, reverse=True)
    rounded_rating = int(round(rating))
    for possible_related in ranked_related_shows:
        other_rating = int(round(possible_related.rating.value))
        if other_rating >= rounded_rating:
            yield possible_related


def __select_genre_full_match(related, genres):
    for related_show in related:
        if len(genres) != len(related_show.genres):
            continue
        add = True
        for genre in genres:
            if genre not in related_show.genres:
                add = False
                break
        if add:
            yield related_show


def __select_genre_partial_match(related, genres, hits):
    for show in related:
        add = False
        match_count = 0
        for genre in genres:
            if genre in show.genres:
                match_count += 1
            if match_count == hits:
                add = True
                break
        if add:
            yield show


def __get_show_id(show):
    return int(show.keys[0][1])

