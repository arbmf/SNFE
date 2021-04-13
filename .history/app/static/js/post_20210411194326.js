$(document).ready(function () {
  var socket;
  socket = io();

  $("#like").click(function () {
    alert("click");
    socket.emit("like");
    return false;
  });
});
