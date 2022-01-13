const socket = io.connect('/webrtc');

// Socket events

  // Whenever the server emits 'login', log the login message
socket.on('newUser', (data) => {
  // Display the welcome message
  var message = "Welcome to Socket.IO Chat  ";
  console.log(message)
  console.log(data)
});

socket.on('userLeave', (data) => {
  const message = "Someone Leave~"
  console.log(message)
  console.log(data)
})

socket.on('disconnect', () => {
  console.log('you have been disconnected');
});

export default socket