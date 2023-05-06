## The idea

Create an app to keep track of your boardgame collection. Also you can keep track of games played, as well as see your friends' collections!

### TODO
- Index page
    - Display stats (update styling to multi-columns)
    - Display playlog
    - Display collection
    - Display friends
- Add Friends
    - Search users
    - Add user
    - Display friends
    - Accept/Decline request
    - Display friends owned games on gamepage.html
- Allow import of collection from BGG
    - ... Not sure yet
- User profile picture
    - Find generic profile pictures
    - Allow user to pick a picture
    - Stretch goal: Allow a user to upload a SQUARE picture
- Create something that catches API errors
    - Decorator?
    - Check for response header and display temporary holding page with timer
- Refine Everything
    - Playlog overlay
    - Other styles
    - Search when no results (boardgames and users)
    - Username is case-sensitive
    - Playlog should have most recent game at top
    - Search needs to have multiple pages when too many results
    - 'Loading...' when searching, to prevent user refreshing
    - User is never auto-logged-out

## Bibliography

### BGG API Guide
https://boardgamegeek.com/wiki/page/BGG_XML_API2
http://www.tayloraliss.com/bggapi/index.html

### Flask Sessions
https://www.youtube.com/watch?v=WsoL4MIhJbg&ab_channel=PrettyPrinted
https://www.youtube.com/watch?v=lvKjQhQ8Fwk&ab_channel=PrettyPrinted

### Checking if a string has any of a set of characters
https://www.oreilly.com/library/view/python-cookbook/0596001673/ch03s07.html

### Xml to dictionary for Python
https://github.com/martinblech/xmltodict


### How to use Flask.make_response()
https://www.educative.io/answers/what-is-flaskmakeresponse




### Friend Table Layout

userid1 = requestee
userid2 = requested
status = status

4 possible options:
- Friends (user1, user2, friends)
- Not Friends (not listed in table)
- Request Sent (user1, user2, pending)
- Request Received (user1, user2, pending)

When user1 is the user logged in, they are the sender of request
When user2 is the user logged in, they are the recipient of request