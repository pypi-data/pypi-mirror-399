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

from pydantic import BaseModel, Field, ConfigDict


# Base response model that all responses inherit from
class SubsonicResponse(BaseModel):
    """Base model for all Subsonic API responses"""
    model_config = ConfigDict(extra='allow')

    status: str
    version: str
    xmlns: str | None = None


# Simple status response (used by many methods)
class StatusResponse(SubsonicResponse):
    """Simple status response for methods that don't return data"""
    pass


# License models
class License(BaseModel):
    model_config = ConfigDict(extra='allow')

    date: str | None = None
    email: str | None = None
    key: str | None = None
    valid: bool | None = None


class LicenseResponse(SubsonicResponse):
    license: License


# Scan status models
class ScanStatus(BaseModel):
    model_config = ConfigDict(extra='allow')

    scanning: bool
    count: int


class ScanStatusResponse(SubsonicResponse):
    scanStatus: ScanStatus | None = Field(None, alias='scanstatus')


# Music folder models
class MusicFolder(BaseModel):
    model_config = ConfigDict(extra='allow')

    id: int | str
    name: str


class MusicFolders(BaseModel):
    model_config = ConfigDict(extra='allow')

    musicFolder: list[MusicFolder] | None = []


class MusicFoldersResponse(SubsonicResponse):
    musicFolders: MusicFolders | None = None


# Song/Entry models (used across many responses)
class Child(BaseModel):
    """Generic child entry (can be a song, album, or directory)"""
    model_config = ConfigDict(extra='allow')

    id: int | str
    parent: int | str | None = None
    isDir: bool | None = None
    title: str | None = None
    album: str | None = None
    albumId: int | str | None = None
    artist: str | None = None
    artistId: int | str | None = None
    track: int | None = None
    year: int | None = None
    genre: str | None = None
    coverArt: int | str | None = None
    size: int | None = None
    contentType: str | None = None
    suffix: str | None = None
    transcodedContentType: str | None = None
    transcodedSuffix: str | None = None
    duration: int | None = None
    bitRate: int | None = None
    path: str | None = None
    isVideo: bool | None = None
    userRating: int | None = None
    averageRating: float | None = None
    playCount: int | None = None
    discNumber: int | None = None
    created: str | None = None
    starred: str | None = None
    albumId: int | str | None = None
    type: str | None = None
    bookmarkPosition: int | None = None
    originalWidth: int | None = None
    originalHeight: int | None = None


# Now Playing models
class NowPlayingEntry(Child):
    """Entry currently being played"""
    playerId: int | None = None
    username: str | None = None
    minutesAgo: int | None = None


class NowPlaying(BaseModel):
    model_config = ConfigDict(extra='allow')

    entry: NowPlayingEntry | list[NowPlayingEntry] | None = None


class NowPlayingResponse(SubsonicResponse):
    nowPlaying: NowPlaying | None = None


# Index/Artist browsing models
class Artist(BaseModel):
    """Artist in folder-based browsing"""
    model_config = ConfigDict(extra='allow')

    id: int | str
    name: str
    starred: str | None = None
    userRating: int | None = None
    averageRating: float | None = None


class Index(BaseModel):
    """Index grouping (e.g., by letter)"""
    model_config = ConfigDict(extra='allow')

    name: str
    artist: list[Artist] | None = []


class Indexes(BaseModel):
    model_config = ConfigDict(extra='allow')

    lastModified: int | None = None
    ignoredArticles: str | None = None
    index: list[Index] | None = []
    shortcut: list[Artist] | None = []
    child: list[Child] | None = []


class IndexesResponse(SubsonicResponse):
    indexes: Indexes | None = None


# Music directory models
class Directory(BaseModel):
    model_config = ConfigDict(extra='allow')

    id: int | str
    parent: int | str | None = None
    name: str
    starred: str | None = None
    userRating: int | None = None
    averageRating: float | None = None
    playCount: int | None = None
    child: list[Child] | None = []


class MusicDirectoryResponse(SubsonicResponse):
    directory: Directory | None = None


# Search models
class SearchResult2(BaseModel):
    model_config = ConfigDict(extra='allow')

    artist: list[Artist] | None = []
    album: list[Child] | None = []
    song: list[Child] | None = []


class SearchResult2Response(SubsonicResponse):
    searchResult2: SearchResult2 | None = None


# ID3 Artist model
class ArtistID3(BaseModel):
    """Artist in ID3-based browsing"""
    model_config = ConfigDict(extra='allow')

    id: int | str
    name: str
    coverArt: int | str | None = None
    artistImageUrl: str | None = None
    albumCount: int | None = None
    starred: str | None = None


class IndexID3(BaseModel):
    """Index grouping for ID3 artists"""
    model_config = ConfigDict(extra='allow')

    name: str
    artist: ArtistID3 | list[ArtistID3] | None = None


class ArtistsID3(BaseModel):
    model_config = ConfigDict(extra='allow')

    ignoredArticles: str | None = None
    index: list[IndexID3] | None = []


class ArtistsResponse(SubsonicResponse):
    artists: ArtistsID3 | None = None


# ID3 Album model
class AlbumID3(BaseModel):
    """Album in ID3-based browsing"""
    model_config = ConfigDict(extra='allow')

    id: int | str
    name: str
    artist: str | None = None
    artistId: int | str | None = None
    coverArt: int | str | None = None
    songCount: int | None = None
    duration: int | None = None
    playCount: int | None = None
    created: str | None = None
    starred: str | None = None
    year: int | None = None
    genre: str | None = None


# Search3 models (ID3)
class SearchResult3(BaseModel):
    model_config = ConfigDict(extra='allow')

    artist: list[ArtistID3] | None = []
    album: list[AlbumID3] | None = []
    song: list[Child] | None = []


class SearchResult3Response(SubsonicResponse):
    searchResult3: SearchResult3 | None = None


# Playlist models
class PlaylistSummary(BaseModel):
    """Summary of a playlist (from getPlaylists)"""
    model_config = ConfigDict(extra='allow')

    id: int | str
    name: str
    comment: str | None = None
    owner: str | None = None
    public: bool | None = None
    songCount: int | None = None
    duration: int | None = None
    created: str | None = None
    changed: str | None = None
    coverArt: int | str | None = None


class Playlists(BaseModel):
    model_config = ConfigDict(extra='allow')

    playlist: list[PlaylistSummary] | None = []


class PlaylistsResponse(SubsonicResponse):
    playlists: Playlists | None = None


class Playlist(PlaylistSummary):
    """Full playlist with entries"""
    entry: list[Child] | None = []


class PlaylistResponse(SubsonicResponse):
    playlist: Playlist | None = None


# User models
class User(BaseModel):
    model_config = ConfigDict(extra='allow')

    username: str
    email: str | None = None
    scrobblingEnabled: bool | None = None
    adminRole: bool | None = None
    settingsRole: bool | None = None
    downloadRole: bool | None = None
    uploadRole: bool | None = None
    playlistRole: bool | None = None
    coverArtRole: bool | None = None
    commentRole: bool | None = None
    podcastRole: bool | None = None
    streamRole: bool | None = None
    jukeboxRole: bool | None = None
    shareRole: bool | None = None
    videoConversionRole: bool | None = None
    folder: list[int | str] | None = []


class UserResponse(SubsonicResponse):
    user: User | None = None


class Users(BaseModel):
    model_config = ConfigDict(extra='allow')

    user: list[User] | None = []


class UsersResponse(SubsonicResponse):
    users: Users | None = None


# Chat models
class ChatMessage(BaseModel):
    model_config = ConfigDict(extra='allow')

    username: str
    time: int
    message: str


class ChatMessages(BaseModel):
    model_config = ConfigDict(extra='allow')

    chatMessage: ChatMessage | list[ChatMessage] | None = None


class ChatMessagesResponse(SubsonicResponse):
    chatMessages: ChatMessages | None = None


# Album list models
class AlbumList(BaseModel):
    model_config = ConfigDict(extra='allow')

    album: list[Child] | None = []


class AlbumListResponse(SubsonicResponse):
    albumList: AlbumList | None = None


class AlbumList2(BaseModel):
    model_config = ConfigDict(extra='allow')

    album: list[AlbumID3] | None = []


class AlbumList2Response(SubsonicResponse):
    albumList2: AlbumList2 | None = None


# Random songs models
class RandomSongs(BaseModel):
    model_config = ConfigDict(extra='allow')

    song: list[Child] | None = []


class RandomSongsResponse(SubsonicResponse):
    randomSongs: RandomSongs | None = None


# Lyrics models
class Lyrics(BaseModel):
    model_config = ConfigDict(extra='allow')

    artist: str | None = None
    title: str | None = None
    content: str | None = Field(None, alias='value')


class LyricsResponse(SubsonicResponse):
    lyrics: Lyrics | None = None


# Podcast models
class PodcastEpisode(Child):
    """Podcast episode (extends Child with additional fields)"""
    streamId: int | str | None = None
    channelId: int | str | None = None
    description: str | None = None
    status: str | None = None
    publishDate: str | None = None


class PodcastChannel(BaseModel):
    model_config = ConfigDict(extra='allow')

    id: int | str
    url: str | None = None
    title: str | None = None
    description: str | None = None
    coverArt: int | str | None = None
    originalImageUrl: str | None = None
    status: str | None = None
    errorMessage: str | None = None
    episode: list[PodcastEpisode] | None = []


class Podcasts(BaseModel):
    model_config = ConfigDict(extra='allow')

    channel: PodcastChannel | list[PodcastChannel] | None = None


class PodcastsResponse(SubsonicResponse):
    podcasts: Podcasts | None = None


# Shares models
class Share(BaseModel):
    model_config = ConfigDict(extra='allow')

    id: int | str
    url: str
    description: str | None = None
    username: str
    created: str
    expires: str | None = None
    lastVisited: str | None = None
    visitCount: int
    entry: list[Child] | None = []


class Shares(BaseModel):
    model_config = ConfigDict(extra='allow')

    share: list[Share] | None = []


class SharesResponse(SubsonicResponse):
    shares: Shares | None = None


# Artist with albums (ID3)
class ArtistWithAlbumsID3(ArtistID3):
    """Artist with list of albums"""
    album: list[AlbumID3] | None = []


class ArtistResponse(SubsonicResponse):
    artist: ArtistWithAlbumsID3 | None = None


# Album with songs (ID3)
class AlbumWithSongs(AlbumID3):
    """Album with list of songs"""
    song: list[Child] | None = []


class AlbumResponse(SubsonicResponse):
    album: AlbumWithSongs | None = None


# Song model (single song)
class SongResponse(SubsonicResponse):
    song: Child | None = None


# Videos models
class Video(BaseModel):
    model_config = ConfigDict(extra='allow')

    id: int | str
    parent: int | str | None = None
    isDir: bool | None = None
    title: str
    album: str | None = None
    artist: str | None = None
    size: int | None = None
    contentType: str | None = None
    suffix: str | None = None
    transcodedContentType: str | None = None
    transcodedSuffix: str | None = None
    path: str | None = None
    isVideo: bool | None = None
    playCount: int | None = None
    created: str | None = None
    duration: int | None = None
    bitRate: int | None = None
    coverArt: int | str | None = None


class Videos(BaseModel):
    model_config = ConfigDict(extra='allow')

    video: Video | list[Video] | None = None


class VideosResponse(SubsonicResponse):
    videos: Videos | None = None


# Starred models
class Starred(BaseModel):
    model_config = ConfigDict(extra='allow')

    artist: list[Artist] | None = []
    album: list[Child] | None = []
    song: list[Child] | None = []


class StarredResponse(SubsonicResponse):
    starred: Starred | None = None


class Starred2(BaseModel):
    model_config = ConfigDict(extra='allow')

    artist: list[ArtistID3] | None = []
    album: list[AlbumID3] | None = []
    song: list[Child] | None = []


class Starred2Response(SubsonicResponse):
    starred2: Starred2 | None = None


# Genres models
class Genre(BaseModel):
    model_config = ConfigDict(extra='allow')

    name: str  # Changed from 'value' to 'name'
    songCount: int | None = None
    albumCount: int | None = None


class Genres(BaseModel):
    model_config = ConfigDict(extra='allow')

    genre: list[Genre] | None = []


class GenresResponse(SubsonicResponse):
    genres: Genres | None = None


# Songs by genre models
class SongsByGenre(BaseModel):
    model_config = ConfigDict(extra='allow')

    song: list[Child] | None = []


class SongsByGenreResponse(SubsonicResponse):
    songsByGenre: SongsByGenre | None = None


# Internet radio models
class InternetRadioStation(BaseModel):
    model_config = ConfigDict(extra='allow')

    id: int | str
    name: str
    streamUrl: str
    homePageUrl: str | None = None


class InternetRadioStations(BaseModel):
    model_config = ConfigDict(extra='allow')

    internetRadioStation: list[InternetRadioStation] | None = []


class InternetRadioStationsResponse(SubsonicResponse):
    internetRadioStations: InternetRadioStations | None = None


# Bookmarks models
class Bookmark(BaseModel):
    model_config = ConfigDict(extra='allow')

    position: int
    username: str
    comment: str | None = None
    created: str
    changed: str
    entry: Child


class Bookmarks(BaseModel):
    model_config = ConfigDict(extra='allow')

    bookmark: list[Bookmark] | None = []


class BookmarksResponse(SubsonicResponse):
    bookmarks: Bookmarks | None = None


# Artist info models
class SimilarArtist(BaseModel):
    model_config = ConfigDict(extra='allow')

    id: int | str
    name: str
    albumCount: int | None = None
    starred: str | None = None


class ArtistInfo(BaseModel):
    model_config = ConfigDict(extra='allow')

    biography: str | None = None
    musicBrainzId: str | None = None
    lastFmUrl: str | None = None
    smallImageUrl: str | None = None
    mediumImageUrl: str | None = None
    largeImageUrl: str | None = None
    similarArtist: list[SimilarArtist] | None = []


class ArtistInfoResponse(SubsonicResponse):
    artistInfo: ArtistInfo | None = None


class ArtistInfo2Response(SubsonicResponse):
    artistInfo2: ArtistInfo | None = None


# Similar songs models
class SimilarSongs(BaseModel):
    model_config = ConfigDict(extra='allow')

    song: list[Child] | None = []


class SimilarSongsResponse(SubsonicResponse):
    similarSongs: SimilarSongs | None = None


class SimilarSongs2Response(SubsonicResponse):
    similarSongs2: SimilarSongs | None = None


# Play queue models
class PlayQueue(BaseModel):
    model_config = ConfigDict(extra='allow')

    entry: list[Child] | None = []
    current: int | str | None = None
    position: int | None = None
    username: str | None = None
    changed: str | None = None
    changedBy: str | None = None


class PlayQueueResponse(SubsonicResponse):
    playQueue: PlayQueue | None = None


# Top songs models
class TopSongs(BaseModel):
    model_config = ConfigDict(extra='allow')

    song: list[Child] | None = []


class TopSongsResponse(SubsonicResponse):
    topSongs: TopSongs | None = None


# Video info models
class AudioTrack(BaseModel):
    model_config = ConfigDict(extra='allow')

    id: int | str
    name: str | None = None
    languageCode: str | None = None


class Captions(BaseModel):
    model_config = ConfigDict(extra='allow')

    id: int | str
    name: str | None = None
    format: str | None = None


class Conversion(BaseModel):
    model_config = ConfigDict(extra='allow')

    id: int | str
    bitRate: int | None = None


class VideoInfo(BaseModel):
    model_config = ConfigDict(extra='allow')

    id: int | str
    captions: list[Captions] | None = []
    audioTrack: list[AudioTrack] | None = []
    conversion: list[Conversion] | None = []


class VideoInfoResponse(SubsonicResponse):
    videoInfo: VideoInfo | None = None


# Album info models
class AlbumInfo(BaseModel):
    model_config = ConfigDict(extra='allow')

    notes: str | None = None
    musicBrainzId: str | None = None
    lastFmUrl: str | None = None
    smallImageUrl: str | None = None
    mediumImageUrl: str | None = None
    largeImageUrl: str | None = None


class AlbumInfoResponse(SubsonicResponse):
    albumInfo: AlbumInfo | None = None
