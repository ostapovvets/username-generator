//wait until the whole page is loaded nd then look for elements on it
document.addEventListener("DOMContentLoaded", function () {
    const form = document.querySelector("#settings");
    const button = document.querySelector("#generate");
    const results = document.querySelector("#results");
    const summary = document.querySelector("#summary");
    const message = document.querySelector("#message");
    const table = document.querySelector("table");
    const filterRow = document.querySelector("#filter-row");
    const onlyAvailable = document.querySelector("#only-available");
    const noAvailable = document.querySelector("#no-available");

    // how many available names the last batch had (used by the filter)
    let lastAvailable = 0;

    // hide or show non-available rows depending on the checkbox
    function applyFilter() {
        const on = onlyAvailable.checked && !filterRow.hidden;
        table.classList.toggle("only-available", on);
        table.classList.toggle("none-available", lastAvailable === 0);
        noAvailable.hidden = !(on && lastAvailable === 0 && results.children.length > 0);
    }

    onlyAvailable.addEventListener("change", applyFilter);

    //show slider value
    for (const slider of document.querySelectorAll("input[type=range]")) {
        slider.addEventListener("input", function () {
            document.querySelector("#" + slider.id + "-value").textContent = slider.value;
        });
    }

    form.addEventListener("submit", async function (event) {
        // stop the browser from reloading the page
        event.preventDefault();

        // show that something is happening, and clear old results
        button.disabled = true;
        button.textContent = "Generating...";
        message.innerHTML = "";
        summary.textContent = "";
        results.innerHTML = "";
        lastAvailable = 0;
        applyFilter();

        // remember which platform this batch is for (only roblox names get checked)
        const platform = document.querySelector("#platform").value;

        try {
            // send the form to flask and wait for the answer
            const response = await fetch("/generate", {
                method: "POST",
                body: new FormData(form),
            });
            const data = await response.json();

            if (data.error) {
                showError(data.error);
            }

            let available = 0;
            let taken = 0;

            // one table row per name
            for (const item of data.names) {
                const row = document.createElement("tr");
                row.dataset.status = item.status;

                const nameCell = document.createElement("td");
                nameCell.textContent = item.name;

                // status as a small colored badge (green = available, red = taken)
                const statusCell = document.createElement("td");
                const badge = document.createElement("span");
                badge.className = "badge";
                if (item.status === "available" || item.status === "taken") {
                    badge.classList.add(item.status);
                }
                badge.textContent = item.status;
                statusCell.appendChild(badge);

                row.appendChild(nameCell);
                row.appendChild(statusCell);
                results.appendChild(row);

                if (item.status === "available") {
                    available++;
                }
                if (item.status === "taken") {
                    taken++;
                }
            }

            summary.textContent = `${data.names.length} generated, ${available} available, ${taken} taken`;

            // the filter only makes sense when names were actually checked
            lastAvailable = available;
            filterRow.hidden = platform !== "roblox" || data.names.length === 0;
            applyFilter();
        } catch (error) {
            showError("Something went wrong talking to the server.");
        }

        // ready for the next click
        button.disabled = false;
        button.textContent = "Generate";
    });

    // show an error message above the results
    function showError(text) {
        const error = document.createElement("p");
        error.textContent = "Error: " + text;
        message.appendChild(error);
    }
});
