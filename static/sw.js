self.addEventListener("push", function(event) {
    const data = event.data.text();
    self.registration.showNotification("PRIZRAK", {
        body: data,
        icon: "/static/icon.png"
    });
});
