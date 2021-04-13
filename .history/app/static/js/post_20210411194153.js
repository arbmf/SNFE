$(document).ready(function () {
  var socket;
  socket = io();

  $("#like").click(function () {
    appendSelf();
    socket.emit("like");
    return false;
  });
});
