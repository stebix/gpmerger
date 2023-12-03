<!-- GETTING STARTED -->
# gpmerger

`gpmerger` is a small Python CLI utility to merge chaptered GoPro MP4 video files.
Humble highlights:

* auto-detect and merge chaptered video files in a directory with pretty terminal summary
* preserve gyroscopic metadata streams for stabilization postprocessing (e.g. via [GyroFlow](https://gyroflow.xyz/))

## Prerequisites

`gpmerger` uses Python version 3.11 and [`rich`](https://github.com/Textualize/rich) for pretty terminal visualization.

## Installation

You can clone and use the scripts as-is. Make sure to use in an Python environment fitting the above criteria.
The heavy lifting in terms of stitching MP4 files together is either done by `FFMPEG` or `mp4merge`.
You thus need to install one or both to use the respective program as a merging backend.

* `FFMPEG` : [Download](https://ffmpeg.org/download.html)
* `mp4merge` : [Download](https://github.com/gyroflow/mp4-merge/releases)

Then you will have to set the installation path of the executables in the `conf.toml`
configuration file.

```python
[binaries]
FFMPEG = "~/your/path/to/ffmpeg.exe"
MP4MERGE = "~/your/path/to/mp4merge.exe"
```

<!-- ROADMAP -->
## Roadmap

* [ ] Improve installation
  * [ ] Auto-install core binaries or detect from path/env ?
* [ ] Expand logging
  * [ ] More log messages
  * [ ] Option for log file saving
* [ ] Add intra-file merging feedback or progress reporting

<!-- LICENSE -->
## License

Distributed under the MIT License. See `LICENSE.txt` for more information.

<!-- CONTACT -->
## Contact

Jannik Stebani ||
Project Link: [https://github.com/stebix/gpmerger](https://github.com/stebix/gpmerger)

<!-- ACKNOWLEDGMENTS -->
## Acknowledgments

FFMPEG project - incredible value for video codec infrastructure
GyroFlow project - incredible tooling for stabilization postprocessing via optical flow and gyroscopic metadata

* [FFMPEG](https://ffmpeg.org/)
* [GyroFlow](https://github.com/gyroflow/gyroflow)