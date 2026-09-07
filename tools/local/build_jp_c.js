// Stage C: the genkan -- an entrance porch hanging off the shoji door.
//
// LimeZu's own version is a stone annex on the building's left wall, but our
// room sits in the canvas's top-left corner and there is nothing to its left,
// so the porch hangs below the shoji and runs west instead. Abang's call.
//
// The floor is left alone on purpose: the canvas's default floor is already
// grey stone tiles, which is exactly the genkan material. There is still no
// floor-material system, so a painted floor is the one thing this cannot do.
(function () {
  var out = { walls: 0, placed: [], errors: [] };
  function P(piece, x, y) {
    var r = cjx.place(piece, x, y, { blockers: false });
    if (r && r.error) out.errors.push([piece, x, y, r.error, r.hint]);
    else out.placed.push([piece, x, y, r && r.id]);
  }

  // Porch interior is x 1..5, y 12..13. The room's own bottom wall (y 10-11)
  // is already its north side, so only the east and south need carving.
  for (var y = 12; y <= 15; y++) { cjx.paint(6, y, "wall"); out.walls++; }
  for (var y = 14; y <= 15; y++) {
    for (var x = 0; x <= 6; x++) { cjx.paint(x, y, "wall"); out.walls++; }
  }
  // The way out, west, towards where the outdoors will be.
  cjx.paint(0, 12, "door");
  cjx.paint(0, 13, "door");

  P("japanese_interiors/60", 4, 12);   // wooden sill under the shoji
  P("japanese_interiors/60", 5, 12);
  P("japanese_interiors/111", 3, 13);  // slippers, off the step
  P("japanese_interiors/56", 1, 12);   // a pot in each far corner
  P("japanese_interiors/56", 5, 13);

  return JSON.stringify(out);
})()
