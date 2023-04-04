# To do

## The idea
Create a board-game collection app, where you can:
- Look up games
    - Search query returns a list of board games with ID's
    - View a page with that game

- Add games to your collection
    - Look up game
    - Button to add games to your collection

- Log plays
    - Date, players
    - Scoreboard
    - Game duration
    - Notes
    - Player stats

- Add friends and see their collections
    - Search other users
    - Add users


- Check the 'hot' games right now
- Rate your collection
- Look for games you would like based on another game

### TODO
- Home Page (Hot games, your collection, friends, friend recent games, menu bar at bottom/top)
    - Only one query at a time?
- Search page
    - Boardgame page
- Profile Page
    - Friends Page
    - Collection Page

#### BGG API
I've got the BGG API working on my computer, however for more flexibility I should look into webscraping
Resources here: https://boardgamegeek.com/thread/687565/pull-down-top-100-games-through-bgg-api


### Database Needed

#### Track individual user accounts
- Users:
- - id | username | password

#### Track user collection using userID's and BGG game ID's. Seeing as I can only make 10-15 requests at a time, I will either have to make multiple pages, or I could create a database that collects image URL's and gamenames, so before making an API request, I could simply search the database first, to potentially save time as well as displaying all collection games.
- collection:
- - id | userid | gameid

#### Table to track individual user play log
- playlog:
- - id | userid | gameid | result | time | note

#### Table to track friend status. Userid1 will always be the 'requestee', for knowing who initiated the request
- friends:
- - id | userid1 | userid2 |status

#### Possible table to cache game images and names to limit API calls
- cache:
- - gameid | image | name


# Bibliography

### BGG API Guide
https://boardgamegeek.com/wiki/page/BGG_XML_API2
http://www.tayloraliss.com/bggapi/index.html

### Flask Sessions
https://www.youtube.com/watch?v=WsoL4MIhJbg&ab_channel=PrettyPrinted
https://www.youtube.com/watch?v=lvKjQhQ8Fwk&ab_channel=PrettyPrinted

### Checking if a string has any of a set of characters
https://www.oreilly.com/library/view/python-cookbook/0596001673/ch03s07.html