//NavBar
function hideIconBar() {
  var iconBar = document.getElementById("iconBar");
  var navigation = document.getElementById("navigation");
  iconBar.setAttribute("style", "display:none;");
  navigation.classList.remove("hide");
}

function showIconBar() {
  var iconBar = document.getElementById("iconBar");
  var navigation = document.getElementById("navigation");
  iconBar.setAttribute("style", "display:block;");
  navigation.classList.add("hide");
}

//Comment
function showComment() {
  var commentArea = document.getElementById("comment-area");
  commentArea.classList.remove("hide");
}

//Reply
function showReply() {
  var replyArea = document.getElementById("reply-area");
  replyArea.classList.remove("hide");
}

// Notification bell
document.addEventListener("DOMContentLoaded", () => {
  // Get references to the notification bell and dropdown content elements
  const notificationBell = document.getElementById("notification-bell");
  const dropdownContent = document.getElementById("notification-dropdown");

  console.log("Script loaded, waiting for bell click");

  // Add click event listener to the notification bell
  notificationBell.addEventListener("click", (event) => {
    // Prevent the default action of the click event
    event.preventDefault();
    console.log("Bell clicked, fetching notifications");

    // Fetch the latest notifications from the server
    fetch("/notifications/latest")
      .then((response) => {
        // Check if the response is okay
        if (!response.ok) {
          throw new Error("Network response was not ok " + response.statusText);
        }
        // Parse the response as JSON
        return response.json();
      })
      .then((data) => {
        console.log("Notifications fetched:", data);

        // Clear the current content of the dropdown
        dropdownContent.innerHTML = "";

        // Check if there are no new notifications
        if (data.length === 0) {
          dropdownContent.innerHTML = "<p>No new notifications</p>";
        } else {
          // Iterate over the fetched notifications and create elements for each
          data.forEach((notification) => {
            console.log("Creating notification element for:", notification);

            // Create a new div element for the notification
            const notificationElement = document.createElement("div");
            notificationElement.classList.add("notification-item");

            // Set the inner HTML of the notification element
            notificationElement.innerHTML = `
              <p>${notification.message} <span class="notification-timestamp">${notification.created_at}</span></p>
            `;

            // Add a click event listener to mark the notification as read when clicked
            notificationElement.addEventListener("click", () => {
              window.location.href = `/notifications/mark_as_read/${notification.id}`;
            });

            console.log("Appending notification element:", notificationElement);
            // Append the notification element to the dropdown content
            dropdownContent.appendChild(notificationElement);
          });
        }

        console.log("Toggling dropdown visibility");
        // Toggle the visibility of the dropdown content
        dropdownContent.classList.toggle("show");
      })
      .catch((error) => console.error("Error fetching notifications:", error));
  });

  // Add click event listener to the document to close the dropdown when clicking outside of it
  document.addEventListener("click", (event) => {
    // Check if the click target is outside the notification bell and dropdown content
    if (
      !notificationBell.contains(event.target) &&
      !dropdownContent.contains(event.target)
    ) {
      // Remove the "show" class to hide the dropdown
      dropdownContent.classList.remove("show");
    }
  });

  // Prevent closing the dropdown when clicking inside it
  dropdownContent.addEventListener("click", (event) => {
    // Stop the event from propagating to parent elements
    event.stopPropagation();
  });
});

// 1.1 handle likes
document.addEventListener("DOMContentLoaded", () => {
  // This event listener ensures that the code runs after the DOM has fully loaded

  // Select all elements with the class 'icon-like' or 'icon-dislike' and add an event listener to each
  document.querySelectorAll(".icon-like, .icon-dislike").forEach((icon) => {
    icon.addEventListener("click", (event) => {
      // Determine if the clicked icon is a 'like' or 'dislike'
      const isLike = event.target.classList.contains("icon-like");
      // Get the ID of the post or reply from the 'data-id' attribute of the clicked icon
      const id = event.target.getAttribute("data-id");
      // Get the type ('post' or 'reply') from the 'data-type' attribute of the clicked icon
      const type = event.target.getAttribute("data-type");
      // Set the action to 'like' if it is a like icon, otherwise set it to 'dislike'
      const action = isLike ? "like" : "dislike";

      // Make a POST request to the server to register the vote
      fetch(`/vote/${type}/${id}/${action}`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "X-CSRFToken": "{{ csrf_token() }}", // Include the CSRF token for security
        },
      })
        .then((response) => response.json()) // Parse the JSON response from the server
        .then((data) => {
          if (data.success) {
            // If the vote was successful, update the like count on the page
            const likeCountElem = document.getElementById(`like-count-${id}`);
            likeCountElem.textContent = data.likes;
            if (data.neutral) {
              // If the vote was reset to neutral, log a message
              console.log("Vote reset to neutral. You can vote again.");
            }
          } else {
            // If there was an error, display an alert with the error message
            alert(data.error);
          }
        })
        .catch((error) => console.error("Error:", error)); // Log any errors to the console
    });
  });
});
