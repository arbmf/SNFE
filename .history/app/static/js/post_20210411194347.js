$(document).ready(function () {
  var socket;
  socket = io();

  $("#like").click(function () {
    socket.emit("like");
    return false;
  });
});
