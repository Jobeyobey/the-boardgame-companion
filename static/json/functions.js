// Enable/Disable Record Session input overlay
function overlayOn() {
    document.getElementById("overlay").style.display = "flex";
}
function overlayOff() {
    document.getElementById("overlay").style.display = "none";
}


// Playlog overlay
function playOverlayOn(tile) {
    overlayOn();
    document.getElementById("overlay-title").innerHTML = tile.name
    document.getElementById("overlay-date").innerHTML = tile.time
    document.getElementById("overlay-result").innerHTML = tile.result
    document.getElementById("overlay-note").innerHTML = tile.note
    document.getElementById("tile-id").setAttribute("value", tile.id)
}


// Function to convert HTML unicode characters
function HTMLconvert(str) {
str = str.replace(/&amp;#10;/g, "<br>");
str = str.replace(/&amp;quot;/g, '"');
str = str.replace(/&amp;rsquo;/g, "'");
return str;
}


// Add/remove/accept/reject friend buttons
function updateFriend(action, user2) {
    var req = new XMLHttpRequest();

    var url = `/updatefriend?action=${action}&user2=${user2}`;

    req.open("GET", url, false)
    req.send()

    location.reload()
}


// Updating user profile icons
function updateIcon(input) {
    button = document.getElementById("icon-submit");
    button.setAttribute("onclick", `sendIconUpdate(${input})`);
}

function sendIconUpdate(input) {
    var req = new XMLHttpRequest();

    var url = `/updateicon?input=${input}`;

    req.open("GET", url, false);
    req.send();

    if (req.status == "200") {
        location.reload()
    }
}


// Boardgame search next/prev page
function changePage(action, query, page) {
    searchType = "boardgames";
    if (action == "next") {
        var pageNo = page + 1;
    } else {
        var pageNo = page - 1;
        if (pageNo < 1) {
            pageNo = 1;
        };
    }
    window.location.replace(`/search?query=${query}&search-type=boardgames&page=${pageNo}`)
}