// Stage A of the Japanese room: clear it, carve it, then floor it.
//
// The canvas is a fixed 30x22 with walls on the border, so "a small room" is a
// partition inside it, not a smaller canvas. 10 wide x 8 tall in the top-left,
// which is exactly 5 x 4 of LimeZu's 2x2 tatami with nothing left over.
//
// The clear pass covers the OLD 14x12 footprint too, so re-running this over a
// 7x6 room leaves no orphan wall out at x=15 / y=14.
(function () {
  var out = { removed: 0, walls: 0, tatami: 0, errors: [] };

  var objs = (cjx.describe().objects || []);
  for (var i = 0; i < objs.length; i++) {
    var r = cjx.remove(objs[i].id);
    if (r && r.error) out.errors.push(["remove", objs[i].id, r.error]);
    else out.removed++;
  }

  for (var y = 2; y <= 14; y++) {
    for (var x = 1; x <= 15; x++) cjx.paint(x, y, "floor");
  }

  for (var y = 2; y <= 10; y++) { cjx.paint(11, y, "wall"); out.walls++; }
  for (var x = 1; x <= 11; x++) { cjx.paint(x, 10, "wall"); out.walls++; }
  cjx.paint(11, 6, "door");

  // Anchored by its bottom-left tile, so a 2x2 mat placed at y covers y-1 and y.
  for (var ty = 3; ty <= 9; ty += 2) {
    for (var tx = 1; tx <= 9; tx += 2) {
      var r = cjx.place("japanese_interiors/2", tx, ty, { rug: true });
      if (r && r.error) out.errors.push([tx, ty, r.error, r.hint]);
      else out.tatami++;
    }
  }
  return JSON.stringify(out);
})()
