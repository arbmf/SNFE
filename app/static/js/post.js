$(document).ready(function () {
  var socket;
  socket = io();

  $("#like").click(function () {
    socket.emit("like", postID);
    return false;
  });

  socket.on("likedUsers", function (msg) {
    console.log(msg);
    $("#likeText").text(`${msg.likedUsers} people liked this`);
  });

    $("#likeq").click(function () {
    socket.emit("likeq", questionID);
    return false;
  });

  socket.on("likedUsersQ", function (msg) {
    console.log(msg);
    $("#likeTextQ").text(`${msg.likedUsersQ} people liked this`);
  });
});


