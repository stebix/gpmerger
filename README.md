<!-- GETTING STARTED -->
# gpmerger

`gpmerger` is a small Python CLI utility to merge chaptered GoPro MP4 video files.
Humble highlights:

* auto-detect and merge chaptered video files in a directory with pretty terminal summary
* preserve gyroscopic metadata streams for stabilization postprocessing (e.g. via [GyroFlow](https://gyroflow.xyz/))

## Prerequisites

`gpmerger` uses Python version 3.11 and [`rich`](https://github.com/Textualize/rich) for pretty terminal visualization.

<!-- ROADMAP -->
## Roadmap

* [ ] Expand logging
  * [ ] More log messages
  * [ ] Option for log file saving
* [ ] Add intra-file merging feedback or progress reporting

<!-- LICENSE -->
## License

Distributed under the MIT License. See `LICENSE.txt` for more information.

<!-- CONTACT -->
## Contact

Jannik Stebani
Project Link: [https://github.com/stebix/gpmerger](https://github.com/stebix/gpmerger)

<!-- ACKNOWLEDGMENTS -->
## Acknowledgments

FFMPEG project - incredible value for video codec infrastructure
GyroFlow project - incredible tooling for stabilization postprocessing via optical flow and gyroscopic metadata

* [FFMPEG](https://ffmpeg.org/)
* [GyroFlow](https://github.com/gyroflow/gyroflow)