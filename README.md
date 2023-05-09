## The idea

Create an app to keep track of your boardgame collection. Also you can keep track of games played, as well as see your friends' collections!

### TODO
- User profile picture
    - Allow user to pick one of X profile pics
- Create something that catches API errors
    - Decorator?
    - Check for response header and display temporary holding page with timer
- Refine Everything
    - Display friends owned games on gamepage.html
    - Playlog overlay
    - Other styles
    - Search when no results (boardgames and users)
    - Playlog should have most recent game at top
    - Search needs to have multiple pages when too many results
    - 'Loading...' when searching, to prevent user refreshing
    - User is currently never auto-logged-out
    - 'Cancel Request' on friend page border
- Allow import of collection from BGG
    - ... Not sure yet

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