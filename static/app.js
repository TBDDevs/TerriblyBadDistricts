$("#aBtnGroup :input").on('click', function(event) {
    console.log(this); // points to the clicked input button
    var choiceID = $(this).attr('id')
    var contentFrame = $(".map")
    if (choiceID === "dem") {
        contentFrame.attr('src', '/democratic_map')
    }
    if (choiceID === "rep"){
        contentFrame.attr('src', '/republican_map')
    }
});
