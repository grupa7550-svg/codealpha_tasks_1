const form = document.querySelector("#shorten-form");
const input = document.querySelector("#url-input");
const submitButton = document.querySelector("#submit-button");
const message = document.querySelector("#message");
const result = document.querySelector("#result");
const shortUrl = document.querySelector("#short-url");
const copyButton = document.querySelector("#copy-button");

form.addEventListener("submit", async (event) => {
  event.preventDefault();
  message.textContent = "";
  result.hidden = true;
  submitButton.disabled = true;
  submitButton.textContent = "Shortening...";

  try {
    const response = await fetch("/api/shorten", {
      method: "POST",
      headers: {"Content-Type": "application/json"},
      body: JSON.stringify({url: input.value.trim()})
    });
    const data = await response.json();
    if (!response.ok) throw new Error(data.error || "Something went wrong.");

    shortUrl.href = data.short_url;
    shortUrl.textContent = data.short_url;
    result.hidden = false;
    message.style.color = "#247a48";
    message.textContent = data.message || "Short URL created.";
  } catch (error) {
    message.style.color = "#c0392b";
    message.textContent = error.message || "Could not connect to the server.";
  } finally {
    submitButton.disabled = false;
    submitButton.innerHTML = 'Shorten URL <span>→</span>';
  }
});

copyButton.addEventListener("click", async () => {
  try {
    await navigator.clipboard.writeText(shortUrl.href);
    copyButton.textContent = "Copied!";
    setTimeout(() => { copyButton.textContent = "Copy link"; }, 1600);
  } catch {
    message.style.color = "#c0392b";
    message.textContent = "Copy failed. Please select and copy the link manually.";
  }
});
