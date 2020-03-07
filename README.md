# Daily Chess Puzzle by Lichess

This is a Slack app that posts a daily chess puzzle from lichess.org to the channel in which the app is installed.

It is currently deployed to Amazon Web Services using:

* AWS Lambda (running Python 3.8)
* Amazon DynamoDB (datastore)
* Amazon Route 53 (domain registrar and DNS)
* Application Load Balancer (targeting AWS Lambda functions)
* Amazon CloudWatch Events (cron)

## Getting Started

Don't expect to run this locally or deploy it anywhere without modifications.

## License

This project is licensed under the AGPL license - see the [LICENSE.md](LICENSE.md) file for details

## Acknowledgments

* https://github.com/ornicar/lila