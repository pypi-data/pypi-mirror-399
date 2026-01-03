"""
This file is part of py-sonic.

py-sonic is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

py-sonic is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with py-sonic.  If not, see <http://www.gnu.org/licenses/>
"""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any, BinaryIO, final

from pydantic import BaseModel

from libsonic.errors import (
    ArgumentError,
    CredentialError,
    get_exc_by_code,
)
from libsonic import models
from netrc import netrc
from hashlib import md5
import urllib.request
import urllib.error
import urllib.parse
from http import client as http_client
from urllib.parse import urlencode
from io import StringIO

import json
import logging
import socket
import ssl
import sys
import os

API_VERSION = "1.16.1"

logger = logging.getLogger(__name__)


@final
class Connection(object):
    def __init__(
        self,
        base_url: str,
        username: str | None = None,
        password: str | None = None,
        port: int = 4040,
        server_path: str = "/rest",
        app_name: str = "py-sonic",
        api_version: str = API_VERSION,
        insecure: bool = False,
        use_netrc: str | bool | None = None,
        legacy_auth: bool = False,
        use_get: bool = False,
        salt: str | None = None,
        token: str | None = None,
        user_agent: str | None = None,
    ) -> None:
        """
        This will create a connection to your subsonic server

        base_url:str         The base url for your server. Be sure to use
                            "https" for SSL connections.  If you are using
                            a port other than the default 4040, be sure to
                            specify that with the port argument.  Do *not*
                            append it here.

                            ex: http://subsonic.example.com

                            If you are running subsonic under a different
                            path, specify that with the "server_path" arg,
                            *not* here.  For example, if your subsonic
                            lives at:

                            https://mydomain.com:8080/path/to/subsonic/rest

                            You would set the following:

                            base_url = "https://mydomain.com"
                            port = 8080
                            server_path = "/path/to/subsonic/rest"
        username:str        The username to use for the connection.  This
                            can be None if `use_netrc' is True (and you
                            have a valid entry in your netrc file)
        password:str        The password to use for the connection.  This
                            can be None if `use_netrc' is True (and you
                            have a valid entry in your netrc file)
        salt:str            Instead of providing a password, the caller can
                            provide both token and salt arguments for
                            authenticaion, reducing the impact of plaintext
                            passwords
        token:str           Must be provided if the salt is provided.
        port:int            The port number to connect on.  The default for
                            unencrypted subsonic connections is 4040
        server_path:str      The base resource path for the subsonic views.
                            This is useful if you have your subsonic server
                            behind a proxy and the path that you are proxying
                            is different from the default of '/rest'.
                            Ex:
                                server_path='/path/to/subs'

                              The full url that would be built then would be
                              (assuming defaults and using "example.com" and
                              you are using the "ping" view):

                                http://example.com:4040/path/to/subs/ping.view
        app_name:str         The name of your application.
        api_version:str      The API version you wish to use for your
                            application.  Subsonic will throw an error if you
                            try to use/send an api version higher than what
                            the server supports.  See the Subsonic API docs
                            to find the Subsonic version -> API version table.
                            This is useful if you are connecting to an older
                            version of Subsonic.
        insecure:bool       This will allow you to use self signed
                            certificates when connecting if set to True.
        use_netrc:str|bool   You can either specify a specific netrc
                            formatted file or True to use your default
                            netrc file ($HOME/.netrc).
        legacy_auth:bool     Use pre-1.13.0 API version authentication
        use_get:bool         Use a GET request instead of the default POST
                            request.  This is not recommended as request
                            URLs can get very long with some API calls
        user_agent:str       If specified, use this User-Agent string in
                            the request header.  If None, the default Python
                            urllib UA will be used.
        """
        self._base_url = base_url
        self._hostname = base_url.split("://")[1].strip()
        self._username = username
        self._raw_pass = password
        self._salt = salt
        self._token = token
        self._legacy_auth = legacy_auth
        self._use_get = use_get
        self._user_agent = user_agent

        self._netrc = None
        if use_netrc is not None:
            self._process_netrc(use_netrc)
        elif username is None or (password is None and (salt is None or token is None)):
            raise CredentialError(
                "You must specify either a username/password "
                'combination or salt/token combination or "use_netrc" must be either True or a string '
                "representing a path to a netrc file"
            )

        self._port = int(port)
        self._api_version = api_version
        self._app_name = app_name
        self._server_path = server_path.strip("/")
        self._insecure = insecure
        self._opener = self._get_opener(self._username, self._raw_pass)

    # Properties
    def set_base_url(self, url: str) -> None:
        self._base_url = url
        self._opener = self._get_opener(self._username, self._raw_pass)

    base_url = property(lambda s: s._base_url, set_base_url)

    def set_port(self, port: int) -> None:
        self._port = int(port)

    port = property(lambda s: s._port, set_port)

    def set_username(self, username: str) -> None:
        self._username = username
        self._opener = self._get_opener(self._username, self._raw_pass)

    username = property(lambda s: s._username, set_username)

    def set_password(self, password: str) -> None:
        self._raw_pass = password
        # Redo the opener with the new creds
        self._opener = self._get_opener(self._username, self._raw_pass)

    password = property(lambda s: s._raw_pass, set_password)

    api_version = property(lambda s: s._api_version)

    def set_app_name(self, app_name: str) -> None:
        self._app_name = app_name

    app_name = property(lambda s: s._app_name, set_app_name)

    def set_server_path(self, path: str) -> None:
        self._server_path = path.strip("/")

    server_path = property(lambda s: s._server_path, set_server_path)

    def set_insecure(self, insecure: bool) -> None:
        self._insecure = insecure

    insecure = property(lambda s: s._insecure, set_insecure)

    def set_legacy_auth(self, lauth: bool) -> None:
        self._legacy_auth = lauth

    legacy_auth = property(lambda s: s._legacy_auth, set_legacy_auth)

    def set_get(self, get: bool) -> None:
        self._use_get = get

    use_get = property(lambda s: s._use_get, set_get)

    # API methods
    def ping(self) -> bool:
        """
        since: 1.0.0

        Returns a boolean True if the server is alive, False otherwise
        """
        method_name = "ping"
        view_name = "%s.view" % method_name

        req = self._get_request(view_name)
        try:
            res = self._do_info_req(req)
        except:
            return False
        if res["status"] == "ok":
            return True
        elif res["status"] == "failed":
            exc = get_exc_by_code(res["error"]["code"])
            raise exc(res["error"]["message"])
        return False

    def get_license(self) -> models.LicenseResponse:
        """
        since: 1.0.0

        Gets details related to the software license

        Returns a dict like the following:

        {u'license': {u'date': u'2010-05-21T11:14:39',
                      u'email': u'email@example.com',
                      u'key': u'12345678901234567890123456789012',
                      u'valid': True},
         u'status': u'ok',
         u'version': u'1.5.0',
         u'xmlns': u'http://subsonic.org/restapi'}
        """
        method_name = "getLicense"
        view_name = "%s.view" % method_name

        req = self._get_request(view_name)
        res = self._do_info_req(req)
        return self._validate_response(res, models.LicenseResponse)

    def get_scan_status(self) -> models.ScanStatusResponse:
        """
        since: 1.15.0

        returns the current status for media library scanning.
        takes no extra parameters.

        returns a dict like the following:

        {'status': 'ok', 'version': '1.15.0',
        'scanstatus': {'scanning': true, 'count': 4680}}

        'count' is the total number of items to be scanned
        """
        method_name = "getScanStatus"
        view_name = "%s.view" % method_name

        req = self._get_request(view_name)
        res = self._do_info_req(req)
        return self._validate_response(res, models.ScanStatusResponse)

    def start_scan(self) -> models.ScanStatusResponse:
        """
        since: 1.15.0

        Initiates a rescan of the media libraries.
        Takes no extra parameters.

        returns a dict like the following:

        {'status': 'ok', 'version': '1.15.0',
        'scanstatus': {'scanning': true, 'count': 0}}

        'scanning' changes to false when a scan is complete
        'count' starts a 0 and ends at the total number of items scanned

        """
        method_name = "startScan"
        view_name = "%s.view" % method_name

        req = self._get_request(view_name)
        res = self._do_info_req(req)
        return self._validate_response(res, models.ScanStatusResponse)

    def get_music_folders(self) -> models.MusicFoldersResponse:
        """
        since: 1.0.0

        Returns all configured music folders

        Returns a dict like the following:

        {u'musicFolders': {u'musicFolder': [{u'id': 0, u'name': u'folder1'},
                                    {u'id': 1, u'name': u'folder2'},
                                    {u'id': 2, u'name': u'folder3'}]},
         u'status': u'ok',
         u'version': u'1.5.0',
         u'xmlns': u'http://subsonic.org/restapi'}
        """
        method_name = "getMusicFolders"
        view_name = "%s.view" % method_name

        req = self._get_request(view_name)
        res = self._do_info_req(req)
        return self._validate_response(res, models.MusicFoldersResponse)

    def get_now_playing(self) -> models.NowPlayingResponse:
        """
        since: 1.0.0

        Returns what is currently being played by all users

        Returns a dict like the following:

        {u'nowPlaying': {u'entry': {u'album': u"Jazz 'Round Midnight 12",
                            u'artist': u'Astrud Gilberto',
                            u'bitRate': 172,
                            u'contentType': u'audio/mpeg',
                            u'coverArt': u'98349284',
                            u'duration': 325,
                            u'genre': u'Jazz',
                            u'id': u'2424324',
                            u'isDir': False,
                            u'isVideo': False,
                            u'minutesAgo': 0,
                            u'parent': u'542352',
                            u'path': u"Astrud Gilberto/Jazz 'Round Midnight 12/01 - The Girl From Ipanema.mp3",
                            u'playerId': 1,
                            u'size': 7004089,
                            u'suffix': u'mp3',
                            u'title': u'The Girl From Ipanema',
                            u'track': 1,
                            u'username': u'user1',
                            u'year': 1996}},
         u'status': u'ok',
         u'version': u'1.5.0',
         u'xmlns': u'http://subsonic.org/restapi'}
        """
        method_name = "getNowPlaying"
        view_name = "%s.view" % method_name

        req = self._get_request(view_name)
        res = self._do_info_req(req)
        return self._validate_response(res, models.NowPlayingResponse)

    def get_indexes(
        self, music_folder_id: int | None = None, if_modified_since: int = 0
    ) -> models.IndexesResponse:
        """
        since: 1.0.0

        Returns an indexed structure of all artists

        music_folder_id:int       If this is specified, it will only return
                                artists for the given folder ID from
                                the getMusicFolders call
        ifModifiedSince:int     If specified, return a result if the artist
                                collection has changed since the given
                                unix timestamp

        Returns a dict like the following:

        {u'indexes': {u'index': [{u'artist': [{u'id': u'29834728934',
                                       u'name': u'A Perfect Circle'},
                                      {u'id': u'238472893',
                                       u'name': u'A Small Good Thing'},
                                      {u'id': u'9327842983',
                                       u'name': u'A Tribe Called Quest'},
                                      {u'id': u'29348729874',
                                       u'name': u'A-Teens, The'},
                                      {u'id': u'298472938',
                                       u'name': u'ABA STRUCTURE'}],
                      u'lastModified': 1303318347000L},
         u'status': u'ok',
         u'version': u'1.5.0',
         u'xmlns': u'http://subsonic.org/restapi'}
        """
        method_name = "getIndexes"
        view_name = "%s.view" % method_name

        q = self._get_query_dict(
            {
                "musicFolderId": music_folder_id,
                "ifModifiedSince": self._ts_2_milli(if_modified_since),
            }
        )

        req = self._get_request(view_name, q)
        res = self._do_info_req(req)
        self._fix_last_modified(res)
        return self._validate_response(res, models.IndexesResponse)

    def get_music_directory(self, mid: str) -> models.MusicDirectoryResponse:
        """
        since: 1.0.0

        Returns a listing of all files in a music directory.  Typically used
        to get a list of albums for an artist or list of songs for an album.

        mid:str     The string ID value which uniquely identifies the
                    folder.  Obtained via calls to getIndexes or
                    getMusicDirectory.  REQUIRED

        Returns a dict like the following:

        {u'directory': {u'child': [{u'artist': u'A Tribe Called Quest',
                            u'coverArt': u'223484',
                            u'id': u'329084',
                            u'isDir': True,
                            u'parent': u'234823940',
                            u'title': u'Beats, Rhymes And Life'},
                           {u'artist': u'A Tribe Called Quest',
                            u'coverArt': u'234823794',
                            u'id': u'238472893',
                            u'isDir': True,
                            u'parent': u'2308472938',
                            u'title': u'Midnight Marauders'},
                           {u'artist': u'A Tribe Called Quest',
                            u'coverArt': u'39284792374',
                            u'id': u'983274892',
                            u'isDir': True,
                            u'parent': u'9823749',
                            u'title': u"People's Instinctive Travels And The Paths Of Rhythm"},
                           {u'artist': u'A Tribe Called Quest',
                            u'coverArt': u'289347293',
                            u'id': u'3894723934',
                            u'isDir': True,
                            u'parent': u'9832942',
                            u'title': u'The Anthology'},
                           {u'artist': u'A Tribe Called Quest',
                            u'coverArt': u'923847923',
                            u'id': u'29834729',
                            u'isDir': True,
                            u'parent': u'2934872893',
                            u'title': u'The Love Movement'},
                           {u'artist': u'A Tribe Called Quest',
                            u'coverArt': u'9238742893',
                            u'id': u'238947293',
                            u'isDir': True,
                            u'parent': u'9432878492',
                            u'title': u'The Low End Theory'}],
                u'id': u'329847293',
                u'name': u'A Tribe Called Quest'},
         u'status': u'ok',
         u'version': u'1.5.0',
         u'xmlns': u'http://subsonic.org/restapi'}
        """
        method_name = "getMusicDirectory"
        view_name = "%s.view" % method_name

        req = self._get_request(view_name, {"id": mid})
        res = self._do_info_req(req)
        return self._validate_response(res, models.MusicDirectoryResponse)

    def search(
        self,
        artist: str | None = None,
        album: str | None = None,
        title: str | None = None,
        any: str | None = None,
        count: int = 20,
        offset: int = 0,
        newer_than: int | None = None,
    ) -> models.SearchResult2Response:
        """
        since: 1.0.0

        DEPRECATED SINCE API 1.4.0!  USE search2() INSTEAD!

        Returns a listing of files matching the given search criteria.
        Supports paging with offset

        artist:str      Search for artist
        album:str       Search for album
        title:str       Search for title of song
        any:str         Search all fields
        count:int       Max number of results to return [default: 20]
        offset:int      Search result offset.  For paging [default: 0]
        newer_than:int   Return matches newer than this timestamp
        """
        if artist == album == title == any == None:
            raise ArgumentError("Invalid search.  You must supply search criteria")
        method_name = "search"
        view_name = "%s.view" % method_name

        q = self._get_query_dict(
            {
                "artist": artist,
                "album": album,
                "title": title,
                "any": any,
                "count": count,
                "offset": offset,
                "newerThan": self._ts_2_milli(newer_than),
            }
        )

        req = self._get_request(view_name, q)
        res = self._do_info_req(req)
        return self._validate_response(res, models.SearchResult2Response)

    def search2(
        self,
        query: str,
        artist_count: int = 20,
        artist_offset: int = 0,
        album_count: int = 20,
        album_offset: int = 0,
        song_count: int = 20,
        song_offset: int = 0,
        music_folder_id: int | None = None,
    ) -> models.SearchResult2Response:
        """
        since: 1.4.0

        Returns albums, artists and songs matching the given search criteria.
        Supports paging through the result.

        query:str           The search query
        artist_count:int     Max number of artists to return [default: 20]
        artist_offset:int    Search offset for artists (for paging) [default: 0]
        album_count:int      Max number of albums to return [default: 20]
        album_offset:int     Search offset for albums (for paging) [default: 0]
        song_count:int       Max number of songs to return [default: 20]
        song_offset:int      Search offset for songs (for paging) [default: 0]
        music_folder_id:int   Only return results from the music folder
                            with the given ID. See getMusicFolders

        Returns a dict like the following:

        {u'searchResult2': {u'album': [{u'artist': u'A Tribe Called Quest',
                                u'coverArt': u'289347',
                                u'id': u'32487298',
                                u'isDir': True,
                                u'parent': u'98374289',
                                u'title': u'The Love Movement'}],
                    u'artist': [{u'id': u'2947839',
                                 u'name': u'A Tribe Called Quest'},
                                {u'id': u'239847239',
                                 u'name': u'Tribe'}],
                    u'song': [{u'album': u'Beats, Rhymes And Life',
                               u'artist': u'A Tribe Called Quest',
                               u'bitRate': 224,
                               u'contentType': u'audio/mpeg',
                               u'coverArt': u'329847',
                               u'duration': 148,
                               u'genre': u'default',
                               u'id': u'3928472893',
                               u'isDir': False,
                               u'isVideo': False,
                               u'parent': u'23984728394',
                               u'path': u'A Tribe Called Quest/Beats, Rhymes And Life/A Tribe Called Quest - Beats, Rhymes And Life - 03 - Motivators.mp3',
                               u'size': 4171913,
                               u'suffix': u'mp3',
                               u'title': u'Motivators',
                               u'track': 3}]},
         u'status': u'ok',
         u'version': u'1.5.0',
         u'xmlns': u'http://subsonic.org/restapi'}
        """
        method_name = "search2"
        view_name = "%s.view" % method_name

        q = self._get_query_dict(
            {
                "query": query,
                "artistCount": artist_count,
                "artistOffset": artist_offset,
                "albumCount": album_count,
                "albumOffset": album_offset,
                "songCount": song_count,
                "songOffset": song_offset,
                "musicFolderId": music_folder_id,
            }
        )

        req = self._get_request(view_name, q)
        res = self._do_info_req(req)
        return self._validate_response(res, models.SearchResult2Response)

    def search3(
        self,
        query: str,
        artist_count: int = 20,
        artist_offset: int = 0,
        album_count: int = 20,
        album_offset: int = 0,
        song_count: int = 20,
        song_offset: int = 0,
        music_folder_id: int | None = None,
    ) -> models.SearchResult3Response:
        """
        since: 1.8.0

        Works the same way as search2, but uses ID3 tags for
        organization

        query:str           The search query
        artist_count:int     Max number of artists to return [default: 20]
        artist_offset:int    Search offset for artists (for paging) [default: 0]
        album_count:int      Max number of albums to return [default: 20]
        album_offset:int     Search offset for albums (for paging) [default: 0]
        song_count:int       Max number of songs to return [default: 20]
        song_offset:int      Search offset for songs (for paging) [default: 0]
        music_folder_id:int   Only return results from the music folder
                            with the given ID. See getMusicFolders

        Returns a dict like the following (search for "Tune Yards":
            {u'searchResult3': {u'album': [{u'artist': u'Tune-Yards',
                                u'artistId': 1,
                                u'coverArt': u'al-7',
                                u'created': u'2012-01-30T12:35:33',
                                u'duration': 3229,
                                u'id': 7,
                                u'name': u'Bird-Brains',
                                u'songCount': 13},
                               {u'artist': u'Tune-Yards',
                                u'artistId': 1,
                                u'coverArt': u'al-8',
                                u'created': u'2011-03-22T15:08:00',
                                u'duration': 2531,
                                u'id': 8,
                                u'name': u'W H O K I L L',
                                u'songCount': 10}],
                    u'artist': {u'albumCount': 2,
                                u'coverArt': u'ar-1',
                                u'id': 1,
                                u'name': u'Tune-Yards'},
                    u'song': [{u'album': u'Bird-Brains',
                               u'albumId': 7,
                               u'artist': u'Tune-Yards',
                               u'artistId': 1,
                               u'bitRate': 160,
                               u'contentType': u'audio/mpeg',
                               u'coverArt': 105,
                               u'created': u'2012-01-30T12:35:33',
                               u'duration': 328,
                               u'genre': u'Lo-Fi',
                               u'id': 107,
                               u'isDir': False,
                               u'isVideo': False,
                               u'parent': 105,
                               u'path': u'Tune Yards/Bird-Brains/10-tune-yards-fiya.mp3',
                               u'size': 6588498,
                               u'suffix': u'mp3',
                               u'title': u'Fiya',
                               u'track': 10,
                               u'type': u'music',
                               u'year': 2009}]},

             u'status': u'ok',
             u'version': u'1.5.0',
             u'xmlns': u'http://subsonic.org/restapi'}
        """
        method_name = "search3"
        view_name = "%s.view" % method_name

        q = self._get_query_dict(
            {
                "query": query,
                "artistCount": artist_count,
                "artistOffset": artist_offset,
                "albumCount": album_count,
                "albumOffset": album_offset,
                "songCount": song_count,
                "songOffset": song_offset,
                "musicFolderId": music_folder_id,
            }
        )

        req = self._get_request(view_name, q)
        res = self._do_info_req(req)
        return self._validate_response(res, models.SearchResult3Response)

    def get_playlists(self, username: str | None = None) -> models.PlaylistsResponse:
        """
        since: 1.0.0

        Returns the ID and name of all saved playlists
        The "username" option was added in 1.8.0.

        username:str        If specified, return playlists for this user
                            rather than for the authenticated user.  The
                            authenticated user must have admin role
                            if this parameter is used

        Returns a dict like the following:

        {u'playlists': {u'playlist': [{u'id': u'62656174732e6d3375',
                               u'name': u'beats'},
                              {u'id': u'766172696574792e6d3375',
                               u'name': u'variety'}]},
         u'status': u'ok',
         u'version': u'1.5.0',
         u'xmlns': u'http://subsonic.org/restapi'}
        """
        method_name = "getPlaylists"
        view_name = "%s.view" % method_name

        q = self._get_query_dict({"username": username})

        req = self._get_request(view_name, q)
        res = self._do_info_req(req)
        return self._validate_response(res, models.PlaylistsResponse)

    def get_playlist(self, pid: str) -> models.PlaylistResponse:
        """
        since: 1.0.0

        Returns a listing of files in a saved playlist

        id:str      The ID of the playlist as returned in getPlaylists()

        Returns a dict like the following:

        {u'playlist': {u'entry': {u'album': u'The Essential Bob Dylan',
                          u'artist': u'Bob Dylan',
                          u'bitRate': 32,
                          u'contentType': u'audio/mpeg',
                          u'coverArt': u'2983478293',
                          u'duration': 984,
                          u'genre': u'Classic Rock',
                          u'id': u'982739428',
                          u'isDir': False,
                          u'isVideo': False,
                          u'parent': u'98327428974',
                          u'path': u"Bob Dylan/Essential Bob Dylan Disc 1/Bob Dylan - The Essential Bob Dylan - 03 - The Times They Are A-Changin'.mp3",
                          u'size': 3921899,
                          u'suffix': u'mp3',
                          u'title': u"The Times They Are A-Changin'",
                          u'track': 3},
               u'id': u'44796c616e2e6d3375',
               u'name': u'Dylan'},
         u'status': u'ok',
         u'version': u'1.5.0',
         u'xmlns': u'http://subsonic.org/restapi'}
        """
        method_name = "getPlaylist"
        view_name = "%s.view" % method_name

        req = self._get_request(view_name, {"id": pid})
        res = self._do_info_req(req)
        return self._validate_response(res, models.PlaylistResponse)

    def create_playlist(
        self,
        playlist_id: str | None = None,
        name: str | None = None,
        song_ids: list[str] | None = None,
    ) -> models.StatusResponse:
        """
        since: 1.2.0

        Creates OR updates a playlist.  If updating the list, the
        playlist_id is required.  If creating a list, the name is required.

        playlist_id:str      The ID of the playlist to UPDATE
        name:str            The name of the playlist to CREATE
        song_ids:list        The list of songIds to populate the list with in
                            either create or update mode.  Note that this
                            list will replace the existing list if updating

        Returns a dict like the following:

        {u'status': u'ok',
         u'version': u'1.5.0',
         u'xmlns': u'http://subsonic.org/restapi'}
        """
        if song_ids is None:
            song_ids = []

        method_name = "createPlaylist"
        view_name = "%s.view" % method_name

        if playlist_id is name is None:
            raise ArgumentError("You must supply either a playlist_id or a name")
        if playlist_id is not None and name is not None:
            raise ArgumentError(
                "You can only supply either a playlist_id OR a name, not both"
            )

        q = self._get_query_dict({"playlistId": playlist_id, "name": name})

        req = self._get_request_with_list(view_name, "songId", song_ids, q)
        res = self._do_info_req(req)
        return self._validate_response(res, models.StatusResponse)

    def delete_playlist(self, pid: str) -> models.StatusResponse:
        """
        since: 1.2.0

        Deletes a saved playlist

        pid:str     ID of the playlist to delete, as obtained by getPlaylists

        Returns a dict like the following:

        """
        method_name = "deletePlaylist"
        view_name = "%s.view" % method_name

        req = self._get_request(view_name, {"id": pid})
        res = self._do_info_req(req)
        return self._validate_response(res, models.StatusResponse)

    def download(self, sid: str) -> BinaryIO:
        """
        since: 1.0.0

        Downloads a given music file.

        sid:str     The ID of the music file to download.

        Returns the file-like object for reading or raises an exception
        on error
        """
        method_name = "download"
        view_name = "%s.view" % method_name

        req = self._get_request(view_name, {"id": sid})
        res = self._do_bin_req(req)
        if isinstance(res, dict):
            self._check_status(res)
        return res

    def stream(
        self,
        sid: str,
        max_bit_rate: int = 0,
        tformat: str | None = None,
        time_offset: int | None = None,
        size: str | None = None,
        estimate_content_length: bool = False,
        converted: bool = False,
    ) -> BinaryIO:
        """
        since: 1.0.0

        Downloads a given music file.

        sid:str         The ID of the music file to download.
        max_bit_rate:int  (since: 1.2.0) If specified, the server will
                        attempt to limit the bitrate to this value, in
                        kilobits per second. If set to zero (default), no limit
                        is imposed. Legal values are: 0, 32, 40, 48, 56, 64,
                        80, 96, 112, 128, 160, 192, 224, 256 and 320.
        tformat:str     (since: 1.6.0) Specifies the target format
                        (e.g. "mp3" or "flv") in case there are multiple
                        applicable transcodings (since: 1.9.0) You can use
                        the special value "raw" to disable transcoding
        time_offset:int  (since: 1.6.0) Only applicable to video
                        streaming.  Start the stream at the given
                        offset (in seconds) into the video
        size:str        (since: 1.6.0) The requested video size in
                        WxH, for instance 640x480
        estimate_content_length:bool  (since: 1.8.0) If set to True,
                                    the HTTP Content-Length header
                                    will be set to an estimated
                                    value for trancoded media
        converted:bool  (since: 1.14.0) Only applicable to video streaming.
                        Subsonic can optimize videos for streaming by
                        converting them to MP4. If a conversion exists for
                        the video in question, then setting this parameter
                        to "true" will cause the converted video to be
                        returned instead of the original.

        Returns the file-like object for reading or raises an exception
        on error
        """
        method_name = "stream"
        view_name = "%s.view" % method_name

        q = self._get_query_dict(
            {
                "id": sid,
                "maxBitRate": max_bit_rate,
                "format": tformat,
                "timeOffset": time_offset,
                "size": size,
                "estimateContentLength": estimate_content_length,
                "converted": converted,
            }
        )

        req = self._get_request(view_name, q)
        res = self._do_bin_req(req)
        if isinstance(res, dict):
            self._check_status(res)
        return res

    def get_cover_art(self, aid: str, size: int | None = None) -> BinaryIO:
        """
        since: 1.0.0

        Returns a cover art image

        aid:str     ID string for the cover art image to download
        size:int    If specified, scale image to this size

        Returns the file-like object for reading or raises an exception
        on error
        """
        method_name = "getCoverArt"
        view_name = "%s.view" % method_name

        q = self._get_query_dict({"id": aid, "size": size})

        req = self._get_request(view_name, q)
        res = self._do_bin_req(req)
        if isinstance(res, dict):
            self._check_status(res)
        return res

    def scrobble(
        self, sid: str, submission: bool = True, listen_time: int | None = None
    ) -> models.StatusResponse:
        """
        since: 1.5.0

        "Scrobbles" a given music file on last.fm.  Requires that the user
        has set this up.

        Since 1.8.0 you may specify multiple id (and optionally time)
        parameters to scrobble multiple files.

        Since 1.11.0 this method will also update the play count and
        last played timestamp for the song and album. It will also make
        the song appear in the "Now playing" page in the web app, and
        appear in the list of songs returned by getNowPlaying

        sid:str             The ID of the file to scrobble
        submission:bool     Whether this is a "submission" or a "now playing"
                            notification
        listen_time:int      (Since 1.8.0) The time (unix timestamp) at
                            which the song was listened to.

        Returns a dict like the following:

        {u'status': u'ok',
         u'version': u'1.5.0',
         u'xmlns': u'http://subsonic.org/restapi'}
        """
        method_name = "scrobble"
        view_name = "%s.view" % method_name

        q = self._get_query_dict(
            {"id": sid, "submission": submission, "time": self._ts_2_milli(listen_time)}
        )

        req = self._get_request(view_name, q)
        res = self._do_info_req(req)
        return self._validate_response(res, models.StatusResponse)

    def change_password(self, username: str, password: str) -> models.StatusResponse:
        """
        since: 1.1.0

        Changes the password of an existing Subsonic user.  Note that the
        user performing this must have admin privileges

        username:str        The username whose password is being changed
        password:str        The new password of the user

        Returns a dict like the following:

        {u'status': u'ok',
         u'version': u'1.5.0',
         u'xmlns': u'http://subsonic.org/restapi'}
        """
        method_name = "changePassword"
        view_name = "%s.view" % method_name
        hex_pass = "enc:%s" % self._hex_enc(password)

        # There seems to be an issue with some subsonic implementations
        # not recognizing the "enc:" precursor to the encoded password and
        # encodes the whole "enc:<hex>" as the password.  Weird.
        # q = {'username': username, 'password': hex_pass.lower()}
        q = {"username": username, "password": password}

        req = self._get_request(view_name, q)
        res = self._do_info_req(req)
        return self._validate_response(res, models.StatusResponse)

    def get_user(self, username: str) -> models.UserResponse:
        """
        since: 1.3.0

        Get details about a given user, including which auth roles it has.
        Can be used to enable/disable certain features in the client, such
        as jukebox control

        username:str        The username to retrieve.  You can only retrieve
                            your own user unless you have admin privs.

        Returns a dict like the following:

        {u'status': u'ok',
         u'user': {u'adminRole': False,
               u'commentRole': False,
               u'coverArtRole': False,
               u'downloadRole': True,
               u'jukeboxRole': False,
               u'playlistRole': True,
               u'podcastRole': False,
               u'settingsRole': True,
               u'streamRole': True,
               u'uploadRole': True,
               u'username': u'test'},
         u'version': u'1.5.0',
         u'xmlns': u'http://subsonic.org/restapi'}
        """
        method_name = "getUser"
        view_name = "%s.view" % method_name

        q = {"username": username}

        req = self._get_request(view_name, q)
        res = self._do_info_req(req)
        return self._validate_response(res, models.UserResponse)

    def get_users(self) -> models.UsersResponse:
        """
        since 1.8.0

        Gets a list of users

        returns a dict like the following

        {u'status': u'ok',
         u'users': {u'user': [{u'adminRole': True,
                   u'commentRole': True,
                   u'coverArtRole': True,
                   u'downloadRole': True,
                   u'jukeboxRole': True,
                   u'playlistRole': True,
                   u'podcastRole': True,
                   u'scrobblingEnabled': True,
                   u'settingsRole': True,
                   u'shareRole': True,
                   u'streamRole': True,
                   u'uploadRole': True,
                   u'username': u'user1'},
                   ...
                   ...
                   ]},
         u'version': u'1.10.2',
         u'xmlns': u'http://subsonic.org/restapi'}
        """
        method_name = "getUsers"
        view_name = "%s.view" % method_name

        req = self._get_request(view_name)
        res = self._do_info_req(req)
        return self._validate_response(res, models.UsersResponse)

    def create_user(
        self,
        username: str,
        password: str,
        email: str,
        ldap_authenticated: bool = False,
        admin_role: bool = False,
        settings_role: bool = True,
        stream_role: bool = True,
        jukebox_role: bool = False,
        download_role: bool = False,
        upload_role: bool = False,
        playlist_role: bool = False,
        cover_art_role: bool = False,
        comment_role: bool = False,
        podcast_role: bool = False,
        share_role: bool = False,
        video_conversion_role: bool = False,
        music_folder_id: int | None = None,
    ) -> models.StatusResponse:
        """
        since: 1.1.0

        Creates a new subsonic user, using the parameters defined.  See the
        documentation at http://subsonic.org for more info on all the roles.

        username:str        The username of the new user
        password:str        The password for the new user
        email:str           The email of the new user
        <For info on the boolean roles, see http://subsonic.org for more info>
        music_folder_id:int   These are the only folders the user has access to

        Returns a dict like the following:

        {u'status': u'ok',
         u'version': u'1.5.0',
         u'xmlns': u'http://subsonic.org/restapi'}
        """
        method_name = "createUser"
        view_name = "%s.view" % method_name
        hex_pass = "enc:%s" % self._hex_enc(password)

        q = self._get_query_dict(
            {
                "username": username,
                "password": hex_pass,
                "email": email,
                "ldapAuthenticated": ldap_authenticated,
                "adminRole": admin_role,
                "settingsRole": settings_role,
                "streamRole": stream_role,
                "jukeboxRole": jukebox_role,
                "downloadRole": download_role,
                "uploadRole": upload_role,
                "playlistRole": playlist_role,
                "coverArtRole": cover_art_role,
                "commentRole": comment_role,
                "podcastRole": podcast_role,
                "shareRole": share_role,
                "videoConversionRole": video_conversion_role,
                "musicFolderId": music_folder_id,
            }
        )

        req = self._get_request(view_name, q)
        res = self._do_info_req(req)
        return self._validate_response(res, models.StatusResponse)

    def update_user(
        self,
        username: str,
        password: str | None = None,
        email: str | None = None,
        ldap_authenticated: bool = False,
        admin_role: bool = False,
        settings_role: bool = True,
        stream_role: bool = True,
        jukebox_role: bool = False,
        download_role: bool = False,
        upload_role: bool = False,
        playlist_role: bool = False,
        cover_art_role: bool = False,
        comment_role: bool = False,
        podcast_role: bool = False,
        share_role: bool = False,
        video_conversion_role: bool = False,
        music_folder_id: int | None = None,
        max_bit_rate: int = 0,
    ) -> models.StatusResponse:
        """
        since 1.10.1

        Modifies an existing Subsonic user.

        username:str        The username of the user to update.
        music_folder_id:int   Only return results from the music folder
                            with the given ID. See getMusicFolders
        max_bit_rate:int      The max bitrate for the user.  0 is unlimited

        All other args are the same as create user and you can update
        whatever item you wish to update for the given username.

        Returns a dict like the following:

        {u'status': u'ok',
         u'version': u'1.5.0',
         u'xmlns': u'http://subsonic.org/restapi'}
        """
        method_name = "updateUser"
        view_name = "%s.view" % method_name
        if password is not None:
            password = "enc:%s" % self._hex_enc(password)
        q = self._get_query_dict(
            {
                "username": username,
                "password": password,
                "email": email,
                "ldapAuthenticated": ldap_authenticated,
                "adminRole": admin_role,
                "settingsRole": settings_role,
                "streamRole": stream_role,
                "jukeboxRole": jukebox_role,
                "downloadRole": download_role,
                "uploadRole": upload_role,
                "playlistRole": playlist_role,
                "coverArtRole": cover_art_role,
                "commentRole": comment_role,
                "podcastRole": podcast_role,
                "shareRole": share_role,
                "videoConversionRole": video_conversion_role,
                "musicFolderId": music_folder_id,
                "maxBitRate": max_bit_rate,
            }
        )
        req = self._get_request(view_name, q)
        res = self._do_info_req(req)
        return self._validate_response(res, models.StatusResponse)

    def delete_user(self, username: str) -> models.StatusResponse:
        """
        since: 1.3.0

        Deletes an existing Subsonic user.  Of course, you must have admin
        rights for this.

        username:str        The username of the user to delete

        Returns a dict like the following:

        {u'status': u'ok',
         u'version': u'1.5.0',
         u'xmlns': u'http://subsonic.org/restapi'}
        """
        method_name = "deleteUser"
        view_name = "%s.view" % method_name

        q = {"username": username}

        req = self._get_request(view_name, q)
        res = self._do_info_req(req)
        return self._validate_response(res, models.StatusResponse)

    def get_chat_messages(
        self, since: int | None = None
    ) -> models.ChatMessagesResponse:
        """
        since: 1.2.0

        Returns the current visible (non-expired) chat messages.

        since:int       Only return messages newer than this timestamp

        NOTE: All times returned are in MILLISECONDS since the Epoch, not
              seconds!

        Returns a dict like the following:
        {u'chatMessages': {u'chatMessage': {u'message': u'testing 123',
                                            u'time': 1303411919872L,
                                            u'username': u'admin'}},
         u'status': u'ok',
         u'version': u'1.5.0',
         u'xmlns': u'http://subsonic.org/restapi'}
        """
        method_name = "getChatMessages"
        view_name = "%s.view" % method_name

        q = {"since": self._ts_2_milli(since)}

        req = self._get_request(view_name, q)
        res = self._do_info_req(req)
        return self._validate_response(res, models.ChatMessagesResponse)

    def add_chat_message(self, message: str) -> models.StatusResponse:
        """
        since: 1.2.0

        Adds a message to the chat log

        message:str     The message to add

        Returns a dict like the following:

        {u'status': u'ok',
         u'version': u'1.5.0',
         u'xmlns': u'http://subsonic.org/restapi'}
        """
        method_name = "addChatMessage"
        view_name = "%s.view" % method_name

        q = {"message": message}

        req = self._get_request(view_name, q)
        res = self._do_info_req(req)
        return self._validate_response(res, models.StatusResponse)

    def get_album_list(
        self,
        ltype: str,
        size: int = 10,
        offset: int = 0,
        from_year: int | None = None,
        to_year: int | None = None,
        genre: str | None = None,
        music_folder_id: int | None = None,
    ) -> models.AlbumListResponse:
        """
        since: 1.2.0

        Returns a list of random, newest, highest rated etc. albums.
        Similar to the album lists on the home page of the Subsonic
        web interface

        ltype:str       The list type. Must be one of the following: random,
                        newest, highest, frequent, recent,
                        (since 1.8.0 -> )starred, alphabeticalByName,
                        alphabeticalByArtist
                        Since 1.10.1 you can use byYear and byGenre to
                        list albums in a given year range or genre.
        size:int        The number of albums to return. Max 500
        offset:int      The list offset. Use for paging. Max 5000
        from_year:int    If you specify the ltype as "byYear", you *must*
                        specify from_year
        to_year:int      If you specify the ltype as "byYear", you *must*
                        specify to_year
        genre:str       The name of the genre e.g. "Rock".  You must specify
                        genre if you set the ltype to "byGenre"
        music_folder_id:str   Only return albums in the music folder with
                            the given ID. See getMusicFolders()

        Returns a dict like the following:

        {u'albumList': {u'album': [{u'artist': u'Hank Williams',
                            u'id': u'3264928374',
                            u'isDir': True,
                            u'parent': u'9238479283',
                            u'title': u'The Original Singles Collection...Plus'},
                           {u'artist': u'Freundeskreis',
                            u'coverArt': u'9823749823',
                            u'id': u'23492834',
                            u'isDir': True,
                            u'parent': u'9827492374',
                            u'title': u'Quadratur des Kreises'}]},
         u'status': u'ok',
         u'version': u'1.5.0',
         u'xmlns': u'http://subsonic.org/restapi'}
        """
        method_name = "getAlbumList"
        view_name = "%s.view" % method_name

        q = self._get_query_dict(
            {
                "type": ltype,
                "size": size,
                "offset": offset,
                "fromYear": from_year,
                "toYear": to_year,
                "genre": genre,
                "musicFolderId": music_folder_id,
            }
        )

        req = self._get_request(view_name, q)
        res = self._do_info_req(req)
        return self._validate_response(res, models.AlbumListResponse)

    def get_album_list2(
        self,
        ltype: str,
        size: int = 10,
        offset: int = 0,
        from_year: int | None = None,
        to_year: int | None = None,
        genre: str | None = None,
    ) -> models.AlbumList2Response:
        """
        since 1.8.0

        Returns a list of random, newest, highest rated etc. albums.
        This is similar to getAlbumList, but uses ID3 tags for
        organization

        ltype:str       The list type. Must be one of the following: random,
                        newest, highest, frequent, recent,
                        (since 1.8.0 -> )starred, alphabeticalByName,
                        alphabeticalByArtist
                        Since 1.10.1 you can use byYear and byGenre to
                        list albums in a given year range or genre.
        size:int        The number of albums to return. Max 500
        offset:int      The list offset. Use for paging. Max 5000
        from_year:int    If you specify the ltype as "byYear", you *must*
                        specify from_year
        to_year:int      If you specify the ltype as "byYear", you *must*
                        specify to_year
        genre:str       The name of the genre e.g. "Rock".  You must specify
                        genre if you set the ltype to "byGenre"

        Returns a dict like the following:
           {u'albumList2': {u'album': [{u'artist': u'Massive Attack',
                             u'artistId': 0,
                             u'coverArt': u'al-0',
                             u'created': u'2009-08-28T10:00:44',
                             u'duration': 3762,
                             u'id': 0,
                             u'name': u'100th Window',
                             u'songCount': 9},
                            {u'artist': u'Massive Attack',
                             u'artistId': 0,
                             u'coverArt': u'al-5',
                             u'created': u'2003-11-03T22:00:00',
                             u'duration': 2715,
                             u'id': 5,
                             u'name': u'Blue Lines',
                             u'songCount': 9}]},
            u'status': u'ok',
            u'version': u'1.8.0',
            u'xmlns': u'http://subsonic.org/restapi'}
        """
        method_name = "getAlbumList2"
        view_name = "%s.view" % method_name

        q = self._get_query_dict(
            {
                "type": ltype,
                "size": size,
                "offset": offset,
                "fromYear": from_year,
                "toYear": to_year,
                "genre": genre,
            }
        )

        req = self._get_request(view_name, q)
        res = self._do_info_req(req)
        return self._validate_response(res, models.AlbumList2Response)

    def get_random_songs(
        self,
        size: int = 10,
        genre: str | None = None,
        from_year: int | None = None,
        to_year: int | None = None,
        music_folder_id: int | None = None,
    ) -> models.RandomSongsResponse:
        """
        since 1.2.0

        Returns random songs matching the given criteria

        size:int            The max number of songs to return. Max 500
        genre:str           Only return songs from this genre
        from_year:int        Only return songs after or in this year
        to_year:int          Only return songs before or in this year
        music_folder_id:str   Only return songs in the music folder with the
                            given ID.  See getMusicFolders

        Returns a dict like the following:

        {u'randomSongs': {u'song': [{u'album': u'1998 EP - Airbag (How Am I Driving)',
                             u'artist': u'Radiohead',
                             u'bitRate': 320,
                             u'contentType': u'audio/mpeg',
                             u'duration': 129,
                             u'id': u'9284728934',
                             u'isDir': False,
                             u'isVideo': False,
                             u'parent': u'983249823',
                             u'path': u'Radiohead/1998 EP - Airbag (How Am I Driving)/06 - Melatonin.mp3',
                             u'size': 5177469,
                             u'suffix': u'mp3',
                             u'title': u'Melatonin'},
                            {u'album': u'Mezmerize',
                             u'artist': u'System Of A Down',
                             u'bitRate': 214,
                             u'contentType': u'audio/mpeg',
                             u'coverArt': u'23849372894',
                             u'duration': 176,
                             u'id': u'28937492834',
                             u'isDir': False,
                             u'isVideo': False,
                             u'parent': u'92837492837',
                             u'path': u'System Of A Down/Mesmerize/10 - System Of A Down - Old School Hollywood.mp3',
                             u'size': 4751360,
                             u'suffix': u'mp3',
                             u'title': u'Old School Hollywood',
                             u'track': 10}]},
         u'status': u'ok',
         u'version': u'1.5.0',
         u'xmlns': u'http://subsonic.org/restapi'}
        """
        method_name = "getRandomSongs"
        view_name = "%s.view" % method_name

        q = self._get_query_dict(
            {
                "size": size,
                "genre": genre,
                "fromYear": from_year,
                "toYear": to_year,
                "musicFolderId": music_folder_id,
            }
        )

        req = self._get_request(view_name, q)
        res = self._do_info_req(req)
        return self._validate_response(res, models.RandomSongsResponse)

    def get_lyrics(
        self, artist: str | None = None, title: str | None = None
    ) -> models.LyricsResponse:
        """
        since: 1.2.0

        Searches for and returns lyrics for a given song

        artist:str      The artist name
        title:str       The song title

        Returns a dict like the following for
        getLyrics('Bob Dylan', 'Blowin in the wind'):

        {u'lyrics': {u'artist': u'Bob Dylan',
             u'content': u"How many roads must a man walk down<snip>",
             u'title': u"Blowin' in the Wind"},
         u'status': u'ok',
         u'version': u'1.5.0',
         u'xmlns': u'http://subsonic.org/restapi'}
        """
        method_name = "getLyrics"
        view_name = "%s.view" % method_name

        q = self._get_query_dict({"artist": artist, "title": title})

        req = self._get_request(view_name, q)
        res = self._do_info_req(req)
        return self._validate_response(res, models.LyricsResponse)

    def jukebox_control(
        self,
        action: str,
        index: int | None = None,
        sids: list[str] | None = None,
        gain: float | None = None,
        offset: int | None = None,
    ) -> models.StatusResponse:
        """
        since: 1.2.0

        NOTE: Some options were added as of API version 1.7.0

        Controls the jukebox, i.e., playback directly on the server's
        audio hardware. Note: The user must be authorized to control
        the jukebox

        action:str      The operation to perform. Must be one of: get,
                        start, stop, skip, add, clear, remove, shuffle,
                        setGain, status (added in API 1.7.0),
                        set (added in API 1.7.0)
        index:int       Used by skip and remove. Zero-based index of the
                        song to skip to or remove.
        sids:str        Used by "add" and "set". ID of song to add to the
                        jukebox playlist. Use multiple id parameters to
                        add many songs in the same request.  Whether you
                        are passing one song or many into this, this
                        parameter MUST be a list
        gain:float      Used by setGain to control the playback volume.
                        A float value between 0.0 and 1.0
        offset:int      (added in API 1.7.0) Used by "skip".  Start playing
                        this many seconds into the track.
        """
        if sids is None:
            sids = []

        method_name = "jukeboxControl"
        view_name = "%s.view" % method_name

        q = self._get_query_dict(
            {"action": action, "index": index, "gain": gain, "offset": offset}
        )

        req = None
        if action == "add":
            # We have to deal with the sids
            # if not (isinstance(sids, list) or isinstance(sids, tuple)):
            #     raise ArgumentError(
            #         'If you are adding songs, "sids" must be a list or tuple!'
            #     )
            req = self._get_request_with_list(view_name, "id", sids, q)
        else:
            req = self._get_request(view_name, q)
        res = self._do_info_req(req)
        return self._validate_response(res, models.StatusResponse)

    def get_podcasts(
        self, inc_episodes: bool = True, pid: str | None = None
    ) -> models.PodcastsResponse:
        """
        since: 1.6.0

        Returns all podcast channels the server subscribes to and their
        episodes.

        inc_episodes:bool    (since: 1.9.0) Whether to include Podcast
                            episodes in the returned result.
        pid:str             (since: 1.9.0) If specified, only return
                            the Podcast channel with this ID.

        Returns a dict like the following:
        {u'status': u'ok',
         u'version': u'1.6.0',
         u'xmlns': u'http://subsonic.org/restapi',
         u'podcasts': {u'channel': {u'description': u"Dr Chris Smith...",
                            u'episode': [{u'album': u'Dr Karl and the Naked Scientist',
                                          u'artist': u'BBC Radio 5 live',
                                          u'bitRate': 64,
                                          u'contentType': u'audio/mpeg',
                                          u'coverArt': u'2f6f7074',
                                          u'description': u'Dr Karl answers all your science related questions.',
                                          u'duration': 2902,
                                          u'genre': u'Podcast',
                                          u'id': 0,
                                          u'isDir': False,
                                          u'isVideo': False,
                                          u'parent': u'2f6f70742f737562736f6e69632f706f6463617374732f4472204b61726c20616e6420746865204e616b656420536369656e74697374',
                                          u'publishDate': u'2011-08-17 22:06:00.0',
                                          u'size': 23313059,
                                          u'status': u'completed',
                                          u'streamId': u'2f6f70742f737562736f6e69632f706f6463617374732f4472204b61726c20616e6420746865204e616b656420536369656e746973742f64726b61726c5f32303131303831382d30343036612e6d7033',
                                          u'suffix': u'mp3',
                                          u'title': u'DrKarl: Peppermints, Chillies & Receptors',
                                          u'year': 2011},
                                         {u'description': u'which is warmer, a bath with bubbles in it or one without?  Just one of the stranger science stories tackled this week by Dr Chris Smith and the Naked Scientists!',
                                          u'id': 1,
                                          u'publishDate': u'2011-08-14 21:05:00.0',
                                          u'status': u'skipped',
                                          u'title': u'DrKarl: how many bubbles in your bath? 15 AUG 11'},
                                          ...
                                         {u'description': u'Dr Karl joins Rhod to answer all your science questions',
                                          u'id': 9,
                                          u'publishDate': u'2011-07-06 22:12:00.0',
                                          u'status': u'skipped',
                                          u'title': u'DrKarl: 8 Jul 11 The Strange Sound of the MRI Scanner'}],
                            u'id': 0,
                            u'status': u'completed',
                            u'title': u'Dr Karl and the Naked Scientist',
                            u'url': u'http://downloads.bbc.co.uk/podcasts/fivelive/drkarl/rss.xml'}}
        }

        See also: http://subsonic.svn.sourceforge.net/viewvc/subsonic/trunk/subsonic-main/src/main/webapp/xsd/podcasts_example_1.xml?view=markup
        """
        method_name = "getPodcasts"
        view_name = "%s.view" % method_name

        q = self._get_query_dict({"includeEpisodes": inc_episodes, "id": pid})
        req = self._get_request(view_name, q)
        res = self._do_info_req(req)
        return self._validate_response(res, models.PodcastsResponse)

    def get_shares(self) -> models.SharesResponse:
        """
        since: 1.6.0

        Returns information about shared media this user is allowed to manage

        Note that entry can be either a single dict or a list of dicts

        Returns a dict like the following:

        {u'status': u'ok',
         u'version': u'1.6.0',
         u'xmlns': u'http://subsonic.org/restapi',
         u'shares': {u'share': [
             {u'created': u'2011-08-18T10:01:35',
              u'entry': {u'artist': u'Alice In Chains',
                         u'coverArt': u'2f66696c65732f6d7033732f412d4d2f416c69636520496e20436861696e732f416c69636520496e20436861696e732f636f7665722e6a7067',
                         u'id': u'2f66696c65732f6d7033732f412d4d2f416c69636520496e20436861696e732f416c69636520496e20436861696e73',
                         u'isDir': True,
                         u'parent': u'2f66696c65732f6d7033732f412d4d2f416c69636520496e20436861696e73',
                         u'title': u'Alice In Chains'},
              u'expires': u'2012-08-18T10:01:35',
              u'id': 0,
              u'url': u'http://crustymonkey.subsonic.org/share/BuLbF',
              u'username': u'admin',
              u'visitCount': 0
             }]}
        }
        """
        method_name = "getShares"
        view_name = "%s.view" % method_name

        req = self._get_request(view_name)
        res = self._do_info_req(req)
        return self._validate_response(res, models.SharesResponse)

    def create_share(
        self,
        shids: list[str] | None = None,
        description: str | None = None,
        expires: int | None = None,
    ) -> models.StatusResponse:
        """
        since: 1.6.0

        Creates a public URL that can be used by anyone to stream music
        or video from the Subsonic server. The URL is short and suitable
        for posting on Facebook, Twitter etc. Note: The user must be
        authorized to share (see Settings > Users > User is allowed to
        share files with anyone).

        shids:list[str]              A list of ids of songs, albums or videos
                                    to share.
        description:str             A description that will be displayed to
                                    people visiting the shared media
                                    (optional).
        expires:float               A timestamp pertaining to the time at
                                    which this should expire (optional)

        This returns a structure like you would get back from getShares()
        containing just your new share.
        """
        if shids is None:
            shids = []

        method_name = "createShare"
        view_name = "%s.view" % method_name

        q = self._get_query_dict(
            {"description": description, "expires": self._ts_2_milli(expires)}
        )
        req = self._get_request_with_list(view_name, "id", shids, q)
        res = self._do_info_req(req)
        return self._validate_response(res, models.StatusResponse)

    def update_share(
        self, shid: str, description: str | None = None, expires: int | None = None
    ) -> models.StatusResponse:
        """
        since: 1.6.0

        Updates the description and/or expiration date for an existing share

        shid:str            The id of the share to update
        description:str     The new description for the share (optional).
        expires:float       The new timestamp for the expiration time of this
                            share (optional).
        """
        method_name = "updateShare"
        view_name = "%s.view" % method_name

        q = self._get_query_dict(
            {
                "id": shid,
                "description": description,
                "expires": self._ts_2_milli(expires),
            }
        )

        req = self._get_request(view_name, q)
        res = self._do_info_req(req)
        return self._validate_response(res, models.StatusResponse)

    def delete_share(self, shid: str) -> models.StatusResponse:
        """
        since: 1.6.0

        Deletes an existing share

        shid:str        The id of the share to delete

        Returns a standard response dict
        """
        method_name = "deleteShare"
        view_name = "%s.view" % method_name

        q = self._get_query_dict({"id": shid})

        req = self._get_request(view_name, q)
        res = self._do_info_req(req)
        return self._validate_response(res, models.StatusResponse)

    def set_rating(self, id: str, rating: int) -> models.StatusResponse:
        """
        since: 1.6.0

        Sets the rating for a music file

        id:str          The id of the item (song/artist/album) to rate
        rating:int      The rating between 1 and 5 (inclusive), or 0 to remove
                        the rating

        Returns a standard response dict
        """
        method_name = "setRating"
        view_name = "%s.view" % method_name

        try:
            rating = int(rating)
        except ValueError:
            raise ArgumentError(
                "Rating must be an integer between 0 and 5: %r" % rating
            )
        if rating < 0 or rating > 5:
            raise ArgumentError(
                "Rating must be an integer between 0 and 5: %r" % rating
            )

        q = self._get_query_dict({"id": id, "rating": rating})

        req = self._get_request(view_name, q)
        res = self._do_info_req(req)
        return self._validate_response(res, models.StatusResponse)

    def get_artists(self, music_folder_id: int | None = None) -> models.ArtistsResponse:
        """
        since 1.8.0

        Similar to getIndexes(), but this method uses the ID3 tags to
        determine the artist

        Returns a dict like the following:
            {u'artists': {u'index': [{u'artist': {u'albumCount': 7,
                                      u'coverArt': u'ar-0',
                                      u'id': 0,
                                      u'name': u'Massive Attack'},
                          u'name': u'M'},
                         {u'artist': {u'albumCount': 2,
                                      u'coverArt': u'ar-1',
                                      u'id': 1,
                                      u'name': u'Tune-Yards'},
                          u'name': u'T'}]},
             u'status': u'ok',
             u'version': u'1.8.0',
             u'xmlns': u'http://subsonic.org/restapi'}
        """
        method_name = "getArtists"
        view_name = "%s.view" % method_name

        req = self._get_request(view_name)
        res = self._do_info_req(req)
        return self._validate_response(res, models.ArtistsResponse)

    def get_artist(self, id: str) -> models.ArtistResponse:
        """
        since 1.8.0

        Returns the info (albums) for an artist.  This method uses
        the ID3 tags for organization

        id:str      The artist ID

        Returns a dict like the following:

           {u'artist': {u'album': [{u'artist': u'Tune-Yards',
                         u'artistId': 1,
                         u'coverArt': u'al-7',
                         u'created': u'2012-01-30T12:35:33',
                         u'duration': 3229,
                         u'id': 7,
                         u'name': u'Bird-Brains',
                         u'songCount': 13},
                        {u'artist': u'Tune-Yards',
                         u'artistId': 1,
                         u'coverArt': u'al-8',
                         u'created': u'2011-03-22T15:08:00',
                         u'duration': 2531,
                         u'id': 8,
                         u'name': u'W H O K I L L',
                         u'songCount': 10}],
             u'albumCount': 2,
             u'coverArt': u'ar-1',
             u'id': 1,
             u'name': u'Tune-Yards'},
            u'status': u'ok',
            u'version': u'1.8.0',
            u'xmlns': u'http://subsonic.org/restapi'}
        """
        method_name = "getArtist"
        view_name = "%s.view" % method_name

        q = self._get_query_dict({"id": id})

        req = self._get_request(view_name, q)
        res = self._do_info_req(req)
        return self._validate_response(res, models.ArtistResponse)

    def get_album(self, id: str) -> models.AlbumResponse:
        """
        since 1.8.0

        Returns the info and songs for an album.  This method uses
        the ID3 tags for organization

        id:str      The album ID

        Returns a dict like the following:

           {u'album': {u'artist': u'Massive Attack',
            u'artistId': 0,
            u'coverArt': u'al-0',
            u'created': u'2009-08-28T10:00:44',
            u'duration': 3762,
            u'id': 0,
            u'name': u'100th Window',
            u'song': [{u'album': u'100th Window',
                       u'albumId': 0,
                       u'artist': u'Massive Attack',
                       u'artistId': 0,
                       u'bitRate': 192,
                       u'contentType': u'audio/mpeg',
                       u'coverArt': 2,
                       u'created': u'2009-08-28T10:00:57',
                       u'duration': 341,
                       u'genre': u'Rock',
                       u'id': 14,
                       u'isDir': False,
                       u'isVideo': False,
                       u'parent': 2,
                       u'path': u'Massive Attack/100th Window/01 - Future Proof.mp3',
                       u'size': 8184445,
                       u'suffix': u'mp3',
                       u'title': u'Future Proof',
                       u'track': 1,
                       u'type': u'music',
                       u'year': 2003}],
              u'songCount': 9},
            u'status': u'ok',
            u'version': u'1.8.0',
            u'xmlns': u'http://subsonic.org/restapi'}
        """
        method_name = "getAlbum"
        view_name = "%s.view" % method_name

        q = self._get_query_dict({"id": id})

        req = self._get_request(view_name, q)
        res = self._do_info_req(req)
        return self._validate_response(res, models.AlbumResponse)

    def get_song(self, id: str) -> models.SongResponse:
        """
        since 1.8.0

        Returns the info for a song.  This method uses the ID3
        tags for organization

        id:str      The song ID

        Returns a dict like the following:
            {u'song': {u'album': u'W H O K I L L',
               u'albumId': 8,
               u'artist': u'Tune-Yards',
               u'artistId': 1,
               u'bitRate': 320,
               u'contentType': u'audio/mpeg',
               u'coverArt': 106,
               u'created': u'2011-03-22T15:08:00',
               u'discNumber': 1,
               u'duration': 192,
               u'genre': u'Indie Rock',
               u'id': 120,
               u'isDir': False,
               u'isVideo': False,
               u'parent': 106,
               u'path': u'Tune Yards/Who Kill/10 Killa.mp3',
               u'size': 7692656,
               u'suffix': u'mp3',
               u'title': u'Killa',
               u'track': 10,
               u'type': u'music',
               u'year': 2011},
             u'status': u'ok',
             u'version': u'1.8.0',
             u'xmlns': u'http://subsonic.org/restapi'}
        """
        method_name = "getSong"
        view_name = "%s.view" % method_name

        q = self._get_query_dict({"id": id})

        req = self._get_request(view_name, q)
        res = self._do_info_req(req)
        return self._validate_response(res, models.SongResponse)

    def get_videos(self) -> models.VideosResponse:
        """
        since 1.8.0

        Returns all video files

        Returns a dict like the following:
            {u'status': u'ok',
             u'version': u'1.8.0',
             u'videos': {u'video': {u'bitRate': 384,
                        u'contentType': u'video/x-matroska',
                        u'created': u'2012-08-26T13:36:44',
                        u'duration': 1301,
                        u'id': 130,
                        u'isDir': False,
                        u'isVideo': True,
                        u'path': u'South Park - 16x07 - Cartman Finds Love.mkv',
                        u'size': 287309613,
                        u'suffix': u'mkv',
                        u'title': u'South Park - 16x07 - Cartman Finds Love',
                        u'transcodedContentType': u'video/x-flv',
                        u'transcodedSuffix': u'flv'}},
             u'xmlns': u'http://subsonic.org/restapi'}
        """
        method_name = "getVideos"
        view_name = "%s.view" % method_name

        req = self._get_request(view_name)
        res = self._do_info_req(req)
        return self._validate_response(res, models.VideosResponse)

    def get_starred(self, music_folder_id: int | None = None) -> models.StarredResponse:
        """
        since 1.8.0

        music_folder_id:int   Only return results from the music folder
                            with the given ID. See getMusicFolders

        Returns starred songs, albums and artists

        Returns a dict like the following:
            {u'starred': {u'album': {u'album': u'Bird-Brains',
                         u'artist': u'Tune-Yards',
                         u'coverArt': 105,
                         u'created': u'2012-01-30T13:16:58',
                         u'id': 105,
                         u'isDir': True,
                         u'parent': 104,
                         u'starred': u'2012-08-26T13:18:34',
                         u'title': u'Bird-Brains'},
              u'song': [{u'album': u'Mezzanine',
                         u'albumId': 4,
                         u'artist': u'Massive Attack',
                         u'artistId': 0,
                         u'bitRate': 256,
                         u'contentType': u'audio/mpeg',
                         u'coverArt': 6,
                         u'created': u'2009-06-15T07:48:28',
                         u'duration': 298,
                         u'genre': u'Dub',
                         u'id': 72,
                         u'isDir': False,
                         u'isVideo': False,
                         u'parent': 6,
                         u'path': u'Massive Attack/Mezzanine/Massive Attack_02_mezzanine.mp3',
                         u'size': 9564160,
                         u'starred': u'2012-08-26T13:19:26',
                         u'suffix': u'mp3',
                         u'title': u'Risingson',
                         u'track': 2,
                         u'type': u'music'},
                        {u'album': u'Mezzanine',
                         u'albumId': 4,
                         u'artist': u'Massive Attack',
                         u'artistId': 0,
                         u'bitRate': 256,
                         u'contentType': u'audio/mpeg',
                         u'coverArt': 6,
                         u'created': u'2009-06-15T07:48:25',
                         u'duration': 380,
                         u'genre': u'Dub',
                         u'id': 71,
                         u'isDir': False,
                         u'isVideo': False,
                         u'parent': 6,
                         u'path': u'Massive Attack/Mezzanine/Massive Attack_01_mezzanine.mp3',
                         u'size': 12179456,
                         u'starred': u'2012-08-26T13:19:03',
                         u'suffix': u'mp3',
                         u'title': u'Angel',
                         u'track': 1,
                         u'type': u'music'}]},
             u'status': u'ok',
             u'version': u'1.8.0',
             u'xmlns': u'http://subsonic.org/restapi'}
        """
        method_name = "getStarred"
        view_name = "%s.view" % method_name

        q = {}
        if music_folder_id:
            q["musicFolderId"] = music_folder_id

        req = self._get_request(view_name, q)
        res = self._do_info_req(req)
        return self._validate_response(res, models.StarredResponse)

    def get_starred2(
        self, music_folder_id: int | None = None
    ) -> models.Starred2Response:
        """
        since 1.8.0

        music_folder_id:int   Only return results from the music folder
                            with the given ID. See getMusicFolders

        Returns starred songs, albums and artists like getStarred(),
        but this uses ID3 tags for organization

        Returns a dict like the following:

            **See the output from getStarred()**
        """
        method_name = "getStarred2"
        view_name = "%s.view" % method_name

        q = {}
        if music_folder_id:
            q["musicFolderId"] = music_folder_id

        req = self._get_request(view_name, q)
        res = self._do_info_req(req)
        return self._validate_response(res, models.Starred2Response)

    def update_playlist(
        self,
        lid: str,
        name: str | None = None,
        comment: str | None = None,
        song_ids_to_add: list[str] | None = None,
        song_indexes_to_remove: list[int] | None = None,
    ) -> models.StatusResponse:
        """
        since 1.8.0

        Updates a playlist.  Only the owner of a playlist is allowed to
        update it.

        lid:str                 The playlist id
        name:str                The human readable name of the playlist
        comment:str             The playlist comment
        song_ids_to_add:list       A list of song IDs to add to the playlist
        song_indexes_to_remove:list    Remove the songs at the
                                    0 BASED INDEXED POSITIONS in the
                                    playlist, NOT the song ids.  Note that
                                    this is always a list.

        Returns a normal status response dict
        """
        if song_ids_to_add is None:
            song_ids_to_add = []
        if song_indexes_to_remove is None:
            song_indexes_to_remove = []

        method_name = "updatePlaylist"
        view_name = "%s.view" % method_name

        q = self._get_query_dict({"playlistId": lid, "name": name, "comment": comment})
        if not isinstance(song_ids_to_add, list) or isinstance(song_ids_to_add, tuple):
            song_ids_to_add = [song_ids_to_add]
        if not isinstance(song_indexes_to_remove, list) or isinstance(
            song_indexes_to_remove, tuple
        ):
            song_indexes_to_remove = [song_indexes_to_remove]
        list_map = {
            "songIdToAdd": song_ids_to_add,
            "songIndexToRemove": song_indexes_to_remove,
        }
        req = self._get_request_with_lists(view_name, list_map, q)
        res = self._do_info_req(req)
        return self._validate_response(res, models.StatusResponse)

    def get_avatar(self, username: str) -> BinaryIO | None:
        """
        since 1.8.0

        Returns the avatar for a user or None if the avatar does not exist

        username:str    The user to retrieve the avatar for

        Returns the file-like object for reading or raises an exception
        on error
        """
        method_name = "getAvatar"
        view_name = "%s.view" % method_name

        q = {"username": username}

        req = self._get_request(view_name, q)
        try:
            res = self._do_bin_req(req)
        except urllib.error.HTTPError:
            # Avatar is not set/does not exist, return None
            return None
        if isinstance(res, dict):
            self._check_status(res)
        return res

    def star(
        self,
        sids: list[str] | None = None,
        album_ids: list[str] | None = None,
        artist_ids: list[str] | None = None,
    ) -> models.StatusResponse:
        """
        since 1.8.0

        Attaches a star to songs, albums or artists

        sids:list       A list of song IDs to star
        album_ids:list   A list of album IDs to star.  Use this rather than
                        "sids" if the client access the media collection
                        according to ID3 tags rather than file
                        structure
        artist_ids:list  The ID of an artist to star.  Use this rather
                        than sids if the client access the media
                        collection according to ID3 tags rather
                        than file structure

        Returns a normal status response dict
        """
        if sids is None:
            sids = []
        if album_ids is None:
            album_ids = []
        if artist_ids is None:
            artist_ids = []

        method_name = "star"
        view_name = "%s.view" % method_name

        # if not isinstance(sids, list) or isinstance(sids, tuple):
        #     sids = [sids]
        # if not isinstance(album_ids, list) or isinstance(album_ids, tuple):
        #     album_ids = [album_ids]
        # if not isinstance(artist_ids, list) or isinstance(artist_ids, tuple):
        #     artist_ids = [artist_ids]
        list_map = {"id": sids, "albumId": album_ids, "artistId": artist_ids}
        req = self._get_request_with_lists(view_name, list_map)
        res = self._do_info_req(req)
        return self._validate_response(res, models.StatusResponse)

    def unstar(
        self,
        sids: list[str] | None = None,
        album_ids: list[str] | None = None,
        artist_ids: list[str] | None = None,
    ) -> models.StatusResponse:
        """
        since 1.8.0

        Removes a star to songs, albums or artists.  Basically, the
        same as star in reverse

        sids:list       A list of song IDs to star
        album_ids:list   A list of album IDs to star.  Use this rather than
                        "sids" if the client access the media collection
                        according to ID3 tags rather than file
                        structure
        artist_ids:list  The ID of an artist to star.  Use this rather
                        than sids if the client access the media
                        collection according to ID3 tags rather
                        than file structure

        Returns a normal status response dict
        """
        if sids is None:
            sids = []
        if album_ids is None:
            album_ids = []
        if artist_ids is None:
            artist_ids = []

        method_name = "unstar"
        view_name = "%s.view" % method_name

        if not isinstance(sids, list) or isinstance(sids, tuple):
            sids = [sids]
        if not isinstance(album_ids, list) or isinstance(album_ids, tuple):
            album_ids = [album_ids]
        if not isinstance(artist_ids, list) or isinstance(artist_ids, tuple):
            artist_ids = [artist_ids]
        list_map = {"id": sids, "albumId": album_ids, "artistId": artist_ids}
        req = self._get_request_with_lists(view_name, list_map)
        res = self._do_info_req(req)
        return self._validate_response(res, models.StatusResponse)

    def get_genres(self) -> models.GenresResponse:
        """
        since 1.9.0

        Returns all genres
        """
        method_name = "getGenres"
        view_name = "%s.view" % method_name

        req = self._get_request(view_name)
        res = self._do_info_req(req)
        return self._validate_response(res, models.GenresResponse)

    def get_songs_by_genre(
        self,
        genre: str,
        count: int = 10,
        offset: int = 0,
        music_folder_id: int | None = None,
    ) -> models.SongsByGenreResponse:
        """
        since 1.9.0

        Returns songs in a given genre

        genre:str       The genre, as returned by getGenres()
        count:int       The maximum number of songs to return.  Max is 500
                        default: 10
        offset:int      The offset if you are paging.  default: 0
        music_folder_id:int   Only return results from the music folder
                            with the given ID. See getMusicFolders
        """
        method_name = "getSongsByGenre"
        view_name = "%s.view" % method_name

        q = self._get_query_dict(
            {
                "genre": genre,
                "count": count,
                "offset": offset,
                "musicFolderId": music_folder_id,
            }
        )

        req = self._get_request(view_name, q)
        res = self._do_info_req(req)
        return self._validate_response(res, models.SongsByGenreResponse)

    def hls(self, mid: str, bitrate: str | None = None) -> str | None:
        """
        since 1.8.0

        Creates an HTTP live streaming playlist for streaming video or
        audio HLS is a streaming protocol implemented by Apple and
        works by breaking the overall stream into a sequence of small
        HTTP-based file downloads. It's supported by iOS and newer
        versions of Android. This method also supports adaptive
        bitrate streaming, see the bitRate parameter.

        mid:str     The ID of the media to stream
        bitrate:str If specified, the server will attempt to limit the
                    bitrate to this value, in kilobits per second. If
                    this parameter is specified more than once, the
                    server will create a variant playlist, suitable
                    for adaptive bitrate streaming. The playlist will
                    support streaming at all the specified bitrates.
                    The server will automatically choose video dimensions
                    that are suitable for the given bitrates.
                    (since: 1.9.0) you may explicitly request a certain
                    width (480) and height (360) like so:
                    bitRate=1000@480x360

        Returns the raw m3u8 file as a string
        """
        method_name = "hls"
        view_name = "%s.view" % method_name

        q = self._get_query_dict({"id": mid, "bitrate": bitrate})
        req = self._get_request(view_name, q)
        try:
            res = self._do_bin_req(req)
        except urllib.error.HTTPError:
            # Avatar is not set/does not exist, return None
            return None
        if isinstance(res, dict):
            self._check_status(res)
        return res.read()

    def refresh_podcasts(self) -> models.StatusResponse:
        """
        since: 1.9.0

        Tells the server to check for new Podcast episodes. Note: The user
        must be authorized for Podcast administration
        """
        method_name = "refreshPodcasts"
        view_name = "%s.view" % method_name

        req = self._get_request(view_name)
        res = self._do_info_req(req)
        return self._validate_response(res, models.StatusResponse)

    def create_podcast_channel(self, url: str) -> models.StatusResponse:
        """
        since: 1.9.0

        Adds a new Podcast channel.  Note: The user must be authorized
        for Podcast administration

        url:str     The URL of the Podcast to add
        """
        method_name = "createPodcastChannel"
        view_name = "%s.view" % method_name

        q = {"url": url}

        req = self._get_request(view_name, q)
        res = self._do_info_req(req)
        return self._validate_response(res, models.StatusResponse)

    def delete_podcast_channel(self, pid: str) -> models.StatusResponse:
        """
        since: 1.9.0

        Deletes a Podcast channel.  Note: The user must be authorized
        for Podcast administration

        pid:str         The ID of the Podcast channel to delete
        """
        method_name = "deletePodcastChannel"
        view_name = "%s.view" % method_name

        q = {"id": pid}

        req = self._get_request(view_name, q)
        res = self._do_info_req(req)
        return self._validate_response(res, models.StatusResponse)

    def delete_podcast_episode(self, pid: str) -> models.StatusResponse:
        """
        since: 1.9.0

        Deletes a Podcast episode.  Note: The user must be authorized
        for Podcast administration

        pid:str         The ID of the Podcast episode to delete
        """
        method_name = "deletePodcastEpisode"
        view_name = "%s.view" % method_name

        q = {"id": pid}

        req = self._get_request(view_name, q)
        res = self._do_info_req(req)
        return self._validate_response(res, models.StatusResponse)

    def download_podcast_episode(self, pid: str) -> models.StatusResponse:
        """
        since: 1.9.0

        Tells the server to start downloading a given Podcast episode.
        Note: The user must be authorized for Podcast administration

        pid:str         The ID of the Podcast episode to download
        """
        method_name = "downloadPodcastEpisode"
        view_name = "%s.view" % method_name

        q = {"id": pid}

        req = self._get_request(view_name, q)
        res = self._do_info_req(req)
        self._check_status(res)
        return res

    def get_internet_radio_stations(self) -> models.InternetRadioStationsResponse:
        """
        since: 1.9.0

        Returns all internet radio stations
        """
        method_name = "getInternetRadioStations"
        view_name = "%s.view" % method_name

        req = self._get_request(view_name)
        res = self._do_info_req(req)
        return self._validate_response(res, models.InternetRadioStationsResponse)

    def create_internet_radio_station(
        self, stream_url: str, name: str, homepage_url: str | None = None
    ) -> models.StatusResponse:
        """
        since 1.16.0

        Create an internet radio station

        stream_url:str   The stream URL for the station
        name:str        The user-defined name for the station
        homepage_url:str The homepage URL for the station
        """
        method_name = "createInternetRadioStation"
        view_name = "{}.view".format(method_name)

        q = self._get_query_dict(
            {"streamUrl": stream_url, "name": name, "homepageUrl": homepage_url}
        )

        req = self._get_request(view_name, q)
        res = self._do_info_req(req)
        return self._validate_response(res, models.StatusResponse)

    def update_internet_radio_station(
        self, iid: str, stream_url: str, name: str, homepage_url: str | None = None
    ) -> models.StatusResponse:
        """
        since 1.16.0

        Create an internet radio station

        iid:str         The ID for the station
        stream_url:str   The stream URL for the station
        name:str        The user-defined name for the station
        homepage_url:str The homepage URL for the station
        """
        method_name = "updateInternetRadioStation"
        view_name = "{}.view".format(method_name)

        q = self._get_query_dict(
            {
                "id": iid,
                "streamUrl": stream_url,
                "name": name,
                "homepageUrl": homepage_url,
            }
        )

        req = self._get_request(view_name, q)
        res = self._do_info_req(req)
        return self._validate_response(res, models.StatusResponse)

    def delete_internet_radio_station(self, iid: str) -> models.StatusResponse:
        """
        since 1.16.0

        Create an internet radio station

        iid:str         The ID for the station
        """
        method_name = "deleteInternetRadioStation"
        view_name = "{}.view".format(method_name)

        q = {"id": iid}

        req = self._get_request(view_name, q)
        res = self._do_info_req(req)
        return self._validate_response(res, models.StatusResponse)

    def get_bookmarks(self) -> models.BookmarksResponse:
        """
        since: 1.9.0

        Returns all bookmarks for this user.  A bookmark is a position
        within a media file
        """
        method_name = "getBookmarks"
        view_name = "%s.view" % method_name

        req = self._get_request(view_name)
        res = self._do_info_req(req)
        return self._validate_response(res, models.BookmarksResponse)

    def create_bookmark(
        self, mid: str, position: int, comment: str | None = None
    ) -> models.StatusResponse:
        """
        since: 1.9.0

        Creates or updates a bookmark (position within a media file).
        Bookmarks are personal and not visible to other users

        mid:str         The ID of the media file to bookmark.  If a bookmark
                        already exists for this file, it will be overwritten
        position:int    The position (in milliseconds) within the media file
        comment:str     A user-defined comment
        """
        method_name = "createBookmark"
        view_name = "%s.view" % method_name

        q = self._get_query_dict({"id": mid, "position": position, "comment": comment})

        req = self._get_request(view_name, q)
        res = self._do_info_req(req)
        return self._validate_response(res, models.StatusResponse)

    def delete_bookmark(self, mid: str) -> models.StatusResponse:
        """
        since: 1.9.0

        Deletes the bookmark for a given file

        mid:str     The ID of the media file to delete the bookmark from.
                    Other users' bookmarks are not affected
        """
        method_name = "deleteBookmark"
        view_name = "%s.view" % method_name

        q = {"id": mid}

        req = self._get_request(view_name, q)
        res = self._do_info_req(req)
        return self._validate_response(res, models.StatusResponse)

    def get_artist_info(
        self, aid: str, count: int = 20, include_not_present: bool = False
    ) -> models.ArtistInfoResponse:
        """
        since: 1.11.0

        Returns artist info with biography, image URLS and similar artists
        using data from last.fm

        aid:str                 The ID of the artist, album or song
        count:int               The max number of similar artists to return
        include_not_present:bool  Whether to return artists that are not
                                present in the media library
        """
        method_name = "getArtistInfo"
        view_name = "%s.view" % method_name

        q = {"id": aid, "count": count, "includeNotPresent": include_not_present}

        req = self._get_request(view_name, q)
        res = self._do_info_req(req)
        return self._validate_response(res, models.ArtistInfoResponse)

    def get_artist_info2(
        self, aid: str, count: int = 20, include_not_present: bool = False
    ) -> models.ArtistInfo2Response:
        """
        since: 1.11.0

        Similar to getArtistInfo(), but organizes music according to ID3 tags

        aid:str                 The ID of the artist, album or song
        count:int               The max number of similar artists to return
        include_not_present:bool  Whether to return artists that are not
                                present in the media library
        """
        method_name = "getArtistInfo2"
        view_name = "%s.view" % method_name

        q = {"id": aid, "count": count, "includeNotPresent": include_not_present}

        req = self._get_request(view_name, q)
        res = self._do_info_req(req)
        return self._validate_response(res, models.ArtistInfo2Response)

    def get_similar_songs(
        self, iid: str, count: int = 50
    ) -> models.SimilarSongsResponse:
        """
        since 1.11.0

        Returns a random collection of songs from the given artist and
        similar artists, using data from last.fm. Typically used for
        artist radio features.

        iid:str     The artist, album, or song ID
        count:int   Max number of songs to return
        """
        method_name = "getSimilarSongs"
        view_name = "%s.view" % method_name

        q = {"id": iid, "count": count}

        req = self._get_request(view_name, q)
        res = self._do_info_req(req)
        return self._validate_response(res, models.SimilarSongsResponse)

    def get_similar_songs2(
        self, iid: str, count: int = 50
    ) -> models.SimilarSongs2Response:
        """
        since 1.11.0

        Similar to getSimilarSongs(), but organizes music according to
        ID3 tags

        iid:str     The artist, album, or song ID
        count:int   Max number of songs to return
        """
        method_name = "getSimilarSongs2"
        view_name = "%s.view" % method_name

        q = {"id": iid, "count": count}

        req = self._get_request(view_name, q)
        res = self._do_info_req(req)
        return self._validate_response(res, models.SimilarSongs2Response)

    def save_play_queue(
        self, qids: list[str], current: str | None = None, position: int | None = None
    ) -> models.StatusResponse:
        """
        since 1.12.0

        qid:list[int]       The list of song ids in the play queue
        current:int         The id of the current playing song
        position:int        The position, in milliseconds, within the current
                            playing song

        Saves the state of the play queue for this user. This includes
        the tracks in the play queue, the currently playing track, and
        the position within this track. Typically used to allow a user to
        move between different clients/apps while retaining the same play
        queue (for instance when listening to an audio book).
        """
        method_name = "savePlayQueue"
        view_name = "%s.view" % method_name

        if not isinstance(qids, (tuple, list)):
            qids = [qids]

        q = self._get_query_dict({"current": current, "position": position})

        req = self._get_request_with_lists(view_name, {"id": qids}, q)
        res = self._do_info_req(req)
        return self._validate_response(res, models.StatusResponse)

    def get_play_queue(self) -> models.PlayQueueResponse:
        """
        since 1.12.0

        Returns the state of the play queue for this user (as set by
        savePlayQueue). This includes the tracks in the play queue,
        the currently playing track, and the position within this track.
        Typically used to allow a user to move between different
        clients/apps while retaining the same play queue (for instance
        when listening to an audio book).
        """
        method_name = "getPlayQueue"
        view_name = "%s.view" % method_name

        req = self._get_request(view_name)
        res = self._do_info_req(req)
        return self._validate_response(res, models.PlayQueueResponse)

    def get_top_songs(self, artist: str, count: int = 50) -> models.TopSongsResponse:
        """
        since 1.13.0

        Returns the top songs for a given artist

        artist:str      The artist to get songs for
        count:int       The number of songs to return
        """
        method_name = "getTopSongs"
        view_name = "%s.view" % method_name

        q = {"artist": artist, "count": count}

        req = self._get_request(view_name, q)
        res = self._do_info_req(req)
        return self._validate_response(res, models.TopSongsResponse)

    def get_newest_podcasts(self, count: int = 20) -> models.PodcastsResponse:
        """
        since 1.13.0

        Returns the most recently published Podcast episodes

        count:int       The number of episodes to return
        """
        method_name = "getNewestPodcasts"
        view_name = "%s.view" % method_name

        q = {"count": count}

        req = self._get_request(view_name, q)
        res = self._do_info_req(req)
        return self._validate_response(res, models.PodcastsResponse)

    def scan_media_folders(self):
        """
        This is not an officially supported method of the API

        Same as selecting 'Settings' > 'Scan media folders now' with
        Subsonic web GUI

        Returns True if refresh successful, False otherwise
        """
        view_name = "scanNow"
        return self._unsupported_api_function(method_name)

    def cleanup_database(self):
        """
        This is not an officially supported method of the API

        Same as selecting 'Settings' > 'Clean-up Database' with Subsonic
        web GUI

        Returns True if cleanup initiated successfully, False otherwise

        Subsonic stores information about all media files ever encountered.
        By cleaning up the database, information about files that are
        no longer in your media collection is permanently removed.
        """
        view_name = "expunge"
        return self._unsupported_api_function(method_name)

    def get_video_info(self, vid: str) -> models.VideoInfoResponse:
        """
        since 1.14.0

        Returns details for a video, including information about available
        audio tracks, subtitles (captions) and conversions.

        vid:int     The video ID
        """
        method_name = "getVideoInfo"
        view_name = "%s.view" % method_name

        q = {"id": int(vid)}
        req = self._get_request(view_name, q)
        res = self._do_info_req(req)
        return self._validate_response(res, models.VideoInfoResponse)

    def get_album_info(self, aid: str) -> models.AlbumInfoResponse:
        """
        since 1.14.0

        Returns the album notes, image URLs, etc., using data from last.fm

        aid:int     The album ID
        """
        method_name = "getAlbumInfo"
        view_name = "%s.view" % method_name

        q = {"id": aid}
        req = self._get_request(view_name, q)
        res = self._do_info_req(req)
        return self._validate_response(res, models.AlbumInfoResponse)

    def get_album_info2(self, aid: str) -> models.AlbumInfoResponse:
        """
        since 1.14.0

        Same as getAlbumInfo, but uses ID3 tags

        aid:int     The album ID
        """
        method_name = "getAlbumInfo2"
        view_name = "%s.view" % method_name

        q = {"id": aid}
        req = self._get_request(view_name, q)
        res = self._do_info_req(req)
        return self._validate_response(res, models.AlbumInfoResponse)

    def get_captions(self, vid: str, fmt: str | None = None) -> BinaryIO:
        """
        since 1.14.0

        Returns captions (subtitles) for a video.  Use getVideoInfo for a list
        of captions.

        vid:int         The ID of the video
        fmt:str         Preferred captions format ("srt" or "vtt")
        """
        method_name = "getCaptions"
        view_name = "%s.view" % method_name

        q = self._get_query_dict({"id": int(vid), "format": fmt})
        req = self._get_request(view_name, q)
        res = self._do_info_req(req)
        self._check_status(res)
        return res

    def _unsupported_api_function(self, method_name: str) -> bool:
        """
        base function to call unsupported API methods

        Returns True if refresh successful, False otherwise
        :rtype : boolean
        """
        baseMethod = "musicFolderSettings"
        view_name = "%s.view" % baseMethod

        url = "%s:%d/%s/%s?%s" % (
            self._base_url,
            self._port,
            self._separate_server_path(),
            view_name,
            method_name,
        )
        req = urllib.request.Request(url)
        res = self._opener.open(req)
        res_msg = res.msg.lower()
        return res_msg == "ok"

    #
    # Private internal methods
    #
    def _get_opener(
        self, username: str | None, passwd: str | None
    ) -> urllib.request.OpenerDirector:
        return urllib.request.build_opener()

    def _get_query_dict(
        self, d: dict[str, str | int | float | None]
    ) -> dict[str, str | int | float | None]:
        """
        Given a dictionary, it cleans out all the values set to None
        """
        for k, v in list(d.items()):
            if v is None:
                del d[k]
        return d

    def _get_base_qdict(self) -> dict[str, str | None]:
        qdict = {
            "f": "json",
            "v": self._api_version,
            "c": self._app_name,
            "u": self._username,
        }

        if self._legacy_auth:
            qdict["p"] = "enc:%s" % self._hex_enc(self._raw_pass)
        else:
            if self._raw_pass:
                salt = self._get_salt()
                token = md5((self._raw_pass + salt).encode("utf-8")).hexdigest()
            else:
                salt = self._salt
                token = self._token
            qdict.update(
                {
                    "s": salt,
                    "t": token,
                }
            )

        return qdict

    def _get_request(
        self,
        view_name: str,
        query: Mapping[str, str | int | float | None] | None = None,
    ) -> urllib.request.Request:
        if query is None:
            query = {}

        qdict = self._get_base_qdict()
        qdict.update(query)
        url = "%s:%d/%s/%s" % (self._base_url, self._port, self._server_path, view_name)
        req = urllib.request.Request(url, urlencode(qdict).encode("utf-8"))

        if self._use_get:
            url += "?%s" % urlencode(qdict)
            req = urllib.request.Request(url)

        if self._user_agent:
            req.add_header("User-Agent", self._user_agent)

        return req

    def _get_request_with_list(
        self,
        view_name: str,
        listName: str,
        alist: list[str],
        query: dict[str, Any] | None = None,
    ) -> urllib.request.Request:
        """
        Like _get_request, but allows appending a number of items with the
        same key (listName).  This bypasses the limitation of urlencode()
        """
        if query is None:
            query = {}

        qdict = self._get_base_qdict()
        qdict.update(query)
        url = "%s:%d/%s/%s" % (self._base_url, self._port, self._server_path, view_name)
        data = StringIO()
        data.write(urlencode(qdict))
        for i in alist:
            data.write("&%s" % urlencode({listName: i}))
        req = urllib.request.Request(url, data.getvalue().encode("utf-8"))

        if self._use_get:
            url += "?%s" % data.getvalue()
            req = urllib2.Request(url)

        if self._user_agent:
            req.add_header("User-Agent", self._user_agent)

        return req

    def _get_request_with_lists(
        self,
        view_name: str,
        list_map: dict[str, list[str | int]],
        query: dict[str, Any] | None = None,
    ) -> urllib.request.Request:
        """
        Like _get_request_with_list(), but you must pass a dictionary
        that maps the listName to the list.  This allows for multiple
        list parameters to be used, like in updatePlaylist()

        view_name:str        The name of the view
        list_map:dict        A mapping of listName to a list of entries
        query:dict          The normal query dict
        """
        if query is None:
            query = {}

        qdict = self._get_base_qdict()
        qdict.update(query)
        url = "%s:%d/%s/%s" % (self._base_url, self._port, self._server_path, view_name)
        data = StringIO()
        data.write(urlencode(qdict))
        for k, l in list_map.items():
            for i in l:
                data.write("&%s" % urlencode({k: i}))
        req = urllib.request.Request(url, data.getvalue().encode("utf-8"))

        if self._use_get:
            url += "?%s" % data.getvalue()
            req = urllib2.Request(url)

        if self._user_agent:
            req.add_header("User-Agent", self._user_agent)

        return req

    def _do_info_req(self, req: urllib.request.Request) -> dict[str, Any]:
        # Returns a parsed dictionary version of the result
        res = self._opener.open(req)
        dres = json.loads(res.read().decode("utf-8"))
        return dres["subsonic-response"]

    def _do_bin_req(self, req: urllib.request.Request) -> dict[str, Any] | BinaryIO:
        res = self._opener.open(req)
        info = res.info()
        if hasattr(info, "getheader"):
            contType = info.getheader("Content-Type")
        else:
            contType = info.get("Content-Type")

        if contType:
            if contType.startswith("text/html") or contType.startswith(
                "application/json"
            ):
                dres = json.loads(res.read())
                return dres["subsonic-response"]
        return res

    def _check_status(self, result: dict[str, Any]) -> bool:
        if result["status"] == "ok":
            return True
        elif result["status"] == "failed":
            exc = get_exc_by_code(result["error"]["code"])
            raise exc(result["error"]["message"])
        else:
            return False

    def _validate_response[T: BaseModel](
        self, result: object, model_class: type[T]
    ) -> T:
        """
        Validates a Subsonic API response using Pydantic models

        result:dict         The raw response dictionary from _do_info_req
        model_class:type    The Pydantic model class to validate against

        Returns a validated Pydantic model instance
        Raises an exception if the status is failed
        """
        self._check_status(result)
        return model_class.model_validate(result)

    def _hex_enc(self, raw: str) -> str:
        """
        Returns a "hex encoded" string per the Subsonic api docs

        raw:str     The string to hex encode
        """
        ret = ""
        for c in raw:
            ret += "%02X" % ord(c)
        return ret

    def _ts_2_milli(self, ts: int | None) -> int | None:
        """
        For whatever reason, Subsonic uses timestamps in milliseconds since
        the unix epoch.  I have no idea what need there is of this precision,
        but this will just multiply the timestamp times 1000 and return the int
        """
        if ts is None:
            return None
        return int(ts * 1000)

    def _separate_server_path(self) -> str:
        """
        separate REST portion of URL from base server path.
        """
        return urllib.parse.splithost(self._server_path)[1].split("/")[0]

    def _fix_last_modified(
        self, data: dict[str, Any] | list[Any] | tuple[Any, ...]
    ) -> None:
        """
        This will recursively walk through a data structure and look for
        a dict key/value pair where the key is "lastModified" and change
        the shitty java millisecond timestamp to a real unix timestamp
        of SECONDS since the unix epoch.  JAVA SUCKS!
        """
        if isinstance(data, dict):
            for k, v in list(data.items()):
                if k == "lastModified":
                    data[k] = int(v) / 1000.0
                    return
                elif isinstance(v, (tuple, list, dict)):
                    return self._fix_last_modified(v)
        elif isinstance(data, (list, tuple)):
            for item in data:
                if isinstance(item, (list, tuple, dict)):
                    return self._fix_last_modified(item)

    def _process_netrc(self, use_netrc: str | bool) -> None:
        """
        The use_netrc var is either a boolean, which means we should use
        the user's default netrc, or a string specifying a path to a
        netrc formatted file

        use_netrc:bool|str      Either set to True to use the user's default
                                netrc file or a string specifying a specific
                                netrc file to use
        """
        if not use_netrc:
            raise CredentialError(
                'useNetrc must be either a boolean "True" '
                + "or a string representing a path to a netrc file, "
                + "not {0}".format(repr(use_netrc))
            )
        if isinstance(use_netrc, bool) and use_netrc:
            self._netrc = netrc()
        else:
            # This should be a string specifying a path to a netrc file
            self._netrc = netrc(os.path.expanduser(use_netrc))
        auth = self._netrc.authenticators(self._hostname)
        if not auth:
            raise CredentialError(
                "No machine entry found for {0} in your netrc file".format(
                    self._hostname
                )
            )

        # If we get here, we have credentials
        self._username = auth[0]
        self._raw_pass = auth[2]

    def _get_salt(self, length: int = 12) -> str:
        salt = md5(os.urandom(100)).hexdigest()
        return salt[:length]
