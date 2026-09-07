// Stage B: two candidate seatings side by side, and the corners.
//
// Whether a zaisu faces the table is not knowable from the sheet -- the pack
// names nothing and a floor chair has no obvious front. So put both candidates
// in the same room and look at them, instead of arguing about which is right.
//
// Everything sits inside the 5x4 room: x 1..10, y 2..9, door at (11,6).
(function () {
  var out = { placed: [], errors: [] };
  function P(piece, x, y, opts) {
    var r = cjx.place(piece, x, y, opts || {});
    if (r && r.error) out.errors.push([piece, x, y, r.error, r.hint]);
    else out.placed.push([piece, x, y, r && r.id]);
    return r;
  }

  // candidate A: the artist's own two-seat kotatsu, one object
  P("japanese_interiors/129", 2, 6);

  // candidate B: a plain low table with a zaisu above and below it.
  // The pack draws a zaisu left-aligned in its tile, so both need the nudge.
  var a = P("japanese_interiors/121", 7, 5, { owner: "Celeste" });
  P("japanese_interiors/23", 7, 6);
  var b = P("japanese_interiors/122", 7, 7, { owner: "Juxtapo" });
  if (a && a.id) cjx.nudge(a.id, 16, 4);
  if (b && b.id) cjx.nudge(b.id, 16, -14);

  // the corners: green, light, one alcove each, scrolls on the top wall
  P("japanese_interiors/58", 1, 3, { blockers: false });   // bonsai, top-left
  P("japanese_interiors/57", 10, 3, { blockers: false });  // bonsai, top-right
  P("japanese_interiors/17", 1, 9, { blockers: false });   // stone lantern
  P("japanese_interiors/71", 3, 3, { blockers: false });   // alcove
  P("japanese_interiors/69", 8, 3, { blockers: false });   // alcove
  P("japanese_interiors/105", 4, 1, { blockers: false });  // hanging scroll
  P("japanese_interiors/106", 7, 1, { blockers: false });  // hanging scroll
  P("japanese_interiors/111", 10, 6, { blockers: false }); // slippers by the door

  return JSON.stringify(out);
})()
