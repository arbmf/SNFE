$(document).ready(function () {
  var socket;
  socket = io();
  socket.on("chat_b", function (msg) {
    if (msg.firstName != userFirstName) {
      $("#chats").append(`
      <li class="d-flex justify-content-between mb-4">
              <div class="chat-body white p-3 z-depth-1">
                <div class="header">
                  <strong class="primary-font"
                    >${msg.FirstName}</strong
                  >
                  <small class="pull-right text-muted"
                    ><i class="far fa-clock"></i> 13 mins ago</small
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
