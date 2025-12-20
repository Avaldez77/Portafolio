from playwright.sync_api import sync_playwright, TimeoutError
import time
import json
import os
import sys
import traceback

# --- Consola Windows: evita UnicodeEncodeError ---
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass  # en algunos entornos no existe reconfigure

# --------------------------------------------------------------------------------------------
# CONFIG (SANITIZED)
# --------------------------------------------------------------------------------------------
LINKS_FILE = r"\\FILESERVER\Shared\RPA\dash_screenshots\links.json"
SCREENSHOT_DIR = r"\\FILESERVER\Shared\RPA\dash_screenshots\output"

LOGIN_URL = "https://internal.portal.company.com/signin"  # URL genérica
LOGIN_READY_SELECTOR = "css=img"  # selector genérico "cuando login está listo"
POST_LOGIN_ANCHOR = "css=body"    # ancla genérica post-login
DASHBOARD_READY_SELECTOR = "css=body"  # algo estable (ajústalo a tu app real)
ZOOM_FACTOR = 0.75

# Credenciales (NO hardcodear en producción; aquí es demo)
USERNAME_VALUE = "your.username"
PASSWORD_VALUE = "your.password"

# Selectores de inputs/botón (placeholders)
USERNAME_SELECTOR = "css=input[name='username']"
PASSWORD_SELECTOR = "css=input[name='password']"
SUBMIT_SELECTOR = "css=button[type='submit']"


def quiet_render_wait(page, max_checks=10, interval_sec=2.0):
    prev_height = -1
    for _ in range(max_checks):
        height = page.evaluate("document.documentElement.scrollHeight")
        if height == prev_height:
            return
        prev_height = height
        time.sleep(interval_sec)
    time.sleep(1.0)


def safe_print(msg: str):
    try:
        print(msg)
    except Exception:
        try:
            print(msg.encode("utf-8", errors="replace").decode("utf-8", errors="replace"))
        except Exception:
            print("[[print failed]]")


def main():
    # Cargar links
    with open(LINKS_FILE, "r", encoding="utf-8") as f:
        payload = json.load(f)

    # payload puede ser dict o lista con dict adentro
    url_dict = payload[0] if isinstance(payload, list) else payload

    os.makedirs(SCREENSHOT_DIR, exist_ok=True)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)

        # Viewport grande para “ver más”
        context = browser.new_context(
            viewport={"width": 1200, "height": 900},
            device_scale_factor=1.0,
        )

        page = context.new_page()
        safe_print("Abriendo login…")
        page.goto(LOGIN_URL, timeout=120_000)
        page.wait_for_selector(LOGIN_READY_SELECTOR, state="visible", timeout=30_000)

        # Completar credenciales (selectors genéricos)
        safe_print("Ingresando credenciales…")
        page.fill(USERNAME_SELECTOR, USERNAME_VALUE)
        page.fill(PASSWORD_SELECTOR, PASSWORD_VALUE)
        page.click(SUBMIT_SELECTOR)

        # Espera post-login basada en selector
        safe_print("Esperando post-login…")
        try:
            page.wait_for_selector(POST_LOGIN_ANCHOR, state="visible", timeout=60_000)
        except TimeoutError:
            safe_print("Post-login selector no apareció a tiempo; continúo con render silencioso…")

        quiet_render_wait(page)

        # --- ITERAR DASHBOARDS ---
        for key, url in url_dict.items():
            new_page = context.new_page()
            safe_print(f"\n→ Abriendo {key}: {url}")

            try:
                new_page.goto(url, timeout=120_000)

                # Espera por selector del dashboard
                try:
                    new_page.wait_for_selector(DASHBOARD_READY_SELECTOR, state="visible", timeout=60_000)
                except TimeoutError:
                    safe_print("Dashboard selector tardó; aplico espera por render estable…")

                quiet_render_wait(new_page)

                # Espera adicional si la app pinta widgets tarde
                time.sleep(5)

                # Zoom-out
                new_page.evaluate(f"document.documentElement.style.zoom = '{ZOOM_FACTOR}'")
                time.sleep(1.0)

                # Screenshot full page
                out_ok = os.path.join(SCREENSHOT_DIR, f"{key}.png")
                new_page.screenshot(path=out_ok, full_page=True)
                safe_print(f"✔ Capturado: {out_ok}")

            except Exception as e:
                safe_print(f"✘ Error en {key}: {e}")
                safe_print(traceback.format_exc())

                # Screenshot de error
                try:
                    out_err = os.path.join(SCREENSHOT_DIR, f"{key}_error.png")
                    new_page.screenshot(path=out_err, full_page=True)
                    safe_print(f"(Screenshot de error guardado: {out_err})")
                except Exception as e2:
                    safe_print(f"(No se pudo capturar screenshot de error: {e2})")

            finally:
                try:
                    new_page.close()
                except Exception:
                    pass

        safe_print("\nProceso completado.")
        context.close()
        browser.close()


if __name__ == "__main__":
    main()
