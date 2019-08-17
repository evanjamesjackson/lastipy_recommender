
import unittest
from spotify_recommender.lastfm import period
from spotify_recommender.lastfm.top_tracks import TopTracksFetcher
from spotify_recommender.spotify import playlist
from spotify_recommender.track import Track
from unittest.mock import patch, Mock
from requests import HTTPError


class TopTracksFetcherTest(unittest.TestCase):
    @patch('requests.get')
    def test_one_page_of_results(self, mock_get):
        expected_track = Track(track_name="Stayin' Alive", artist="Bee Gees")

        mock_get.ok = True

        json_track = self._build_json(expected_track)

        first_page_response = {
            'toptracks': {
                'track': [json_track]
            }
        }

        second_page_response = {
            'toptracks': {
                'track': []
            }
        }

        mock_responses = [Mock(), Mock()]
        mock_responses[0].json.return_value = first_page_response
        mock_responses[1].json.return_value = second_page_response
        mock_get.side_effect = mock_responses

        fetcher = TopTracksFetcher()
        self.assertEqual(fetcher.fetch(user='sonofjack3', a_period=period.SEVEN_DAYS)[0], expected_track)

    @patch('requests.get')
    def test_multiple_tracks_over_multiple_pages(self, mock_get):
        expected_track_1 = Track(track_name="Penny Lane", artist="The Beatles")
        expected_track_2 = Track(track_name="Won't Get Fooled Again", artist="The Who")
        expected_track_3 = Track(track_name="Like the FBI", artist="Bob Dylan")
        expected_tracks = [expected_track_1, expected_track_2, expected_track_3]

        mock_get.ok = True

        json_track_1 = self._build_json(expected_track_1)
        json_track_2 = self._build_json(expected_track_2)
        json_track_3 = self._build_json(expected_track_3)

        first_page_response = {
            'toptracks': {
                'track': [json_track_1, json_track_2]
            }
        }

        second_page_response = {
            'toptracks': {
                'track': [json_track_3]
            }
        }

        third_page_response = {
            'toptracks': {
                'track': []
            }
        }

        mock_responses = [Mock(), Mock(), Mock()]
        mock_responses[0].json.return_value = first_page_response
        mock_responses[1].json.return_value = second_page_response
        mock_responses[2].json.return_value = third_page_response
        mock_get.side_effect = mock_responses

        fetcher = TopTracksFetcher()
        fetched_tracks = fetcher.fetch(user="sonofjack3", a_period=period.SEVEN_DAYS)
        self.assertCountEqual(fetched_tracks, expected_tracks)

    @patch('requests.get')
    def test_songs_with_one_playcount_ignored(self, mock_get):
        ignored_track_1 = Track(track_name="Stayin' Alive", artist="Bee Gees")
        non_ignored_track = Track(track_name="Ventura Highway", artist="America")
        ignored_track_2 = Track(track_name="Anesthetized Lesson", artist="Gum")

        mock_get.ok = True

        json_track_1 = self._build_json(ignored_track_1, playcount=1)
        json_track_2 = self._build_json(non_ignored_track, playcount=2)
        json_track_3 = self._build_json(ignored_track_2, playcount=1)

        first_page_response = {
            'toptracks': {
                'track': [json_track_1, json_track_2, json_track_3]
            }
        }

        second_page_response = {
            'toptracks': {
                'track': []
            }
        }

        mock_responses = [Mock(), Mock()]
        mock_responses[0].json.return_value = first_page_response
        mock_responses[1].json.return_value = second_page_response
        mock_get.side_effect = mock_responses

        fetcher = TopTracksFetcher()
        fetched_tracks = fetcher.fetch(user='sonofjack3', a_period=period.SEVEN_DAYS)
        self.assertEqual(fetched_tracks.__len__(), 1)
        self.assertEqual(fetched_tracks[0], non_ignored_track)

    @patch('requests.get')
    def test_failure(self, mock_get):
        mock_get.ok = False
        mock_get.side_effect = HTTPError("Mock")

        fetcher = TopTracksFetcher()
        with self.assertRaises(HTTPError):
            fetcher.fetch('sonofjack3', period.SEVEN_DAYS)

    def _build_json(self, track, playcount=2):
        return {
            'name': track.track_name,
            'artist': {
                'name': track.artist
            },
            'playcount': playcount
        }
