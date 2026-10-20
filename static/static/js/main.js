
"use strict";

/**
 * Shopora — Frontend JavaScript
 *
 * Features:
 * 1. Responsive mobile navigation
 * 2. Dismissible Django messages
 * 3. Show/hide password controls
 * 4. Quantity validation
 * 5. Add-to-cart loading feedback
 * 6. Duplicate form-submission protection
 * 7. Broken product-image fallback
 *
 * No external JavaScript libraries required.
 */

document.addEventListener("DOMContentLoaded", () => {
    initializeMobileNavigation();
    initializeDismissibleAlerts();
    initializePasswordVisibility();
    initializeQuantityControls();
    initializeAddToCartFeedback();
    initializeFormSubmissionProtection();
    initializeImageFallbacks();
});

/* =========================================================
   1. RESPONSIVE MOBILE NAVIGATION
   ========================================================= */

function initializeMobileNavigation() {
    const toggle = document.querySelector(".menu-toggle");
    const navigation = document.querySelector(
        "#site-navigation, .site-navigation, .nav-links"
    );

    if (!toggle || !navigation) return;

    function closeMenu() {
        navigation.classList.remove("is-open");
        toggle.setAttribute("aria-expanded", "false");
    }

    function openMenu() {
        navigation.classList.add("is-open");
        toggle.setAttribute("aria-expanded", "true");
    }

    toggle.addEventListener("click", () => {
        const isOpen = navigation.classList.contains("is-open");

        if (isOpen) {
            closeMenu();
        } else {
            openMenu();
        }
    });

    // Close the menu after selecting a navigation link.
    navigation.addEventListener("click", (event) => {
        if (event.target.closest("a")) {
            closeMenu();
        }
    });

    // Close the menu when clicking outside it.
    document.addEventListener("click", (event) => {
        if (
            !navigation.contains(event.target) &&
            !toggle.contains(event.target)
        ) {
            closeMenu();
        }
    });

    // Allow keyboard users to close the menu.
    document.addEventListener("keydown", (event) => {
        if (event.key === "Escape") {
            const wasOpen = navigation.classList.contains("is-open");
            closeMenu();

            if (wasOpen) {
                toggle.focus();
            }
        }
    });

    // Reset mobile-menu state when switching to desktop layout.
    window.addEventListener("resize", () => {
        if (window.matchMedia("(min-width: 761px)").matches) {
            closeMenu();
        }
    });
}

/* =========================================================
   2. DISMISSIBLE DJANGO MESSAGES
   ========================================================= */

function initializeDismissibleAlerts() {
    const alerts = document.querySelectorAll(
        '[data-dismissible="true"]'
    );

    alerts.forEach((alert) => {
        // Prevent duplicate close buttons.
        if (alert.querySelector(".alert-close")) return;

        const closeButton = document.createElement("button");

        closeButton.type = "button";
        closeButton.className = "alert-close";
        closeButton.setAttribute(
            "aria-label",
            "Dismiss notification"
        );
        closeButton.textContent = "×";

        closeButton.addEventListener("click", () => {
            alert.remove();
        });

        alert.appendChild(closeButton);
    });
}

/* =========================================================
   3. SHOW / HIDE PASSWORD
   ========================================================= */

/*
   Example HTML:

   <input type="password" id="password">
   <button
       type="button"
       data-toggle-password="password"
       aria-label="Show password">
       Show
   </button>
*/

function initializePasswordVisibility() {
    const buttons = document.querySelectorAll(
        "[data-toggle-password]"
    );

    buttons.forEach((button) => {
        const inputId = button.getAttribute(
            "data-toggle-password"
        );

        const passwordInput = inputId
            ? document.getElementById(inputId)
            : null;

        if (!passwordInput) return;

        // Avoid registering the same listener twice.
        if (passwordInput.dataset.passwordToggleReady === "true") {
            return;
        }

        passwordInput.dataset.passwordToggleReady = "true";

        button.addEventListener("click", () => {
            const shouldShow = passwordInput.type === "password";

            passwordInput.type = shouldShow ? "text" : "password";

            button.setAttribute(
                "aria-pressed",
                String(shouldShow)
            );

            button.setAttribute(
                "aria-label",
                shouldShow ? "Hide password" : "Show password"
            );

            if (button.dataset.showText && button.dataset.hideText) {
                button.textContent = shouldShow
                    ? button.dataset.hideText
                    : button.dataset.showText;
            }
        });
    });
}

/* =========================================================
   4. QUANTITY INPUT VALIDATION
   ========================================================= */

function initializeQuantityControls() {
    const inputs = document.querySelectorAll(
        'input[data-quantity-input], input[name="quantity"]'
    );

    inputs.forEach((input) => {
        if (input.dataset.quantityReady === "true") return;

        input.dataset.quantityReady = "true";
        input.setAttribute("inputmode", "numeric");

        if (!input.hasAttribute("min")) {
            input.min = "1";
        }

        if (!input.hasAttribute("step")) {
            input.step = "1";
        }

        input.addEventListener("input", () => {
            const rawValue = input.value.trim();

            if (rawValue === "") {
                input.setCustomValidity("");
                return;
            }

            const value = Number(rawValue);
            const min = input.min === ""
                ? 1
                : Number(input.min);

            const max = input.max === ""
                ? Number.POSITIVE_INFINITY
                : Number(input.max);

            if (
                !Number.isInteger(value) ||
                value < min ||
                value > max
            ) {
                const maximumMessage =
                    max === Number.POSITIVE_INFINITY
                        ? "the available limit"
                        : String(max);

                input.setCustomValidity(
                    `Enter a whole number between ${min} and ${maximumMessage}.`
                );
            } else {
                input.setCustomValidity("");
            }
        });

        input.addEventListener("change", () => {
            if (input.value.trim() === "") return;

            const value = Number(input.value);
            const min = input.min === ""
                ? 1
                : Number(input.min);

            const max = input.max === ""
                ? Number.POSITIVE_INFINITY
                : Number(input.max);

            if (Number.isInteger(value)) {
                input.value = String(
                    Math.max(min, Math.min(max, value))
                );
            }

            input.setCustomValidity("");
        });
    });
}

/* =========================================================
   5. ADD-TO-CART FEEDBACK
   ========================================================= */

/*
   Add data-add-to-cart or class="add-to-cart-form"
   to the add-to-cart form to enable this behavior.

   The form still submits normally to Django.
*/

function initializeAddToCartFeedback() {
    const forms = document.querySelectorAll(
        'form[data-add-to-cart], form.add-to-cart-form'
    );

    forms.forEach((form) => {
        if (form.dataset.feedbackReady === "true") return;

        form.dataset.feedbackReady = "true";

        form.addEventListener("submit", (event) => {
            if (!form.checkValidity()) return;

            const button = form.querySelector(
                'button[type="submit"], input[type="submit"]'
            );

            if (!button || button.disabled) return;

            const originalText = button.tagName === "INPUT"
                ? button.value
                : button.textContent;

            button.disabled = true;

            if (button.tagName === "INPUT") {
                button.value = "Adding…";
            } else {
                button.textContent = "Adding…";
            }

            // Restore the control if navigation does not occur.
            window.setTimeout(() => {
                if (!button.isConnected) return;

                button.disabled = false;

                if (button.tagName === "INPUT") {
                    button.value = originalText;
                } else {
                    button.textContent = originalText;
                }
            }, 5000);
        });
    });
}

/* =========================================================
   6. PREVENT ACCIDENTAL DOUBLE FORM SUBMISSIONS
   ========================================================= */

/*
   Enable on selected forms with:

   <form data-prevent-double-submit="true">

   Useful for registration, login, and checkout.
*/

function initializeFormSubmissionProtection() {
    const forms = document.querySelectorAll(
        'form[data-prevent-double-submit="true"]'
    );

    forms.forEach((form) => {
        if (form.dataset.submissionProtectionReady === "true") {
            return;
        }

        form.dataset.submissionProtectionReady = "true";

        form.addEventListener("submit", (event) => {
            // Let native HTML validation run first.
            if (!form.checkValidity()) return;

            // Stop repeated submissions from this form.
            if (form.dataset.submitting === "true") {
                event.preventDefault();
                return;
            }

            form.dataset.submitting = "true";

            const controls = form.querySelectorAll(
                'button[type="submit"], input[type="submit"]'
            );

            controls.forEach((control) => {
                // Do not modify a control that was already disabled.
                if (control.disabled) return;

                control.dataset.originalText =
                    control.tagName === "INPUT"
                        ? control.value
                        : control.textContent;

                control.disabled = true;

                const loadingText =
                    control.dataset.loadingText || "Please wait…";

                if (control.tagName === "INPUT") {
                    control.value = loadingText;
                } else {
                    control.textContent = loadingText;
                }
            });
        });
    });
}

/* =========================================================
   7. BROKEN PRODUCT IMAGE FALLBACK
   ========================================================= */

/*
   Example:

   <img
       src="{{ product.image.url }}"
       data-image-fallback="/static/images/product-placeholder.png"
       alt="{{ product.name }}">
*/

function initializeImageFallbacks() {
    const images = document.querySelectorAll(
        "img[data-image-fallback]"
    );

    images.forEach((image) => {
        if (image.dataset.fallbackReady === "true") return;

        image.dataset.fallbackReady = "true";

        image.addEventListener(
            "error",
            () => {
                const fallback = image.dataset.imageFallback;

                if (fallback) {
                    const fallbackUrl = new URL(
                        fallback,
                        window.location.href
                    ).href;

                    // Avoid an infinite fallback loop.
                    if (image.src !== fallbackUrl) {
                        image.src = fallbackUrl;
                        return;
                    }
                }

                image.hidden = true;

                const wrapper = image.parentElement;

                if (
                    wrapper &&
                    !wrapper.querySelector(".image-fallback-message")
                ) {
                    const message = document.createElement("span");

                    message.className = "image-fallback-message";
                    message.textContent = "Image unavailable";
                    message.setAttribute("role", "img");
                    message.setAttribute(
                        "aria-label",
                        "Product image unavailable"
                    );

                    wrapper.appendChild(message);
                }
            },
            { once: true }
        );
    });
}
