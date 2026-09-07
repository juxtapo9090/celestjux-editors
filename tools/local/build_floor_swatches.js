// Scatter floor materials on the map itself, so a floor is judged at the size
// it will actually be walked on. A swatch sheet flatters everything; four tiles
// beside the real room does not.
//
// Reading order is left to right, top to bottom -- the same order as the list
// in chat, so a patch can be named without writing labels on the floor.
(function () {
  var PICKS = [60, 63, 58,
               5, 69, 2,
               45, 22, 52,
               56, 64, 31];
  var COLS = [13, 18, 23], ROWS = [2, 7, 12, 17], SIZE = 4;
  var out = { laid: [], errors: [] };

  for (var i = 0; i < PICKS.length; i++) {
    var x = COLS[i % 3], y = ROWS[Math.floor(i / 3)];
    var r = cjx.floor(x, y, x + SIZE - 1, y + SIZE - 1, "floor/" + PICKS[i]);
    if (r && r.error) out.errors.push([PICKS[i], x, y, r.error, r.hint]);
    else out.laid.push(["floor/" + PICKS[i], x, y]);
  }
  return JSON.stringify(out);
})()
