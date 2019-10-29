import copy
import logging
from src.lastfm.library.recent_artists import fetch_recent_artists


def calculate_ratings(user, top_tracks_to_recommendations, prefer_unheard_artists=True):
    """Returns a copy of the list of recommendations in the given map, with ratings set based on recommendation
    'strength', which can be used to determine its chances of showing up in the final playlist"""

    # Create a copy of the given map and modify it instead
    top_tracks_to_recommendations_copy = copy.deepcopy(top_tracks_to_recommendations)

    _set_ratings_to_playcounts(top_tracks_to_recommendations_copy)

    if prefer_unheard_artists:
        _adjust_ratings_based_on_recent_artists(top_tracks_to_recommendations_copy, user)

    return _extract_tracks_from_map(top_tracks_to_recommendations_copy)

def _set_ratings_to_playcounts(top_tracks_to_recommendations_copy):
    """Initially set rating to associated top track's playcount, the thought being that more frequently listened-to
    tracks should get a greater chance of showing up in the final playlist."""
    for top_track in top_tracks_to_recommendations_copy:
        recommendations = top_tracks_to_recommendations_copy[top_track]
        for recommendation in recommendations:
            recommendation.recommendation_rating += top_track.playcount

def _adjust_ratings_based_on_recent_artists(top_tracks_to_recommendations, user):
    """Reduces tracks ratings based on their artists' playcount"""
    recent_artists = fetch_recent_artists(user)
    for top_track in top_tracks_to_recommendations:
        recommendations = top_tracks_to_recommendations[top_track]
        for recommendation in recommendations:
            for artist in recent_artists:
                if recommendation.artist.lower() == artist.artist_name.lower():
                    # Adjusting the rating by the reciprocal of the artist's playcount, plus one. The "plus one" is
                    # to account for artist's with a playcount of just 1 - those should reduce the rating too.
                    recommendation.recommendation_rating = (1 / (artist.playcount + 1)) * recommendation.recommendation_rating

def _extract_tracks_from_map(top_tracks_to_recommendations):
    all_recommendations = []
    for top_track in top_tracks_to_recommendations:
        recommendations = top_tracks_to_recommendations[top_track]
        all_recommendations = all_recommendations + recommendations
    return all_recommendations
