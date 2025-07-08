// favorite.js
const SVG_FILLED = `
<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" fill="yellow" stroke="black" stroke-width="2" viewBox="0 0 24 24">
  <path d="M12 .587l3.668 7.568L24 9.423l-6 5.847L19.335 24
           12 19.77 4.665 24 6 15.27 0 9.423l8.332-1.268z"/>
</svg>`;
const SVG_OUTLINE = `
<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" fill="none" stroke="black" stroke-width="2" viewBox="0 0 24 24">
  <path d="M12 .587l3.668 7.568L24 9.423l-6 5.847L19.335 24
           12 19.77 4.665 24 6 15.27 0 9.423l8.332-1.268z"/>
</svg>`;

document.addEventListener('DOMContentLoaded', () => {
  document.querySelectorAll('.fav-btn').forEach(btn => {
    btn.addEventListener('click', e => {
      e.preventDefault();
      const id = btn.dataset.id;

      // 1) いったん即時にUIをトグル
      const nowFav = btn.classList.contains('filled');
      const newFav = !nowFav;
      btn.classList.toggle('filled', newFav);
      btn.classList.toggle('outline', !newFav);
      btn.innerHTML = newFav ? SVG_FILLED : SVG_OUTLINE;

      // 2) サーバーに状態をPOST（非同期）
      fetch(`/favorite/${id}`, { method: 'POST' })
        .then(r => r.json())
        .then(data => {
          // サーバー状態とズレがあれば再修正
          if (data.is_favorite !== newFav) {
            btn.classList.toggle('filled', data.is_favorite);
            btn.classList.toggle('outline', !data.is_favorite);
            btn.innerHTML = data.is_favorite ? SVG_FILLED : SVG_OUTLINE;
          }
        })
        .catch(err => {
          console.error(err);
          // エラー時は元に戻す
          btn.classList.toggle('filled', nowFav);
          btn.classList.toggle('outline', !nowFav);
          btn.innerHTML = nowFav ? SVG_FILLED : SVG_OUTLINE;
        });
    });
  });
});
