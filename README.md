# EA NHL End of Game stats reader

## Prerequisites

Docker and Docker compose need to be installed in order to run the application.


## Usage

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
