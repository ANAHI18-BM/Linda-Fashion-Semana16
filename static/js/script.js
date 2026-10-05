document.querySelectorAll('form[data-confirmar]').forEach(form => {
  form.addEventListener('submit', event => { if (!confirm(form.dataset.confirmar)) event.preventDefault(); });
});
const buscar = document.getElementById('buscar');
if (buscar) buscar.addEventListener('input', () => {
  const texto = buscar.value.toLocaleLowerCase();
  document.querySelectorAll('#registros tr').forEach(row => { row.hidden = !row.textContent.toLocaleLowerCase().includes(texto); });
});
