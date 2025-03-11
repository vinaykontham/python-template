async function shortenUrl() {
    const longUrl = document.getElementById("long-url").value;

    const response = await fetch("/shorten/", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ long_url: longUrl })
    });

    const data = await response.json();

    if (response.status === 200) {
        document.getElementById("short-url").innerHTML = `Shortened URL: <a href="/${data.short_url}" target="_blank">${window.location.origin}/${data.short_url}</a>`;
    } else {
        document.getElementById("short-url").innerHTML = "Error: " + data.detail;
    }
}
