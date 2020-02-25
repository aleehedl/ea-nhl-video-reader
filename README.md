# EA NHL Video analyzer

## Prerequisites

Docker and Docker compose need to be installed in order to run the application.


## Usage

### Video analysis
The Tensoflow model required in order to use the classifier for video stream. This can be
created by training or used a pretrained model. A pretrained model can downloaded from:
https://drive.google.com/open?id=1jYaGyjpTR7gRpY4QQLzLQxbzh8RV5b2o


To run the video analyzer for a YouTube link, run:

```bash
docker-compose run --rm app ./video_analyzer.py https://www.youtube.com/watch?v=MjhNIDqOO5Q
```

To run the video analyzer for a local video file, run:

```bash
docker-compose run --rm app ./video_analyzer.py <video_path>
```

Output is an array of (event time, class)-tuples. Example:
```python
[
  (1, 'game'),
  (2, 'game'),
  # ...
  (1000, 'goal'),
  # ...
  (1600, 'results'),
]
```

**TODO:** Do something useful with the classes.

### Image classification model training

Training data expects a root path containing images in three adjacent folders named `train` `val` `test`.
Example dataset can be downloaded from: https://drive.google.com/open?id=1hlDgZ2pVPAmMbXuxpyrgv-i9sUF89Q7U

Run training:

```bash
docker-compose run --rm app ./image_classifier.py train <data_path>
```

### Data extractor for results page
Use docker-compose to run the extractor:

```bash
docker-compose run --rm app ./stat_extractor.py examples/NASC_Turku_21-4_screenshot.png
```

This outputs the extracted stats into a csv file to `out` directory. Example output:

```csv
Stat,Away,Home
Team,DAL,COL
Goals,2,4
Shots,20,19
Hits,99,15
Time on attack,06:09,08:11
Passing,58.6%,76.4%
Faceoffs won,10,15
Penalty minutes,08:00,04:00
Powerplays,1/2,1/4
Powerplay minutes,01:48,05:29
Shorthanded goals,0,00
```

## Contributing
Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

Please make sure to update tests as appropriate.

## License
[MIT](https://choosealicense.com/licenses/mit/)
