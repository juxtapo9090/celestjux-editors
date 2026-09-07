// A small bathroom tucked into the map's bottom-right corner.
//
// It uses the canvas's own east and south borders as two of its walls, so only
// the north and west sides are carved -- a room in a corner should look like it
// belongs to the building, not like a box parked against it.
//
// The north wall is two rows because that is what LimeZu's wall art is: a top
// course carrying the rail and a bottom course carrying the baseboard.
(function () {
  var out = { walls: 0, floor: null, errors: [] };

  for (var y = 16; y <= 20; y++) { cjx.paint(24, y, "wall"); out.walls++; }
  for (var y = 16; y <= 17; y++) {
    for (var x = 24; x <= 28; x++) { cjx.paint(x, y, "wall"); out.walls++; }
  }
  cjx.paint(26, 16, "door");
  cjx.paint(26, 17, "door");

  out.floor = cjx.floor(25, 18, 28, 20, "floor/56");
  if (out.floor && out.floor.error) out.errors.push(out.floor);
  return JSON.stringify(out);
})()
