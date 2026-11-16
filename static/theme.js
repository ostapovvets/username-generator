// theme (light / dark / amoled) and button color
// this file is loaded in the <head>, so the saved theme is applied before the page is drawn
// (otherwise the page would flash white for a moment in dark mode)

const root = document.documentElement;

// localStorage can throw in private windows, so wrap reads and writes
function load(key) {
    try {
        return localStorage.getItem(key);
    } catch (error) {
        return null;
    }
}

function save(key, value) {
    try {
        if (value === null) {
            localStorage.removeItem(key);
        } else {
            localStorage.setItem(key, value);
        }
    } catch (error) {
        // nothing to do, the setting just won't be remembered
    }
}

// light themes use the default colors from :root, so no attribute is needed
function setTheme(theme) {
    if (theme === "dark" || theme === "amoled") {
        root.dataset.theme = theme;
    } else {
        delete root.dataset.theme;
    }
}

// pick white or dark text so the button label stays readable on any color
function textColorFor(hex) {
    const r = parseInt(hex.slice(1, 3), 16);
    const g = parseInt(hex.slice(3, 5), 16);
    const b = parseInt(hex.slice(5, 7), 16);
    const brightness = (r * 299 + g * 587 + b * 114) / 1000;
    if (brightness > 160) {
        return "#111111";
    }
    return "#ffffff";
}

// null means "use the theme's own default color"
function setAccent(hex) {
    if (hex) {
        root.style.setProperty("--accent", hex);
        root.style.setProperty("--accent-text", textColorFor(hex));
    } else {
        root.style.removeProperty("--accent");
        root.style.removeProperty("--accent-text");
    }
}

// apply saved settings right away
setTheme(load("theme"));
setAccent(load("accent"));

// hook up the controls once the page exists
document.addEventListener("DOMContentLoaded", function () {
    const themeButtons = document.querySelectorAll("[data-theme-choice]");
    const picker = document.querySelector("#accent-picker");
    const reset = document.querySelector("#accent-reset");

    // show which theme button is active, and put the current color in the picker
    function refresh() {
        const current = root.dataset.theme || "light";
        for (const button of themeButtons) {
            button.setAttribute("aria-pressed", button.dataset.themeChoice === current);
        }
        picker.value = getComputedStyle(root).getPropertyValue("--accent").trim();
        reset.hidden = load("accent") === null;
    }

    for (const button of themeButtons) {
        button.addEventListener("click", function () {
            setTheme(button.dataset.themeChoice);
            save("theme", button.dataset.themeChoice);
            refresh();
        });
    }

    // "input" fires while dragging around in the picker, so the color updates live
    picker.addEventListener("input", function () {
        setAccent(picker.value);
        save("accent", picker.value);
        reset.hidden = false;
    });

    reset.addEventListener("click", function () {
        setAccent(null);
        save("accent", null);
        refresh();
    });

    refresh();
});
