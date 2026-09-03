---
name: New game
about: Submit a new game for inclusion in the Defold Showcase page on www.defold.com/showcase
title: ''
labels: ''
assignees: ''

---

```json
{
    "name": "",
	"description": "",
    "url": "",
    "developer": "",
    "publisher": "",
    "releasedate": "",
    "platforms": "iOS,Android,macOS,Windows,Linux,HTML5,Steam,Poki,itch.io,Kongregate,Facebook Instant Games,...",
    "images": {
        "full": "",
        "half": "",
        "third": ""
    }
}
```

* `name` - (REQUIRED) Name of the Defold game.
* `description` - (REQUIRED) Text describing the game.
* `url` - (REQUIRED) Link to a game or store page.
* `developer` - (REQUIRED) Name of the developer/studio.
* `publisher` - (OPTIONAL) Name of the publisher.
* `releasedate` - (REQUIRED) Date of release (month year, eg April 2020, or just year).
* `platforms` - (REQUIRED) The platforms where the game can be played. Comma separated list.
* `images` - (REQUIRED) Filenames of the submitted images. WebP is preferred, but PNG/JPG source images are accepted on the issue and will be optimized and converted to WebP when preparing the repository PR.
  * `full` - Filename for the full-width card. Target size: 2000x750. Name: `game-name-full.webp`.
  * `half` - Filename for the two-column/mobile card. Target size: 1200x600. Name: `game-name-half.webp`.
  * `third` - Filename for carousel/compact cards. Target size: 800x600. Name: `game-name-third.webp`.

Note: The Defold team decides whether to accept a submitted game and where it should appear when preparing and reviewing the repository PR..
