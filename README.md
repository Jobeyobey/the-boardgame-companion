# The Boardgame Companion
#### Video Demo:  <https://youtu.be/1EMgKK6fADw>
#### Site Link: http://jobeyobey.pythonanywhere.com/login
#### Description:

<br>

I wanted to create an app to keep track of your boardgame collection. As well as this, I thought it'd be nice if you could also keep track of your games played, as well as being able to see what games your friends have in their collections.

<br>

**Languages/Frameworks used:**
- Python
- Flask
- SQLite
- HTML/CSS/Javascript

---
## User Accounts

I knew that I'd need user accounts to keep track of games, plays and friends.  For this, I used the approach I was familiar with from the CS50 Finance project, which uses Flask Sessions.

Through 'register.html', users are able to register with just a username and password. I make sure the username and password fit a certain criteria, and that the username is not already taken. If all is ok, the password is hashed and salted using werkzeug's 'generate_password_hash' function, and they are stored in a 'users' table with an 'id', 'username', 'hash' and 'icon'. Icon is a randomly assigned number (1-8) which corresponds to one of eight profile pictures. (Users can change this later).

Then, when logging in, the username and password's hash are compared to the ones in the database to check for a match.

---

## Profile page

On the user profile page, you can see a summary of the user's profile. Clicking the profile picture runs some JS to open an overlay from where you can pick a new profile picture, which will run an UPDATE statement on the user table to update their 'icon' value. Also, to display the user's stats, various SELECT commands are used to search the 'collection' and 'playlog' tables, using the returned information to calculate their collection size, games played, unique games played, wins/losses and win rate. Jinja is used to add these values into the HTML.

The above information, as well as a SELECT command to find user friends from the 'friends' table is used to display their playlog, collection and friends.

When viewing another person's profile, the queries in the URL are compared to the user's session value. If they match, they are viewing their own profile. If they do not, they are viewing someone else's. In this case, an 'add' / 'remove / 'cancel request' / 'accept/reject' button is displayed depending on these two user's relationship.

---

## Searching and Displaying boardgames

**Searching for games**

Users can add games to their collection, by first searching for them. The navbar at the top contains a search box, where the user can input a game name. This then uses the input query and adds it on to a BGG API query, to get a list of games.

This didn't work quite how I wanted, it only returns some basic information for example gameId, name, published year. However, I wanted to display thumbnails of the game. To do this, I get the gameId's from the initial query result and add them to a list. I then iterate through the list, making a new API request for each individual game. I could use this to get game ratings, thumbnails, number of players, estimated playtime and more. Using this, I was able to return more information about the game results to the user.

This did cause a few issues however, related to the number of API requests I was making. Requests would get rejected if too many were made within a short space of time (approx 15). Because of this, I made it so that only 7 games are visible per page, then the user can click 'next' to go through the results, without everything breaking! There was also an issue where game expansions and add-ons were being returned as well. I had to make API requests for results that weren't even boardgames, they might just be alternate pieces. This meant more unnecessary API requests being made, possibly breaking the search if too many add-ons were found. I added into the loop a total limit, so that if it was getting too many add-ons, it would just display on the page the boardgame results it had so far. Expansions and add-ons are not displayed, and I decided not to include them in this project.

In the case where a user does end up making too many API requests in a short time, the user would be redirected to a page explaining this issue, with a 20 second timer which would then enable a button to continue their search

**Displaying games**

When a user clicked on a game result after searching, it would display a page with more information about the game. This would be its own API request, where JS would be used to parse the XML, then grab the information I wanted and display it on the page. There would be some cases where some boardgame XML's were slightly different to others, so I had to write in some exceptions to prevent error's popping up if, for example, the thumbnail wasn't where it would usually be. In this case, there was only two places it could be and it would just check that second place.

A user's friends who own the game are also displayed at the bottom of the page, using a combination of SELECT statements across the 'friends' and 'collections' tables.

---

## Collection and Playlog

**Adding games and recording plays**

From the game page, users can add or remove games from their collection. When loading, a SELECT query is used to check if the user owns the game, by checking if their userid and gameid are present in the same row in a 'collection' table. Adding or removing the game runs an INSERT/DELETE statement, respectively.

Users can also record game plays from this page. They are prompted to record the result, as well as any notes they wish to take on the game. These are then INSERTed into a 'playlog' table, along with the userid and the current date, using the datetime module.

I noticed that in future, with a large enough playlog or collection, I would need to make multiple API requests to get the images of each game. Because of this, I decided to make a 'gamecache' table, which stores gameId's and the URL for their thumbnail. This way, I could just search my own database for the relevant thumbnails in future, saving myself making further API requests.

**Displaying collection and playlog**

The collection and playlog are displayed by using a SELECT statement using the userid and grabbing the relevant information from the 'collection' and 'playlog' tables. However they also made use of the 'gamecache' table mentioned above. The gameid's that show up in the user's collection or playlog to run a SELECT request on the 'gamecache' table, allowing the thumbnails to be displayed without worrying about making too many API requests.

From the collection, you are able to click on a game to view it's game page. I am able to use the gameid for the BGG API to request the relevant information and display the correct game page. In the playlog, clicking a tile will bring up the information recorded from that play. The user is also able to delete playlog entries from here.

---


## Searching for other users and adding friends

In the navbar, the search bar is also able to search for other users. This is done by using the 'select' menu. When making a search, the value of the select menu is used to know whether the user is making a 'boardgame' or 'user' search. The query is then inserted into an SQL statement, using a LIKE comparison. For example '%query%'. This way, only a part of a username is needed to find another user. From here, you can visit another user's page and add them as a friend.

The 'friends' table is made up of an 'id', 'userid1', 'userid2', and 'status' values. The 'status' can be 'friends' or 'pending'. If they are friends, it's quite simple, the two are friends. If a userid combination doesn't exist in a row, they have no relation and are not friends. However, a 'pending' status is for when someone has sent a request to another. 'userid1' is always the person making the request. This information is used to display whether a 'cancel request' or 'accept/reject request' button should be displayed for the user.

---

## Styling

The site is responsive, and should be viewable on most screen sizes and mobile. On larger screens, more information is displayed on some pages, for example when searching boardgames, or looking at your playlog. Different media queries are used to hide and display more or less information as well as adapting the layout to better fit on the screen.

---


## Sanitising inputs

I did my best to check user inputs hadn't been messed with. For example checking userid's to the logged in user, gameid's and names to the relevant gameid and name when used for an API request to BGG. I also made sure to use the '?' placeholder when making SQL statements to prevent SQL injection attacks.

---

## Bibliography
<br>

**BGG API Guide**

The [BGG API](https://boardgamegeek.com/wiki/page/BGG_XML_API2), as well as a [guide](http://www.tayloraliss.com/bggapi/index.html) on how to get it working.

<br>

**Flask Sessions**

How to use flask sessions. They were mostly already set up in the CS50 project, so I did some research on getting them working from scratch.

[Video 1](https://www.youtube.com/watch?v=WsoL4MIhJbg&ab_channel=PrettyPrinted)
[video 2](https://www.youtube.com/watch?v=lvKjQhQ8Fwk&ab_channel=PrettyPrinted)

<br>

**Checking if a string has any of a set of characters**

[Useful for username and password checking during register](https://www.oreilly.com/library/view/python-cookbook/0596001673/ch03s07.html)

<br>

**Xml to dictionary for Python**

Most of my API requests were made in JS, however I needed to make an XML request in Python when I wanted to check users weren't messing with gameid values when recording plays. I used [xmltodict](https://github.com/martinblech/xmltodict) to make the XML easier to work with. In hindsight, if I were to create this project from scratch, I would consider making all the API requests within Python rather than in JS.

<br>

**How to use Flask.make_response()**

I tried a couple of different methods of adding things, for example games to collections or friends. Some using forms to submit POST requests which would then redirect the user back to the GET request when the table is updated. Some used an onclick JS function to send an XMLHTTPRequest. I used [Flask.make_response](https://www.educative.io/answers/what-is-flaskmakeresponse) when using the JS methods, so that I could practice responses.

<br>

**CS50**

And of course, everything I learnt during [CS50](https://cs50.harvard.edu/x/2023/) was quite handy.
