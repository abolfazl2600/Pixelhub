{{flutter_js}}
{{flutter_build_config}}

function showBootstrapError() {
  const status = document.getElementById('bootstrap-status');
  if (!status) return;
  status.replaceChildren();
  const message = document.createElement('p');
  message.textContent = 'برنامه بارگذاری نشد. اتصال و پشتیبانی مرورگر را بررسی کنید.';
  const retry = document.createElement('button');
  retry.textContent = 'تلاش دوباره';
  retry.addEventListener('click', () => window.location.reload());
  status.append(message, retry);
}

_flutter.loader.load({
  onEntrypointLoaded: async function (engineInitializer) {
    try {
      const appRunner = await engineInitializer.initializeEngine();
      await appRunner.runApp();
      document.getElementById('bootstrap-status')?.remove();
    } catch (_) {
      showBootstrapError();
    }
  },
}).catch(showBootstrapError);
