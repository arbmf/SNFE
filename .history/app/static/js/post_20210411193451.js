$(document).ready(function () {
  var socket;
  socket = io();
  socket.emit("like");
});
