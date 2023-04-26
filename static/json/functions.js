// Enable/Disable Record Session input overlay
function overlayOn() {
    document.getElementById("overlay").style.display = "flex";
}
function overlayOff() {
    document.getElementById("overlay").style.display = "none";
}

// Function to convert HTML unicode characters
function HTMLconvert(str)
{
str = str.replace(/&amp;#10;/g, "<br>");
str = str.replace(/&amp;quot;/g, '"');
return str;
}