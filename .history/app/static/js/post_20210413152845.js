$(document).ready(function () {
  var socket;
  socket = io();

  $("#like").click(function () {
    socket.emit("like", postID);
    return false;
  });

  socket.on("likedUsers", function (msg) {
    console.log(msg);
    $("#chats").append(`${msg.likedUsers}`);
  });
});
