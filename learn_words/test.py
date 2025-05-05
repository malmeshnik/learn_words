
import logging
from playwright.sync_api import sync_playwright  # Используем синхронную версию Playwright
# from undetected_playwright import stealth_sync

import time

logger = logging.getLogger(__name__)
# Настройка логирования
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

with sync_playwright() as pw:
            browser_args = [
                "--disable-blink-features=AutomationControlled",
                # "--disable-features=IsolateOrigins",
                # "--disable-site-isolation-trials",
                # "--no-sandbox",
                # "--disable-setuid-sandbox",
                # "--disable-dev-shm-usage",
                # "--disable-accelerated-2d-canvas",
                # "--no-first-run",
                # "--no-zygote",
                # "--disable-gpu",
                # "--lang=uk-UA,uk;q=0.9,ru;q=0.8,en-US;q=0.7,en;q=0.6",
                # "--accept-lang=uk-UA,uk;q=0.9,ru;q=0.8,en-US;q=0.7,en;q=0.6"
            ]

            browser = pw.chromium.launch(
                channel="chrome",
                headless=True,  # Для отладки можно поставить False
                args=browser_args,
                slow_mo=50,
            )
            # 1) Создаём контекст с заголовками из Request Headers
            context = browser.new_context(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
                viewport={"width": 1920, "height": 1080},
                locale="en-US",
                extra_http_headers={
                    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
                    "accept-encoding": "gzip, deflate, br, zstd",
                    "accept-language": "en-US,en;q=0.9,uk;q=0.8",
                    "cache-control": "max-age=0",
                    # "sec-ch-ua-platform": "Windows",
                    
                    # "referer": "https://freelancehunt.com/profile/login",
                    # "upgrade-insecure-requests": "1",
                    # "sec-fetch-dest": "document",
                    # "sec-fetch-mode": "navigate",
                    # "sec-fetch-site": "same-origin",
                    # "sec-fetch-user": "?1",
                    # "te": "trailers",
                }
            )

            # 2) Прописиваем куки из вашего скрина
            #    Обратите внимание: разбиваем длинную строку на отдельные объекты
            cookies = [
                {
                    "name": "cf_clearance",
                    "value": "wRy8zk9ahCg6DLPl3CELHzZeG1k_eYf5LPNHD42b6II-1744700408-1.2.1.1-4he9vi.9fjPayFK3CeON4xgMdDdKdQI7BjCGrXMv5sP6cU4Is6fCmHLfgizZS5Wv7crOvDFnA_PvkI7Ztgb1DgdDsYOZUNTMJ.bzWmO2IXTSW3fagAYM3U8fym8PxAxHtBmTGTg9hEdpyLNQ3Ara5T2ew2fazdJwriYJd53NLmlQ1SXjM3Q.oNVVvhW9zgn7l20y6ysogdN7ezjKjD_4S562Cf2CtEJ_h.ojXtdsMlfAwzVTEh5Meu3nE_q.fbXySJM2ozmwAEefa9r2ga3q7lubE0cgiDCo7lP8cMlbVh2DxW13sokWWZdYhoxBhdnw8XQ6xNBaMFM9VMQeI5jX6ZMwyEv0xj4ModO2GyhW1BWAmOi.EbltLKa1BNbuhehI",
                    "domain": "freelancehunt.com",
                    "path": "/",
                    "httpOnly": True,
                    "secure": True,
                    "sameSite": "Lax",
                },
                {
                    "name": "cookieyes-consent",
                    "value": "consentid:Rk9ITEw0a09RVUx5YWFyRUFOaUtFZ3NaT2RjNTdEbGU,consent:yes,action:no,necessary:yes,functional:yes,analytics:yes,performance:yes,advertisement:yes,other:yes",
                    "domain": "freelancehunt.com",
                    "path": "/",
                },
                {
                    "name": "_ga",
                    "value": "GA1.1.1931416852.1737191794",
                    "domain": "freelancehunt.com",
                    "path": "/",
                }
            ]
            context.add_cookies(cookies)

            page = context.new_page()

            # stealth_sync(page)

            # page.add_init_script("""
            #     // Маскируем webdriver
            #     Object.defineProperty(navigator, 'webdriver', {
            #         get: () => false
            #     });
                
            #     // Подделываем navigator.plugins
            #     Object.defineProperty(navigator, 'plugins', {
            #         get: () => {
            #             return {
            #                 length: 5,
            #                 item: () => { return {}; },
            #                 namedItem: () => { return {}; },
            #                 refresh: () => {},
            #                 [Symbol.iterator]: function* () {
            #                     yield { description: "Chrome PDF Plugin", filename: "internal-pdf-viewer", name: "Chrome PDF Plugin" };
            #                     yield { description: "Chrome PDF Viewer", filename: "mhjfbmdgcfjbbpaeojofohoefgiehjai", name: "Chrome PDF Viewer" };
            #                     yield { description: "Native Client", filename: "internal-nacl-plugin", name: "Native Client" };
            #                 }
            #             };
            #         }
            #     });
                
            #     // Подделываем userAgent для Windows
            #     Object.defineProperty(navigator, 'userAgent', {
            #         get: () => "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
            #     });
                
            #     // Подделываем platform
            #     Object.defineProperty(navigator, 'platform', {
            #         get: () => "Win32"
            #     });
                
            #     // Подделываем languages
            #     Object.defineProperty(navigator, 'languages', {
            #         get: () => ["uk-UA", "uk", "ru", "en-US", "en"]
            #     });
                
            #     // Добавляем определение для window.chrome
            #     window.chrome = {
            #         app: {
            #             isInstalled: false,
            #             InstallState: { DISABLED: 'disabled', INSTALLED: 'installed', NOT_INSTALLED: 'not_installed' },
            #             RunningState: { CANNOT_RUN: 'cannot_run', READY_TO_RUN: 'ready_to_run', RUNNING: 'running' }
            #         },
            #         runtime: {
            #             OnInstalledReason: {
            #                 CHROME_UPDATE: 'chrome_update',
            #                 INSTALL: 'install',
            #                 SHARED_MODULE_UPDATE: 'shared_module_update',
            #                 UPDATE: 'update'
            #             },
            #             OnRestartRequiredReason: {
            #                 APP_UPDATE: 'app_update',
            #                 OS_UPDATE: 'os_update',
            #                 PERIODIC: 'periodic'
            #             },
            #             PlatformArch: {
            #                 ARM: 'arm',
            #                 ARM64: 'arm64',
            #                 MIPS: 'mips',
            #                 MIPS64: 'mips64',
            #                 X86_32: 'x86-32',
            #                 X86_64: 'x86-64'
            #             },
            #             PlatformNaclArch: {
            #                 ARM: 'arm',
            #                 MIPS: 'mips',
            #                 MIPS64: 'mips64',
            #                 X86_32: 'x86-32',
            #                 X86_64: 'x86-64'
            #             },
            #             PlatformOs: {
            #                 ANDROID: 'android',
            #                 CROS: 'cros',
            #                 LINUX: 'linux',
            #                 MAC: 'mac',
            #                 OPENBSD: 'openbsd',
            #                 WIN: 'win'
            #             },
            #             RequestUpdateCheckStatus: {
            #                 NO_UPDATE: 'no_update',
            #                 THROTTLED: 'throttled',
            #                 UPDATE_AVAILABLE: 'update_available'
            #             }
            #         }
            #     };
                
            #     // Обфусцировано для автоматизации
            #     const newProto = navigator.__proto__;
            #     delete newProto.webdriver;
            #     navigator.__proto__ = newProto;
                
            #     // Подделываем разрешение экрана (часто проверяется)
            #     Object.defineProperty(window.screen, 'width', { get: () => 1920 });
            #     Object.defineProperty(window.screen, 'height', { get: () => 1080 });
            #     Object.defineProperty(window.screen, 'availWidth', { get: () => 1920 });
            #     Object.defineProperty(window.screen, 'availHeight', { get: () => 1040 });
            #     Object.defineProperty(window.screen, 'colorDepth', { get: () => 24 });
            #     Object.defineProperty(window.screen, 'pixelDepth', { get: () => 24 });
                
            #     // Эмуляция функций для событий мыши
            #     const originalQuery = document.querySelector;
            #     document.querySelector = function(...args) {
            #       const element = originalQuery.apply(document, args);
            #       if (element === null) {
            #         return null;
            #       }
            #       element.scrollIntoView = function() { };
            #       return element;
            #     };
            # """)

            # Логин в Freelancehunt через /profile/login
            logger.info("🔑 Logging in to Freelancehunt...")
            page.goto("https://freelancehunt.com", wait_until="load")
            logging.info(f'{page.url} - {page.title()}')
            # page.fill("input[name='login']", account.username)
            # page.fill("input[name='password']", account.password)
            page.click("button:has-text('Войти')")
            context.storage_state(path="state.json")
