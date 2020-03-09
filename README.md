# Daily Chess Puzzle by Lichess

This is a Slack app that posts a daily chess puzzle from lichess.org to the channel in which the app is installed.

It is currently deployed to Amazon Web Services using:

* AWS Lambda (running Python 3.8)
* Amazon DynamoDB (serverless NoSQL datastore)
* Amazon Route 53 (domain registrar and DNS)
* AWS Certificate Manager (SSL/TLS certificate)
* Application Load Balancer (targeting AWS Lambda functions)
* Amazon CloudWatch Events (cron)
* Amazon CloudWatch Logs (logging)
* AWS X-Ray (monitoring)

The aws_xray_sdk package is installed via an AWS Lambda layer.

## Getting Started

Don't expect to run this locally or deploy it anywhere without modifications.

## License

This project is licensed under the AGPL license - see the [LICENSE.md](LICENSE.md) file for details

## Acknowledgments

* https://github.com/ornicar/lila