# Floating Bar

A full [Omarchy](https://omarchy.org) bar replacement (`"kind": "bar"`): the
stock bar, floating off the top (or left/right/bottom) of the screen with
rounded corners instead of spanning edge-to-edge.

The floating gap isn't a fixed number — it's read from Hyprland's own
`general:gaps_out` at startup, so the space around the bar matches the gap
Hyprland already puts between windows and the screen edge instead of
introducing a second, inconsistent gap value.

## Install

```bash
omarchy plugin add https://github.com/Charlieras262/omarchy-floating-bar.git --enable
```

`omarchy plugin update` later pulls new versions the same way any
git-managed plugin does.

## Configure

Optional, set on the bar's own entry in `~/.config/omarchy/shell.json`
(same place `position` and `transparent` already live):

```json
{
  "bar": {
    "id": "charlieras262.floating-bar",
    "cornerRadius": 14,
    "floatGap": 12
  }
}
```

| Key | Type | Default | Description |
|---|---|---|---|
| `cornerRadius` | number (px) | `14` | Corner radius of the floating bar. |
| `floatGap` | number (px) | *(auto)* | Gap between the bar and the screen edges it floats away from. If omitted, it's read once at startup from `hyprctl getoption general:gaps_out` — set it explicitly to override that. |

The bar is anchored to one edge (`position: "top"` by default, same as
stock). The gap applies to the anchored edge and both perpendicular sides;
the edge *opposite* `position` gets none, since that's the side already
facing Hyprland's own window-to-window gap — adding floatGap there too
would make that one side look bigger than the other three.

## Why this needs a workaround, and when it stops needing one

Cloning any `"kind": "bar"` plugin in Omarchy 4.0.0-1 fails to render at
all, even completely unedited — filed as
[basecamp/omarchy#8007](https://github.com/basecamp/omarchy/issues/8007).
The cause: a cloned bar loads through `Loader.source` (a URL), which can't
supply QML `required property` values at construction the way the built-in
bar's `sourceComponent` can — `configureBar()` in `shell.qml` only sets
`omarchyPath`, `barWidgetRegistry`, and `barConfig` shortly *after*
construction, too late for `required`.

This plugin works around it: those three properties in `Bar.qml` get
inline defaults instead of `required`, since `configureBar()` still sets
the real values immediately after and nothing reads them before that.

[basecamp/omarchy#8146](https://github.com/basecamp/omarchy/pull/8146)
fixes this properly upstream (passing the properties through
`Loader.setSource(url, initialProperties)`). Once that ships in a stable
Omarchy release, this plugin's workaround becomes redundant — check the
issue/PR status if a future Omarchy update seems to double-apply something
or warns about the properties being both set and required.

## License

MIT — see [LICENSE](LICENSE).
