var members = [];
$(document).ready(function () {
  window.onbeforeunload = function (e) {
    e.preventDefault();
    socket.emit("closed", chatroomId);
    return;
  };
  var socket;
  socket = io();
  socket.on("chat_b", function (msg) {
    console.log(msg);
    console.log(userEmail);
    if (msg.email != userEmail) {
      $("#chats").append(`
      <li class="d-flex justify-content-between mb-4">
              <div class="chat-body white p-3 z-depth-1">
                <div class="header">
                  <strong class="primary-font"
                    >${msg.FirstName}</strong
                  >
                </div>
                <hr class="w-100" />
                <p class="mb-0">${msg.message}</p>
              </div>
              <img
                src="{{ url_for('static', filename='profile_pictures/' + ${msg.ProfilePicture}) }}"
                style="height: 60px; width: 60px"
                alt="avatar"
                class="avatar rounded-circle mr-0 ml-3 z-depth-1"
              />
            </li>
      `);
    }
  });
  socket.on("join_b", function (msg) {
    console.log(msg.Members);
    $("#members").html(getMemberHtml(msg.Members));
  });
  socket.emit("join", chatroomId);

  $("#send_message").click(function () {
    appendSelf();
    socket.emit("chat", { room: chatroomId, data: $("#message").val() });
    return false;
  });
});

function appendSelf() {
  $("#chats").append(`
          <li class="d-flex justify-content-between mb-4">
              <img
                src="{{ url_for('static', filename='profile_pictures/' + ${profilePicture}) }}"
                style="height: 60px; width: 60px"
                alt="avatar"
                class="avatar rounded-circle mr-2 ml-lg-3 ml-0 z-depth-1"
              />
              <div class="chat-body white p-3 ml-2 z-depth-1">
                <div class="header">
                  <strong class="primary-font"
                    >${userFirstName}</strong
                  >
                  <small class="pull-right text-muted"
                    ><i class="far fa-clock"></i> 12 mins ago</small
                  >
                </div>
                <hr class="w-100" />
                <p class="mb-0">${$("#message").val()}</p>
              </div>
            </li>
    `);
}

function getMemberHtml(members) {
  var html = "";

  members.forEach((element) => {
    html += `
      <li class="active grey lighten-3 p-2">
                <a href="#" class="d-flex">
                  <img
                    src="{{ url_for('static', filename='profile_pictures/' + ${element.ProfilePicture}) }}"
                    style="height: 60px; width: 60px"
                    alt="avatar"
                    class="avatar rounded-circle d-flex align-self-center mr-2 z-depth-1"
                  />
                  <div style="padding-left:30px; padding-top:10px" class="text-small">
                    <strong>${element.FirstName}</strong>
                    <p class="last-message text-muted">Hello, Are you there?</p>
                  </div>
                </a>
              </li>`;
  });
  return html;
}
